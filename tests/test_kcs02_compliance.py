from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kairoseed"))

from kcs02.engine import canonicalize, evaluate_vector  # noqa: E402

FIXTURE = json.loads((ROOT / "tests" / "golden_vectors.json").read_text(encoding="utf-8"))
VECTORS = {vector["id"]: vector for vector in FIXTURE["vectors"]}


def test_all_frozen_vectors_match_python_reference() -> None:
    assert FIXTURE["profile"] == "KCS-0.2"
    assert len(VECTORS) == 18

    for vector in FIXTURE["vectors"]:
        result = evaluate_vector(vector)
        if "expected" in vector:
            assert result == {"id": vector["id"], **vector["expected"]}
        else:
            assert result["status"] == "PASS"
            assert result["canonical_utf8_hex"] == vector["expected_utf8_hex"]
            assert result["sha256"] == vector["expected_sha256"]


def test_nfc_equivalent_inputs_have_one_representation() -> None:
    decomposed = canonicalize({"label": "Cafe\u0301"})
    precomposed = canonicalize({"label": "Café"})
    assert decomposed == precomposed


def test_utf16_key_order_places_astral_before_high_bmp() -> None:
    assert canonicalize({"\ue000": 1, "😀": 2}) == b'{"\xf0\x9f\x98\x80":2,"\xee\x80\x80":1}'


def test_arrays_preserve_declared_order() -> None:
    assert canonicalize([3, 1, 2]) == b"[3,1,2]"


def test_reserved_javascript_keys_are_data() -> None:
    result = evaluate_vector(VECTORS["reserved-javascript-keys"])
    assert result["status"] == "PASS"
