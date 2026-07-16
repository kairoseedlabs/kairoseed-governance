"""Canonical boundary objects for governed execution."""

import json
import math
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from typing import Any
from uuid import UUID


_MAX_METADATA_DEPTH = 64


def _json_domain_errors(
    value: Any,
    *,
    path: str,
    active_containers: set[int],
    depth: int = 0,
) -> list[str]:
    """Validate a value without applying JSON's lossy key coercions."""
    if depth > _MAX_METADATA_DEPTH:
        return [f"{path} exceeds maximum metadata depth"]

    if value is None or isinstance(value, (bool, str, int)):
        return []

    if isinstance(value, float):
        return [] if math.isfinite(value) else [f"{path} contains a non-finite number"]

    if isinstance(value, dict):
        container_id = id(value)
        if container_id in active_containers:
            return [f"{path} contains a recursive object"]

        active_containers.add(container_id)
        errors: list[str] = []
        for key, item in value.items():
            if not isinstance(key, str):
                errors.append(f"{path} contains a non-string object key")
                continue
            errors.extend(
                _json_domain_errors(
                    item,
                    path=f"{path}.{key}",
                    active_containers=active_containers,
                    depth=depth + 1,
                )
            )
        active_containers.remove(container_id)
        return errors

    if isinstance(value, list):
        container_id = id(value)
        if container_id in active_containers:
            return [f"{path} contains a recursive array"]

        active_containers.add(container_id)
        errors = []
        for index, item in enumerate(value):
            errors.extend(
                _json_domain_errors(
                    item,
                    path=f"{path}[{index}]",
                    active_containers=active_containers,
                    depth=depth + 1,
                )
            )
        active_containers.remove(container_id)
        return errors

    return [f"{path} contains a value outside the strict JSON domain"]


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

        if not isinstance(self.evidence_references, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.evidence_references
        ):
            errors.append("evidence_references must be a tuple of non-empty strings")

        if not isinstance(self.uncertainty_profile, dict):
            errors.append("uncertainty_profile must be an object")
        else:
            errors.extend(
                _json_domain_errors(
                    self.uncertainty_profile,
                    path="uncertainty_profile",
                    active_containers=set(),
                )
            )

        return tuple(errors)

    def canonical_bytes(self) -> bytes:
        """Return strict provisional bytes for packet binding.

        This representation is intentionally not claimed as KCS-0.2 compliant.
        """
        return json.dumps(
            asdict(self),
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def digest(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()
