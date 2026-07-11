"""Canonical boundary objects for governed execution."""

import json
from dataclasses import asdict, dataclass, field
from hashlib import sha256
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

        if not isinstance(self.packet_id, str):
            errors.append("packet_id must be a UUID string")
        else:
            try:
                UUID(self.packet_id)
            except ValueError:
                errors.append("packet_id must be a UUID string")

        required = {
            "agent_id": self.agent_id,
            "experiment_id": self.experiment_id,
            "declared_hypothesis": self.declared_hypothesis,
            "declared_purpose": self.declared_purpose,
            "tool_request": self.tool_request,
            "rollback_plan": self.rollback_plan,
        }
        for name, value in required.items():
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{name} must be a non-empty string")

        if (
            not isinstance(self.resource_budget, int)
            or isinstance(self.resource_budget, bool)
            or self.resource_budget <= 0
        ):
            errors.append("resource_budget must be a positive integer")

        if (
            not isinstance(self.authorization_scope, tuple)
            or not self.authorization_scope
            or any(not isinstance(item, str) or not item.strip() for item in self.authorization_scope)
        ):
            errors.append("authorization_scope must be a non-empty tuple of strings")

        return tuple(errors)

    def canonical_bytes(self) -> bytes:
        """Return deterministic reference bytes for packet binding."""
        return json.dumps(
            asdict(self),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def digest(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()
