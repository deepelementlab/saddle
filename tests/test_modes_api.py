from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from saddle.memory_api.server import app


def test_modes_list_and_show(tmp_path: Path, monkeypatch) -> None:
    modes_dir = tmp_path / ".saddle" / "modes"
    modes_dir.mkdir(parents=True, exist_ok=True)
    (modes_dir / "default.yaml").write_text(
        """
name: default
pipeline:
  order: [spec, design, develop]
role_mindsets:
  architect: systems-thinking
tool_policy:
  enable_web_search: true
  enable_shell: true
  enable_subagent: true
  risk_level: balanced
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    r = client.get("/api/v1/modes")
    assert r.status_code == 200
    assert "default" in r.json()["modes"]

    s = client.get("/api/v1/modes/default")
    assert s.status_code == 200
    body = s.json()
    assert body["name"] == "default"
    assert body["pipeline"]["order"] == ["spec", "design", "develop"]
    assert body["role_mindsets"]["architect"] == "systems-thinking"
    assert "collaboration_config" in body
    assert "primitives" in body["collaboration_config"]["design"]
    assert isinstance(body["collaboration_config"]["design"]["primitives"], list)


def test_modes_validate_and_save(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    payload = {
        "name": "pro",
        "pipeline": {"enabled": True, "order": ["spec", "design", "develop"]},
        "spec": {"enabled": True},
        "design": {"enabled": True, "deep_loop": True, "max_iters": 8, "prompt_profile": "full"},
        "develop": {"enabled": True, "deep_loop": False, "max_iters": 12, "prompt_profile": "compact"},
        "agent_selection": {"strategy": "balanced", "custom_roles": []},
        "thresholds": {"min_gap_delta": 0.04, "convergence_rounds": 2, "handoff_target": 0.9},
        "role_mindsets": {"pm": "user-value-first"},
        "tool_policy": {
            "enable_web_search": True,
            "enable_shell": True,
            "enable_subagent": True,
            "risk_level": "balanced",
        },
        "collaboration_config": {
            "design": {
                "collaboration_format": {"team": "designteam", "mode": "custom-design"},
                "operation_primitives": ["clarify_requirement", "custom_design_step"],
            },
            "develop": {
                "collaboration_format": {"team": "clawteam", "mode": "custom-develop"},
                "operation_primitives": ["scope_decomposition", "custom_develop_step"],
            },
        },
    }

    v = client.post("/api/v1/modes/validate", json=payload)
    assert v.status_code == 200
    assert v.json()["ok"] is True

    w = client.post("/api/v1/modes/save", json=payload)
    assert w.status_code == 200
    assert w.json()["mode"] == "pro"

    saved = tmp_path / ".saddle" / "modes" / "pro.yaml"
    assert saved.is_file()
    text = saved.read_text(encoding="utf-8")
    assert "role_mindsets" in text
    assert "tool_policy" in text
    assert "collaboration_config" in text
