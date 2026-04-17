"""Pending metadata for deep-loop finalize."""

from __future__ import annotations

from typing import Any

_PENDING: dict[str, dict[str, Any]] = {}


def set_pending(session_id: str, team: str, meta: dict[str, Any] | None) -> None:
    sid = (session_id or "").strip()
    if not sid:
        return
    key = f"{team}:{sid}"
    if meta:
        _PENDING[key] = dict(meta)
    else:
        _PENDING.pop(key, None)


def get_pending(session_id: str, team: str) -> dict[str, Any] | None:
    sid = (session_id or "").strip()
    if not sid:
        return None
    key = f"{team}:{sid}"
    m = _PENDING.get(key)
    return dict(m) if isinstance(m, dict) else None


def clear_pending(session_id: str, team: str) -> None:
    sid = (session_id or "").strip()
    if not sid:
        return
    _PENDING.pop(f"{team}:{sid}", None)
