from __future__ import annotations

from pathlib import Path

from saddle.orchestrator.prompts import (
    build_clawteam_prompt,
    build_designteam_prompt,
    normalize_team_slash_prefix,
    parse_clawteam_args,
    parse_designteam_args,
)
from saddle.orchestrator.team_service import TeamOrchestrationOptions, TeamService


def test_normalize_clawteam_namespace() -> None:
    assert normalize_team_slash_prefix("clawteam", "/clawteam:qa fix auth") == "--agent qa fix auth"


def test_parse_clawteam_args_deep_loop() -> None:
    agent, req, deep, iters, err = parse_clawteam_args(
        "--deep_loop --max_iters 3 implement login"
    )
    assert err == ""
    assert agent is None
    assert deep is True
    assert iters == 3
    assert "login" in req


def test_build_clawteam_prompt_has_deep_loop_contract() -> None:
    p = build_clawteam_prompt(
        "ship MVP",
        None,
        deep_loop=True,
        max_iters=5,
    )
    assert "DEEP_LOOP_EVAL_JSON:" in p
    assert "DEEP_LOOP_WRITEBACK_JSON:" in p
    assert "gap_delta" in p
    assert "检查" in p


def test_build_designteam_prompt_has_phase_table() -> None:
    p = build_designteam_prompt(
        "design onboarding",
        None,
        deep_loop=True,
        max_iters=8,
        iter_idx=2,
    )
    assert "7-phase product design workflow" in p
    assert "探索与研究" in p or "定义与策略" in p
    assert "DEEP_LOOP_EVAL_JSON:" in p


def test_team_service_orchestrate_writes_run_meta(tmp_path: Path) -> None:
    svc = TeamService(project_root=tmp_path)
    r = svc.orchestrate("clawteam", "add metrics", session_id="sid-1")
    assert r.session_id == "sid-1"
    meta = tmp_path / ".saddle" / "runs" / f"clawteam-{r.session_id}.json"
    assert meta.is_file()


def test_team_service_finalize_writeback(tmp_path: Path) -> None:
    svc = TeamService(project_root=tmp_path)
    r = svc.orchestrate("clawteam", "--deep_loop do work", session_id="sid-2")
    assert r.deep_loop is True
    assistant = 'ok\nDEEP_LOOP_WRITEBACK_JSON: {"iteration":1,"result":"success"}\n'
    out = svc.finalize("clawteam", "sid-2", assistant)
    assert out["status"] == "ok"
    assert Path(out["file"]).is_file()


def test_team_service_strategy_injection_compact_keeps_protocol(tmp_path: Path) -> None:
    svc = TeamService(project_root=tmp_path)
    r = svc.orchestrate(
        "clawteam",
        "--deep_loop build infra",
        session_id="sid-3",
        options=TeamOrchestrationOptions(
            selection_strategy="balanced",
            prompt_profile="compact",
            force_deep_loop=True,
            force_max_iters=9,
        ),
    )
    assert r.deep_loop is True
    assert r.max_iters == 9
    # compact profile truncates but should preserve protocol signal
    assert "DEEP_LOOP_EVAL_JSON" in r.prompt
