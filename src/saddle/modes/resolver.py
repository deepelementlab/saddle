"""Resolve mode config with file + CLI overrides."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from saddle.modes.loader import load_mode_from_file, mode_from_dict
from saddle.modes.schema import ModeConfig


def _set_by_path(obj: dict[str, Any], path: str, value: Any) -> None:
    parts = [p for p in path.split(".") if p]
    if not parts:
        return
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def _parse_value(raw: str) -> Any:
    s = raw.strip()
    if s.lower() in {"true", "false"}:
        return s.lower() == "true"
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        pass
    if s.startswith("[") and s.endswith("]"):
        body = s[1:-1].strip()
        if not body:
            return []
        return [x.strip().strip("'\"") for x in body.split(",")]
    return s


def apply_overrides(mode: ModeConfig, overrides: list[str] | None) -> ModeConfig:
    if not overrides:
        return mode
    d = asdict(mode)
    for item in overrides:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        _set_by_path(d, k.strip(), _parse_value(v))
    return mode_from_dict(d)


def resolve_mode(project_root: str, mode_name: str = "default", overrides: list[str] | None = None) -> ModeConfig:
    base = load_mode_from_file(project_root, mode_name)
    return apply_overrides(base, overrides)

