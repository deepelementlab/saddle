"""Team orchestration service for /clawteam and /designteam (clawcode-compatible prompts)."""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from saddle.agents.loader import load_agents
from saddle.orchestrator.design_config import load_designteam_design_context_block
from saddle.orchestrator.pending import clear_pending, get_pending, set_pending
from saddle.orchestrator.prompts import (
    CLAWTEAM_AGENT_CAPABILITIES,
    DESIGNTEAM_AGENT_CAPABILITIES,
    build_clawteam_prompt,
    build_designteam_prompt,
    parse_clawteam_args,
    parse_designteam_args,
)


@dataclass
class TeamResult:
    team: str
    prompt: str
    selected_agents: list[str]
    deep_loop: bool
    max_iters: int
    session_id: str


@dataclass
class TeamOrchestrationOptions:
    selection_strategy: str = "minimal"
    thresholds: dict[str, object] | None = None
    prompt_profile: str = "full"
    custom_roles: list[str] | None = None
    force_deep_loop: bool | None = None
    force_max_iters: int | None = None


def _capability_map(team: str) -> dict[str, str]:
    if team == "clawteam":
        return CLAWTEAM_AGENT_CAPABILITIES
    if team == "designteam":
        return DESIGNTEAM_AGENT_CAPABILITIES
    return {}


def _select_agents(
    team: str,
    agents: dict[str, Any],
    selected_agent: str | None,
    strategy: str = "minimal",
    custom_roles: list[str] | None = None,
) -> list[str]:
    cap = _capability_map(team)
    tier1 = [k for k in sorted(cap.keys()) if k in agents]
    if selected_agent:
        return [selected_agent] if selected_agent in agents else []
    if strategy == "balanced":
        return tier1[:8]
    if strategy == "custom":
        out = [r for r in (custom_roles or []) if r in agents]
        return out or tier1[:6]
    return tier1[:6]


class TeamService:
    def __init__(self, project_root: str | Path):
        self.project_root = str(Path(project_root).expanduser().resolve())

    def orchestrate(
        self,
        team: str,
        content: str,
        *,
        session_id: str | None = None,
        options: TeamOrchestrationOptions | None = None,
    ) -> TeamResult:
        if team not in ("clawteam", "designteam"):
            raise ValueError(f"unknown team: {team}")

        sid = session_id or str(uuid.uuid4())
        if team == "clawteam":
            selected_agent, request, deep_loop, max_iters, err = parse_clawteam_args(content)
        else:
            selected_agent, request, deep_loop, max_iters, err = parse_designteam_args(content)
        if err:
            raise ValueError(err.strip())

        agents = load_agents(self.project_root)
        opts = options or TeamOrchestrationOptions()
        if opts.force_deep_loop is not None:
            deep_loop = bool(opts.force_deep_loop)
        if opts.force_max_iters is not None:
            max_iters = int(opts.force_max_iters)
        selected = _select_agents(
            team,
            agents,
            selected_agent,
            strategy=opts.selection_strategy,
            custom_roles=opts.custom_roles,
        )
        if not selected:
            fallback = (
                ["clawteam-team-lead", "clawteam-system-architect"]
                if team == "clawteam"
                else ["designteam-product-designer", "designteam-interaction-designer"]
            )
            selected = [r for r in fallback if r in agents][:2]

        design_yaml_context = ""
        if team == "designteam":
            design_yaml_context = load_designteam_design_context_block(
                Path(self.project_root), selected
            )

        thresholds: dict[str, object] = {
            "min_gap_delta": 0.05,
            "convergence_rounds": 2,
            "handoff_target": 0.85,
        }
        if opts.thresholds:
            thresholds.update(opts.thresholds)

        if team == "clawteam":
            prompt = build_clawteam_prompt(
                request,
                selected_agent,
                deep_loop=deep_loop,
                max_iters=max_iters,
                tecap_context=None,
                role_ecap_context=None,
                deeploop_thresholds=thresholds,
            )
        else:
            prompt = build_designteam_prompt(
                request,
                selected_agent,
                deep_loop=deep_loop,
                max_iters=max_iters,
                iter_idx=1,
                tecap_context=None,
                role_ecap_context=None,
                design_yaml_context=design_yaml_context,
                deeploop_thresholds=thresholds,
            )
        if opts.prompt_profile == "compact":
            compact_head = "\n".join(prompt.splitlines()[:80])
            prompt = (
                compact_head
                + "\n\n[truncated for compact profile]\n"
                + "Protocol keepers:\n"
                + "DEEP_LOOP_EVAL_JSON:\n"
                + "DEEP_LOOP_WRITEBACK_JSON:\n"
            )

        orchestration: dict[str, Any] = {
            "team": team,
            "deep_loop": deep_loop,
            "max_iters": max_iters,
            "selected_agents": selected,
            "selected_agent": selected_agent,
            "request": request.strip(),
            "timestamp": int(time.time()),
        }

        if deep_loop:
            set_pending(
                sid,
                team,
                {
                    "tecap_id": f"{team}-{sid[:8]}",
                    "max_iters": max_iters,
                    "selected_agents": selected,
                    "request": request.strip(),
                },
            )

        meta_path = Path(self.project_root) / ".saddle" / "runs"
        meta_path.mkdir(parents=True, exist_ok=True)
        (meta_path / f"{team}-{sid}.json").write_text(
            json.dumps(orchestration, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return TeamResult(
            team=team,
            prompt=prompt,
            selected_agents=selected,
            deep_loop=deep_loop,
            max_iters=max_iters,
            session_id=sid,
        )

    def finalize(self, team: str, session_id: str, assistant_text: str) -> dict[str, str]:
        pending = get_pending(session_id, team)
        if not pending:
            raise ValueError(f"未找到 {team} 的 deep-loop pending，会话: {session_id}")
        m = re.search(r"DEEP_LOOP_WRITEBACK_JSON:\s*(\{.*\})", assistant_text, re.DOTALL)
        if not m:
            raise ValueError("未找到 DEEP_LOOP_WRITEBACK_JSON")
        payload = m.group(1).strip()
        out_dir = Path(self.project_root) / ".saddle" / "learning"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{team}-writeback-{session_id}.json"
        out_file.write_text(payload, encoding="utf-8")
        clear_pending(session_id, team)
        return {"status": "ok", "file": str(out_file), "tecap_id": str(pending.get("tecap_id", ""))}
