"""Load YAML collaboration modes from .saddle/modes."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from saddle.modes.schema import (
    AgentSelectionConfig,
    ModeConfig,
    PipelineConfig,
    StageSpecConfig,
    StageTeamConfig,
)


def _mode_files(project_root: Path, mode_name: str) -> list[Path]:
    base = project_root / ".saddle" / "modes"
    return [base / f"{mode_name}.yaml", base / f"{mode_name}.yml"]


def _deep_update(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = dict(target)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_update(out[k], v)
        else:
            out[k] = v
    return out


def _normalize_stage_name(stage: str) -> str:
    if stage == "designteam":
        return "design"
    if stage == "clawteam":
        return "develop"
    return stage


def mode_from_dict(data: dict[str, Any]) -> ModeConfig:
    mode = ModeConfig()
    mode.name = str(data.get("name") or mode.name)
    pipeline = data.get("pipeline") or {}
    order = list(pipeline.get("order") or ["spec", "design", "develop"])
    mode.pipeline = PipelineConfig(
        enabled=bool(pipeline.get("enabled", True)),
        order=[_normalize_stage_name(str(s)) for s in order],
    )
    spec = data.get("spec") or {}
    mode.spec = StageSpecConfig(enabled=bool(spec.get("enabled", True)))
    d = data.get("design") or data.get("designteam") or {}
    mode.design = StageTeamConfig(
        enabled=bool(d.get("enabled", True)),
        deep_loop=bool(d.get("deep_loop", False)),
        max_iters=int(d.get("max_iters", 100)),
        prompt_profile=str(d.get("prompt_profile", "full")),
    )
    c = data.get("develop") or data.get("clawteam") or {}
    mode.develop = StageTeamConfig(
        enabled=bool(c.get("enabled", True)),
        deep_loop=bool(c.get("deep_loop", False)),
        max_iters=int(c.get("max_iters", 100)),
        prompt_profile=str(c.get("prompt_profile", "full")),
    )
    a = data.get("agent_selection") or {}
    mode.agent_selection = AgentSelectionConfig(
        strategy=str(a.get("strategy", "minimal")),
        custom_roles=[str(x) for x in (a.get("custom_roles") or [])],
    )
    mode.thresholds = {
        "min_gap_delta": float((data.get("thresholds") or {}).get("min_gap_delta", 0.05)),
        "convergence_rounds": float((data.get("thresholds") or {}).get("convergence_rounds", 2)),
        "handoff_target": float((data.get("thresholds") or {}).get("handoff_target", 0.85)),
    }
    return mode


def default_mode() -> ModeConfig:
    return ModeConfig(name="default")


def load_mode_from_file(project_root: str | Path, mode_name: str) -> ModeConfig:
    root = Path(project_root).expanduser().resolve()
    base = asdict(default_mode())
    loaded: dict[str, Any] = {}
    for p in _mode_files(root, mode_name):
        if p.is_file():
            raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            if not isinstance(raw, dict):
                raise ValueError(f"Invalid mode YAML object: {p}")
            loaded = raw
            break
    merged = _deep_update(base, loaded)
    merged["name"] = mode_name
    return mode_from_dict(merged)

