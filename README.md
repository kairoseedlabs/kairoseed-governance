# KAIROSEED Governance

> Verification-first governance architecture for bounded, auditable, and policy-controlled agentic AI execution.

```yaml
domain:
  - AI Safety
  - Agent Governance
  - Governance-as-Code
  - Runtime Verification
invariant: "Capability ≠ Permission"
lifecycle_version: kairoseed/v1
status: reference-implementation
```

## Purpose

KAIROSEED separates what an agent *can* do from what it is *authorized* to do. Every requested capability must first be expressed as a Verified Experiment Packet (VEP), evaluated against deterministic policy, and presented to a deny-by-default enforcement point.

```text
Intent → VEP → Policy Evaluation → PASS/WARN/BLOCK
                                  ↓
                       Authorization Evidence
                                  ↓
                        Enforcement → Execution
                                  ↓
                            Audit Record
```

No packet. No evaluation. No authorization. No execution.

## Current reference kernel

- immutable `VerifiedExperimentPacket` boundary object
- deterministic PASS/WARN/BLOCK policy evaluation
- authorization-scope and resource-budget enforcement
- human-review requirement for critical capabilities
- short-lived governance authorization token
- deny-by-default policy enforcement point
- canonical SHA-256 audit record primitive
- automated tests through GitHub Actions

This is an early reference implementation. It is not yet a production security boundary, cryptographic signing service, or independently validated safety system.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
python examples/evaluate_packet.py
```

## Repository map

```text
src/kairoseed/
  schemas.py         VEP boundary and validation
  governance.py      deterministic policy decision point
  authorization.py   time-bounded authorization evidence
  enforcement.py     deny-by-default enforcement point
  audit.py           tamper-evident audit primitives
policies/            declarative policy examples
examples/            executable usage examples
tests/               governance invariant tests
```

## Relationship to other KAIROSEED repositories

- `kairoseed-core`: stochastic attractor and transition experiments
- `kairoseed-governance`: governed agent authorization and enforcement
- `dataset-viewer`: upstream Hugging Face fork; not part of the governance kernel unless explicitly integrated later

## Development rule

All material changes should enter through a bounded issue, a dedicated branch, automated tests, and a reviewed pull request.

Strong Accept + Pass + DoD
Done = Amen.