"""Authorization evidence produced only after policy evaluation."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from .governance import Decision, Evaluation


@dataclass(frozen=True)
class GovernanceAuthorizationToken:
    packet_id: str
    decision: Decision
    issued_at: datetime
    expires_at: datetime
    evidence_hash: str

    def is_active(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(UTC)
        return self.decision is Decision.PASS and current < self.expires_at


def issue_token(packet_id: str, evaluation: Evaluation, ttl_seconds: int = 300) -> GovernanceAuthorizationToken:
    if evaluation.decision is not Decision.PASS:
        raise PermissionError("only PASS evaluations can produce authorization")
    issued_at = datetime.now(UTC)
    material = f"{packet_id}|{evaluation.decision}|{issued_at.isoformat()}"
    return GovernanceAuthorizationToken(
        packet_id=packet_id,
        decision=evaluation.decision,
        issued_at=issued_at,
        expires_at=issued_at + timedelta(seconds=ttl_seconds),
        evidence_hash=sha256(material.encode("utf-8")).hexdigest(),
    )
