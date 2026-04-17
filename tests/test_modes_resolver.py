from __future__ import annotations

from pathlib import Path

from saddle.modes.resolver import resolve_mode


def test_cli_overrides_take_precedence(tmp_path: Path) -> None:
    modes = tmp_path / ".saddle" / "modes"
    modes.mkdir(parents=True, exist_ok=True)
    (modes / "default.yaml").write_text(
        """
name: default
develop:
  deep_loop: false
  max_iters: 10
""",
        encoding="utf-8",
    )
    m = resolve_mode(
        str(tmp_path),
        mode_name="default",
        overrides=["develop.deep_loop=true", "develop.max_iters=25", "pipeline.order=[spec,develop]"],
    )
    assert m.develop.deep_loop is True
    assert m.develop.max_iters == 25
    assert m.pipeline.order == ["spec", "develop"]

