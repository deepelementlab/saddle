"""Contract tests for Claude/OpenClaw plugins against saddle serve REST."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from saddle.memory_api.server import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SADDLE_MEMORY_DIR", str(tmp_path / "mem"))
    monkeypatch.chdir(tmp_path)
    return TestClient(app)


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


def test_post_memories_group_payload(client: TestClient) -> None:
    body = {
        "group_id": "g1",
        "user_id": "u1",
        "messages": [{"role": "user", "content": "hello plugin", "timestamp": 1}],
        "async_mode": True,
    }
    r = client.post("/api/v1/memories", json=body)
    assert r.status_code == 200


def test_post_search_matches_plugin_body(client: TestClient) -> None:
    client.post(
        "/api/v1/memories",
        json={
            "group_id": "g-search",
            "user_id": "u1",
            "messages": [{"role": "user", "content": "unique-keyword-xyz", "timestamp": 1}],
            "async_mode": True,
        },
    )
    r = client.post(
        "/api/v1/memories/search",
        json={"query": "unique-keyword-xyz", "top_k": 5, "filters": {"group_id": "g-search"}},
    )
    assert r.status_code == 200
    data = r.json()
    assert "data" in data
    assert "memories" in data["data"]
    assert "count" in data["data"]
    assert isinstance(data["data"]["memories"], list)
