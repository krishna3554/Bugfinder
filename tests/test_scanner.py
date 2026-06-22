from pathlib import Path

from bugfinder.config import Settings
from bugfinder.scanner import scan


def test_scanner_finds_shell_true(tmp_path: Path):
    (tmp_path / "app.py").write_text("subprocess.run(user_input, shell=True)\n", encoding="utf-8")  # bugfinder: ignore
    findings = scan(tmp_path)
    assert [(f.rule, f.line) for f in findings] == [("python-shell-injection", 1)]


def test_settings_provider_defaults(monkeypatch):
    monkeypatch.setenv("BUGFINDER_PROVIDER", "xai")
    monkeypatch.delenv("BUGFINDER_BASE_URL", raising=False)
    monkeypatch.delenv("BUGFINDER_MODEL", raising=False)
    settings = Settings.from_env()
    assert settings.base_url == "https://api.x.ai/v1"
    assert settings.model == "grok-3-mini"


def test_placeholder_key_is_not_configured(monkeypatch):
    monkeypatch.setenv("BUGFINDER_PROVIDER", "openrouter")
    monkeypatch.setenv("BUGFINDER_API_KEY", "your_api_key_here")
    settings = Settings.from_env()
    assert not settings.has_api_key
