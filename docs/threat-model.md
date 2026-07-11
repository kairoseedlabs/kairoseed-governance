# KAIROSEED Governance Threat Model

Status: **DRAFT — normative review required**  
Scope: KAIROSEED governance reference kernel  
Lifecycle: `kairoseed/v1`  
Invariant: **Capability ≠ Permission**

## 1. Purpose

This document defines the security boundaries, assets, adversaries, threats, required controls, non-claims, and acceptance evidence for the KAIROSEED governance reference kernel.

It is a design and review artifact. It does not claim that every required control is implemented.

## 2. Current and target capabilities

| Property | Current state | Target state |
|---|---|---|
| VEP structural validation | Implemented reference control | Hardened and fuzz-tested |
| PASS/WARN/BLOCK evaluation | Implemented reference control | Versioned deterministic PDP |
| Packet-to-token binding | Provisional SHA-256 digest binding | KCS-0.2 canonical digest binding |
| Canonicalization | Strict provisional Python JSON | Cross-runtime KCS-0.2 |
| Cryptographic signing | Not implemented | Ed25519 or reviewed equivalent |
| Replay protection | Not implemented | Context-bound, time-bound and auditable |
| Cross-runtime parity | Not demonstrated | Python/TypeScript golden-vector parity |
| Production security boundary | Not claimed | Requires independent validation |

The current serializer is explicitly **not KCS-0.2 compliant**.

## 3. System model

The reference flow is:

```text
Untrusted request
      |
      v
VEP parsing and structural validation
      |
      v
Policy Decision Point: PASS / WARN / BLOCK
      |
      v
Authorization evidence
      |
      v
Policy Enforcement Point
      |
      v
JIREH runtime viability and recovery
      |
      v
Bounded runtime action and audit event
```

OPA, external agent runtimes, micro-VMs, databases, networks, approval interfaces, and deployment systems are integration targets and are not currently part of this repository's implemented trusted computing base.

### 3.1 JIREH runtime boundary

> JIREH is KAIROSEED’s runtime viability and recovery layer, designed to monitor authorized agent execution and trigger bounded responses when operational conditions become unsafe or unstable.

The canonical component boundary is:

- authorization: `VEP → Govana Core → GAT → PEP`;
- runtime supervision: `PEP → JIREH`;
- observations: environment, affinity, resources, liveness, and stability;
- bounded responses: `CONTINUE | THROTTLE | FAILOVER | BLOCK | COMPLETE`.

JIREH may confirm that it received a valid, already-authorized execution context. It does not independently recreate the authorization decision, replace the PEP, or treat runtime viability as permission.

JIREH does not guarantee safety, prevent every failure, prove global stability, or replace cryptographic authorization. Runtime viability and recovery controls remain target integration work unless explicitly identified as implemented and tested in this repository.

## 4. Security invariants

1. Capability does not imply permission.
2. Missing, malformed, ambiguous, expired, unbound, or unverifiable inputs fail closed.
3. No token may authorize a packet other than the exact packet evaluated.
4. WARN is not executable authorization.
5. BLOCK is terminal for the evaluated request.
6. Policy evaluation must not execute the requested capability.
7. Authorization evidence must be checked by an independent enforcement point.
8. Audit evidence must not be treated as authorization evidence.
9. Current provisional hashes must not be represented as cryptographic signatures.
10. Security-sensitive state transitions require explicit evidence.

## 5. Protected assets

| ID | Asset | Security objective |
|---|---|---|
| A-01 | VEP contents and identity | Integrity, exact binding |
| A-02 | Policy rules and versions | Integrity, provenance |
| A-03 | Evaluation result | Integrity, determinism |
| A-04 | Authorization evidence | Authenticity, integrity, expiry |
| A-05 | Signing and verification keys | Confidentiality or integrity, lifecycle control |
| A-06 | Nonces and token identifiers | Uniqueness, replay resistance |
| A-07 | Trusted time source | Integrity, bounded skew |
| A-08 | Audit chain | Integrity, ordering, non-repudiation evidence |
| A-09 | CI artifacts and provenance | Integrity, reproducibility |
| A-10 | Runtime resource budget | Availability, enforcement |
| A-11 | Sensitive telemetry | Confidentiality, minimization |
| A-12 | Release and rollback state | Integrity, anti-downgrade |

## 6. Actors and trust assumptions

### External submitter — untrusted

May send arbitrary, malformed, deeply nested, ambiguous, replayed, or adversarial inputs. Knowledge of the public specification is assumed.

### Agent runtime — untrusted

May generate unsafe requests, omit context, misrepresent intent, repeat requests, or attempt confused-deputy escalation.

### Policy Decision Point — constrained trust assumption

Govana Core or another PDP is not inherently trusted. Its decisions are relied upon only when its code, policy version, inputs, configuration, and execution environment satisfy documented integrity assumptions.

### Policy Enforcement Point — constrained trust assumption

The PEP must deny by default and must verify authorization evidence independently. PDP success alone cannot trigger execution.

### Human approver — conditionally trusted

Approval is valid only when identity, scope, intent, freshness, and approval evidence are verified. A UI click or chat message alone is not cryptographic authorization.

### Repository, CI and connected applications — semi-trusted

GitHub, CI runners, dependencies, installed applications, collaborators, and provider logs remain within the operational trust boundary and may be compromised.

### Host and runtime platform — external trust dependency

Operating system, container, micro-VM, hardware, clock, key store, and network controls are outside the kernel and require separate assurance.

## 7. Trust boundaries and entry points

| ID | Boundary or entry point | Untrusted input |
|---|---|---|
| EP-01 | VEP ingestion | Raw request bytes and decoded values |
| EP-02 | Metadata validation | Nested JSON-domain values |
| EP-03 | Policy evaluation | Packet, policy and context |
| EP-04 | Token issuance | Evaluation identity and temporal claims |
| EP-05 | Token verification | Signature, claims, key ID and context |
| EP-06 | Enforcement adapter | Tool name, arguments and authorization evidence |
| EP-07 | Audit sink | Events, hashes, timestamps and lineage |
| EP-08 | Policy/configuration loading | Rules, versions and kill-switch state |
| EP-09 | CI and dependency pipeline | Source, actions, packages and artifacts |
| EP-10 | Human approval channel | Approver identity and signed decision |

## 8. STRIDE analysis

### Spoofing

Threats:

- forged agent, approver, issuer, runtime or key identity;
- substitution of a token issued for another audience;
- acceptance of an unknown or retired key.

Required controls:

- authenticated issuer and approver identities;
- `issuer`, `audience`, `key_id`, `agent_id` and subject binding;
- trusted key registry with rotation and revocation;
- constant-time signature verification where applicable.

### Tampering

Threats:

- VEP mutation after evaluation;
- JSON key coercion or duplicate-key ambiguity;
- policy or configuration modification;
- audit event alteration;
- build artifact substitution.

Required controls:

- KCS-0.2 single-representation encoding;
- exact packet digest binding;
- signed authorization claims;
- policy version and artifact provenance;
- append-only or hash-linked audit evidence;
- protected branches and reviewed changes.

### Repudiation

Threats:

- approver denies granting permission;
- runtime denies executing an action;
- operator alters or deletes audit history;
- policy version cannot be reconstructed.

Required controls:

- signed approval and authorization records;
- stable event IDs, actor IDs and timestamps;
- policy and code revision identifiers;
- durable, access-controlled audit storage;
- clock source and skew evidence.

These controls provide evidence; they do not create absolute legal non-repudiation.

### Information disclosure

Threats:

- secrets, nonces, tokens, packet contents or policy internals exposed in logs;
- verbose failures reveal sensitive state;
- CI artifacts retain private data.

Required controls:

- zero-secrets repository policy;
- structured redaction and data minimization;
- bounded error messages;
- log access controls and retention limits;
- test fixtures containing synthetic data only.

The system targets controlled disclosure, not “zero leakage.”

### Denial of service

Threats:

- deeply nested or oversized metadata;
- expensive policy evaluation;
- request floods;
- audit-sink backpressure;
- replay storms.

Required controls:

- input size, depth and collection-count limits;
- evaluation timeout and resource budgets;
- upstream rate limiting and admission control;
- bounded queues, circuit breakers and safe degradation;
- no authorization on timeout or overload.

Network flood protection is an upstream responsibility.

### Elevation of privilege

Threats:

- WARN treated as PASS;
- critical tool execution without human authorization;
- confused-deputy use of a valid token;
- policy rollback to a weaker version;
- bypass of the PEP;
- overly broad authorization scope.

Required controls:

- deny-by-default PEP;
- exact tool, resource, argument and environment scope;
- mandatory critical-action approval evidence;
- anti-rollback policy version;
- audience and runtime binding;
- independent verification immediately before execution.

## 9. Replay-control requirements

Future authorization evidence must bind at least:

- issuer;
- audience;
- subject or agent identity;
- packet digest;
- policy version;
- decision;
- authorization scope;
- key ID;
- token ID or nonce;
- issued-at time;
- not-before time when used;
- expiry;
- approval identity and evidence for critical actions.

Single-use semantics require an atomic consumed-token registry. Without durable state, the system may provide time-bounded replay resistance but cannot claim strict single use.

## 10. Cross-language and canonicalization requirements

KCS-0.2 must define:

- accepted data model and rejected values;
- Unicode normalization policy;
- object-key ordering using the specified comparison domain;
- duplicate-key rejection before object construction;
- integer and floating-point bounds;
- encoding of arrays, strings, booleans and null;
- UTF-8 output requirements;
- exact failure behavior;
- maximum nesting and size limits;
- golden vectors shared by Python and TypeScript.

Prototype pollution, special object properties, Python type coercion, non-finite numbers, oversized integers, surrogate handling, and Unicode normalization are explicit parity risks.

## 11. Supply-chain and operational threats

Required review areas:

- dependency confusion and malicious package releases;
- unpinned or mutable CI actions;
- compromised connected applications;
- collaborator credential compromise;
- malicious pull requests and workflow changes;
- artifact substitution;
- vulnerable native dependencies;
- rollback to a vulnerable code or policy revision;
- leaked CI tokens and excessive workflow permissions.

Mitigations include least-privilege workflow permissions, dependency review, provenance, immutable references where practical, branch protection, review requirements, secret scanning, and incident response procedures.

## 12. Language-specific risk

The Python reference kernel's most direct risks are logical bypass, unsafe parsing, type confusion, ambiguous serialization, dependency compromise, resource exhaustion, and exception-path authorization errors.

Memory corruption is primarily inherited from the interpreter, native extensions, cryptographic libraries, operating system, and runtime dependencies. The repository does not claim memory safety.

## 13. Security non-claims

This reference kernel does not currently claim:

- resistance to a compromised host or Python runtime;
- production-grade cryptographic authorization;
- KCS-0.2 compliance;
- cross-language deterministic parity;
- protection from network-layer denial of service;
- confidentiality of data committed to Git history;
- safety against malicious authorized maintainers;
- formal verification;
- independent security audit;
- compliance certification;
- suitability for unsupervised high-risk production deployment.

## 14. Verification and release evidence

The following evidence is required before the relevant claims may advance:

### Canonicalization

- fixed public and adversarial golden-vector corpus;
- recorded toolchain and runtime versions;
- Python/TypeScript byte-for-byte equality;
- reordered equivalent objects produce identical bytes;
- distinct typed inputs cannot collide through coercion;
- duplicate keys and unsupported values are rejected.

### Fuzzing

- versioned initial corpus;
- recorded random seeds;
- documented generator and mutation strategy;
- explicit coverage metric and baseline;
- bounded time, memory, input size and depth;
- zero unhandled crashes;
- zero unauthorized PASS outcomes;
- reproducible failure artifacts.

No arbitrary iteration count alone constitutes sufficient evidence.

### Signing and replay

- valid-signature acceptance vectors;
- tampered-packet rejection;
- wrong issuer, audience, scope, key and policy-version rejection;
- expiry, not-before and clock-skew tests;
- replay and consumed-token tests;
- key rotation and revocation tests.

### Supply chain and release

- secret and Git-history scan;
- dependency and workflow review;
- branch-protection evidence;
- license, contribution and security policies;
- residual-risk register;
- release approval record.

## 15. Residual risks

Residual risks must be tracked with:

- unique identifier;
- affected asset;
- likelihood and impact;
- existing controls;
- control owner;
- acceptance or remediation decision;
- review date;
- evidence link.

A passing test suite does not eliminate residual risk.

## 16. Threat-model acceptance gate

This document may become the normative threat model only when:

1. all current-versus-target claims are accurate;
2. every STRIDE category has reviewed threats and controls;
3. trust assumptions and external dependencies are explicit;
4. replay and canonicalization requirements are testable;
5. security non-claims are retained;
6. unresolved review findings are addressed;
7. CI and documentation checks pass;
8. a human reviewer explicitly accepts the residual scope.

Until acceptance:

- KCS-0.2 implementation remains blocked;
- cryptographic integration remains blocked;
- public repository visibility remains blocked.
