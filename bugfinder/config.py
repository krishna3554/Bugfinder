from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PLACEHOLDER_KEYS = {"", "your_api_key_here", "paste_your_key_here", "..."}


def read_dotenv(path: Path = Path(".env")) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip("'\"")
        values[key] = value
    return values


@dataclass(frozen=True)
class Settings:
    provider: str
    api_key: str
    model: str
    base_url: str
    github_token: str = ""
    max_file_bytes: int = 200_000

    @classmethod
    def from_env(cls) -> "Settings":
        dotenv = read_dotenv()

        def configured(name: str, default: str = "") -> str:
            return os.environ.get(name, dotenv.get(name, default))

        provider = configured("BUGFINDER_PROVIDER", "none").lower().strip()
        defaults = {
            "openrouter": ("https://openrouter.ai/api/v1", "openrouter/free"),
            "xai": ("https://api.x.ai/v1", "grok-3-mini"),
            "none": ("", ""),
        }
        if provider not in defaults:
            raise ValueError("BUGFINDER_PROVIDER must be openrouter, xai, or none")
        default_url, default_model = defaults[provider]
        dotenv_provider = dotenv.get("BUGFINDER_PROVIDER", "none").lower().strip()
        provider_was_overridden = (
            "BUGFINDER_PROVIDER" in os.environ
            and provider != dotenv_provider
        )

        def provider_setting(name: str, default: str) -> str:
            if name in os.environ:
                return os.environ[name]
            if provider_was_overridden:
                return default
            return dotenv.get(name, default)

        return cls(
            provider=provider,
            api_key=provider_setting("BUGFINDER_API_KEY", "").strip(),
            model=provider_setting("BUGFINDER_MODEL", default_model).strip(),
            base_url=provider_setting("BUGFINDER_BASE_URL", default_url).rstrip("/"),
            github_token=configured("GITHUB_TOKEN").strip(),
            max_file_bytes=int(configured("BUGFINDER_MAX_FILE_BYTES", "200000")),
        )

    @property
    def has_api_key(self) -> bool:
        return self.api_key.lower() not in PLACEHOLDER_KEYS

    def require_llm(self) -> None:
        if self.provider == "none":
            raise ValueError("Set BUGFINDER_PROVIDER to openrouter or xai")
        if not self.has_api_key:
            raise ValueError(
                "BUGFINDER_API_KEY is still a placeholder. Open .env, replace "
                "'your_api_key_here' with your real provider key, and retry."
            )
