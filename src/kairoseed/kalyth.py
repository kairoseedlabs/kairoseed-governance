"""KALYTH normative admission contract.

KALYTH defines the governance boundary above the C0 reference gate.  It does
not execute capabilities and it does not turn WARN/BLOCK into authorization.
The contract is intentionally small so that it can be tested independently
from any concrete executor.
"""

from dataclasses import dataclass
from enum import StrEnum

from .c0 import C0, C0Evidence, C0Result
from .governance import Decision, GovernancePolicy
from .schemas import VerifiedExperimentPacket


class AdmissionDecision(StrEnum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"


@dataclass(frozen=True)
class Admission:
    """Immutable governance decision record."""

    decision: AdmissionDecision
    packet_id: str | None
    packet_digest: str | None
    reasons: tuple[str, ...]
    evidence: C0Evidence | None = None

    @property
    def effect_permitted(self) -> bool:
        """Only an approved admission can authorize an effect."""
        return self.decision is AdmissionDecision.APPROVED


class KALYTH:
    """Normative admission facade over the deterministic C0 boundary."""

    def __init__(self, policy: GovernancePolicy) -> None:
        self._c0 = C0(policy)

    def admit(self, packet: VerifiedExperimentPacket) -> Admission:
        """Return an immutable APPROVED/DENIED admission record."""
        result = self._c0.authorize(packet)
        return self._admission_from_result(result)

    def execute(self, packet: VerifiedExperimentPacket, effect) -> Admission:
        """Execute only after C0 returns PASS evidence."""
        result = self._c0.execute(packet, effect)
        return self._admission_from_result(result)

    @staticmethod
    def _admission_from_result(result: C0Result) -> Admission:
        evaluation = result.evaluation
        approved = result.effect_permitted and evaluation.decision is Decision.PASS
        return Admission(
            decision=(
                AdmissionDecision.APPROVED
                if approved
                else AdmissionDecision.DENIED
            ),
            packet_id=evaluation.packet_id,
            packet_digest=evaluation.packet_digest,
            reasons=evaluation.reasons,
            evidence=result.evidence,
        )


def verify_admission(
    packet: VerifiedExperimentPacket, admission: Admission
) -> bool:
    """Verify the admission is bound to the exact packet and PASS evidence."""
    if admission.decision is not AdmissionDecision.APPROVED:
        return False
    if admission.evidence is None:
        return False
    if admission.packet_id != packet.packet_id:
        return False
    if admission.packet_digest != packet.digest():
        return False
    return admission.evidence.packet_digest == packet.digest()
