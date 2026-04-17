"""HTTP API for visual mode management."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from saddle.modes.collaboration_payload import normalize_collaboration_config
from saddle.modes.loader import mode_from_dict
from saddle.modes.resolver import resolve_mode
from saddle.modes.tools import list_mode_names, validate_mode_config

router = APIRouter(prefix="/api/v1/modes", tags=["modes"])


class TeamStagePayload(BaseModel):
    enabled: bool = True
    deep_loop: bool = False
    max_iters: int = 100
    prompt_profile: Literal["full", "compact"] = "full"


class ModePayload(BaseModel):
    name: str = "default"
    pipeline: dict[str, Any] = Field(default_factory=lambda: {"enabled": True, "order": ["spec", "design", "develop"]})
    spec: dict[str, Any] = Field(default_factory=lambda: {"enabled": True})
    design: TeamStagePayload = Field(default_factory=TeamStagePayload)
    develop: TeamStagePayload = Field(default_factory=TeamStagePayload)
    agent_selection: dict[str, Any] = Field(default_factory=lambda: {"strategy": "minimal", "custom_roles": []})
    thresholds: dict[str, float] = Field(
        default_factory=lambda: {"min_gap_delta": 0.05, "convergence_rounds": 2.0, "handoff_target": 0.85}
    )
    role_mindsets: dict[str, str] = Field(default_factory=dict)
    tool_policy: dict[str, Any] = Field(
        default_factory=lambda: {
            "enable_web_search": True,
            "enable_shell": True,
            "enable_subagent": True,
            "risk_level": "balanced",
        }
    )
    collaboration_config: dict[str, Any] = Field(default_factory=dict)

    def to_mode_dict(self) -> dict[str, Any]:
        data = self.model_dump()
        data["design"] = self.design.model_dump()
        data["develop"] = self.develop.model_dump()
        return data


def _project_root() -> Path:
    return Path.cwd().expanduser().resolve()


def _mode_path(root: Path, name: str) -> Path:
    return root / ".saddle" / "modes" / f"{name}.yaml"


def _load_extras_from_yaml(path: Path) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    if not path.is_file():
        return {}, {}, {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {}, {}, {}
    role_mindsets = raw.get("role_mindsets")
    tool_policy = raw.get("tool_policy")
    collaboration_config = raw.get("collaboration_config")
    return (
        role_mindsets if isinstance(role_mindsets, dict) else {},
        tool_policy if isinstance(tool_policy, dict) else {},
        collaboration_config if isinstance(collaboration_config, dict) else {},
    )


@router.get("")
def list_modes() -> dict[str, Any]:
    root = _project_root()
    return {"modes": list_mode_names(root), "path": str(root / ".saddle" / "modes")}


@router.get("/{name}")
def show_mode(name: str) -> dict[str, Any]:
    root = _project_root()
    try:
        cfg = resolve_mode(str(root), mode_name=name, overrides=None)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    payload = asdict(cfg)
    role_mindsets, tool_policy, collaboration_config = _load_extras_from_yaml(_mode_path(root, name))
    payload["role_mindsets"] = role_mindsets
    payload["tool_policy"] = tool_policy or {
        "enable_web_search": True,
        "enable_shell": True,
        "enable_subagent": True,
        "risk_level": "balanced",
    }
    merged_cc = collaboration_config if isinstance(collaboration_config, dict) else {}
    payload["collaboration_config"] = normalize_collaboration_config(merged_cc)
    return payload


@router.post("/validate")
def validate_mode(payload: ModePayload) -> dict[str, Any]:
    data = payload.to_mode_dict()
    cfg = mode_from_dict(data)
    errors, warnings = validate_mode_config(cfg)
    return {"mode": cfg.name, "ok": len(errors) == 0, "errors": errors, "warnings": warnings}


@router.post("/save")
def save_mode(payload: ModePayload) -> dict[str, Any]:
    data = payload.to_mode_dict()
    cfg = mode_from_dict(data)
    errors, warnings = validate_mode_config(cfg)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors, "warnings": warnings})

    root = _project_root()
    target = _mode_path(root, cfg.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    out = payload.to_mode_dict()
    out["name"] = cfg.name
    target.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"saved": str(target), "mode": cfg.name, "warnings": warnings}
