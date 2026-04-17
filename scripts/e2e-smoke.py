"""Saddle end-to-end smoke test.

Run after starting `saddle serve`.
"""

from __future__ import annotations

import json
import urllib.request

BASE = "http://127.0.0.1:1995"


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    print("health:", get("/health"))
    save = post(
        "/api/v1/memories/group",
        {
            "group_id": "e2e-group",
            "user_id": "tester",
            "messages": [
                {"role": "user", "content": "remember that I prefer dark mode"},
                {"role": "assistant", "content": "saved preference: dark mode"},
            ],
        },
    )
    print("save:", save)
    search = post(
        "/api/v1/memories/search",
        {"query": "dark mode", "top_k": 3, "filters": {"group_id": "e2e-group"}},
    )
    print("search_count:", search.get("data", {}).get("count"))
    assert search.get("data", {}).get("count", 0) >= 1, "expected at least one memory hit"
    print("E2E smoke passed.")


if __name__ == "__main__":
    main()
