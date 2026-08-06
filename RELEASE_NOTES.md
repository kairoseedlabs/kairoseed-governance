# v0.1.0 — Governance Foundation & Claim Boundary

## Short summary
Initial public governance foundation for Kairoseed Labs. Establishes license, contribution process, security policy, and audit trail with no proprietary evidence.

## Highlights
- Added `LICENSE` - Apache-2.0
- Added `CONTRIBUTING.md` - Encodes Seed→Trace→Test→Align→Architect→Verify→Govern
- Added `SECURITY.md` - Vulnerability reporting + claim boundary
- Added `README.md` disclaimer - Evidence-based, no operational claims
- Established Codex automation audit via Issue #24

## Breaking changes
- None. This is v0.1.0 foundation release.

## Changelog
- #23 — docs: add clean public release checklist + governance files (@kairoseedlabs)
- #24 — chore: log Codex automated review for audit traceability (@kairoseedlabs)

## Contributors
- @kairoseedlabs

## Traces to
ISO 42001 A.4.1 | NIST AI RMF Govern-1 | Kairoseed: Seed

---

## How to publish (commands)
1. Create and push tag

```bash
git tag -a v0.1.0-governance-foundation -m "v0.1.0 — Governance Foundation & Claim Boundary"
git push origin v0.1.0-governance-foundation
```

2. Create release with gh CLI

```bash
gh release create v0.1.0-governance-foundation \
  --target main \
  --title "v0.1.0 — Governance Foundation & Claim Boundary" \
  --notes-file ./RELEASE_NOTES.md
```

Or GitHub UI: Repository → Releases → Draft a new release → Tag: `v0.1.0-governance-foundation` → Paste notes above → Publish release

---

If you'd like, I can also create the git tag and draft the GitHub release (requires a personal access token / push access or you can run the commands above).