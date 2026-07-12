from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kairoseed"))

from kcs02.engine import evaluate_vector  # noqa: E402

FIXTURE = json.loads((ROOT / "tests" / "golden_vectors.json").read_text(encoding="utf-8"))
VECTORS = {vector["id"]: vector for vector in FIXTURE["vectors"]}


def assert_block(vector_id: str, reason_code: str) -> None:
    result = evaluate_vector(VECTORS[vector_id])
    assert result == {"id": vector_id, "status": "BLOCK", "reason_code": reason_code}
    assert "canonical_utf8_hex" not in result
    assert "sha256" not in result


def test_tampered_signed_field_blocks() -> None:
    assert_block("tampered-signed-field-block", "SIGNED_CONTENT_MISMATCH")


def test_expired_authorization_blocks() -> None:
    assert_block("expired-timestamp-block", "EXPIRED")


def test_reused_nonce_blocks() -> None:
    assert_block("reused-nonce-block", "NONCE_REUSED")


def test_wrong_audience_blocks() -> None:
    assert_block("wrong-audience-block", "WRONG_AUDIENCE")


def test_govana_block_never_produces_gat() -> None:
    vector = VECTORS["govana-block-produces-no-gat"]
    assert vector["input"]["gat"] is None
    assert_block("govana-block-produces-no-gat", "GOVANA_BLOCK")
