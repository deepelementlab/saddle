import type { StageCollaboration } from "./collaboration";

export type PromptProfile = "full" | "compact";
export type SelectionStrategy = "minimal" | "balanced" | "custom";

export interface TeamStageConfig {
  enabled: boolean;
  deep_loop: boolean;
  max_iters: number;
  prompt_profile: PromptProfile;
}

export interface ModeConfig {
  name: string;
  pipeline: {
    enabled: boolean;
    order: string[];
  };
  spec: {
    enabled: boolean;
  };
  design: TeamStageConfig;
  develop: TeamStageConfig;
  agent_selection: {
    strategy: SelectionStrategy;
    custom_roles: string[];
  };
  thresholds: {
    min_gap_delta: number;
    convergence_rounds: number;
    handoff_target: number;
  };
  role_mindsets?: Record<string, string>;
  tool_policy?: {
    enable_web_search: boolean;
    enable_shell: boolean;
    enable_subagent: boolean;
    risk_level: "strict" | "balanced" | "aggressive";
  };
  collaboration_config?: {
    design: StageCollaboration;
    develop: StageCollaboration;
  };
}

export interface ValidationResult {
  mode: string;
  ok: boolean;
  errors: string[];
  warnings: string[];
}
