from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from saddle.memory_api.studio_static import build_studio_router, studio_dist_dir


def test_studio_dist_dir_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>x</html>", encoding="utf-8")
    monkeypatch.setenv("SADDLE_STUDIO_DIR", str(dist))
    assert studio_dist_dir() == dist.resolve()


def test_build_studio_router_serves_spa_and_assets(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>studio</title>", encoding="utf-8")
    assets = dist / "assets"
    assets.mkdir()
    (assets / "app.js").write_text("console.log(1)", encoding="utf-8")

    app = FastAPI()
    app.include_router(build_studio_router(dist))
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert "studio" in r.text

    a = client.get("/assets/app.js")
    assert a.status_code == 200
    assert "console" in a.text

    spa = client.get("/studio")
    assert spa.status_code == 200
    assert "studio" in spa.text
