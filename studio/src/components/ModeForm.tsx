import type { ChangeEvent } from "react";
import { useMemo } from "react";
import { CollaborationEditor } from "./CollaborationEditor";
import { text, type Lang } from "../i18n";
import type { ModeConfig } from "../types/mode";
import { defaultCollaborationConfig, normalizeStageCollaboration } from "../utils/collaboration";

interface Props {
  lang: Lang;
  mode: ModeConfig;
  onModeChange: (next: ModeConfig) => void;
  onValidate: () => void;
  onSave: () => void;
  busy: boolean;
}

function parseCsv(value: string): string[] {
  return value
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}

export function ModeForm({ lang, mode, onModeChange, onValidate, onSave, busy }: Props): JSX.Element {
  const t = text[lang];
  const set = <K extends keyof ModeConfig>(key: K, value: ModeConfig[K]): void => {
    onModeChange({ ...mode, [key]: value });
  };

  const collaboration = useMemo(
    () => ({
      design: normalizeStageCollaboration("design", mode.collaboration_config?.design),
      develop: normalizeStageCollaboration("develop", mode.collaboration_config?.develop),
    }),
    [mode.collaboration_config]
  );

  const onName = (e: ChangeEvent<HTMLInputElement>): void => set("name", e.target.value);

  return (
    <div className="form-stack">
      <section className="panel">
        <h3>{t.baseConfig}</h3>
        <label>
          {t.modeName}
          <input value={mode.name} onChange={onName} />
        </label>
        <label>
          pipeline.order (CSV)
          <input
            value={mode.pipeline.order.join(",")}
            onChange={(e) =>
              set("pipeline", {
                ...mode.pipeline,
                order: parseCsv(e.target.value),
              })
            }
          />
        </label>
        <label>
          spec.enabled
          <input
            type="checkbox"
            checked={mode.spec.enabled}
            onChange={(e) => set("spec", { enabled: e.target.checked })}
          />
        </label>
      </section>

      <section className="panel">
        <h3>{t.stageSection}</h3>
        {(["design", "develop"] as const).map((stage) => (
          <div key={stage} className="stage-grid">
            <h4>{stage}</h4>
            <label>
              enabled
              <input
                type="checkbox"
                checked={mode[stage].enabled}
                onChange={(e) =>
                  set(stage, {
                    ...mode[stage],
                    enabled: e.target.checked,
                  })
                }
              />
            </label>
            <label>
              deep_loop
              <input
                type="checkbox"
                checked={mode[stage].deep_loop}
                onChange={(e) =>
                  set(stage, {
                    ...mode[stage],
                    deep_loop: e.target.checked,
                  })
                }
              />
            </label>
            <label>
              max_iters
              <input
                type="number"
                value={mode[stage].max_iters}
                onChange={(e) =>
                  set(stage, {
                    ...mode[stage],
                    max_iters: Number(e.target.value),
                  })
                }
              />
            </label>
            <label>
              prompt_profile
              <select
                value={mode[stage].prompt_profile}
                onChange={(e) =>
                  set(stage, {
                    ...mode[stage],
                    prompt_profile: e.target.value as "full" | "compact",
                  })
                }
              >
                <option value="full">full</option>
                <option value="compact">compact</option>
              </select>
            </label>
          </div>
        ))}
      </section>

      <section className="panel">
        <h3>{t.proConfig}</h3>
        <label>
          agent_selection.strategy
          <select
            value={mode.agent_selection.strategy}
            onChange={(e) =>
              set("agent_selection", {
                ...mode.agent_selection,
                strategy: e.target.value as "minimal" | "balanced" | "custom",
              })
            }
          >
            <option value="minimal">minimal</option>
            <option value="balanced">balanced</option>
            <option value="custom">custom</option>
          </select>
        </label>
        <label>
          custom_roles (CSV)
          <input
            value={mode.agent_selection.custom_roles.join(",")}
            onChange={(e) =>
              set("agent_selection", {
                ...mode.agent_selection,
                custom_roles: parseCsv(e.target.value),
              })
            }
          />
        </label>

        <label>
          thresholds.min_gap_delta
          <input
            type="number"
            step="0.01"
            value={mode.thresholds.min_gap_delta}
            onChange={(e) =>
              set("thresholds", {
                ...mode.thresholds,
                min_gap_delta: Number(e.target.value),
              })
            }
          />
        </label>
        <label>
          thresholds.convergence_rounds
          <input
            type="number"
            value={mode.thresholds.convergence_rounds}
            onChange={(e) =>
              set("thresholds", {
                ...mode.thresholds,
                convergence_rounds: Number(e.target.value),
              })
            }
          />
        </label>
        <label>
          thresholds.handoff_target
          <input
            type="number"
            step="0.01"
            value={mode.thresholds.handoff_target}
            onChange={(e) =>
              set("thresholds", {
                ...mode.thresholds,
                handoff_target: Number(e.target.value),
              })
            }
          />
        </label>

        <label>
          {t.roleMindset}
          <textarea
            value={JSON.stringify(mode.role_mindsets ?? {}, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value) as Record<string, string>;
                set("role_mindsets", parsed);
              } catch {
                // keep previous value while typing invalid json
              }
            }}
          />
        </label>
        <label>
          {t.toolPolicy}
          <textarea
            value={
              JSON.stringify(
                mode.tool_policy ?? {
                  enable_web_search: true,
                  enable_shell: true,
                  enable_subagent: true,
                  risk_level: "balanced",
                },
                null,
                2
              )
            }
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value) as ModeConfig["tool_policy"];
                set("tool_policy", parsed);
              } catch {
                // keep previous value while typing invalid json
              }
            }}
          />
        </label>
      </section>
      <section className="panel">
        <h3>{t.collabConfig}</h3>
        <p className="section-hint">{t.collabHint}</p>
        {(["design", "develop"] as const).map((stage) => (
          <div key={`cc-${stage}`} className="collab-stage-wrap">
            <CollaborationEditor
              lang={lang}
              stage={stage}
              value={collaboration[stage]}
              onChange={(next) =>
                set("collaboration_config", {
                  ...(mode.collaboration_config ?? defaultCollaborationConfig()),
                  [stage]: next,
                })
              }
            />
          </div>
        ))}
      </section>

      <div className="button-row">
        <button className="btn btn-secondary" onClick={onValidate} disabled={busy}>
          {t.validate}
        </button>
        <button className="btn btn-primary" onClick={onSave} disabled={busy}>
          {t.save}
        </button>
      </div>
    </div>
  );
}
