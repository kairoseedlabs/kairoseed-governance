# KCS-0.2 Cross-Language Parity Gate

```yaml
domain:
  - AI Safety
  - Agent Governance
  - Governance-as-Code
  - Runtime Verification
invariant: "Capability ≠ Permission"
lifecycle_version: kairoseed/v1
execution_status: READY_FOR_CI_IMPLEMENTATION
```

## Classification

This gate is deterministic verification evidence. It is not authorization evidence and does not grant runtime or deployment capability.

## Boundary

The Python and TypeScript canonicalizers are independent implementations. They share only the frozen synthetic fixture contract. A single CI job produces both result documents from one checkout and compares:

```text
Python bytes == TypeScript bytes == frozen golden bytes
```

Negative vectors must produce the same deterministic `BLOCK` reason and must not emit canonical bytes or digests.

The workflow uses no `secrets.*` references, no `pull_request_target`, no production environment, no production identities or signing material, and no artifact upload. External actions are pinned to full commit SHAs. The workflow token is limited to `contents: read`, and checkout credentials are not persisted.

## Recovery

Any byte, digest, result-ID, status, or reason-code mismatch exits non-zero and blocks CI. KCS-0.2 remains RC1 until the required check is green and receives human review.

Required branch-protection check:

```text
KCS-0.2 Cross-Language Parity / Python == TypeScript == Golden
```

## Runtime governance non-claim

A raw tool request is not authorization. Canonicalization evidence does not replace the governed chain:

```text
VEP → Govana Core → GAT → PEP → bounded adapter → witness → commit or rollback
```
