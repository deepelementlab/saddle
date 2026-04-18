"""HTTP endpoint to run the default Saddle pipeline (same as `saddle run` CLI)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from saddle.modes.resolver import resolve_mode
from saddle.pipeline.runner import PipelineRunner

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


class PipelineRunPayload(BaseModel):
    """Body for POST /api/v1/pipeline/run (mirrors `saddle run` + `--set`)."""

    model_config = ConfigDict(populate_by_name=True)

    requirement: str = Field(..., min_length=1, description="Pipeline requirement text")
    mode: str = Field(default="default", description="Mode name (stem under .saddle/modes/)")
    overrides: list[str] | None = Field(
        default=None,
        alias="set",
        description="Override key=value entries, same as CLI --set (JSON key: set)",
    )
    project_root: str | None = Field(
        default=None,
        description="Absolute project root; defaults to server process cwd",
    )
    session_id: str | None = Field(default=None, description="Optional session id (UUID if omitted)")


@router.post("/run")
def run_pipeline(payload: PipelineRunPayload) -> dict[str, Any]:
    """Execute PipelineRunner in ``project_root`` (same logic as ``saddle run``)."""
    raw_root = payload.project_root or str(Path.cwd())
    root = Path(raw_root).expanduser().resolve()
    if not root.is_dir():
        raise HTTPException(status_code=400, detail=f"project_root is not a directory: {root}")

    sid = payload.session_id or str(uuid.uuid4())
    try:
        resolved = resolve_mode(str(root), mode_name=payload.mode, overrides=payload.overrides)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        runner = PipelineRunner(root)
        result = runner.run(
            requirement=payload.requirement.strip(),
            mode=resolved,
            session_id=sid,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"ok": True, "project_root": str(root), "result": result.to_dict()}
