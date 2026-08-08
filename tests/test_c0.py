from dataclasses import replace

import pytest

from kairoseed.c0 import C0, canonical_fingerprint, verify_evidence
from kairoseed.governance import Decision, GovernancePolicy
from kairoseed.schemas import VerifiedExperimentPacket


PACKET_ID = "00000000-0000-4000-8000-000000000001"


def packet(**changes: object) -> VerifiedExperimentPacket:
    base = VerifiedExperimentPacket(
        packet_id=PACKET_ID,
        agent_id="agent-01",
        experiment_id="exp-01",
        declared_hypothesis="verify C0",
        declared_purpose="test authorization",
        tool_request="safe.write",
        resource_budget=10,
        rollback_plan="restore fixture",
        authorization_scope=("safe.write",),
        evidence_references=("evidence-01",),
        uncertainty_profile={"risk": "low"},
    )
    return replace(base, **changes)


@pytest.fixture
def c0() -> C0:
    return C0(
        GovernancePolicy(
            allowed_tools=frozenset({"safe.write"}),
            critical_tools=frozenset({"critical.write"}),
            max_resource_budget=100,
        )
    )


def test_pass_produces_bound_evidence(c0: C0) -> None:
    result = c0.authorize(packet())

    assert result.evaluation.decision is Decision.PASS
    assert result.effect_permitted is True
    assert result.evidence is not None
    assert verify_evidence(packet(), result.evidence)


def test_block_never_permits_effect(c0: C0) -> None:
    result = c0.authorize(packet(tool_request="unknown.write"))

    assert result.evaluation.decision is Decision.BLOCK
    assert result.effect_permitted is False
    assert result.evidence is None


def test_warn_never_permits_effect(c0: C0) -> None:
    result = c0.authorize(
        packet(
            tool_request="critical.write",
            authorization_scope=("critical.write",),
        )
    )

    assert result.evaluation.decision is Decision.WARN
    assert result.effect_permitted is False
    assert result.evidence is None


def test_mutation_breaks_evidence_binding(c0: C0) -> None:
    original = packet()
    result = c0.authorize(original)
    assert result.evidence is not None

    mutated = packet(declared_purpose="different purpose")
    assert not verify_evidence(mutated, result.evidence)


def test_canonical_fingerprint_changes_for_governance_field() -> None:
    assert canonical_fingerprint(packet()) != canonical_fingerprint(
        packet(resource_budget=11)
    )


def test_same_packet_has_same_canonical_fingerprint() -> None:
    assert canonical_fingerprint(packet()) == canonical_fingerprint(packet())


def test_invalid_packet_fails_closed(c0: C0) -> None:
    invalid = packet(packet_id="not-a-uuid")
    result = c0.authorize(invalid)

    assert result.evaluation.decision is Decision.BLOCK
    assert result.effect_permitted is False


def test_executor_called_only_after_pass(c0: C0) -> None:
    effects: list[str] = []

    blocked = c0.execute(
        packet(tool_request="unknown.write"),
        lambda: effects.append("blocked"),
    )
    passed = c0.execute(packet(), lambda: effects.append("passed"))

    assert blocked.evaluation.decision is Decision.BLOCK
    assert passed.evaluation.decision is Decision.PASS
    assert effects == ["passed"]
