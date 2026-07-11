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
    request = packet()
    result = evaluate(request, POLICY)
    token = issue_token(result)

    assert result.decision is Decision.PASS
    assert token.packet_id == request.packet_id
    assert token.packet_digest == request.digest()
    assert authorize_execution(token)


def test_pass_evaluation_cannot_mint_token_for_another_packet():
    first = packet()
    second = packet()
    token = issue_token(evaluate(first, POLICY))

    assert token.packet_id == first.packet_id
    assert token.packet_digest == first.digest()
    assert token.packet_id != second.packet_id
    assert token.packet_digest != second.digest()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("packet_id", None),
        ("agent_id", None),
        ("declared_purpose", None),
        ("tool_request", None),
        ("resource_budget", None),
        ("authorization_scope", None),
    ],
)
def test_malformed_required_values_fail_closed(field, value):
    result = evaluate(packet(**{field: value}), POLICY)
    assert result.decision is Decision.BLOCK


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
        issue_token(result)
