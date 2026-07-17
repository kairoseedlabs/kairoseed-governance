#!/usr/bin/env python3
"""Neutral exact-byte parity comparator for KCS-0.2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROFILE = "KCS-0.2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", required=True, type=Path)
    parser.add_argument("--python-results", required=True, type=Path)
    parser.add_argument("--typescript-results", required=True, type=Path)
    return parser.parse_args()


def block(vector_id: str, detail: str) -> None:
    raise SystemExit(f"BLOCK {vector_id}: {detail}")


def mismatch_offset(left: bytes, right: bytes) -> int:
    for offset, (left_byte, right_byte) in enumerate(zip(left, right, strict=False)):
        if left_byte != right_byte:
            return offset
    return min(len(left), len(right))


def index_results(document: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    if document.get("profile") != PROFILE or not isinstance(document.get("results"), list):
        raise SystemExit(f"BLOCK result-envelope: invalid {label} result envelope")
    indexed: dict[str, dict[str, Any]] = {}
    for result in document["results"]:
        if not isinstance(result, dict) or not isinstance(result.get("id"), str):
            raise SystemExit(f"BLOCK result-envelope: invalid {label} result")
        vector_id = result["id"]
        if vector_id in indexed:
            block(vector_id, f"duplicate {label} result")
        indexed[vector_id] = result
    return indexed


def compare_positive(
    golden: dict[str, Any],
    python_result: dict[str, Any],
    typescript_result: dict[str, Any],
) -> None:
    vector_id = golden["id"]
    if python_result.get("status") != "PASS" or typescript_result.get("status") != "PASS":
        block(vector_id, "positive vector did not PASS in both runtimes")

    try:
        expected = bytes.fromhex(golden["expected_utf8_hex"])
        python_bytes = bytes.fromhex(python_result["canonical_utf8_hex"])
        typescript_bytes = bytes.fromhex(typescript_result["canonical_utf8_hex"])
    except (KeyError, TypeError, ValueError):
        block(vector_id, "invalid canonical byte encoding")

    if python_bytes != typescript_bytes:
        block(vector_id, f"byte mismatch at offset {mismatch_offset(python_bytes, typescript_bytes)}")
    if python_bytes != expected:
        block(vector_id, f"golden byte mismatch at offset {mismatch_offset(python_bytes, expected)}")
    if python_result.get("sha256") != golden.get("expected_sha256"):
        block(vector_id, "Python digest mismatch")
    if typescript_result.get("sha256") != golden.get("expected_sha256"):
        block(vector_id, "TypeScript digest mismatch")


def compare_negative(
    golden: dict[str, Any],
    python_result: dict[str, Any],
    typescript_result: dict[str, Any],
) -> None:
    vector_id = golden["id"]
    expected = golden["expected"]
    expected_status = expected.get("status")
    expected_reason = expected.get("reason_code")

    for label, result in (("Python", python_result), ("TypeScript", typescript_result)):
        if result.get("status") != expected_status or result.get("reason_code") != expected_reason:
            block(vector_id, f"{label} BLOCK outcome mismatch")
        if "canonical_utf8_hex" in result or "sha256" in result:
            block(vector_id, f"{label} emitted bytes for BLOCK vector")


def main() -> int:
    args = parse_args()
    fixture = json.loads(args.vectors.read_text(encoding="utf-8"))
    python_document = json.loads(args.python_results.read_text(encoding="utf-8"))
    typescript_document = json.loads(args.typescript_results.read_text(encoding="utf-8"))

    if fixture.get("profile") != PROFILE or not isinstance(fixture.get("vectors"), list):
        raise SystemExit("BLOCK fixture-envelope: invalid golden vector envelope")

    python_results = index_results(python_document, "Python")
    typescript_results = index_results(typescript_document, "TypeScript")
    expected_ids = {vector["id"] for vector in fixture["vectors"]}
    if set(python_results) != expected_ids or set(typescript_results) != expected_ids:
        raise SystemExit("BLOCK result-envelope: result ID set mismatch")

    for vector in fixture["vectors"]:
        vector_id = vector["id"]
        if "expected" in vector:
            compare_negative(vector, python_results[vector_id], typescript_results[vector_id])
        else:
            compare_positive(vector, python_results[vector_id], typescript_results[vector_id])
        print(f"PASS {vector_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
