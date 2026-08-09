"""LangChain integration for the KAIROSEED authorization boundary.

LangChain is an orchestration/proposal layer here. It must not become an
implicit authority source. The adapter converts a structured proposal into a
VerifiedExperimentPacket and evaluates it through the existing deterministic
KAIROSEED policy boundary.

No tool is executed by this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from uuid import uuid4

from .governance import Evaluation, GovernancePolicy, evaluate
from .schemas import VerifiedExperimentPacket

try:
    from langchain_core.runnables import RunnableLambda
except ImportError as exc:  # pragma: no cover - exercised when optional dep is absent
    raise ImportError(
        "LangChain integration requires 'langchain-core'. "
        "Install it with: python -m pip install langchain-core"
    ) from exc


@dataclass(frozen=True)
class LangChainProposal:
    """Structured proposal emitted by a LangChain workflow."""

    agent_id: str
    experiment_id: str
    declared_hypothesis: str
    declared_purpose: str
    tool_request: str
    resource_budget: int
    rollback_plan: str
    authorization_scope: tuple[str, ...]
    evidence_references: tuple[str, ...] = ()
    uncertainty_profile: Mapping[str, Any] | None = None
    packet_id: str | None = None

    def to_packet(self) -> VerifiedExperimentPacket:
        return VerifiedExperimentPacket(
            packet_id=self.packet_id or str(uuid4()),
            agent_id=self.agent_id,
            experiment_id=self.experiment_id,
            declared_hypothesis=self.declared_hypothesis,
            declared_purpose=self.declared_purpose,
            tool_request=self.tool_request,
            resource_budget=self.resource_budget,
            rollback_plan=self.rollback_plan,
            authorization_scope=self.authorization_scope,
            evidence_references=self.evidence_references,
            uncertainty_profile=dict(self.uncertainty_profile or {}),
        )


def authorize_proposal(
    proposal: LangChainProposal,
    policy: GovernancePolicy,
) -> Evaluation:
    """Evaluate a LangChain proposal without executing its requested tool."""
    return evaluate(proposal.to_packet(), policy)


def build_governed_runnable(policy: GovernancePolicy) -> RunnableLambda:
    """Build a LangChain Runnable that stops at KAIROSEED authorization.

    Input must be a mapping accepted by ``LangChainProposal``. Output contains
    the policy decision and reasons. The runnable never invokes a tool.
    """

    def _authorize(payload: Mapping[str, Any]) -> dict[str, Any]:
        proposal = LangChainProposal(
            agent_id=str(payload["agent_id"]),
            experiment_id=str(payload["experiment_id"]),
            declared_hypothesis=str(payload["declared_hypothesis"]),
            declared_purpose=str(payload["declared_purpose"]),
            tool_request=str(payload["tool_request"]),
            resource_budget=payload["resource_budget"],
            rollback_plan=str(payload["rollback_plan"]),
            authorization_scope=tuple(payload["authorization_scope"]),
            evidence_references=tuple(payload.get("evidence_references", ())),
            uncertainty_profile=payload.get("uncertainty_profile", {}),
            packet_id=payload.get("packet_id"),
        )
        evaluation = authorize_proposal(proposal, policy)
        return {
            "decision": evaluation.decision.value,
            "reasons": evaluation.reasons,
            "packet_id": evaluation.packet_id,
            "packet_digest": evaluation.packet_digest,
            "requires_human_review": evaluation.requires_human_review,
            "execution_permitted": evaluation.decision.value == "PASS",
        }

    return RunnableLambda(_authorize)
