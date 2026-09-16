from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Opportunity:
    repository: str
    stars: int
    issue_title: str
    issue_url: str
    updated_at: str


class GitHubClient:
    def __init__(self, token: str = ""):
        self.token = token

    def _get(self, endpoint: str, params: dict[str, str | int]) -> dict:
        query = urllib.parse.urlencode(params)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "bugfinder-agent/0.1"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(f"https://api.github.com{endpoint}?{query}", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def discover(self, orgs: list[str], language: str = "", limit: int = 10) -> list[Opportunity]:
        if limit <= 0:
            raise ValueError("--limit must be a positive integer")
        if limit > 100:
            raise ValueError("--limit must not exceed 100")
        results: list[Opportunity] = []
        for org in orgs:
            query = f"org:{org} is:issue is:open label:\"good first issue\""
            if language:
                query += f" language:{language}"
            payload = self._get("/search/issues", {"q": query, "sort": "updated", "per_page": min(limit, 30)})
            for issue in payload.get("items", []):
                try:
                    repo_url = issue["repository_url"]
                    title = issue["title"]
                    html_url = issue["html_url"]
                    updated_at = issue["updated_at"]
                except KeyError as exc:
                    raise ValueError(f"GitHub API returned a malformed issue payload (missing {exc})") from exc
                repo_name = repo_url.rsplit("/repos/", 1)[-1]
                if "/" not in repo_name:
                    raise ValueError(f"GitHub API returned a malformed repository_url: {repo_url!r}")
                repo = self._get(f"/repos/{repo_name}", {})
                if repo.get("archived") or repo.get("disabled"):
                    continue
                results.append(Opportunity(repo_name, repo.get("stargazers_count", 0), title, html_url, updated_at))
        return sorted(results, key=lambda x: (x.updated_at, x.stars), reverse=True)[:limit]
