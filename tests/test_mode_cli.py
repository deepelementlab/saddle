"""Tests for `saddle mode` CLI and mode tools."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from saddle.cli import app
from saddle.modes.resolver import resolve_mode
from saddle.modes.tools import list_mode_names, validate_mode_config


def test_list_mode_names_pkg_root() -> None:
    root = Path(__file__).resolve().parents[1]
    names = list_mode_names(root)
    assert "default" in names
    assert "fast" in names
    assert "deep" in names


def test_validate_default_mode_ok() -> None:
    root = str(Path(__file__).resolve().parents[1])
    cfg = resolve_mode(root, mode_name="default", overrides=None)
    errors, warnings = validate_mode_config(cfg)
    assert errors == []


def test_validate_invalid_pipeline_stage() -> None:
    root = str(Path(__file__).resolve().parents[1])
    cfg = resolve_mode(root, mode_name="default", overrides=["pipeline.order=[spec,unknown,develop]"])
    errors, _ = validate_mode_config(cfg)
    assert any("invalid stage" in e for e in errors)


def test_cli_root_help_uses_prog_name_saddle() -> None:
    runner = CliRunner()
    r = runner.invoke(app, ["--help"], prog_name="saddle")
    assert r.exit_code == 0
    assert "Usage: saddle" in r.output


def test_python_m_saddle_no_args_shows_help_exit_zero() -> None:
    pkg = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(pkg / "src")}
    r = subprocess.run(
        [sys.executable, "-m", "saddle"],
        capture_output=True,
        text=True,
        cwd=str(pkg),
        env=env,
        check=False,
    )
    assert r.returncode == 0
    assert "Usage: saddle" in r.stdout
    assert "run" in r.stdout
    assert "/ ___|" in r.stdout


def test_python_m_saddle_help() -> None:
    pkg = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(pkg / "src")}
    r = subprocess.run(
        [sys.executable, "-m", "saddle", "--help"],
        capture_output=True,
        text=True,
        cwd=str(pkg),
        env=env,
        check=False,
    )
    assert r.returncode == 0
    assert "Usage: saddle" in r.stdout
    assert "/ ___|" in r.stdout
    assert "|____/" in r.stdout


def test_cli_mode_list() -> None:
    runner = CliRunner()
    pkg = Path(__file__).resolve().parents[1]
    r = runner.invoke(app, ["mode", "list", "--project", str(pkg)])
    assert r.exit_code == 0
    data = json.loads(r.stdout)
    assert "default" in data["modes"]


def test_cli_mode_show() -> None:
    runner = CliRunner()
    pkg = Path(__file__).resolve().parents[1]
    r = runner.invoke(app, ["mode", "show", "fast", "--project", str(pkg)])
    assert r.exit_code == 0
    data = json.loads(r.stdout)
    assert data["name"] == "fast"


def test_cli_mode_validate_ok() -> None:
    runner = CliRunner()
    pkg = Path(__file__).resolve().parents[1]
    r = runner.invoke(app, ["mode", "validate", "default", "--project", str(pkg)])
    assert r.exit_code == 0
    data = json.loads(r.stdout)
    assert data["ok"] is True


def test_cli_mode_validate_fail() -> None:
    runner = CliRunner()
    pkg = Path(__file__).resolve().parents[1]
    r = runner.invoke(
        app,
        ["mode", "validate", "default", "--project", str(pkg), "--set", "pipeline.order=[spec,bad,develop]"],
    )
    assert r.exit_code == 1
    data = json.loads(r.stdout)
    assert data["ok"] is False
    assert data["errors"]
