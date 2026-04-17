"""Default auto-pipeline runner: spec -> design -> develop."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from saddle.modes.schema import ModeConfig
from saddle.orchestrator.team_service import TeamOrchestrationOptions, TeamService
from saddle.spec.service import SpecService


@dataclass
class StageResult:
    stage: str
    ok: bool
    elapsed_ms: int
    output: dict[str, Any]


@dataclass
class PipelineResult:
    mode: str
    session_id: str
    stages: list[StageResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "session_id": self.session_id,
            "stages": [asdict(s) for s in self.stages],
        }


class PipelineRunner:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).expanduser().resolve()
        self.spec_service = SpecService(working_directory=str(self.project_root))
        self.team_service = TeamService(project_root=self.project_root)

    def run(self, requirement: str, mode: ModeConfig, session_id: str) -> PipelineResult:
        stages: list[StageResult] = []
        request = requirement.strip()
        spec_summary = ""

        for stage in mode.pipeline.order:
            if stage == "spec" and mode.spec.enabled:
                t0 = time.time()
                b = self.spec_service.create_bundle(request, session_id=session_id)
                spec_summary = b.spec_markdown[:400]
                stages.append(
                    StageResult(
                        stage="spec",
                        ok=True,
                        elapsed_ms=int((time.time() - t0) * 1000),
                        output={"spec_dir": b.spec_dir, "session_id": b.session_id},
                    )
                )
            elif stage == "design" and mode.design.enabled:
                t0 = time.time()
                content = request
                if spec_summary:
                    content += f"\n\nSpec summary:\n{spec_summary}"
                r = self.team_service.orchestrate(
                    "designteam",
                    content,
                    session_id=session_id,
                    options=TeamOrchestrationOptions(
                        selection_strategy=mode.agent_selection.strategy,
                        thresholds=mode.thresholds,
                        prompt_profile=mode.design.prompt_profile,
                        custom_roles=mode.agent_selection.custom_roles,
                        force_deep_loop=mode.design.deep_loop,
                        force_max_iters=mode.design.max_iters,
                    ),
                )
                stages.append(
                    StageResult(
                        stage="design",
                        ok=True,
                        elapsed_ms=int((time.time() - t0) * 1000),
                        output={
                            "selected_agents": r.selected_agents,
                            "deep_loop": r.deep_loop,
                            "max_iters": r.max_iters,
                        },
                    )
                )
            elif stage == "develop" and mode.develop.enabled:
                t0 = time.time()
                content = request
                if spec_summary:
                    content += f"\n\nSpec summary:\n{spec_summary}"
                r = self.team_service.orchestrate(
                    "clawteam",
                    content,
                    session_id=session_id,
                    options=TeamOrchestrationOptions(
                        selection_strategy=mode.agent_selection.strategy,
                        thresholds=mode.thresholds,
                        prompt_profile=mode.develop.prompt_profile,
                        custom_roles=mode.agent_selection.custom_roles,
                        force_deep_loop=mode.develop.deep_loop,
                        force_max_iters=mode.develop.max_iters,
                    ),
                )
                stages.append(
                    StageResult(
                        stage="develop",
                        ok=True,
                        elapsed_ms=int((time.time() - t0) * 1000),
                        output={
                            "selected_agents": r.selected_agents,
                            "deep_loop": r.deep_loop,
                            "max_iters": r.max_iters,
                        },
                    )
                )
        return PipelineResult(mode=mode.name, session_id=session_id, stages=stages)

