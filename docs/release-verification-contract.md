# KAIROSEED Release Verification Contract

Status: **NORMATIVE**  
Scope: release minting for the KAIROSEED governance reference kernel  
Invariant: **Capability ≠ Permission**

## 1. Release boundary

The pipeline **MAY** build an unsigned candidate artifact for testing.

The pipeline **MUST NOT** sign, attest, publish, promote, or deploy that candidate as a release artifact until every mandatory verification control returns an exact `PASS` for the same source revision.

Candidate construction is capability. Release minting is permission. The former never implies the latter.

## 2. Release authorization equation

For every candidate inside the declared release domain:

\[
\forall c \in D_{\mathrm{release}},\quad
\operatorname{ReleaseAllowed}(c)
\iff
\operatorname{RequiredChecksPass}(c)
\land \operatorname{EvidenceComplete}(c)
\land \operatorname{SourceBound}(c)
\land \operatorname{AuthorityValid}(c)
\]

Where:

- `RequiredChecksPass`: every mandatory static-analysis, regression, parity, build-integrity, and policy check returns exact `PASS`;
- `EvidenceComplete`: required logs, reports, hashes, provenance, and decision evidence exist and are internally consistent;
- `SourceBound`: the candidate, verification evidence, and authorization evidence identify the same immutable source revision;
- `AuthorityValid`: release authority is authenticated, current, scoped to the candidate and release action, and not revoked or expired.

## 3. Fail-closed outcome

Any condition other than exact, complete, source-bound, authorized `PASS` returns `BLOCK`.

This includes:

- a failed control;
- a timeout;
- missing or unreadable evidence;
- an unauthorized skip or override;
- a flaky or non-reproducible result;
- an inconclusive evaluation;
- an unknown outcome or exception;
- stale, expired, revoked, or mismatched authority;
- source, artifact, evidence, or authority mismatch.

A blocked decision **MUST** be recorded. The pipeline **MUST** preserve the last known approved release and **MUST NOT** replace, mutate, promote, or redeploy it as though the candidate had passed.

## 4. Universal enforcement claim

The release rule is universal over the declared release domain:

\[
\forall c \in D_{\mathrm{release}},\quad
\neg\operatorname{VerificationContractPass}(c)
\Rightarrow
\operatorname{Mint}(c)=\operatorname{BLOCK}
\]

This is a universal quantification over all in-scope release candidates and all modeled control outcomes. It is **not** a claim that the software is universally safe, correct, suitable for every environment, or proven against every possible threat.

Mathematical alignment with this contract proves contract conformance only to the extent that:

- the contract is complete for the claimed release property;
- the implementation correctly realizes the contract;
- evidence is authentic and source-bound;
- trusted components and authorities satisfy their stated assumptions;
- the evaluated domain matches the deployed domain.

## 5. Meaning of perfect success

“Perfect success” means complete success against the defined verification contract for the evaluated candidate and declared domain.

It does not mean universal safety, absence of unknown vulnerabilities, correctness outside the model, or infallibility of external systems and human authorities.

## 6. Required pipeline behavior

1. Build the unsigned candidate in an isolated test context.
2. Run every mandatory static-analysis and regression control.
3. Collect complete source-bound evidence.
4. Evaluate release authority independently from build capability.
5. Return `PASS` only when all four release predicates are exact `PASS`.
6. Return `BLOCK` for every other state.
7. Record the decision and preserve the last known approved release.
8. Permit signing, attestation, publication, promotion, or deployment only after the release policy decision returns `PASS`.

## 7. Prohibited interpretations

- A successful build is not release authorization.
- A green subset of checks is not complete verification.
- A retried flaky check is not automatically reliable evidence.
- Administrator capability is not authority to bypass mandatory controls.
- A cryptographic signature proves control of a key and binding to signed bytes; it does not independently prove safety or correctness.
- Passing this contract does not erase residual risk.
