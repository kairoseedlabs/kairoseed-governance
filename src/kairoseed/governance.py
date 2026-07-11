"""Deterministic policy decision point for KAIROSEED."""

from dataclasses import dataclass
from enum import StrEnum

from .schemas import VerifiedExperimentPacket


class Decision(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class GovernancePolicy:
    allowed_tools: frozenset[str]
    critical_tools: frozenset[str]
    max_resource_budget: int
    require_evidence: bool = True


@dataclass(frozen=True)
class Evaluation:
    decision: Decision
    reasons: tuple[str, ...]
    packet_id: str | None = None
    packet_digest: str | None = None
    requires_human_review: bool = False


def evaluate(packet: VerifiedExperimentPacket, policy: GovernancePolicy) -> Evaluation:
    """Evaluate a VEP without executing its requested capability."""
    errors = packet.validate()
    if errors:
        return Evaluation(Decision.BLOCK, errors)

    packet_id = packet.packet_id
    packet_digest = packet.digest()

    if packet.tool_request not in policy.allowed_tools | policy.critical_tools:
        return Evaluation(
            Decision.BLOCK,
            ("tool is outside policy",),
            packet_id,
            packet_digest,
        )

    if packet.tool_request not in packet.authorization_scope:
        return Evaluation(
            Decision.BLOCK,
            ("tool is outside authorization scope",),
            packet_id,
            packet_digest,
        )

    if packet.resource_budget > policy.max_resource_budget:
        return Evaluation(
            Decision.BLOCK,
            ("resource budget exceeds policy ceiling",),
            packet_id,
            packet_digest,
        )

    if packet.tool_request in policy.critical_tools:
        return Evaluation(
            Decision.WARN,
            ("critical capability requires explicit human authorization",),
            packet_id,
            packet_digest,
            requires_human_review=True,
        )

    if policy.require_evidence and not packet.evidence_references:
        return Evaluation(
            Decision.WARN,
            ("evidence is required before authorization",),
            packet_id,
            packet_digest,
            requires_human_review=True,
        )

    return Evaluation(
        Decision.PASS,
        ("policy requirements satisfied",),
        packet_id,
        packet_digest,
    )
