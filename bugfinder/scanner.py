from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "vendor",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}
SOURCE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".php", ".rs", ".c", ".cpp", ".h"}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    evidence: str
    remediation: str


RULES = [
    ("HIGH", "python-shell-injection", re.compile(r"subprocess\.(?:run|call|Popen)\([^\n]*shell\s*=\s*True"), "Avoid shell=True; pass a fixed argument list and validate untrusted input."),
    ("HIGH", "python-unsafe-deserialization", re.compile(r"\b(?:pickle\.loads?|yaml\.load)\s*\("), "Use a safe format; for YAML use safe_load and never deserialize untrusted pickle data."),
    ("HIGH", "javascript-code-execution", re.compile(r"\b(?:eval|new\s+Function)\s*\("), "Remove dynamic code execution or strictly constrain input with a safe parser."),
    ("MEDIUM", "weak-hash", re.compile(r"\b(?:md5|sha1)\s*\(", re.I), "Use SHA-256+ for integrity or a password KDF such as Argon2/bcrypt for passwords."),
    ("MEDIUM", "tls-verification-disabled", re.compile(r"(?:verify\s*=\s*False|rejectUnauthorized\s*:\s*false)"), "Enable certificate validation and configure a trusted CA when needed."),
    ("MEDIUM", "hardcoded-secret", re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*[=:]\s*['\"][A-Za-z0-9_\-/.+=]{16,}['\"]"), "Load secrets from a secret manager or environment and rotate any exposed credential."),
]


def source_files(root: Path, max_bytes: int = 200_000):
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
        except OSError:
            continue
        yield path


def scan(root: Path, max_bytes: int = 200_000) -> list[Finding]:
    findings: list[Finding] = []
    for path in source_files(root, max_bytes):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            if "bugfinder: ignore" in line:
                continue
            for severity, rule, pattern, remediation in RULES:
                if pattern.search(line):
                    findings.append(Finding(severity, rule, str(path.relative_to(root)), number, line.strip()[:240], remediation))
    return findings


def markdown_report(root: Path, findings: list[Finding], llm_review: str = "") -> str:
    rows = ["# Defensive security review", "", f"Target: `{root.resolve()}`", "", "Static matches require manual validation; they are leads, not confirmed vulnerabilities.", ""]
    if not findings:
        rows += ["## Static findings", "", "No rule matches found.", ""]
    else:
        rows += ["## Static findings", ""]
        for finding in findings:
            rows += [f"### {finding.severity}: {finding.rule}", "", f"- Location: `{finding.path}:{finding.line}`", f"- Evidence: `{finding.evidence}`", f"- Remediation: {finding.remediation}", ""]
    if llm_review:
        rows += ["## Model-assisted review", "", llm_review.strip(), ""]
    rows += ["## Disclosure", "", "Verify each issue, minimize sensitive detail, and report privately via the repository's SECURITY.md policy. Do not test against live systems without explicit authorization.", ""]
    return "\n".join(rows)
