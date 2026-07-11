"""Canonical boundary objects for governed execution."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class VerifiedExperimentPacket:
    """Minimum packet required before an agent request may be evaluated."""

    packet_id: str
    agent_id: str
    experiment_id: str
    declared_hypothesis: str
    declared_purpose: str
    tool_request: str
    resource_budget: int
    rollback_plan: str
    authorization_scope: tuple[str, ...]
    evidence_references: tuple[str, ...] = ()
    uncertainty_profile: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        try:
            UUID(self.packet_id)
        except ValueError:
            errors.append("packet_id must be a UUID")

        required = {
            "agent_id": self.agent_id,
            "experiment_id": self.experiment_id,
            "declared_hypothesis": self.declared_hypothesis,
            "declared_purpose": self.declared_purpose,
            "tool_request": self.tool_request,
            "rollback_plan": self.rollback_plan,
        }
        errors.extend(f"{name} is required" for name, value in required.items() if not value.strip())

        if self.resource_budget <= 0:
            errors.append("resource_budget must be positive")
        if not self.authorization_scope:
            errors.append("authorization_scope must not be empty")
        return tuple(errors)
