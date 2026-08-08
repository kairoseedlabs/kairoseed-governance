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
- **C0 deterministic authorization boundary** with invariant tests

### C0 reference contract

```text
PROPOSED ACTION
      ↓
C0 LOCK
      ↓
CANONICALIZE + VALIDATE
      ↓
GOVANA POLICY
      ↓
PASS / WARN / BLOCK
      ↓
AUTHORIZATION EVIDENCE
      ↓
PERMITTED EFFECT
```

Core tested property:

```text
¬PASS ⇒ ¬EFFECT
```

The current C0 implementation uses provisional in-process locking and SHA-256 evidence binding. It does **not** claim TPM-backed signing, kernel isolation, transactional atomicity across external systems, or production security-boundary status.

This is an early reference implementation and must be treated as a research artifact until independently tested and validated.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
python examples/evaluate_packet.py
```

## KCS-0.2 parity check

The cross-language canonicalization gate can be reproduced locally with the same frozen vectors used in CI:

```bash
python tests/run_python_vectors.py \
  --vectors tests/golden_vectors.json \
  --output /tmp/kcs02-python-results.json

(cd kairoseed/kcs02-ts && npm ci --ignore-scripts && npm run parity)

python tests/compare_kcs02_vectors.py \
  --vectors tests/golden_vectors.json \
  --python-results /tmp/kcs02-python-results.json \
  --typescript-results /tmp/kcs02-typescript-results.json
```

## Repository map

```text
src/kairoseed/
  schemas.py         VEP boundary and validation
  governance.py      deterministic policy decision point
  authorization.py   time-bounded authorization evidence
  enforcement.py     deny-by-default enforcement point
  audit.py            tamper-evident audit primitives
  c0.py              minimal C0 authorization boundary
tests/               governance and C0 invariant tests
policies/            declarative policy examples
examples/            executable usage examples
docs/foundations/    theological and architectural foundations
docs/sops/           repeatable governance review procedures
```

## Documentation

- [Created Time and Appointed Arrival](docs/foundations/created-time-and-appointed-arrival.md) — the Kairos–Chronos distinction, readiness invariants, lifecycle model, and current implementation mapping
- [KAIROSEED Architectural Audit SOP](docs/sops/kairoseed-architectural-audit.md) — the Three-Gate PASS/WARN/BLOCK review workflow and reusable audit prompt

## Relationship to other KAIROSEED repositories

- `kairoseed-core`: stochastic attractor and transition experiments
- `kairoseed-governance`: governed agent authorization and enforcement
- `dataset-viewer`: upstream Hugging Face fork; not part of the governance kernel unless explicitly integrated later

## Development rule

All material changes should enter through a bounded issue, a dedicated branch, automated tests, and a reviewed pull request.

Strong Accept + Pass + DoD
Done = Amen.