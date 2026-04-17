import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ConfigPreview } from "../components/ConfigPreview";
import { ModeForm } from "../components/ModeForm";
import { SaddleLogo } from "../components/SaddleLogo";
import { text, type Lang } from "../i18n";
import { listModes, saveMode, showMode, validateMode } from "../api/modes";
import type { ModeConfig, ValidationResult } from "../types/mode";
import { defaultCollaborationConfig, normalizeStageCollaboration } from "../utils/collaboration";

const DEFAULT_MODE: ModeConfig = {
  name: "default",
  pipeline: { enabled: true, order: ["spec", "design", "develop"] },
  spec: { enabled: true },
  design: { enabled: true, deep_loop: false, max_iters: 100, prompt_profile: "full" },
  develop: { enabled: true, deep_loop: false, max_iters: 100, prompt_profile: "full" },
  agent_selection: { strategy: "minimal", custom_roles: [] },
  thresholds: { min_gap_delta: 0.05, convergence_rounds: 2, handoff_target: 0.85 },
  role_mindsets: {},
  tool_policy: {
    enable_web_search: true,
    enable_shell: true,
    enable_subagent: true,
    risk_level: "balanced",
  },
  collaboration_config: defaultCollaborationConfig(),
};

export function ModeStudioPage(): JSX.Element {
  const [mode, setMode] = useState<ModeConfig>(DEFAULT_MODE);
  const [modeList, setModeList] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [message, setMessage] = useState<string>("");
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    const saved = localStorage.getItem("saddle_studio_lang");
    if (saved === "en" || saved === "zh") setLang(saved);
    void (async () => {
      try {
        setModeList(await listModes());
      } catch {
        setMessage(saved === "zh" ? "无法获取模式列表，请确认 saddle serve 已启动。" : "Failed to load mode list. Ensure `saddle serve` is running.");
      }
    })();
  }, []);

  const isValid = useMemo(() => result?.ok ?? true, [result]);
  const t = text[lang];
  const toggle = (): void => {
    const next: Lang = lang === "en" ? "zh" : "en";
    setLang(next);
    localStorage.setItem("saddle_studio_lang", next);
  };

  const onLoad = async (name: string): Promise<void> => {
    setBusy(true);
    setMessage("");
    try {
      const loaded = await showMode(name);
      setMode({
        ...loaded,
        collaboration_config: {
          design: normalizeStageCollaboration("design", loaded.collaboration_config?.design),
          develop: normalizeStageCollaboration("develop", loaded.collaboration_config?.develop),
        },
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : lang === "zh" ? "加载失败" : "Load failed");
    } finally {
      setBusy(false);
    }
  };

  const onValidate = async (): Promise<void> => {
    setBusy(true);
    setMessage("");
    try {
      setResult(await validateMode(mode));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : lang === "zh" ? "校验失败" : "Validation failed");
    } finally {
      setBusy(false);
    }
  };

  const onSave = async (): Promise<void> => {
    setBusy(true);
    setMessage("");
    try {
      const r = await saveMode(mode);
      setMessage(lang === "zh" ? `已保存到 ${r.saved}` : `Saved to ${r.saved}`);
      setModeList(await listModes());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : lang === "zh" ? "保存失败" : "Save failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="page page-studio">
      <header className="studio-header">
        <div className="studio-brand">
          <SaddleLogo />
          <div>
            <h1>{t.studioTitle}</h1>
            <p>{t.studioSubtitle}</p>
          </div>
        </div>
        <button className="btn btn-secondary" onClick={toggle}>
          {t.langToggle}
        </button>
        <Link to="/" className="btn btn-secondary">
          {t.backWelcome}
        </Link>
      </header>

      <section className="panel">
        <h3>{t.loadTemplate}</h3>
        <div className="button-row">
          {modeList.map((name) => (
            <button key={name} className="btn btn-secondary" onClick={() => void onLoad(name)} disabled={busy}>
              {name}
            </button>
          ))}
        </div>
      </section>

      <ModeForm
        lang={lang}
        mode={mode}
        onModeChange={setMode}
        onValidate={() => void onValidate()}
        onSave={() => void onSave()}
        busy={busy}
      />

      {result && (
        <section className={`panel ${isValid ? "status-ok" : "status-error"}`}>
          <h3>{t.validateResult}</h3>
          <p>ok: {String(result.ok)}</p>
          {result.errors.length > 0 && <pre>{result.errors.join("\n")}</pre>}
          {result.warnings.length > 0 && <pre>{result.warnings.join("\n")}</pre>}
        </section>
      )}

      {message && <section className="panel">{message}</section>}

      <ConfigPreview mode={mode} />
    </main>
  );
}
