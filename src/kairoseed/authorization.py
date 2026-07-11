"""Authorization evidence produced only after policy evaluation."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from .governance import Decision, Evaluation


@dataclass(frozen=True)
class GovernanceAuthorizationToken:
    packet_id: str
    packet_digest: str
    decision: Decision
    issued_at: datetime
    expires_at: datetime
    evidence_hash: str

    def is_active(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return (
            self.decision is Decision.PASS
            and bool(self.packet_id)
            and bool(self.packet_digest)
            and current < self.expires_at
        )


def issue_token(
    evaluation: Evaluation,
    ttl_seconds: int = 300,
) -> GovernanceAuthorizationToken:
    """Issue evidence only for the exact packet bound to a PASS evaluation."""
    if evaluation.decision is not Decision.PASS:
        raise PermissionError("only PASS evaluations can produce authorization")
    if not evaluation.packet_id or not evaluation.packet_digest:
        raise PermissionError("evaluation is not bound to a verified packet")
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")

    issued_at = datetime.now(UTC)
    material = "|".join(
        (
            evaluation.packet_id,
            evaluation.packet_digest,
            str(evaluation.decision),
            issued_at.isoformat(),
        )
    )
    return GovernanceAuthorizationToken(
        packet_id=evaluation.packet_id,
        packet_digest=evaluation.packet_digest,
        decision=evaluation.decision,
        issued_at=issued_at,
        expires_at=issued_at + timedelta(seconds=ttl_seconds),
        evidence_hash=sha256(material.encode("utf-8")).hexdigest(),
    )
