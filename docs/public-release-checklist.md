# Public Release Checklist

Use this checklist before changing repository visibility from private to public.

## Authorization

- [ ] Repository owner has explicitly authorized publication.
- [ ] All open review comments are resolved or explicitly accepted as follow-up work.
- [ ] The review decision record has a strong-accept/pass outcome or documents the remaining exception.
- [ ] The default branch reflects the intended public baseline.

## Repository Hygiene

- [ ] CI passes on the publication candidate.
- [ ] Linting, formatting, type checking, and regression tests pass.
- [ ] Dependabot is enabled for GitHub Actions and Python dependencies.
- [ ] Pull requests use the repository verification checklist.
- [ ] The release decision is recorded in `docs/review-decision-record.md`.

## Public Documentation

- [ ] README claims are accurate and conservative.
- [ ] SECURITY.md explains the supported scope and private vulnerability reporting path.
- [ ] Limitations are clear: this repository is a reference implementation, not a production security boundary.

## Secret and History Review

- [ ] No private keys, credentials, tokens, unpublished research data, or confidential operational details are present in the working tree.
- [ ] Git history has been reviewed for secrets or confidential material before publication.
- [ ] Any generated artifacts, caches, or local environment files are excluded from publication.
