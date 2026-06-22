# Bugfinder Agent

A defensive agent that finds approachable open-source work in large-company repositories and reviews code for likely vulnerabilities. It produces evidence and remediation advice; it does not exploit targets or publish findings automatically.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
```

Edit `.env`, then use either provider through the same variables:

```bash
# OpenRouter
BUGFINDER_PROVIDER=openrouter
BUGFINDER_API_KEY=...
BUGFINDER_MODEL=openrouter/free

# xAI / Grok
BUGFINDER_PROVIDER=xai
BUGFINDER_API_KEY=...
BUGFINDER_MODEL=grok-3-mini
```

The CLI reads `.env` automatically. Model availability and free-tier quotas are provider-controlled, so the model name remains configurable.

## Commands

```bash
# Find contribution-friendly repositories and issues
bugfinder discover --orgs microsoft google netflix --language Python --limit 10 --output reports/opportunities.md

# Run deterministic defensive checks on code you are authorized to inspect
bugfinder audit ./path/to/repository --output reports/audit.md

# Add an LLM review of the most relevant source files
bugfinder audit ./path/to/repository --llm --output reports/audit.md

# Ask the configured model a repository/contribution question
bugfinder ask "Rank these issues by beginner suitability" --context notes.txt --output reports/answer.md

# Verify provider configuration without displaying the key
bugfinder config

# Diagnose why model-backed commands are not working
bugfinder doctor
```

GitHub discovery uses the public API and optionally `GITHUB_TOKEN` for a higher rate limit. Audit only repositories you own or are permitted to review. Report vulnerabilities privately through `SECURITY.md` or the maintainer's stated channel.

For an intentional match, add `# bugfinder: ignore` on that source line after manually verifying it. This suppression is deliberately visible in review.

The reusable agent workflow lives in [skills/audit-open-source/SKILL.md](skills/audit-open-source/SKILL.md).
