from __future__ import annotations

from pathlib import Path

from saddle.modes.loader import default_mode, load_mode_from_file


def test_default_mode_values() -> None:
    m = default_mode()
    assert m.pipeline.enabled is True
    assert m.pipeline.order == ["spec", "design", "develop"]
    assert m.agent_selection.strategy == "minimal"


def test_load_mode_from_yaml(tmp_path: Path) -> None:
    modes = tmp_path / ".saddle" / "modes"
    modes.mkdir(parents=True, exist_ok=True)
    (modes / "custom.yaml").write_text(
        """
name: custom
design:
  deep_loop: true
  max_iters: 7
agent_selection:
  strategy: balanced
""",
        encoding="utf-8",
    )
    m = load_mode_from_file(tmp_path, "custom")
    assert m.name == "custom"
    assert m.design.deep_loop is True
    assert m.design.max_iters == 7
    assert m.agent_selection.strategy == "balanced"

