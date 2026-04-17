"""Saddle CLI entrypoint."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import typer
import uvicorn

from saddle.modes.resolver import resolve_mode
from saddle.modes.tools import list_mode_names, mode_to_jsonable, validate_mode_config
from saddle.pipeline.runner import PipelineRunner
from saddle.orchestrator.team_service import TeamService
from saddle.spec.service import SpecService

app = typer.Typer(help="Saddle standalone runtime")

mode_app = typer.Typer(help="Inspect and validate collaboration modes")


@mode_app.command("list")
def mode_list(
    project_root: Path | None = typer.Option(None, "--project", "-p", help="Project root (default cwd)"),
) -> None:
    """List mode names found under .saddle/modes/."""
    root = project_root or Path.cwd()
    names = list_mode_names(root)
    typer.echo(json.dumps({"modes": names, "path": str(root / ".saddle" / "modes")}, ensure_ascii=False, indent=2))


@mode_app.command("show")
def mode_show(
    name: str = typer.Argument("default", help="Mode name (stem of .saddle/modes/<name>.yaml)"),
    set_: list[str] | None = typer.Option(None, "--set", help="Override key=value (dot path)"),
    project_root: Path | None = typer.Option(None, "--project", help="Project root (default cwd)"),
) -> None:
    """Show resolved mode configuration (defaults + file + --set)."""
    root = str((project_root or Path.cwd()).resolve())
    cfg = resolve_mode(root, mode_name=name, overrides=set_)
    typer.echo(json.dumps(mode_to_jsonable(cfg), ensure_ascii=False, indent=2))


@mode_app.command("validate")
def mode_validate(
    name: str = typer.Argument("default", help="Mode name to validate"),
    set_: list[str] | None = typer.Option(None, "--set", help="Override key=value before validation"),
    project_root: Path | None = typer.Option(None, "--project", help="Project root (default cwd)"),
) -> None:
    """Validate a mode configuration; exits non-zero on errors."""
    root = str((project_root or Path.cwd()).resolve())
    cfg = resolve_mode(root, mode_name=name, overrides=set_)
    errors, warnings = validate_mode_config(cfg)
    payload = {
        "mode": cfg.name,
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    if errors:
        raise typer.Exit(code=1)


app.add_typer(mode_app, name="mode")


@app.command("serve")
def serve(
    host: str = "127.0.0.1",
    port: int = 1995,
    studio_dir: str | None = typer.Option(
        None,
        "--studio-dir",
        help="Directory of `vite build` output (contains index.html). Sets SADDLE_STUDIO_DIR.",
    ),
) -> None:
    """Run Saddle memory API server (optionally hosts built Saddle Studio from studio/dist)."""
    if studio_dir:
        os.environ["SADDLE_STUDIO_DIR"] = studio_dir
    uvicorn.run("saddle.memory_api.server:app", host=host, port=port, reload=False)


@app.command("spec")
def spec(request: str, session_id: str | None = None) -> None:
    """Create a spec bundle."""
    svc = SpecService(working_directory=".")
    bundle = svc.create_bundle(request, session_id=session_id)
    typer.echo(json.dumps({"session_id": bundle.session_id, "spec_dir": bundle.spec_dir}, ensure_ascii=False))


def _handle_team(team: str, content: str, session_id: str | None = None) -> None:
    svc = TeamService(project_root=Path.cwd())
    result = svc.orchestrate(team=team, content=content, session_id=session_id)
    typer.echo(
        json.dumps(
            {
                "team": result.team,
                "session_id": result.session_id,
                "selected_agents": result.selected_agents,
                "deep_loop": result.deep_loop,
                "max_iters": result.max_iters,
                "prompt": result.prompt,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command("run")
def run(
    requirement: str,
    mode: str = "default",
    set_: list[str] | None = typer.Option(None, "--set"),
    session_id: str | None = None,
) -> None:
    """Run default auto-pipeline using collaboration mode."""
    sid = session_id or str(uuid.uuid4())
    resolved = resolve_mode(str(Path.cwd()), mode_name=mode, overrides=set_)
    runner = PipelineRunner(Path.cwd())
    result = runner.run(requirement=requirement, mode=resolved, session_id=sid)
    typer.echo(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


@app.command("develop")
def develop(content: str, session_id: str | None = None) -> None:
    """Run /develop orchestration parser."""
    _handle_team("clawteam", content=content, session_id=session_id)


@app.command("design")
def design(content: str, session_id: str | None = None) -> None:
    """Run /design orchestration parser."""
    _handle_team("designteam", content=content, session_id=session_id)


@app.command("clawteam")
def clawteam_alias(content: str, session_id: str | None = None) -> None:
    """Backward-compatible alias of `saddle develop`."""
    develop(content=content, session_id=session_id)


@app.command("designteam")
def designteam_alias(content: str, session_id: str | None = None) -> None:
    """Backward-compatible alias of `saddle design`."""
    design(content=content, session_id=session_id)


@app.command("finalize")
def finalize(team: str, session_id: str, text_file: str) -> None:
    """Finalize deep-loop writeback from assistant output file."""
    text = Path(text_file).read_text(encoding="utf-8")
    svc = TeamService(project_root=Path.cwd())
    result = svc.finalize(team=team, session_id=session_id, assistant_text=text)
    typer.echo(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    app()
