"""Fail-closed release verification contract.

The pipeline may build an unsigned candidate artifact for testing. It must not
sign, attest, publish, promote, or deploy that candidate as a release artifact
unless every mandatory release control returns an exact PASS for the same
source revision.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from .governance import Decision


class ControlOutcome(StrEnum):
    """Recognized outcomes for a mandatory release control."""

    PASS = "PASS"
    BLOCK = "BLOCK"
    TIMEOUT = "TIMEOUT"
    MISSING = "MISSING"
    UNAUTHORIZED_SKIP = "UNAUTHORIZED_SKIP"
    FLAKY = "FLAKY"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class ReleaseEvidence:
    """Evidence evaluated by the release policy decision point."""

    required_checks: str | None
    evidence_complete: str | None
    authority_valid: str | None
    candidate_source: str | None
    evidence_source: str | None
    authority_source: str | None
    last_approved_release: str | None = None

    @property
    def source_bound(self) -> bool:
        """Return True only when all evidence names one exact source revision."""
        return bool(self.candidate_source) and (
            self.candidate_source == self.evidence_source == self.authority_source
        )


@dataclass(frozen=True)
class ReleaseGateResult:
    """Deterministic release authorization result."""

    decision: Decision
    reasons: tuple[str, ...]
    preserved_release: str | None

    @property
    def release_allowed(self) -> bool:
        """Return True only for complete success against the contract."""
        return self.decision is Decision.PASS

    def as_dict(self) -> dict[str, Any]:
        """Return a stable JSON-domain representation for audit output."""
        return {
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "preserved_release": self.preserved_release,
            "release_allowed": self.release_allowed,
        }


def _exact_pass(value: str | None) -> bool:
    return value == ControlOutcome.PASS.value


def evaluate_release(evidence: ReleaseEvidence) -> ReleaseGateResult:
    """Evaluate release evidence; every non-PASS or unknown state is BLOCK."""
    reasons: list[str] = []

    controls = {
        "RequiredChecksPass": evidence.required_checks,
        "EvidenceComplete": evidence.evidence_complete,
        "AuthorityValid": evidence.authority_valid,
    }
    for name, outcome in controls.items():
        if not _exact_pass(outcome):
            rendered = outcome if outcome is not None else ControlOutcome.MISSING.value
            reasons.append(f"{name} is {rendered}, not PASS")

    if not evidence.source_bound:
        reasons.append("SourceBound is BLOCK")

    if reasons:
        return ReleaseGateResult(
            decision=Decision.BLOCK,
            reasons=tuple(reasons),
            preserved_release=evidence.last_approved_release,
        )

    return ReleaseGateResult(
        decision=Decision.PASS,
        reasons=("defined verification contract satisfied",),
        preserved_release=evidence.last_approved_release,
    )


def _read_evidence(path: Path) -> ReleaseEvidence:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("release evidence must be a JSON object")

    return ReleaseEvidence(
        required_checks=data.get("required_checks"),
        evidence_complete=data.get("evidence_complete"),
        authority_valid=data.get("authority_valid"),
        candidate_source=data.get("candidate_source"),
        evidence_source=data.get("evidence_source"),
        authority_source=data.get("authority_source"),
        last_approved_release=data.get("last_approved_release"),
    )


def main() -> int:
    """Evaluate a release-evidence file and return zero only for PASS."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        result = evaluate_release(_read_evidence(args.evidence))
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        result = ReleaseGateResult(
            decision=Decision.BLOCK,
            reasons=(f"release evidence could not be evaluated: {type(exc).__name__}",),
            preserved_release=None,
        )

    rendered = json.dumps(result.as_dict(), sort_keys=True, separators=(",", ":"))
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result.release_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
