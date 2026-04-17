"""Helpers for `saddle mode` CLI: list, validate."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from saddle.modes.schema import ModeConfig

_VALID_STAGES = frozenset({"spec", "design", "develop"})
_VALID_STRATEGIES = frozenset({"minimal", "balanced", "custom"})
_VALID_PROFILES = frozenset({"full", "compact"})


def list_mode_names(project_root: str | Path) -> list[str]:
    root = Path(project_root).expanduser().resolve()
    base = root / ".saddle" / "modes"
    if not base.is_dir():
        return []
    names: set[str] = set()
    for p in sorted(base.glob("*.yaml")):
        names.add(p.stem)
    for p in sorted(base.glob("*.yml")):
        names.add(p.stem)
    return sorted(names)


def validate_mode_config(mode: ModeConfig) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a resolved ModeConfig."""
    errors: list[str] = []
    warnings: list[str] = []

    if not mode.pipeline.order:
        errors.append("pipeline.order must be non-empty")
    for i, stage in enumerate(mode.pipeline.order):
        if stage not in _VALID_STAGES:
            errors.append(f"pipeline.order[{i}] invalid stage {stage!r} (allowed: spec, design, develop)")

    if mode.design.max_iters < 1:
        errors.append("design.max_iters must be >= 1")
    if mode.develop.max_iters < 1:
        errors.append("develop.max_iters must be >= 1")

    if mode.agent_selection.strategy not in _VALID_STRATEGIES:
        errors.append(
            f"agent_selection.strategy invalid {mode.agent_selection.strategy!r} "
            f"(allowed: {', '.join(sorted(_VALID_STRATEGIES))})"
        )

    if mode.design.prompt_profile not in _VALID_PROFILES:
        errors.append(f"design.prompt_profile invalid {mode.design.prompt_profile!r}")
    if mode.develop.prompt_profile not in _VALID_PROFILES:
        errors.append(f"develop.prompt_profile invalid {mode.develop.prompt_profile!r}")

    mgd = mode.thresholds.get("min_gap_delta")
    if mgd is not None and float(mgd) <= 0:
        errors.append("thresholds.min_gap_delta must be > 0")

    cr = mode.thresholds.get("convergence_rounds")
    if cr is not None and float(cr) < 1:
        errors.append("thresholds.convergence_rounds must be >= 1")

    ht = mode.thresholds.get("handoff_target")
    if ht is not None:
        htf = float(ht)
        if htf < 0 or htf > 1:
            errors.append("thresholds.handoff_target must be in [0, 1]")

    if mode.agent_selection.strategy == "custom" and not mode.agent_selection.custom_roles:
        warnings.append("agent_selection.strategy is custom but custom_roles is empty (will fall back at runtime)")

    if not mode.spec.enabled and "spec" in mode.pipeline.order:
        warnings.append("spec stage is disabled but still listed in pipeline.order")

    return errors, warnings


def mode_to_jsonable(mode: ModeConfig) -> dict[str, Any]:
    """Serialize ModeConfig for CLI JSON output."""
    return asdict(mode)
