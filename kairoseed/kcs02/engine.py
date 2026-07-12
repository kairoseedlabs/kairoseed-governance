"""Independent Python implementation of the KCS-0.2 parity profile."""

from __future__ import annotations

import base64
import binascii
import json
import re
import unicodedata
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

PROFILE = "KCS-0.2"
MIN_SAFE_INTEGER = -(2**53 - 1)
MAX_SAFE_INTEGER = 2**53 - 1
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class KCS02Block(ValueError):
    """Deterministic fail-closed outcome."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


def _reject_surrogates(value: str) -> None:
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise KCS02Block("INVALID_UNICODE")


def _normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value < MIN_SAFE_INTEGER or value > MAX_SAFE_INTEGER:
            raise KCS02Block("UNSAFE_INTEGER")
        return value

    if isinstance(value, float):
        raise KCS02Block("UNSUPPORTED_NUMBER")

    if isinstance(value, str):
        _reject_surrogates(value)
        return unicodedata.normalize("NFC", value)

    if isinstance(value, list):
        return [_normalize(item) for item in value]

    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise KCS02Block("NON_STRING_KEY")
            _reject_surrogates(key)
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise KCS02Block("NORMALIZED_KEY_COLLISION")
            normalized[normalized_key] = _normalize(item)
        return normalized

    raise KCS02Block("UNSUPPORTED_TYPE")


def _utf16_sort_key(value: str) -> bytes:
    return value.encode("utf-16-be")


def _render(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(_render(item) for item in value) + "]"
    if isinstance(value, dict):
        entries = []
        for key in sorted(value, key=_utf16_sort_key):
            entries.append(f"{_render(key)}:{_render(value[key])}")
        return "{" + ",".join(entries) + "}"
    raise AssertionError("normalized value escaped the KCS-0.2 domain")


def canonicalize(value: Any) -> bytes:
    """Return the single KCS-0.2 UTF-8 representation or raise KCS02Block."""
    normalized = _normalize(value)
    return _render(normalized).encode("utf-8")


def _validate_base64url(value: Any) -> None:
    if not isinstance(value, str) or not value or not _BASE64URL_RE.fullmatch(value):
        raise KCS02Block("INVALID_SIGNATURE_ENCODING")
    padding = "=" * ((4 - len(value) % 4) % 4)
    try:
        decoded = base64.urlsafe_b64decode(value + padding)
    except (ValueError, binascii.Error) as exc:
        raise KCS02Block("INVALID_SIGNATURE_ENCODING") from exc
    encoded = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    if encoded != value:
        raise KCS02Block("INVALID_SIGNATURE_ENCODING")


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise KCS02Block("INVALID_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise KCS02Block("INVALID_TIMESTAMP") from exc
    return parsed.astimezone(UTC)


def _apply_checks(vector: dict[str, Any], canonical_bytes: bytes) -> None:
    checks = vector.get("checks", {})
    payload = vector.get("input")
    if not isinstance(checks, dict) or not isinstance(payload, dict):
        raise KCS02Block("INVALID_VECTOR")

    signature_field = checks.get("signature_base64url_field")
    if signature_field is not None:
        _validate_base64url(payload.get(signature_field))

    expected_hash = checks.get("expected_signed_content_sha256")
    if expected_hash is not None and sha256(canonical_bytes).hexdigest() != expected_hash:
        raise KCS02Block("SIGNED_CONTENT_MISMATCH")

    if "expires_at" in checks:
        expires_at = _parse_timestamp(payload.get(checks["expires_at"]))
        now = _parse_timestamp(checks.get("now"))
        if now >= expires_at:
            raise KCS02Block("EXPIRED")

    if checks.get("nonce_reused") is True:
        raise KCS02Block("NONCE_REUSED")

    required_audience = checks.get("required_audience")
    if required_audience is not None and payload.get("authorization_audience") != required_audience:
        raise KCS02Block("WRONG_AUDIENCE")

    if checks.get("require_govana_pass") is True:
        if payload.get("govana_decision") != "PASS":
            if payload.get("gat") is not None:
                raise KCS02Block("GOVANA_BLOCK_HAS_GAT")
            raise KCS02Block("GOVANA_BLOCK")


def evaluate_vector(vector: dict[str, Any]) -> dict[str, str]:
    """Evaluate one frozen parity vector without logging its payload."""
    vector_id = vector.get("id")
    if not isinstance(vector_id, str) or not vector_id:
        raise KCS02Block("INVALID_VECTOR")

    try:
        canonical_bytes = canonicalize(vector.get("input"))
        _apply_checks(vector, canonical_bytes)
    except KCS02Block as exc:
        return {"id": vector_id, "status": "BLOCK", "reason_code": exc.reason_code}

    return {
        "id": vector_id,
        "status": "PASS",
        "canonical_utf8_hex": canonical_bytes.hex(),
        "sha256": sha256(canonical_bytes).hexdigest(),
    }
