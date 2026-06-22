# Contribution and disclosure policy

## Contribution checks

- Confirm the repository license and contribution guide permit the intended work.
- Search open pull requests and issue comments to avoid duplicating active work.
- Do not submit mass-generated patches. Understand, test, and explain every change.
- Follow the project's developer certificate, CLA, style, test, and changelog rules.

## Defensive review boundaries

- Review code and local fixtures only unless the owner explicitly authorizes a broader target and method.
- Avoid denial of service, credential access, persistence, social engineering, or third-party data.
- Preserve only minimal evidence and redact secrets.
- Prefer a regression test over an exploit demonstration.

## Private report template

Include: concise title, affected component/version, prerequisites, code-path evidence, impact, confidence, inert reproduction or regression test, suggested remediation, and reporter contact. Follow `SECURITY.md`; if absent, use the repository's private security advisory feature or a published security contact. Allow maintainers time to investigate before any coordinated publication.
