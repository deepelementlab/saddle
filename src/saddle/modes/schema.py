"""Schema for Saddle collaboration modes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


SelectionStrategy = Literal["minimal", "balanced", "custom"]
PromptProfile = Literal["full", "compact"]


@dataclass
class StageTeamConfig:
    enabled: bool = True
    deep_loop: bool = False
    max_iters: int = 100
    prompt_profile: PromptProfile = "full"


@dataclass
class StageSpecConfig:
    enabled: bool = True


@dataclass
class PipelineConfig:
    enabled: bool = True
    order: list[str] = field(default_factory=lambda: ["spec", "design", "develop"])


@dataclass
class AgentSelectionConfig:
    strategy: SelectionStrategy = "minimal"
    custom_roles: list[str] = field(default_factory=list)


@dataclass
class ModeConfig:
    name: str = "default"
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    spec: StageSpecConfig = field(default_factory=StageSpecConfig)
    design: StageTeamConfig = field(default_factory=StageTeamConfig)
    develop: StageTeamConfig = field(default_factory=StageTeamConfig)
    agent_selection: AgentSelectionConfig = field(default_factory=AgentSelectionConfig)
    thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "min_gap_delta": 0.05,
            "convergence_rounds": 2.0,
            "handoff_target": 0.85,
        }
    )

