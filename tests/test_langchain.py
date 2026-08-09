from __future__ import annotations

import pytest

langchain_core = pytest.importorskip("langchain_core")

from kairoseed.governance import Decision, GovernancePolicy
from kairoseed.langchain import LangChainProposal, build_governed_runnable


POLICY = GovernancePolicy(
    allowed_tools=frozenset({"safe.write"}),
    critical_tools=frozenset({"critical.write"}),
    max_resource_budget=100,
)


def payload(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "agent_id": "agent-01",
        "experiment_id": "exp-01",
        "declared_hypothesis": "test LangChain boundary",
        "declared_purpose": "test authorization",
        "tool_request": "safe.write",
        "resource_budget": 10,
        "rollback_plan": "restore fixture",
        "authorization_scope": ("safe.write",),
        "evidence_references": ("evidence-01",),
    }
    value.update(changes)
    return value


def test_langchain_runnable_passes_safe_proposal() -> None:
    result = build_governed_runnable(POLICY).invoke(payload())

    assert result["decision"] == Decision.PASS.value
    assert result["execution_permitted"] is True


def test_langchain_runnable_blocks_unauthorized_tool() -> None:
    result = build_governed_runnable(POLICY).invoke(
        payload(tool_request="unknown.write")
    )

    assert result["decision"] == Decision.BLOCK.value
    assert result["execution_permitted"] is False


def test_langchain_runnable_warns_on_critical_tool() -> None:
    result = build_governed_runnable(POLICY).invoke(
        payload(
            tool_request="critical.write",
            authorization_scope=("critical.write",),
        )
    )

    assert result["decision"] == Decision.WARN.value
    assert result["execution_permitted"] is False


def test_proposal_is_only_a_packet_adapter() -> None:
    proposal = LangChainProposal(
        agent_id="agent-01",
        experiment_id="exp-01",
        declared_hypothesis="test",
        declared_purpose="test",
        tool_request="safe.write",
        resource_budget=10,
        rollback_plan="restore",
        authorization_scope=("safe.write",),
    )

    packet = proposal.to_packet()
    assert packet.tool_request == "safe.write"
    assert packet.validate() == ()
