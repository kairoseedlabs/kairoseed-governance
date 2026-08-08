"""C0: minimal deterministic authorization boundary.

C0 deliberately stops at the authorization boundary. It does not claim that
TPM signing, kernel isolation, or process execution are atomic with policy
approval. The executor is an injected capability and must remain deny-by-
default outside this module.
"""

from dataclasses import dataclass
from hashlib import sha256
from threading import Lock
from typing import Callable

from .authorization import issue_token
from .governance import Decision, Evaluation, GovernancePolicy, evaluate
from .schemas import VerifiedExperimentPacket


@dataclass(frozen=True)
class C0Evidence:
    packet_id: str
    packet_digest: str
    decision: Decision
    evidence_hash: str


@dataclass(frozen=True)
class C0Result:
    evaluation: Evaluation
    evidence: C0Evidence | None
    effect_permitted: bool


class C0:
    """Serialize authorization and expose effects only after PASS evidence.

    The lock protects C0's in-process decision/evidence transition. It does
    not make external systems transactional. A caller must treat a result as
    authorization evidence, not as proof of atomic execution.
    """

    def __init__(self, policy: GovernancePolicy) -> None:
        self._policy = policy
        self._lock = Lock()

    def _authorize_locked(self, packet: VerifiedExperimentPacket) -> C0Result:
        evaluation = evaluate(packet, self._policy)
        if evaluation.decision is not Decision.PASS:
            return C0Result(evaluation, None, False)

        token = issue_token(evaluation)
        evidence = C0Evidence(
            packet_id=token.packet_id,
            packet_digest=token.packet_digest,
            decision=token.decision,
            evidence_hash=token.evidence_hash,
        )
        return C0Result(evaluation, evidence, True)

    def authorize(self, packet: VerifiedExperimentPacket) -> C0Result:
        """Evaluate a packet and issue evidence only for PASS."""
        with self._lock:
            return self._authorize_locked(packet)

    def execute(
        self,
        packet: VerifiedExperimentPacket,
        effect: Callable[[], None],
    ) -> C0Result:
        """Authorize and invoke the supplied effect only after PASS.

        This is a reference/test execution seam, not a sandbox. Production
        integrations must place an independently enforced boundary around the
        effect target.
        """
        with self._lock:
            result = self._authorize_locked(packet)
            if not result.effect_permitted:
                return result
            effect()
            return result


def verify_evidence(packet: VerifiedExperimentPacket, evidence: C0Evidence) -> bool:
    """Verify that evidence is bound to the exact canonical packet."""
    if evidence.decision is not Decision.PASS:
        return False
    if evidence.packet_id != packet.packet_id:
        return False
    if evidence.packet_digest != packet.digest():
        return False
    return bool(evidence.evidence_hash)


def canonical_fingerprint(packet: VerifiedExperimentPacket) -> str:
    """Return the SHA-256 fingerprint used as the C0 request binding."""
    return sha256(packet.canonical_bytes()).hexdigest()
