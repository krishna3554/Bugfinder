---
name: audit-open-source
description: Find contribution-ready issues in public repositories maintained by large organizations, inspect unfamiliar codebases, and perform authorized defensive vulnerability reviews with evidence and responsible-disclosure guidance. Use for open-source opportunity discovery, repository orientation, contribution planning, local static review, secure fix preparation, or private maintainer reports; never use it to exploit systems or probe targets without permission.
---

# Audit Open Source

Use the project CLI for repeatable discovery and initial scanning. Treat every automated match and model observation as a hypothesis until code flow and tests confirm it.

## Choose the workflow

- For a contribution request, run `bugfinder discover`, shortlist maintained repositories, then read `README`, `CONTRIBUTING`, issue history, and the relevant tests before proposing work.
- For an authorized security review, run `bugfinder audit <local-repo>`, manually trace each result, add a regression test, and propose the smallest safe fix.
- For model-assisted analysis, configure one provider in `.env` and add `--llm`. Keep deterministic checks available when quota is exhausted.
- For disclosure or contribution etiquette, read [references/policy.md](references/policy.md).

## Discover contributions

1. Search official organization repositories for open `good first issue` or `help wanted` issues.
2. Reject archived repositories, stale issues, unclear licenses, generated-code-only changes, and work already claimed in recent comments.
3. Prefer reproducible bugs with nearby tests, responsive maintainers, and a contribution guide.
4. Reproduce the issue locally before editing.
5. Keep the patch scoped; run the repository's formatter and focused tests.
6. In the handoff, cite the issue, explain the cause, summarize tests, and state uncertainty.

## Review security safely

1. Confirm the repository is local/public and the requested activity is authorized. Do not interact with deployed endpoints.
2. Read threat boundaries, dependency manifests, `SECURITY.md`, entry points, authentication, parsers, subprocesses, file access, and network clients.
3. Run the deterministic scanner. Inspect data flow around every match; discard false positives explicitly.
4. Validate using local unit tests or inert fixtures. Never access real secrets, bypass controls, establish persistence, or weaponize a proof of concept.
5. Record affected versions, preconditions, file/line evidence, impact, confidence, and remediation.
6. Prepare a regression test and minimal fix when requested.
7. Report privately using the maintainer's security channel. Do not open a public issue containing exploitable detail.

## Use models economically

- Send only relevant excerpts and redact credentials or personal data.
- Use the shared `BUGFINDER_API_KEY`, `BUGFINDER_PROVIDER`, and `BUGFINDER_MODEL` variables; never commit `.env`.
- Ask the model for evidence, confidence, counterexamples, and validation steps.
- Fall back to local scanning when rate-limited; free-tier availability is not guaranteed.
- Never accept model-generated line numbers or vulnerability claims without checking the repository.

## Required output

For contribution work, return repository and issue links, suitability reasons, reproduction status, proposed files, and test plan. For security work, return scoped findings with evidence, confidence, impact, safe validation, remediation, and the private disclosure route. Clearly label unverified suspicions.
