# Supply-chain security controls

This document describes the implementation mapping for the Govana/KALYTH software-supply-chain baseline.

## Control chain

```text
SOURCE
  -> SECURE DEVELOPMENT
  -> CONTROLLED BUILD
  -> ARTIFACT DIGEST
  -> SLSA PROVENANCE
  -> VERIFICATION
  -> KYVERNO ADMISSION
  -> DEPLOYMENT
  -> EVIDENCE
  -> CLOSED LOOP
```

## NIST SSDF

`compliance/nist-ssdf-mapping.yaml` maps the implemented controls to NIST SP 800-218 SSDF v1.1 practices. The mapping is an implementation alignment record; it is not a certification or regulatory compliance claim.

## SLSA provenance

The target is **SLSA Build L3**, not merely a JSON document. A conforming release requires a trusted/hardened build service, authenticated provenance, isolation between build executions, protection of provenance-signing material, and downstream verification.

`provenance/examples/slsa-provenance.json` is a schema-level example only. It intentionally contains placeholders and MUST NOT be treated as a valid attestation.

For a container release, the release workflow must:

1. Build and push the image.
2. Capture the immutable image digest from the build output.
3. Generate signed provenance in an isolated trusted workflow.
4. Publish the attestation alongside the image.
5. Verify the attestation against the expected source repository and trusted builder identity.
6. Admit only the verified artifact.

The authoritative artifact identity is the digest, not a mutable tag.

## Kyverno

The policy suite enforces:

- immutable image digests
- approved image registry
- non-root execution
- `allowPrivilegeEscalation: false`
- all Linux capabilities dropped
- read-only root filesystem
- resource requests and limits
- `RuntimeDefault` or approved `Localhost` seccomp

`tests/kyverno/kyverno-test.yaml` contains positive and negative admission cases. The GitHub Actions workflow runs the Kyverno CLI tests on pull requests and manual dispatch.

## Release gate

```text
Source integrity       PASS
Secure build           PASS
Artifact digest        PASS
SLSA provenance        PASS
Provenance verification PASS
Kyverno tests          PASS
Admission policy       PASS
Evidence retained      PASS

RELEASE AUTHORIZATION = PASS
```

No provenance means no trusted artifact. No policy compliance means no admission. No evidence means no security acceptance.
