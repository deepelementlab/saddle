"""FastAPI application for Saddle memory APIs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from saddle.memory_api.pipeline_route import router as pipeline_router
from saddle.memory_api.store import MemoryStore
from saddle.memory_api.studio_static import build_studio_router, studio_dist_dir
from saddle.modes.api import router as modes_router

app = FastAPI(title="Saddle Memory API", version="0.1.0")
app.include_router(modes_router)
app.include_router(pipeline_router)

_memory_root = Path(
    os.environ.get("SADDLE_MEMORY_DIR", str(Path.cwd() / ".saddle" / "memory"))
)
_store = MemoryStore(_memory_root)


class GroupMessage(BaseModel):
    role: str = "user"
    content: str
    timestamp: int | None = None


class GroupPayload(BaseModel):
    group_id: str = "saddle-default-group"
    user_id: str = "saddle-user"
    messages: list[GroupMessage] = Field(default_factory=list)
    async_mode: bool = True


class SearchPayload(BaseModel):
    query: str
    top_k: int = 5
    filters: dict[str, Any] | None = None


class GetPayload(BaseModel):
    filters: dict[str, Any] | None = None
    page: int = 1
    page_size: int = 50


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "saddle-memory"}


@app.post("/api/v1/memories/group")
def add_group_memory(payload: GroupPayload) -> dict[str, Any]:
    result = _store.append_messages(
        group_id=payload.group_id,
        user_id=payload.user_id,
        messages=[m.model_dump() for m in payload.messages],
    )
    return {"message": "Message accepted and queued for processing", **result}


@app.post("/api/v1/memories")
def add_memory(payload: GroupPayload) -> dict[str, Any]:
    return add_group_memory(payload)


@app.post("/api/v1/memories/search")
def search_memories(payload: SearchPayload) -> dict[str, Any]:
    group_id = None
    if payload.filters:
        group_id = payload.filters.get("group_id")
    data = _store.search(payload.query, group_id=group_id, top_k=payload.top_k)
    return {"data": {"memories": data, "count": len(data)}}


@app.post("/api/v1/memories/get")
def get_memories(payload: GetPayload) -> dict[str, Any]:
    group_id = None
    if payload.filters:
        group_id = payload.filters.get("group_id")
    data = _store.get(group_id=group_id, page=payload.page, page_size=payload.page_size)
    return {"data": data}


# Studio static build (after all API routes so /health, /api/*, /docs match first).
_studio_dist = studio_dist_dir()
if _studio_dist is not None:
    app.include_router(build_studio_router(_studio_dist))
