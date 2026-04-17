"""Load saddle team agent definitions from markdown files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from saddle.orchestrator.prompts import CLAWTEAM_AGENT_CAPABILITIES, DESIGNTEAM_AGENT_CAPABILITIES


@dataclass
class AgentDefinition:
    name: str
    description: str
    prompt: str
    source: str


def load_agents(project_root: str | Path) -> dict[str, AgentDefinition]:
    root = Path(project_root).expanduser().resolve()
    agents_dir = root / ".saddle" / "agents"
    out: dict[str, AgentDefinition] = {}
    if agents_dir.is_dir():
        for p in sorted(agents_dir.glob("*.md")):
            text = p.read_text(encoding="utf-8", errors="replace").strip()
            if not text:
                continue
            first = text.splitlines()[0].strip("# ").strip()
            out[p.stem] = AgentDefinition(
                name=p.stem,
                description=first or p.stem,
                prompt=text,
                source=str(p),
            )
    return _with_capability_defaults(out)


def _with_capability_defaults(current: dict[str, AgentDefinition]) -> dict[str, AgentDefinition]:
    out = dict(current)
    for name, description in {**CLAWTEAM_AGENT_CAPABILITIES, **DESIGNTEAM_AGENT_CAPABILITIES}.items():
        if name not in out:
            out[name] = AgentDefinition(
                name=name,
                description=description,
                prompt=f"# {name}\n\n{description}\n",
                source="builtin",
            )
    return out
