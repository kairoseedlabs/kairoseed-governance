# SOP: KAIROSEED Architectural Audit

## Purpose

Use this procedure to evaluate a proposed architecture, code change, workflow, agent, automation, or authorization path against KAIROSEED governance principles.

The audit is designed to answer one central question:

> Can untrusted information, elapsed time, remembered context, or mere possession of a capability become execution authority without a current, bounded, auditable governance decision?

## Required inputs

Provide as much of the following as is available:

- architecture diagram or execution flow;
- source code or pull-request diff;
- identities and trust boundaries;
- requested tools and capabilities;
- data sources, memory stores, and retrieval paths;
- trigger conditions, schedules, webhooks, and event sources;
- policy definitions and authorization logic;
- token, session, and credential lifecycle;
- failure, rollback, revocation, and cleanup behavior;
- audit records and security assumptions.

Missing information is not silently assumed safe. Material uncertainty produces `WARN` or `BLOCK` according to impact.

## Result vocabulary

- **PASS** — the control is explicit, bounded, auditable, and supported by evidence.
- **WARN** — the design may be acceptable only with stated assumptions, human review, or a defined remediation.
- **BLOCK** — the design permits an unbounded or unauthorized transition and must not proceed as proposed.
- **N/A** — the control does not apply; the reason must be recorded.

A final result is the most severe applicable gate result:

```text
BLOCK > WARN > PASS
```

## Audit sequence

### Step 1 — Define the privileged transition

Write the transition as a concrete tuple:

```text
(subject, action, resource, environment, purpose)
```

Record:

- who or what acts;
- the exact operation requested;
- the target resource;
- the relevant deployment or runtime context;
- the declared purpose;
- the maximum resource budget;
- the rollback or containment plan.

**BLOCK** when the requested authority cannot be stated precisely enough to bind and evaluate.

### Step 2 — Trace the complete path

Trace the path from initial input to final side effect:

```text
Input → Parsing → Memory/Retrieval → Boundary Object → Policy Decision
      → Authorization Evidence → Enforcement → Execution → Cleanup → Audit
```

Mark every location where data crosses a trust boundary or where execution authority can be created, widened, delegated, cached, replayed, or retained.

Do not stop at the intended control path. Include error handlers, retries, fallbacks, queues, background workers, administrative endpoints, test modes, and recovery paths.

## Gate I — Inert Observation

### Objective

Confirm strict separation between the data plane and the control plane.

### Questions

1. Can user input, retrieved documents, model memory, tool output, event payloads, or telemetry directly alter authorization policy?
2. Can text such as “approved,” “administrator,” “system,” or “run now” be interpreted as permission without independent verification?
3. Can a scheduled time, cron event, delay, timeout, or timestamp directly grant a privileged capability?
4. Can untrusted data choose the enforcement path, policy version, evaluator, identity, or credential?
5. Can remembered approval from a prior session authorize a present action?
6. Are parsing and canonicalization failures deny-by-default?
7. Is the request converted into a bounded object before policy evaluation?

### PASS conditions

- inputs may request evaluation but cannot grant permission;
- memory and retrieved context are inert evidence;
- policy and enforcement configuration come from a protected control plane;
- schedules and events create evaluation opportunities, not authorization;
- malformed, ambiguous, or uncanonicalizable requests are denied;
- the exact requested capability is represented in a stable boundary object.

### Common BLOCK findings

- prompt content selects privileged tools;
- an LLM decides whether its own action is authorized;
- a cron job invokes a privileged operation with no fresh policy decision;
- prior chat memory is treated as persistent approval;
- a retrieved document contains instructions that alter control behavior;
- a client-supplied role or policy identifier is trusted without verification.

## Gate II — Verified Alignment

### Objective

Confirm that authorization represents current, bounded readiness for one exact transition.

### Required bindings

Authorization should be bound, as applicable, to:

- subject or workload identity;
- action or tool;
- resource or target;
- request identifier and canonical digest;
- declared purpose;
- resource budget;
- policy identifier and version;
- environment or deployment;
- evidence set;
- approval identity when human authorization is required;
- issuance, freshness, and expiry constraints;
- nonce, challenge, or transaction identifier when replay is in scope.

### Questions

1. Is there an explicit `PASS`, `WARN`, or `BLOCK` decision before execution?
2. Does absence of a decision result in denial?
3. Is the evaluator separate from the executor?
4. Can the executor verify that authorization matches the exact request presented?
5. Are critical capabilities held for explicit human approval?
6. Can policy changes, identity changes, environment drift, or revocation invalidate prior authorization?
7. Is wall-clock time used only as a constraint rather than the source of permission?
8. Are freshness and clock-source assumptions documented?
9. Can authorization be widened after issuance?
10. Are retries and delegated calls bound to the original scope and budget?

### PASS conditions

- a current policy decision precedes authorization;
- authorization is narrowly bound and independently checked at enforcement;
- stale or mismatched evidence is rejected;
- critical actions require explicit approval;
- time limits authorization eligibility but never creates permission;
- policy, identity, scope, and environment changes fail closed.

### Common BLOCK findings

- possession of a tool credential is treated as permission;
- token scope is broader than the evaluated request;
- the token binds only to a user but not action or resource;
- execution proceeds after `WARN` without required review;
- approval has no policy version, request digest, or expiry;
- the executor accepts caller assertions about authorization.

## Gate III — Asymmetric Dissolution

### Objective

Confirm that authorization and latent execution state can be terminated safely and cannot remain reusable without renewed verification.

### Questions

1. Does authorization expire?
2. Can it be explicitly revoked?
3. Is it consumed after successful use when single-use semantics are required?
4. Are replay attempts detected and denied?
5. What happens to authorization after failure, cancellation, timeout, or partial execution?
6. Are queued jobs invalidated when their authorization expires or policy changes?
7. Are delegated credentials, temporary files, caches, handles, and subprocesses cleaned up?
8. Does rollback require its own bounded authority?
9. Are terminal state and reason recorded in the audit trail?
10. Can destruction or invalidation occur even when the primary executor is unavailable?

### PASS conditions

- every authorization has a defined terminal state;
- revocation and expiry are checked at enforcement time;
- replay-sensitive authorization is single-use or nonce-bound;
- queued and delegated work cannot outlive its authority;
- cleanup is deterministic, observable, and fail-safe;
- audit records preserve issuance, use, rejection, expiry, revocation, and cleanup outcomes.

### Common BLOCK findings

- a valid token can be reused indefinitely;
- queued commands execute after authorization expiry;
- cancellation stops the caller but not delegated work;
- temporary credentials survive failure paths;
- cleanup is best-effort with no verification or alerting;
- audit records omit terminal state.

## Cross-cutting checks

### Deny-by-default

Verify that every missing, malformed, stale, mismatched, unreachable, or indeterminate control condition results in denial rather than implicit allowance.

### Least privilege

Verify that the authorization scope, duration, resource budget, and delegated authority are no broader than necessary for the declared purpose.

### Determinism and auditability

Verify that the same canonical request, policy version, and evidence set produce a reproducible governance result, or that any nondeterminism is explicitly bounded and reviewed.

### Human review

Verify that human approval is:

- attached to the exact request;
- attributable to a verified reviewer;
- informed by the evidence and risk;
- bounded by expiry and policy version;
- not reusable as a general standing privilege unless explicitly designed and governed as such.

### Failure and rollback

Verify that rollback does not bypass the same governance boundary. Emergency controls may be different, but they must be explicit, narrowly scoped, independently auditable, and protected against routine use.

## Compliance matrix

Use the following output table:

| Gate | Result | Evidence | Finding | Required remediation |
|---|---|---|---|---|
| I — Inert Observation | PASS/WARN/BLOCK | Files, functions, diagrams, tests | Data/control-plane result | Patch or control |
| II — Verified Alignment | PASS/WARN/BLOCK | Policy and authorization evidence | Kairos readiness result | Patch or control |
| III — Asymmetric Dissolution | PASS/WARN/BLOCK | Lifecycle and cleanup evidence | Terminal-state result | Patch or control |

Then record:

```text
Overall result: PASS | WARN | BLOCK
Privileged transition:
Threat assumptions:
Implemented controls:
Proposed controls:
Residual risk:
Verification tests:
```

## Required recommendation format

For every `WARN` or `BLOCK`, provide:

1. **Finding** — the exact unsafe path or missing invariant;
2. **Impact** — what unauthorized or persistent state may result;
3. **Evidence** — the file, function, configuration, or architecture edge;
4. **Patch** — the smallest concrete change that restores the invariant;
5. **Test** — a negative test that fails before the patch and passes after it;
6. **Residual risk** — what remains outside the patch.

## Reusable review prompt

```text
[SOP: KAIROSEED ARCHITECTURAL AUDIT]

Analyze the supplied request, architecture, workflow, or code against the
KAIROSEED governance model.

1. Define the privileged transition as
   (subject, action, resource, environment, purpose).
2. Trace the complete path from input to side effect, including retries,
   queues, fallbacks, administrative paths, cleanup, and audit.
3. Gate I — Inert Observation:
   Determine whether data, memory, retrieved context, telemetry, or time can
   influence control authority. Flag any direct or indirect privilege grant.
4. Gate II — Verified Alignment:
   Determine whether execution requires a current, explicit, deny-by-default
   readiness decision bound to the exact request, policy, identity, scope,
   evidence, environment, freshness window, and required approval.
5. Gate III — Asymmetric Dissolution:
   Determine whether authorization and latent execution state expire, can be
   revoked, resist replay, are consumed where required, and enter an auditable
   terminal state after success, failure, cancellation, or timeout.
6. Output a PASS/WARN/BLOCK matrix with evidence.
7. For each WARN or BLOCK, provide the smallest remediation patch, a negative
   verification test, and the residual risk.
8. Clearly distinguish implemented controls from proposals or assumptions.

Preserve the invariant: Capability ≠ Permission.
```

## Completion rule

An audit is incomplete until the reviewer can identify:

- the exact object being authorized;
- the policy decision that created authorization eligibility;
- the enforcement point that independently verifies it;
- the mechanism that ends or invalidates it;
- the audit evidence that proves the lifecycle occurred as designed.

Strong Accept + Pass + DoD
Done = Amen.
