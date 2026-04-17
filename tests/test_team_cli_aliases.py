from __future__ import annotations

from typer.testing import CliRunner

import saddle.cli as cli


def test_design_and_designteam_route_to_same_team(monkeypatch) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str, str | None]] = []

    def fake_handle_team(team: str, content: str, session_id: str | None = None) -> None:
        calls.append((team, content, session_id))

    monkeypatch.setattr(cli, "_handle_team", fake_handle_team)

    r1 = runner.invoke(cli.app, ["design", "draft ux"])
    r2 = runner.invoke(cli.app, ["designteam", "draft ux", "--session-id", "sid-1"])

    assert r1.exit_code == 0
    assert r2.exit_code == 0
    assert calls == [
        ("designteam", "draft ux", None),
        ("designteam", "draft ux", "sid-1"),
    ]


def test_develop_and_clawteam_route_to_same_team(monkeypatch) -> None:
    runner = CliRunner()
    calls: list[tuple[str, str, str | None]] = []

    def fake_handle_team(team: str, content: str, session_id: str | None = None) -> None:
        calls.append((team, content, session_id))

    monkeypatch.setattr(cli, "_handle_team", fake_handle_team)

    r1 = runner.invoke(cli.app, ["develop", "build api"])
    r2 = runner.invoke(cli.app, ["clawteam", "build api", "--session-id", "sid-2"])

    assert r1.exit_code == 0
    assert r2.exit_code == 0
    assert calls == [
        ("clawteam", "build api", None),
        ("clawteam", "build api", "sid-2"),
    ]
