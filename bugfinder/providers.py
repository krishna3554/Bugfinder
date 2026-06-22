from __future__ import annotations

import json
import urllib.error
import urllib.request

from .config import Settings


class LLMClient:
    """Small OpenAI-compatible client shared by OpenRouter and xAI."""

    def __init__(self, settings: Settings):
        settings.require_llm()
        self.settings = settings

    def complete(self, system: str, user: str, max_tokens: int = 1800) -> str:
        body = json.dumps({
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        }).encode()
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "bugfinder-agent/0.1",
        }
        if self.settings.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/bugfinder-agent"
            headers["X-Title"] = "Bugfinder Agent"
        request = urllib.request.Request(
            f"{self.settings.base_url}/chat/completions", body, headers
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:500]
            raise RuntimeError(f"Provider returned HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach provider: {exc.reason}") from exc
        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Provider returned an unexpected response") from exc
