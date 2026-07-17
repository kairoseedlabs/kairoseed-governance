# Security Policy

KAIROSEED Governance is an early reference implementation for verification-first agent governance. It is not a production security boundary, cryptographic signing service, or independently validated safety system.

## Supported Versions

Security review currently applies to the default branch only. Tagged releases are not yet maintained as independently supported security lines.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately to the repository maintainers instead of opening a public issue with exploit details.

A useful report includes:

- the affected component or workflow;
- reproduction steps or a minimal proof of concept;
- expected and actual behavior;
- impact assessment; and
- any proposed mitigation.

Maintainers should acknowledge the report, investigate the affected governance invariant, and publish a fix or advisory when the issue has been resolved.

## Public Release Readiness

Before making this repository public, maintainers should verify that:

- all review comments have been resolved;
- CI, linting, formatting, type checking, and regression tests pass;
- dependency maintenance is enabled for GitHub Actions and Python dependencies;
- public documentation accurately describes the project as a reference implementation; and
- no private keys, credentials, unpublished research data, or confidential operational details are present in the repository history.
