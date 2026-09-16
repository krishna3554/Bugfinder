from __future__ import annotations

import argparse
import sys
import urllib.error
from pathlib import Path

from .config import Settings
from .github import GitHubClient
from .providers import LLMClient
from .scanner import markdown_report, scan, source_files


SYSTEM = """You are a defensive open-source engineering agent. Be evidence-based. Never invent findings, exploit systems, expose secrets, or recommend testing without authorization. Distinguish suspicious patterns from confirmed vulnerabilities. Prefer small maintainable contributions and private coordinated disclosure."""


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bugfinder", description="Open-source contribution and defensive audit agent")
    sub = p.add_subparsers(dest="command", required=True)
    discover = sub.add_parser("discover", help="find good-first-issue opportunities")
    discover.add_argument("--orgs", nargs="+", default=["microsoft", "google", "netflix", "meta", "cloudflare"])
    discover.add_argument("--language", default="")
    discover.add_argument("--limit", type=int, default=10)
    discover.add_argument("--output", type=Path, help="write results to a Markdown file")
    audit = sub.add_parser("audit", help="scan an authorized local repository")
    audit.add_argument("path", type=Path)
    audit.add_argument("--llm", action="store_true")
    audit.add_argument("--output", type=Path)
    ask = sub.add_parser("ask", help="ask the configured defensive agent")
    ask.add_argument("prompt")
    ask.add_argument("--context", type=Path)
    ask.add_argument("--output", type=Path, help="write the response to a Markdown file")
    sub.add_parser("config", help="show non-secret provider configuration")
    sub.add_parser("doctor", help="diagnose local configuration")
    return p


def llm_audit(root: Path, settings: Settings) -> str:
    from itertools import islice

    excerpts = []
    for path in islice(source_files(root, settings.max_file_bytes), 20):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:8000]
        except OSError:
            continue
        excerpts.append(f"\n--- {path.relative_to(root)} ---\n{text}")
    if not excerpts:
        return "No supported source files were available for model review."
    prompt = "Review these excerpts for defensible security concerns. Give file/line evidence, confidence, impact, and a safe fix. Do not claim a vulnerability without sufficient evidence.\n" + "".join(excerpts)
    return LLMClient(settings).complete(SYSTEM, prompt, max_tokens=2500)


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        settings = Settings.from_env()
        if args.command == "config":
            print(f"provider={settings.provider}\nmodel={settings.model or '(none)'}\nbase_url={settings.base_url or '(none)'}\napi_key={'configured' if settings.has_api_key else 'missing'}")
        elif args.command == "doctor":
            problems = []
            if settings.provider == "none":
                problems.append("BUGFINDER_PROVIDER is not set to openrouter or xai")
            if not settings.has_api_key:
                problems.append("BUGFINDER_API_KEY is missing or still the example placeholder")
            if not settings.model:
                problems.append("BUGFINDER_MODEL is empty")
            print(f"provider: {settings.provider}")
            print(f"model: {settings.model or '(none)'}")
            print(f"API key: {'configured' if settings.has_api_key else 'not configured'}")
            print(f"GitHub token: {'configured' if settings.github_token else 'not configured (optional)'}")
            if problems:
                print("\nModel-backed commands are not ready:")
                for problem in problems:
                    print(f"- {problem}")
                print("\nEdit .env, then run: bugfinder doctor")
                return 2
            print("\nConfiguration is ready. Test it with: bugfinder ask \"Reply with OK\"")
        elif args.command == "discover":
            items = GitHubClient(settings.github_token).discover(args.orgs, args.language, args.limit)
            lines = ["# Open-source contribution opportunities", ""]
            if not items:
                lines.append("No matching open issues found.")
            for item in items:
                lines.extend([
                    f"## {item.repository}", "",
                    f"- Stars: {item.stars}",
                    f"- Issue: [{item.issue_title}]({item.issue_url})",
                    f"- Last updated: {item.updated_at}", "",
                ])
            result = "\n".join(lines)
            if args.output:
                write_markdown(args.output, result)
                print(f"Wrote {len(items)} opportunity result(s) to {args.output}")
            else:
                print(result)
        elif args.command == "audit":
            root = args.path.resolve()
            if not root.is_dir():
                raise ValueError(f"Not a directory: {root}")
            findings = scan(root, settings.max_file_bytes)
            review = llm_audit(root, settings) if args.llm else ""
            report = markdown_report(root, findings, review)
            if args.output:
                write_markdown(args.output, report)
                print(f"Wrote {len(findings)} static finding(s) to {args.output}")
            else:
                print(report)
        elif args.command == "ask":
            context = ""
            if args.context:
                context = "\n\nContext:\n" + args.context.read_text(encoding="utf-8")[:50_000]
            response = LLMClient(settings).complete(SYSTEM, args.prompt + context)
            result = f"# Bugfinder agent response\n\n## Request\n\n{args.prompt}\n\n## Response\n\n{response}"
            if args.output:
                write_markdown(args.output, result)
                print(f"Wrote agent response to {args.output}")
            else:
                print(response)
        return 0
    except (ValueError, RuntimeError, OSError, urllib.error.URLError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
