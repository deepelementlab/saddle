from __future__ import annotations

from pathlib import Path

from saddle.modes.loader import default_mode
from saddle.pipeline.runner import PipelineRunner


def test_pipeline_default_order(tmp_path: Path) -> None:
    runner = PipelineRunner(project_root=tmp_path)
    mode = default_mode()
    result = runner.run("build demo", mode=mode, session_id="sid-p1")
    assert [s.stage for s in result.stages] == ["spec", "design", "develop"]


def test_pipeline_respects_disabled_stage(tmp_path: Path) -> None:
    runner = PipelineRunner(project_root=tmp_path)
    mode = default_mode()
    mode.design.enabled = False
    result = runner.run("build demo", mode=mode, session_id="sid-p2")
    assert [s.stage for s in result.stages] == ["spec", "develop"]

