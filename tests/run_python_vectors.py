#!/usr/bin/env python3
"""Produce neutral KCS-0.2 Python results without logging payload bytes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kairoseed"))

from kcs02.engine import PROFILE, evaluate_vector  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = json.loads(args.vectors.read_text(encoding="utf-8"))
    if fixture.get("profile") != PROFILE or not isinstance(fixture.get("vectors"), list):
        raise SystemExit("BLOCK runner: invalid KCS-0.2 fixture envelope")

    result = {
        "profile": PROFILE,
        "results": [evaluate_vector(vector) for vector in fixture["vectors"]],
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    os.chmod(args.output, 0o600)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
