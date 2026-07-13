# Public Release Checklist

This branch is a **public-release candidate** prepared from the private KAIROSEED governance repository.

Do not publish the private repository by changing its visibility. Create a separate public repository and copy only the approved working-tree contents so private commit history, branches, pull requests, discussions, and deleted files remain private.

## Proposed public repository

- Owner: `kairoseedlabs`
- Suggested name: `kairoseed`
- Suggested description: `Verification-first governance architecture for bounded, auditable, and policy-controlled agentic AI execution.`
- Default branch: `main`
- Initial release: `v0.1.0-reference`

## Approved public scope

Include:

- `.github/workflows/test.yml`
- `.gitignore`
- `README.md`
- `SECURITY.md`
- `PUBLIC_RELEASE_CHECKLIST.md`
- `docs/foundational-principles.md`
- `docs/glossary.md`
- `docs/threat-model.md`
- `examples/`
- `policies/`
- `src/`
- `tests/`
- `pyproject.toml`

Review before including:

- future design drafts not marked for public release;
- internal roadmaps, customer notes, personal data, unpublished research, or operational credentials;
- CI logs, generated audit records, local environment files, and exported datasets.

## Required gates

### 1. Secret and privacy review

Confirm that the public snapshot contains none of the following:

- API keys, tokens, passwords, cookies, or private keys;
- `.env` files or local configuration containing credentials;
- personal addresses, phone numbers, private email threads, or customer data;
- private repository URLs or internal-only infrastructure details;
- audit logs containing user prompts, identifiers, or sensitive payloads.

The repository `.gitignore` already excludes `.env` and `audit/*.jsonl`, but ignored files must still be checked before export.

### 2. Claims review

Public documentation must preserve these limitations:

- the project is an early reference implementation;
- current packet serialization is provisional and is not claimed as KCS-0.2 compliant;
- current hashes are not cryptographic signatures;
- signing, replay protection, cross-runtime parity, and production validation are not yet complete;
- conceptual use of Chronos, Discernment, and Kairos does not claim that software detects or commands divine timing.

### 3. Test gate

Run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
python examples/evaluate_packet.py
```

The public repository must not be tagged or announced if tests fail.

### 4. License decision

Choose and add a license before describing the repository as open source.

Until a license is added, public access does not grant general permission to copy, modify, or redistribute the code.

Recommended options for explicit review:

- Apache License 2.0 for permissive reuse with an express patent grant;
- MIT License for a shorter permissive license;
- no open-source license when the repository is intended only for public inspection.

### 5. Clean-history export

Create the new public repository with a fresh initial commit. Do not push the private repository's existing `.git` directory or mirror private branches.

A safe local export pattern is:

```bash
# From a clean temporary directory
mkdir kairoseed-public
cd kairoseed-public

# Copy approved files from the release/public-v0.1 working tree here.
# Do not copy .git, .env, audit logs, caches, or local virtual environments.

git init
git branch -M main
git add .
git commit -m "Initial public KAIROSEED reference release"
git remote add origin <NEW_PUBLIC_REPOSITORY_URL>
git push -u origin main
```

### 6. Repository settings

After creation:

- enable branch protection for `main`;
- require the test workflow before merge;
- enable private vulnerability reporting;
- disable force pushes and branch deletion on `main`;
- enable Dependabot security updates where appropriate;
- add repository topics such as `ai-governance`, `ai-safety`, `agentic-ai`, `governance-as-code`, and `runtime-verification`;
- create release `v0.1.0-reference` only after the test and claims gates pass.

## Definition of done

The public repository is ready only when:

```text
DONE = Separate_Public_Repository
    ∧ Clean_History
    ∧ Approved_Files_Only
    ∧ No_Known_Secrets
    ∧ Tests_Pass
    ∧ Claims_Are_Qualified
    ∧ License_State_Is_Explicit
    ∧ Main_Branch_Is_Protected
```
