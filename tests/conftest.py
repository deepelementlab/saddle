"""Pytest fixtures for Saddle."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure `src/` layout is importable when pytest is invoked from repo root.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
