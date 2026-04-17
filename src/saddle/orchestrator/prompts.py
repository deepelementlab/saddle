"""clawcode-compatible `/clawteam` and `/designteam` orchestrator prompts and argument parsing."""

from __future__ import annotations

import re
import shlex
from typing import Any

from saddle.orchestrator.design_phases import (
    DESIGN_PHASES_TABLE_MARKDOWN,
    designteam_phase_label_for_iteration,
)

CLAWTEAM_AGENT_CAPABILITIES: dict[str, str] = {
    "clawteam-product-manager": "Define product scope, goals, priorities, and acceptance criteria.",
    "clawteam-business-analyst": "Translate business needs into constraints, workflows, and requirement details.",
    "clawteam-system-architect": "Design technical architecture, interfaces, trade-offs, and risk controls.",
    "clawteam-ui-ux-designer": "Design user journeys, interaction flows, and interface proposals.",
    "clawteam-dev-manager": "Plan engineering execution, staffing, milestones, and delivery sequencing.",
    "clawteam-team-lead": "Coordinate cross-role execution, resolve blockers, and keep technical direction aligned.",
    "clawteam-rnd-backend": "Implement backend services, APIs, data models, and reliability-focused logic.",
    "clawteam-rnd-frontend": "Implement frontend UI, state flows, and client-side integrations.",
    "clawteam-rnd-mobile": "Implement mobile application features and platform-specific integration concerns.",
    "clawteam-devops": "Handle CI/CD pipelines, build/release automation, and deployment architecture.",
    "clawteam-qa": "Define test strategy, test cases, verification gates, and quality risk analysis.",
    "clawteam-sre": "Design observability, resilience, incident readiness, and operational reliability controls.",
    "clawteam-project-manager": "Track scope/schedule/resources and delivery status with execution governance.",
    "clawteam-scrum-master": "Facilitate agile ceremonies, flow efficiency, and team process improvements.",
}

CLAWTEAM_AGENT_ALIASES: dict[str, str] = {
    "product-manager": "clawteam-product-manager",
    "business-analyst": "clawteam-business-analyst",
    "system-architect": "clawteam-system-architect",
    "ui-ux-designer": "clawteam-ui-ux-designer",
    "dev-manager": "clawteam-dev-manager",
    "team-lead": "clawteam-team-lead",
    "rnd-backend": "clawteam-rnd-backend",
    "rnd-frontend": "clawteam-rnd-frontend",
    "rnd-mobile": "clawteam-rnd-mobile",
    "devops": "clawteam-devops",
    "qa": "clawteam-qa",
    "sre": "clawteam-sre",
    "project-manager": "clawteam-project-manager",
    "scrum-master": "clawteam-scrum-master",
}

_CLAWTEAM_USAGE = (
    "Usage:\n"
    "- `/clawteam <requirement>`: auto-select and orchestrate multiple roles.\n"
    "- `/clawteam:<agent> <requirement>`: run one role only.\n"
    "- `/clawteam --agent <agent> <requirement>`: explicit single-role mode.\n\n"
    "- `/clawteam --deep_loop <requirement>`: run iterative deep loop workflow.\n"
    "- `/clawteam --deep_loop --max_iters <n> <requirement>`: deep loop with custom iteration cap.\n\n"
    "Available agents: "
    + ", ".join(f"`{k}`" for k in sorted(CLAWTEAM_AGENT_CAPABILITIES))
)

DESIGNTEAM_AGENT_CAPABILITIES: dict[str, str] = {
    "designteam-user-researcher": (
        "Qualitative/quant framing, personas, journey signals, research questions, and evidence-backed assumptions."
    ),
    "designteam-interaction-designer": (
        "Task flows, states, navigation, IA, edge/error paths, and interaction specifications."
    ),
    "designteam-ui-designer": (
        "Layout hierarchy, UI patterns, components, density, and design-system-aligned interface specs."
    ),
    "designteam-product-designer": (
        "Problem framing, outcomes and success metrics, scope IN/OUT, prioritization of UX problems vs business goals."
    ),
    "designteam-visual-ops-designer": (
        "Brand-consistent visuals, marketing/growth touchpoints, campaign surfaces, and conversion-oriented layout."
    ),
    "designteam-experience-design-expert": (
        "Cross-cutting experience principles, heuristic review, accessibility posture, metrics, and risk synthesis."
    ),
}

DESIGNTEAM_AGENT_ALIASES: dict[str, str] = {
    "ur": "designteam-user-researcher",
    "user-researcher": "designteam-user-researcher",
    "ixd": "designteam-interaction-designer",
    "interaction-designer": "designteam-interaction-designer",
    "ui": "designteam-ui-designer",
    "ui-designer": "designteam-ui-designer",
    "pd": "designteam-product-designer",
    "product-designer": "designteam-product-designer",
    "visual": "designteam-visual-ops-designer",
    "visual-ops": "designteam-visual-ops-designer",
    "xd": "designteam-experience-design-expert",
    "experience": "designteam-experience-design-expert",
}

_DESIGNTEAM_USAGE = (
    "Usage:\n"
    "- `/designteam <requirement>`: auto-select and orchestrate multiple design roles.\n"
    "- `/designteam:<agent> <requirement>`: run one role only.\n"
    "- `/designteam --agent <agent> <requirement>`: explicit single-role mode.\n\n"
    "- `/designteam --deep_loop <requirement>`: outer deep loop over the 7-phase design workflow.\n"
    "- `/designteam --deep_loop --max_iters <n> <requirement>`: deep loop with custom iteration cap.\n\n"
    "Available agents: "
    + ", ".join(f"`{k}`" for k in sorted(DESIGNTEAM_AGENT_CAPABILITIES))
)

_NS_HEAD = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]*$")


def normalize_team_slash_prefix(team: str, raw: str) -> str:
    """Map `/team:agent tail` or `team:agent tail` to `--agent agent tail`."""
    text = (raw or "").strip()
    for prefix in (f"/{team}:", f"{team}:"):
        if text.startswith(prefix):
            rest = text[len(prefix) :].strip()
            if not rest:
                return text
            head, sep, tail = rest.partition(" ")
            if sep and _NS_HEAD.match(head):
                return f"--agent {head} {tail}".strip()
            if _NS_HEAD.match(rest):
                return f"--agent {rest}"
            return rest
    return text


def parse_designteam_args(tail: str) -> tuple[str | None, str, bool, int, str]:
    """Return (selected_agent, request, deep_loop, max_iters, error)."""
    raw = normalize_team_slash_prefix("designteam", (tail or "").strip())
    default_max_iters = 100
    if not raw:
        return None, "", False, default_max_iters, _DESIGNTEAM_USAGE
    try:
        tokens = shlex.split(raw)
    except ValueError as e:
        return None, "", False, default_max_iters, f"Invalid `/designteam` arguments: {e}\n\n{_DESIGNTEAM_USAGE}"

    selected_agent: str | None = None
    deep_loop = False
    max_iters = 100
    req_tokens: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--agent":
            if i + 1 >= len(tokens):
                return None, "", False, 5, f"`--agent` requires a value.\n\n{_DESIGNTEAM_USAGE}"
            selected_agent = tokens[i + 1].strip().lower()
            i += 2
            continue
        if tok == "--deep_loop":
            deep_loop = True
            i += 1
            continue
        if tok == "--max_iters":
            if i + 1 >= len(tokens):
                return (
                    None,
                    "",
                    False,
                    default_max_iters,
                    f"`--max_iters` requires an integer value.\n\n{_DESIGNTEAM_USAGE}",
                )
            raw_iters = tokens[i + 1].strip()
            try:
                max_iters = int(raw_iters)
            except ValueError:
                return (
                    None,
                    "",
                    False,
                    default_max_iters,
                    f"`--max_iters` must be an integer (got `{raw_iters}`).\n\n{_DESIGNTEAM_USAGE}",
                )
            if max_iters < 1:
                return (
                    None,
                    "",
                    False,
                    default_max_iters,
                    f"`--max_iters` must be >= 1 (got `{max_iters}`).\n\n{_DESIGNTEAM_USAGE}",
                )
            i += 2
            continue
        req_tokens.append(tok)
        i += 1

    req = " ".join(req_tokens).strip()
    if selected_agent and selected_agent not in DESIGNTEAM_AGENT_CAPABILITIES:
        selected_agent = DESIGNTEAM_AGENT_ALIASES.get(selected_agent, selected_agent)
    if selected_agent and selected_agent not in DESIGNTEAM_AGENT_CAPABILITIES:
        return (
            None,
            "",
            False,
            default_max_iters,
            f"Unknown `/designteam` agent `{selected_agent}`.\n\n{_DESIGNTEAM_USAGE}",
        )
    if not req:
        return None, "", False, default_max_iters, _DESIGNTEAM_USAGE
    return selected_agent, req, deep_loop, max_iters, ""


def parse_clawteam_args(tail: str) -> tuple[str | None, str, bool, int, str]:
    """Return (selected_agent, request, deep_loop, max_iters, error)."""
    raw = normalize_team_slash_prefix("clawteam", (tail or "").strip())
    default_max_iters = 100
    if not raw:
        return None, "", False, default_max_iters, _CLAWTEAM_USAGE
    try:
        tokens = shlex.split(raw)
    except ValueError as e:
        return None, "", False, default_max_iters, f"Invalid `/clawteam` arguments: {e}\n\n{_CLAWTEAM_USAGE}"

    selected_agent: str | None = None
    deep_loop = False
    max_iters = 100
    req_tokens: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "--agent":
            if i + 1 >= len(tokens):
                return None, "", False, 5, f"`--agent` requires a value.\n\n{_CLAWTEAM_USAGE}"
            selected_agent = tokens[i + 1].strip().lower()
            i += 2
            continue
        if tok == "--deep_loop":
            deep_loop = True
            i += 1
            continue
        if tok == "--max_iters":
            if i + 1 >= len(tokens):
                return (
                    None,
                    "",
                    False,
                    default_max_iters,
                    f"`--max_iters` requires an integer value.\n\n{_CLAWTEAM_USAGE}",
                )
            raw_iters = tokens[i + 1].strip()
            try:
                max_iters = int(raw_iters)
            except ValueError:
                return (
                    None,
                    "",
                    False,
                    default_max_iters,
                    f"`--max_iters` must be an integer (got `{raw_iters}`).\n\n{_CLAWTEAM_USAGE}",
                )
            if max_iters < 1:
                return (
                    None,
                    "",
                    False,
                    default_max_iters,
                    f"`--max_iters` must be >= 1 (got `{max_iters}`).\n\n{_CLAWTEAM_USAGE}",
                )
            i += 2
            continue
        req_tokens.append(tok)
        i += 1

    req = " ".join(req_tokens).strip()
    if selected_agent and selected_agent not in CLAWTEAM_AGENT_CAPABILITIES:
        selected_agent = CLAWTEAM_AGENT_ALIASES.get(selected_agent, selected_agent)
    if selected_agent and selected_agent not in CLAWTEAM_AGENT_CAPABILITIES:
        return (
            None,
            "",
            False,
            default_max_iters,
            f"Unknown `/clawteam` agent `{selected_agent}`.\n\n{_CLAWTEAM_USAGE}",
        )
    if not req:
        return None, "", False, default_max_iters, _CLAWTEAM_USAGE
    return selected_agent, req, deep_loop, max_iters, ""


def build_designteam_prompt(
    user_request: str,
    selected_agent: str | None,
    *,
    deep_loop: bool = False,
    max_iters: int = 100,
    iter_idx: int = 1,
    tecap_context: list[dict[str, object]] | None = None,
    role_ecap_context: dict[str, dict[str, object]] | None = None,
    design_yaml_context: str = "",
    deeploop_thresholds: dict[str, object] | None = None,
) -> str:
    req = (user_request or "").strip() or "(no requirement text provided)"
    roster_lines = [
        f"- `{name}`: {desc}" for name, desc in sorted(DESIGNTEAM_AGENT_CAPABILITIES.items())
    ]
    roster_block = "\n".join(roster_lines)
    if selected_agent:
        mode_block = (
            "Execution mode: SINGLE-ROLE.\n"
            f"Use only this role unless a hard blocker requires escalation: `{selected_agent}`.\n"
        )
    else:
        mode_block = (
            "Execution mode: AUTO-ORCHESTRATION.\n"
            "Select a **minimal but sufficient** set of roles from the roster.\n"
            "Compose an adaptive workflow with serial and parallel stages when beneficial.\n"
        )
    raci_block = (
        "Role boundaries (RACI — avoid duplicate work):\n"
        "- `designteam-product-designer`: **Outcomes, scope, prioritization** — what problem, for whom, "
        "what success looks like; IN/OUT; trade-offs vs business goals.\n"
        "- `designteam-interaction-designer`: **Flows and structure** — tasks, states, IA, navigation, "
        "happy/edge/error paths.\n"
        "- `designteam-ui-designer`: **Interface structure and patterns** — layout hierarchy, components, "
        "density, design-system usage (not marketing campaign art direction unless asked).\n"
        "- `designteam-experience-design-expert`: **Horizontal review** — principles, heuristics, accessibility "
        "posture, metrics, risk synthesis; do not re-own PD’s goals section unless single-role mode.\n"
        "- `designteam-user-researcher` / `designteam-visual-ops-designer`: invoke when research or growth/visual "
        "touchpoints are central.\n"
    )
    model_block = (
        "Design process models (pick 1–2 primary; cite user signals):\n"
        "- **0→1 / discovery**: Double Diamond or Design Thinking (diverge then converge).\n"
        "- **Fast validation**: Design Sprint (time-boxed).\n"
        "- **Enterprise / B2B workflow**: task analysis + Double Diamond + service-blueprint fragments.\n"
        "- **Growth / landing**: conversion-oriented layout + light journey map + metrics.\n"
        "- **Iteration**: Lean UX + usability metrics (e.g. task success, SUS).\n"
    )
    tier2_block = (
        "Optional extended roles (only if clearly needed; list assumptions):\n"
        "- `designteam-content-designer` (microcopy / UX writing)\n"
        "- `designteam-design-systems` (tokens, components, governance)\n"
        "- `designteam-accessibility` or `designteam-service-designer` for compliance-heavy or service-heavy work.\n"
        "These are **not** in the built-in roster; simulate their outputs or recommend human follow-up.\n"
    )
    doc_block = (
        "Deliver one structured **系统设计文档** (system design document). Final integration MUST cover "
        "(trim only with explicit rationale):\n"
        "1) Background, goals, success criteria\n"
        "2) Users and scenarios (assumptions)\n"
        "3) Research summary (if UR used)\n"
        "4) IA and key flows (IXD)\n"
        "5) UI / component-level notes (UI)\n"
        "6) Brand / visual / ops touchpoints (if Visual/Ops used)\n"
        "7) Experience principles, accessibility, risks\n"
        "8) Open questions, validation plan, next steps\n"
    )
    boundary_block = (
        "Boundary: `/designteam` produces **design documentation and specs**. Engineering delivery, "
        "implementation, and cross-functional execution remain **`/clawteam`** or normal dev workflows.\n"
    )
    tecap_lines: list[str] = []
    for row in list(tecap_context or [])[:3]:
        if not isinstance(row, dict):
            continue
        tecap_lines.append(
            f"- tecap_id=`{row.get('tecap_id','')}` score=`{row.get('score',0.0)}` "
            f"confidence=`{row.get('confidence',0.0)}` role_coverage=`{row.get('role_coverage',0.0)}`"
        )
    tecap_block = "\n".join(tecap_lines) if tecap_lines else "- (no matched TECAP)"
    role_lines: list[str] = []
    for role, row in sorted((role_ecap_context or {}).items()):
        if not isinstance(row, dict):
            continue
        role_lines.append(
            f"- {role}: ecap_id=`{row.get('ecap_id','')}` score=`{row.get('experience_score',0.0)}` "
            f"confidence=`{row.get('confidence',0.0)}` skill=`{row.get('skill_ref','')}`"
        )
    role_block = "\n".join(role_lines) if role_lines else "- (no role ECAP context)"
    design_cfg_block = (design_yaml_context or "").strip() or (
        "- (no `design/designteam/*.yaml` found under `.saddle` or legacy `.claw`)"
    )
    phase_n, phase_label = designteam_phase_label_for_iteration(iter_idx)
    phase_focus_line = (
        f"Current outer-loop iteration: {iter_idx}. "
        f"Workflow phase focus: **{phase_n}/8 — {phase_label}** "
        "(phases 1–7 follow the table below; phase 8 is 整合与收敛 after round 7).\n"
    )
    deep_loop_block = ""
    if deep_loop:
        thresholds = deeploop_thresholds or {}
        min_gap_delta = float(thresholds.get("min_gap_delta", 0.05) or 0.05)
        rounds = int(thresholds.get("convergence_rounds", 2) or 2)
        handoff_target = float(thresholds.get("handoff_target", 0.85) or 0.85)
        deep_loop_block = (
            "Deep loop mode: ENABLED (`--deep_loop`).\n"
            f"Iteration cap: {max_iters} (`--max_iters`).\n"
            f"Convergence threshold (gap delta): {min_gap_delta}.\n"
            f"Convergence rounds: {rounds}.\n"
            f"Handoff target: {handoff_target}.\n\n"
            f"{phase_focus_line}\n"
            "**7-phase product design workflow** (diverge/converge logic; each phase has clear outputs):\n\n"
            f"{DESIGN_PHASES_TABLE_MARKDOWN}\n"
            "Iteration-to-phase mapping (outer loop index `i` starts at 1 for the first agent run):\n"
            "- For `i` in 1..7: primary focus = **phase i** in the table above (`current_phase = min(i, 7)`).\n"
            "- For `i` >= 8: **整合与收敛** — merge the full 系统设计文档, resolve gaps, declare convergence via "
            "`DEEP_LOOP_EVAL_JSON`.\n\n"
            "Do **not** use the `/clawteam` engineering deep-loop steps (检查 / 扩展实现 / code-focused). "
            "Stay in designteam: research, IXD, UI, PD, visual/ops, XD as needed; produce design artifacts and "
            "the cumulative system design document.\n\n"
            "Deep loop output contract (required every iteration):\n"
            "- Iteration index\n"
            "- iteration_goal\n"
            "- current_phase (1–8) and phase label\n"
            "- role_handoff_result\n"
            "- gap_before\n"
            "- gap_after\n"
            "- gap_delta\n"
            "- deviation_reason\n"
            "- Phase-appropriate outputs and updates to the integrated system design document\n"
            "- IntegratedFinalOutcome (structured, reusable for next iteration)\n"
            "- Convergence report JSON-like block with keys:\n"
            "  - `delta_score`\n"
            "  - `converged`\n"
            "  - `reasons`\n"
            "  - `critical_risks`\n"
            "- Final line MUST be exactly one machine-readable line prefixed with `DEEP_LOOP_EVAL_JSON:`\n"
            "  Example:\n"
            '  DEEP_LOOP_EVAL_JSON: {"delta_score": 0.08, "converged": true, "reasons": "stabilized", "critical_risks": []}\n'
            "- Finalization line SHOULD be provided to support automatic writeback:\n"
            '  DEEP_LOOP_WRITEBACK_JSON: {"iteration": 1, "iteration_goal": "...", "role_handoff_result": "ok", '
            '"gap_before": 0.3, "gap_after": 0.1, "deviation_reason": "", "handoff_success_rate": 0.9, '
            '"observed_score": 0.85, "result": "success"}\n'
            "After loop ends, provide one final consolidated system design document summary.\n\n"
        )
    return (
        "You are running Saddle built-in `/designteam` as the primary orchestrator agent "
        "(protocol aligned with clawcode).\n"
        "You can autonomously call tools and delegate design tasks using the `Agent`/`Task` tool.\n\n"
        "Primary objective:\n"
        "Deliver structured design outcomes through role-based collaboration.\n\n"
        f"{boundary_block}\n"
        f"{mode_block}\n"
        f"{deep_loop_block}"
        f"{raci_block}\n"
        f"{model_block}\n"
        f"{tier2_block}\n"
        f"{doc_block}\n"
        "TECAP context (retrieved):\n"
        f"{tecap_block}\n\n"
        "Role ECAP context (retrieved):\n"
        f"{role_block}\n\n"
        f"{design_cfg_block}\n\n"
        "Role roster (agent id -> capability):\n"
        f"{roster_block}\n\n"
        "Mandatory orchestration protocol:\n"
        "1) Analyze the requirement and pick signals (industry, B2B/B2C, stage, constraints, compliance, a11y).\n"
        "2) Choose the design process model(s) and justify.\n"
        "3) Choose roles strictly from the roster (minimal sufficient set) and explain why.\n"
        "4) Build execution flow: parallel vs serial stages.\n"
        "5) Dispatch via `Agent` or `Task` with `agent=<role-id>`.\n"
        "6) Integrate into the system design document structure above; resolve conflicts explicitly.\n\n"
        "Output structure requirements:\n"
        "- Role selection\n"
        "- Workflow plan (parallel/serial)\n"
        "- Role execution results\n"
        "- Integrated system design document (all required sections)\n"
        "- Risks, assumptions, next steps\n\n"
        f"User requirement:\n{req}\n"
    )


def build_clawteam_prompt(
    user_request: str,
    selected_agent: str | None,
    *,
    deep_loop: bool = False,
    max_iters: int = 100,
    tecap_context: list[dict[str, object]] | None = None,
    role_ecap_context: dict[str, dict[str, object]] | None = None,
    deeploop_thresholds: dict[str, object] | None = None,
) -> str:
    req = (user_request or "").strip() or "(no requirement text provided)"
    roster_lines = [
        f"- `{name}`: {desc}" for name, desc in sorted(CLAWTEAM_AGENT_CAPABILITIES.items())
    ]
    roster_block = "\n".join(roster_lines)
    if selected_agent:
        mode_block = (
            "Execution mode: SINGLE-ROLE.\n"
            f"Use only this role unless a hard blocker requires escalation: `{selected_agent}`.\n"
        )
    else:
        mode_block = (
            "Execution mode: AUTO-ORCHESTRATION.\n"
            "Select a minimal but sufficient set of roles from the roster.\n"
            "Compose an adaptive workflow with serial and parallel stages when beneficial.\n"
        )
    if deep_loop:
        thresholds = deeploop_thresholds or {}
        min_gap_delta = float(thresholds.get("min_gap_delta", 0.05) or 0.05)
        rounds = int(thresholds.get("convergence_rounds", 2) or 2)
        handoff_target = float(thresholds.get("handoff_target", 0.85) or 0.85)
        deep_loop_block = (
            "Deep loop mode: ENABLED (`--deep_loop`).\n"
            f"Iteration cap: {max_iters} (`--max_iters`).\n"
            f"Convergence threshold (gap delta): {min_gap_delta}.\n"
            f"Convergence rounds: {rounds}.\n"
            f"Handoff target: {handoff_target}.\n\n"
            "Run an OUTER deep loop over clawteam collaboration until convergence or max iterations.\n"
            "For each iteration i, execute these four steps in order (each step must still follow the "
            "same clawteam orchestration protocol and role roster):\n"
            "1) 检查:\n"
            "   - Inspect previous integrated outcome and implementation status.\n"
            "   - Identify defects, risks, missing requirements, and quality gaps.\n"
            "   - Resolve prioritized issues and produce an updated integrated outcome.\n"
            "2) 深化设计:\n"
            "   - Deepen architecture, interfaces, constraints, and trade-off decisions.\n"
            "   - Refine design rationale and implementation-ready decisions.\n"
            "3) 扩展实现:\n"
            "   - Expand feature scope and implementation depth based on current outcome.\n"
            "   - Strengthen test coverage, reliability, and docs where applicable.\n"
            "4) 最终收敛:\n"
            "   - Run a dedicated evaluation pass comparing current vs previous iteration outcome.\n"
            "   - Compute/estimate `delta_score` in [0, 1] and set `converged`.\n"
            "   - If `delta_score <= 0.15` and there is no critical unresolved risk, stop loop.\n"
            "   - Otherwise continue to next iteration.\n\n"
            "Deep loop output contract (required every iteration):\n"
            "- Iteration index\n"
            "- iteration_goal\n"
            "- role_handoff_result\n"
            "- gap_before\n"
            "- gap_after\n"
            "- gap_delta\n"
            "- deviation_reason\n"
            "- Step outputs for the 4 steps above\n"
            "- IntegratedFinalOutcome (structured, reusable for next iteration)\n"
            "- Convergence report JSON-like block with keys:\n"
            "  - `delta_score`\n"
            "  - `converged`\n"
            "  - `reasons`\n"
            "  - `critical_risks`\n"
            "- Final line MUST be exactly one machine-readable line prefixed with `DEEP_LOOP_EVAL_JSON:`\n"
            "  Example:\n"
            '  DEEP_LOOP_EVAL_JSON: {"delta_score": 0.08, "converged": true, "reasons": "stabilized", "critical_risks": []}\n'
            "- Finalization line SHOULD be provided to support automatic writeback:\n"
            '  DEEP_LOOP_WRITEBACK_JSON: {"iteration": 1, "iteration_goal": "close gaps", "role_handoff_result": "ok", "gap_before": 0.3, "gap_after": 0.1, "deviation_reason": "", "handoff_success_rate": 0.9, "observed_score": 0.85, "result": "success"}\n'
            "After loop ends, provide one final mature high-level product version summary.\n\n"
        )
    else:
        deep_loop_block = ""
    tecap_lines: list[str] = []
    for row in list(tecap_context or [])[:3]:
        if not isinstance(row, dict):
            continue
        tecap_lines.append(
            f"- tecap_id=`{row.get('tecap_id','')}` score=`{row.get('score',0.0)}` "
            f"confidence=`{row.get('confidence',0.0)}` role_coverage=`{row.get('role_coverage',0.0)}`"
        )
    tecap_block = "\n".join(tecap_lines) if tecap_lines else "- (no matched TECAP)"
    role_lines: list[str] = []
    for role, row in sorted((role_ecap_context or {}).items()):
        if not isinstance(row, dict):
            continue
        role_lines.append(
            f"- {role}: ecap_id=`{row.get('ecap_id','')}` score=`{row.get('experience_score',0.0)}` "
            f"confidence=`{row.get('confidence',0.0)}` skill=`{row.get('skill_ref','')}`"
        )
    role_block = "\n".join(role_lines) if role_lines else "- (no role ECAP context)"
    return (
        "You are running Saddle built-in `/clawteam` as the primary orchestrator agent "
        "(protocol aligned with clawcode).\n"
        "You can autonomously call tools and delegate role tasks using the `Agent`/`Task` tool.\n\n"
        "Primary objective:\n"
        "Deliver the user's requested outcome through role-based collaboration.\n\n"
        f"{mode_block}\n"
        f"{deep_loop_block}"
        "TECAP context (retrieved):\n"
        f"{tecap_block}\n\n"
        "Role ECAP context (retrieved):\n"
        f"{role_block}\n\n"
        "Role roster (agent id -> capability):\n"
        f"{roster_block}\n\n"
        "Mandatory orchestration protocol:\n"
        "1) Analyze requirement and identify key workstreams.\n"
        "2) Choose roles strictly from the roster and explain why each role is needed.\n"
        "3) Build execution flow with explicit stages:\n"
        "   - which stages are parallel\n"
        "   - which stages are serial and dependency-gated\n"
        "4) Dispatch role tasks via `Agent` or `Task` using `agent=<role-id>`.\n"
        "5) Integrate outputs, resolve conflicts, and produce final consolidated deliverable.\n"
        "6) Include risks, assumptions, and recommended next actions.\n\n"
        "Output structure requirements:\n"
        "- Role selection\n"
        "- Workflow plan (parallel/serial)\n"
        "- Role execution results\n"
        "- Integrated final outcome\n"
        "- Risks and next steps\n\n"
        f"User requirement:\n{req}\n"
    )
