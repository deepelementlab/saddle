from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from saddle.memory_api import server as srv
from saddle.memory_api.store import MemoryStore


@pytest.fixture
def memory_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SADDLE_MEMORY_DIR", str(tmp_path / "mem"))
    srv._store = MemoryStore(tmp_path / "mem")  # type: ignore[attr-defined]
    return TestClient(srv.app)


def test_health(memory_client: TestClient) -> None:
    r = memory_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_memory_group_search(memory_client: TestClient) -> None:
    w = memory_client.post(
        "/api/v1/memories/group",
        json={
            "group_id": "g1",
            "user_id": "u1",
            "messages": [
                {"role": "user", "content": "I prefer dark mode"},
                {"role": "assistant", "content": "Noted."},
            ],
        },
    )
    assert w.status_code == 200
    s = memory_client.post(
        "/api/v1/memories/search",
        json={"query": "dark mode", "top_k": 5, "filters": {"group_id": "g1"}},
    )
    assert s.status_code == 200
    assert s.json()["data"]["count"] >= 1
