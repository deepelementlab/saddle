"""Resolve and serve Saddle Studio (Vite) static build from `saddle serve`."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles


def studio_dist_dir() -> Path | None:
    """Return directory containing built `index.html`, or None if not available."""
    env = os.environ.get("SADDLE_STUDIO_DIR", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "index.html").is_file():
            return p
    here = Path(__file__).resolve().parent
    for base in here.parents:
        cand = base / "studio" / "dist"
        if (cand / "index.html").is_file():
            return cand.resolve()
    return None


def _safe_file_under(dist: Path, relative_path: str) -> Path | None:
    rel = relative_path.lstrip("/")
    if not rel or any(part == ".." for part in rel.split("/")):
        return None
    target = (dist / rel).resolve()
    dist_r = dist.resolve()
    try:
        target.relative_to(dist_r)
    except ValueError:
        return None
    return target if target.is_file() else None


def build_studio_router(dist: Path) -> APIRouter:
    """Routes + mounts for Studio SPA (register after all API routes)."""
    router = APIRouter()

    assets = dist / "assets"
    if assets.is_dir():
        router.mount("/assets", StaticFiles(directory=str(assets)), name="studio-assets")

    @router.get("/", include_in_schema=False)
    async def studio_index() -> FileResponse:
        return FileResponse(dist / "index.html")

    @router.get("/{full_path:path}", include_in_schema=False)
    async def studio_static_or_spa(full_path: str) -> FileResponse:
        first = full_path.split("/")[0]
        if first in ("api", "docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404)
        hit = _safe_file_under(dist, full_path)
        if hit is not None:
            return FileResponse(hit)
        return FileResponse(dist / "index.html")

    return router
