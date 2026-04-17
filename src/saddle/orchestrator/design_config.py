"""Load per-role design YAML from `.saddle/design/designteam/` or legacy `.claw/design/designteam/`."""

from __future__ import annotations

from pathlib import Path


def _yaml_stem_for_agent_id(agent_id: str) -> str:
    s = str(agent_id).strip().lower()
    if s.startswith("designteam-"):
        s = s[len("designteam-") :]
    return s.replace("_", "-")


def load_designteam_design_context_block(workspace_root: Path, role_ids: list[str]) -> str:
    bases = [
        workspace_root / ".saddle" / "design" / "designteam",
        workspace_root / ".claw" / "design" / "designteam",
    ]
    chunks: list[str] = []
    seen: set[str] = set()
    for rid in role_ids:
        r = str(rid).strip()
        if not r or r in seen:
            continue
        seen.add(r)
        stem = _yaml_stem_for_agent_id(r)
        for name in (f"{stem}.yaml", f"{stem}.yml"):
            raw = ""
            rel = ""
            for base in bases:
                path = base / name
                if path.is_file():
                    raw = path.read_text(encoding="utf-8", errors="replace").strip()
                    try:
                        rel = str(path.relative_to(workspace_root))
                    except ValueError:
                        rel = str(path)
                    break
            if raw:
                chunks.append(f"#### `{r}` ({rel})\n{raw[:6000]}\n")
            break
    if not chunks:
        return ""
    return (
        "Role design config (from workspace `design/designteam/*.yaml`; "
        "`.saddle` preferred, `.claw` legacy):\n\n"
        + "\n".join(chunks)
    )
