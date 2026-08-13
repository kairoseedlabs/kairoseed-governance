from dataclasses import replace

from kairoseed.governance import GovernancePolicy
from kairoseed.kalyth import AdmissionDecision, KALYTH, verify_admission
from kairoseed.schemas import VerifiedExperimentPacket


def make_packet():
    return VerifiedExperimentPacket(
        packet_id="00000000-0000-4000-8000-000000000001",
        agent_id="agent-kalyth",
        experiment_id="experiment-kalyth",
        declared_hypothesis="authorized read remains bounded",
        declared_purpose="test admission boundary",
        tool_request="read",
        resource_budget=10,
        rollback_plan="no external effect",
        authorization_scope=("read",),
        evidence_references=("evidence:001",),
    )


def policy():
    return GovernancePolicy(
        allowed_tools=frozenset({"read"}),
        critical_tools=frozenset(),
        max_resource_budget=100,
    )


def test_pass_becomes_approved_with_bound_evidence():
    packet = make_packet()
    admission = KALYTH(policy()).admit(packet)

    assert admission.decision is AdmissionDecision.APPROVED
    assert admission.effect_permitted
    assert admission.evidence is not None
    assert verify_admission(packet, admission)


def test_block_becomes_denied_without_effect_permission():
    packet = replace(make_packet(), tool_request="write")
    admission = KALYTH(policy()).admit(packet)

    assert admission.decision is AdmissionDecision.DENIED
    assert not admission.effect_permitted
    assert admission.evidence is None
    assert not verify_admission(packet, admission)


def test_warn_becomes_denied_at_c0_boundary():
    packet = replace(make_packet(), evidence_references=())
    admission = KALYTH(policy()).admit(packet)

    assert admission.decision is AdmissionDecision.DENIED
    assert not admission.effect_permitted


def test_tampered_packet_invalidates_admission():
    packet = make_packet()
    admission = KALYTH(policy()).admit(packet)
    tampered = replace(packet, resource_budget=11)

    assert admission.decision is AdmissionDecision.APPROVED
    assert not verify_admission(tampered, admission)


def test_denied_execution_never_invokes_effect():
    packet = replace(make_packet(), tool_request="write")
    called = False

    def effect():
        nonlocal called
        called = True

    admission = KALYTH(policy()).execute(packet, effect)

    assert admission.decision is AdmissionDecision.DENIED
    assert not called
