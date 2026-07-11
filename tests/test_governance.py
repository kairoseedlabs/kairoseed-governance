from uuid import uuid4

import pytest

from kairoseed.authorization import issue_token
from kairoseed.enforcement import authorize_execution
from kairoseed.governance import Decision, GovernancePolicy, evaluate
from kairoseed.schemas import VerifiedExperimentPacket


POLICY = GovernancePolicy(
    allowed_tools=frozenset({"read_db"}),
    critical_tools=frozenset({"write_db"}),
    max_resource_budget=100,
)


def packet(**overrides):
    values = {
        "packet_id": str(uuid4()),
        "agent_id": "agent-1",
        "experiment_id": "experiment-1",
        "declared_hypothesis": "bounded read is sufficient",
        "declared_purpose": "test governance",
        "tool_request": "read_db",
        "resource_budget": 50,
        "rollback_plan": "discard result",
        "authorization_scope": ("read_db",),
        "evidence_references": ("evidence://test",),
    }
    values.update(overrides)
    return VerifiedExperimentPacket(**values)


def test_valid_bounded_request_passes():
    result = evaluate(packet(), POLICY)
    assert result.decision is Decision.PASS
    assert authorize_execution(issue_token(packet_id="p1", evaluation=result))


def test_missing_packet_data_blocks():
    result = evaluate(packet(declared_purpose=""), POLICY)
    assert result.decision is Decision.BLOCK


def test_out_of_scope_tool_blocks():
    result = evaluate(packet(tool_request="write_db"), POLICY)
    assert result.decision is Decision.BLOCK


def test_critical_tool_requires_review_when_scoped():
    result = evaluate(
        packet(tool_request="write_db", authorization_scope=("write_db",)),
        POLICY,
    )
    assert result.decision is Decision.WARN
    assert result.requires_human_review


def test_warn_cannot_issue_authorization():
    result = evaluate(packet(evidence_references=()), POLICY)
    with pytest.raises(PermissionError):
        issue_token(packet_id="p2", evaluation=result)
