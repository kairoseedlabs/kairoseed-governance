# KAIROSEED Capability Skill Contract v0.1

Formal name: **Verified Capability Execution Contract**

Status: specification only.

```text
Agent Intent
  → Verified Experiment Packet
  → Static Structural Checks
  → Static Policy Checks
  → Dynamic State Checks
  → Effect Hash Calculation
  → Governance Authorization Token
  → Policy Enforcement Point
  → Capability Adapter
  → Sandbox / Overlay Execution
  → Effect Witnessing
  → Commit or Rollback
  → Audit Log / Capability Freeze on Drift
```

A skill is not authorized because it exists. It is authorized only when its predicted effect is packetized, verified, scoped, tokenized, enforced, witnessed, and recoverable.

The effect-bound authorization envelope should bind at least:

- predicted-effect hash;
- authorization scope;
- TTL and single-use semantics;
- adapter identity;
- sandbox limits;
- rollback plan;
- required postconditions;
- policy version, packet identity, audience, and budget.

Canonical runtime invariants:

```text
No VEP. No evaluation.
No valid signature. No authorization.
No GAT. No execution.
No PEP witness. No commit.
Observed drift. Rollback and freeze.
```

This contract does not broaden KCS-0.2. Canonical bytes are evidence inputs; they do not independently authorize execution.
