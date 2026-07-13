# Security Policy

## Project status

KAIROSEED is an early reference implementation. It is not currently represented as a production security boundary, independently validated safety system, cryptographic signing service, or complete runtime enforcement platform.

The current code demonstrates governance concepts and fail-closed behavior. Several controls described in the threat model remain target capabilities rather than implemented guarantees.

## Supported versions

| Version | Supported |
|---|---|
| `0.1.x` | Yes, for reference-level fixes |
| Earlier versions | No |

## Reporting a vulnerability

Do not publish exploit details, secrets, or sensitive reproduction data in a public issue.

Use GitHub private vulnerability reporting when it is enabled for the repository. Until then, open a minimal public issue stating that you need a private security-reporting channel, without including exploit details.

A useful report includes:

- affected file, function, or boundary;
- expected and observed behavior;
- minimum reproduction steps;
- security consequence;
- whether the issue permits authorization bypass, replay, scope expansion, audit failure, or unsafe execution;
- suggested verification test, when available.

## Security invariants

Reports are especially important when they show that any of the following can occur:

1. capability becomes permission without explicit authorization;
2. malformed, missing, expired, ambiguous, or unverifiable input does not fail closed;
3. one packet's authorization evidence can authorize another packet;
4. `WARN` or `BLOCK` can reach execution;
5. policy evaluation directly executes the requested action;
6. the enforcement point accepts evidence it did not independently verify;
7. audit evidence is treated as authorization evidence;
8. runtime recovery expands authorization scope;
9. an undefined condition silently selects continued execution.

## Disclosure expectations

Please allow reasonable time for validation and remediation before public disclosure. Acknowledgement does not imply that a report is valid until it has been reproduced and assessed against the documented architecture and threat model.
