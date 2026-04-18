"""Tests for POST /api/v1/pipeline/run."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from saddle.memory_api.server import app
from saddle.pipeline.runner import PipelineResult, PipelineRunner


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SADDLE_MEMORY_DIR", str(tmp_path / "mem"))
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".saddle" / "modes").mkdir(parents=True)
    return TestClient(app)


def test_pipeline_run_validation(client: TestClient) -> None:
    r = client.post("/api/v1/pipeline/run", json={})
    assert r.status_code == 422


def test_pipeline_run_bad_project_root(client: TestClient, tmp_path: Path) -> None:
    r = client.post(
        "/api/v1/pipeline/run",
        json={"requirement": "x", "project_root": str(tmp_path / "does-not-exist")},
    )
    assert r.status_code == 400


def test_pipeline_run_ok_mocked(client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(self: PipelineRunner, requirement: str, mode: object, session_id: str) -> PipelineResult:
        return PipelineResult(mode=mode.name, session_id=session_id, stages=[])

    monkeypatch.setattr(PipelineRunner, "run", fake_run)

    r = client.post(
        "/api/v1/pipeline/run",
        json={
            "requirement": "implement feature",
            "mode": "default",
            "project_root": str(tmp_path),
            "set": ["develop.max_iters=5"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["project_root"] == str(tmp_path.resolve())
    assert data["result"]["mode"] == "default"
    assert "session_id" in data["result"]
