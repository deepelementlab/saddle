"""Default and normalized collaboration_config (design/develop) for Studio API."""

from __future__ import annotations

import uuid
from typing import Any


def _empty_object_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": True, "properties": {}}


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def _default_design_stage() -> dict[str, Any]:
    groups: list[dict[str, Any]] = [
        {"id": "design-research", "label": "Research & Alignment", "order": 0},
        {"id": "design-ux", "label": "UX & Information Architecture", "order": 1},
        {"id": "design-review", "label": "Review & Handoff", "order": 2},
    ]
    primitives: list[dict[str, Any]] = [
        {
            "id": _new_id("clarify_requirement"),
            "key": "clarify_requirement",
            "label": "Clarify requirement",
            "group_id": "design-research",
            "constraints": ["Must capture user goals and non-goals"],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("research_context"),
            "key": "research_context",
            "label": "Research context",
            "group_id": "design-research",
            "constraints": ["Cite assumptions and unknowns explicitly"],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("define_persona_journey"),
            "key": "define_persona_journey",
            "label": "Define persona journey",
            "group_id": "design-ux",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("draft_interaction_flow"),
            "key": "draft_interaction_flow",
            "label": "Draft interaction flow",
            "group_id": "design-ux",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("propose_ui_structure"),
            "key": "propose_ui_structure",
            "label": "Propose UI structure",
            "group_id": "design-ux",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("cross_role_review"),
            "key": "cross_role_review",
            "label": "Cross-role review",
            "group_id": "design-review",
            "constraints": ["At least two roles must sign off"],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("design_handoff"),
            "key": "design_handoff",
            "label": "Design handoff",
            "group_id": "design-review",
            "constraints": ["Produce handoff artifact for develop"],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
    ]
    return {
        "collaboration_format": {
            "team": "designteam",
            "mode": "multi-role orchestration",
            "default_output": "design documentation and specs",
            "handoff": "implementation handoff to develop",
        },
        "groups": groups,
        "primitives": primitives,
    }


def _default_develop_stage() -> dict[str, Any]:
    groups: list[dict[str, Any]] = [
        {"id": "dev-planning", "label": "Planning & Architecture", "order": 0},
        {"id": "dev-execution", "label": "Execution", "order": 1},
        {"id": "dev-quality", "label": "Quality & Release", "order": 2},
    ]
    primitives: list[dict[str, Any]] = [
        {
            "id": _new_id("scope_decomposition"),
            "key": "scope_decomposition",
            "label": "Scope decomposition",
            "group_id": "dev-planning",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("architecture_tradeoff"),
            "key": "architecture_tradeoff",
            "label": "Architecture tradeoff",
            "group_id": "dev-planning",
            "constraints": ["Document trade-offs and risks"],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("task_scheduling"),
            "key": "task_scheduling",
            "label": "Task scheduling",
            "group_id": "dev-planning",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("implementation_execution"),
            "key": "implementation_execution",
            "label": "Implementation execution",
            "group_id": "dev-execution",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("quality_validation"),
            "key": "quality_validation",
            "label": "Quality validation",
            "group_id": "dev-quality",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("risk_mitigation"),
            "key": "risk_mitigation",
            "label": "Risk mitigation",
            "group_id": "dev-quality",
            "constraints": [],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
        {
            "id": _new_id("release_readiness"),
            "key": "release_readiness",
            "label": "Release readiness",
            "group_id": "dev-quality",
            "constraints": ["Exit criteria must be explicit"],
            "input_schema": _empty_object_schema(),
            "output_schema": _empty_object_schema(),
        },
    ]
    return {
        "collaboration_format": {
            "team": "clawteam",
            "mode": "engineering multi-role orchestration",
            "default_output": "implementation plan and execution-ready prompt",
            "handoff": "delivery and QA closure",
        },
        "groups": groups,
        "primitives": primitives,
    }


def default_collaboration_config() -> dict[str, Any]:
    return {"design": _default_design_stage(), "develop": _default_develop_stage()}


def _deep_merge_str_dict(base: dict[str, str], patch: Any) -> dict[str, str]:
    out = dict(base)
    if isinstance(patch, dict):
        for k, v in patch.items():
            if isinstance(k, str) and isinstance(v, str):
                out[k] = v
    return out


def _normalize_groups(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for g in raw:
        if not isinstance(g, dict):
            continue
        gid = g.get("id")
        if not isinstance(gid, str) or not gid:
            continue
        label = g.get("label") if isinstance(g.get("label"), str) else gid
        order = g.get("order") if isinstance(g.get("order"), (int, float)) else len(out)
        out.append({"id": gid, "label": str(label), "order": int(order)})
    return sorted(out, key=lambda x: x["order"])


def _ensure_primitive(p: Any, prefix: str) -> dict[str, Any] | None:
    if not isinstance(p, dict):
        return None
    key = p.get("key")
    if not isinstance(key, str) or not key:
        return None
    pid = p.get("id") if isinstance(p.get("id"), str) else _new_id(prefix)
    label = p.get("label") if isinstance(p.get("label"), str) else key
    gid = p.get("group_id")
    group_id: str | None
    if gid is None:
        group_id = None
    elif isinstance(gid, str):
        group_id = gid
    else:
        group_id = None
    constraints: list[str] = []
    if isinstance(p.get("constraints"), list):
        constraints = [str(x) for x in p["constraints"] if str(x)]
    in_s = p.get("input_schema")
    out_s = p.get("output_schema")
    input_schema = in_s if isinstance(in_s, dict) and not isinstance(in_s, list) else _empty_object_schema()
    output_schema = out_s if isinstance(out_s, dict) and not isinstance(out_s, list) else _empty_object_schema()
    return {
        "id": pid,
        "key": key,
        "label": label,
        "group_id": group_id,
        "constraints": constraints,
        "input_schema": input_schema,
        "output_schema": output_schema,
    }


def _migrate_string_primitives(keys: list[str], group_by_index: Any) -> list[dict[str, Any]]:
    primitives: list[dict[str, Any]] = []
    for i, key in enumerate(keys):
        gid = None
        if callable(group_by_index):
            try:
                gid = group_by_index(i)
            except Exception:
                gid = None
        primitives.append(
            {
                "id": _new_id(key),
                "key": key,
                "label": key.replace("_", " "),
                "group_id": gid,
                "constraints": [],
                "input_schema": _empty_object_schema(),
                "output_schema": _empty_object_schema(),
            }
        )
    return primitives


def normalize_stage_collaboration(stage: str, raw: Any) -> dict[str, Any]:
    default = _default_design_stage() if stage == "design" else _default_develop_stage()
    if not isinstance(raw, dict):
        return default

    fmt = _deep_merge_str_dict(
        {k: str(v) for k, v in default["collaboration_format"].items()},
        raw.get("collaboration_format"),
    )

    prim_raw = raw.get("primitives")
    if isinstance(prim_raw, list) and prim_raw and isinstance(prim_raw[0], dict):
        primitives = [x for x in (_ensure_primitive(p, stage) for p in prim_raw) if x is not None]
        groups = _normalize_groups(raw.get("groups"))
        if primitives and not groups:
            groups = list(default["groups"])
        return {"collaboration_format": fmt, "groups": groups, "primitives": primitives}

    ops = raw.get("operation_primitives")
    if isinstance(ops, list) and ops and all(isinstance(x, str) for x in ops):
        keys = [str(x) for x in ops]
        if stage == "design":

            def gid_design(i: int) -> str | None:
                if i <= 1:
                    return "design-research"
                if i <= 4:
                    return "design-ux"
                return "design-review"

            prims = _migrate_string_primitives(keys, gid_design)
            return {"collaboration_format": fmt, "groups": list(_default_design_stage()["groups"]), "primitives": prims}

        def gid_dev(i: int) -> str | None:
            if i <= 2:
                return "dev-planning"
            if i <= 4:
                return "dev-execution"
            return "dev-quality"

        prims = _migrate_string_primitives(keys, gid_dev)
        return {"collaboration_format": fmt, "groups": list(_default_develop_stage()["groups"]), "primitives": prims}

    return {
        "collaboration_format": fmt,
        "groups": list(default["groups"]),
        "primitives": list(default["primitives"]),
    }


def normalize_collaboration_config(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return default_collaboration_config()
    d_raw = raw.get("design")
    dv_raw = raw.get("develop")
    return {
        "design": normalize_stage_collaboration("design", d_raw if isinstance(d_raw, dict) else None),
        "develop": normalize_stage_collaboration("develop", dv_raw if isinstance(dv_raw, dict) else None),
    }
