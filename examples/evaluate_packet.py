from uuid import uuid4

from kairoseed import GovernancePolicy, VerifiedExperimentPacket, evaluate


packet = VerifiedExperimentPacket(
    packet_id=str(uuid4()),
    agent_id="example-agent",
    experiment_id="EXP-001",
    declared_hypothesis="Bounded retrieval can answer the request.",
    declared_purpose="Demonstrate verification before execution.",
    tool_request="read_db",
    resource_budget=50,
    rollback_plan="Discard transient results.",
    authorization_scope=("read_db",),
    evidence_references=("policy://default",),
)

policy = GovernancePolicy(
    allowed_tools=frozenset({"read_db"}),
    critical_tools=frozenset({"write_db", "execute_shell"}),
    max_resource_budget=100,
)

print(evaluate(packet, policy))
