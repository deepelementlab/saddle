import "../monacoEnv";
import { useCallback, useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { JsonSchemaQuickForm } from "./JsonSchemaQuickForm";
import type { Lang } from "../i18n";
import type { text } from "../i18n";

type Tab = "monaco" | "form";

interface Props {
  /** Unique virtual path for Monaco JSON worker (diagnostics scope). */
  pathId: string;
  label: string;
  schema: Record<string, unknown>;
  onCommit: (next: Record<string, unknown>) => void;
  t: (typeof text)[Lang];
}

export function SchemaFieldEditor({ pathId, label, schema, onCommit, t }: Props): JSX.Element {
  const snap = JSON.stringify(schema);
  const [str, setStr] = useState(() => JSON.stringify(schema, null, 2));
  const [tab, setTab] = useState<Tab>("monaco");
  const [err, setErr] = useState<string | null>(null);
  const commitRef = useRef(onCommit);
  commitRef.current = onCommit;
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    setStr(JSON.stringify(schema, null, 2));
    setErr(null);
  }, [pathId, snap]);

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const scheduleCommit = useCallback((json: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      debounceRef.current = undefined;
      try {
        commitRef.current(JSON.parse(json) as Record<string, unknown>);
        setErr(null);
      } catch {
        setErr(t.schemaInvalid);
      }
    }, 450);
  }, [t.schemaInvalid]);

  const handleEditorChange = useCallback(
    (v: string | undefined) => {
      const next = v ?? "";
      setStr(next);
      try {
        JSON.parse(next);
        setErr(null);
        scheduleCommit(next);
      } catch {
        setErr(t.schemaInvalid);
      }
    },
    [scheduleCommit, t.schemaInvalid]
  );

  const handleFormChange = useCallback(
    (nextObj: Record<string, unknown>) => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
        debounceRef.current = undefined;
      }
      onCommit(nextObj);
      setStr(JSON.stringify(nextObj, null, 2));
      setErr(null);
    },
    [onCommit]
  );

  const handleMount = useCallback((ed: editor.IStandaloneCodeEditor, monaco: typeof import("monaco-editor")) => {
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      allowComments: false,
      enableSchemaRequest: true,
    });
    ed.updateOptions({
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 13,
      tabSize: 2,
      automaticLayout: true,
      wordWrap: "on",
    });
  }, []);

  let formValue: Record<string, unknown> | null = null;
  try {
    const p = JSON.parse(str) as unknown;
    if (typeof p === "object" && p !== null && !Array.isArray(p)) {
      formValue = p as Record<string, unknown>;
    }
  } catch {
    formValue = null;
  }

  return (
    <div className={`schema-field-editor ${err ? "has-error" : ""}`}>
      <div className="schema-field-label">{label}</div>
      <div className="schema-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "monaco"}
          className={tab === "monaco" ? "schema-tab active" : "schema-tab"}
          onClick={() => setTab("monaco")}
        >
          {t.schemaTabMonaco}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "form"}
          className={tab === "form" ? "schema-tab active" : "schema-tab"}
          onClick={() => setTab("form")}
        >
          {t.schemaTabForm}
        </button>
      </div>
      {tab === "monaco" && (
        <div className="schema-monaco-wrap">
          <Editor
            height="228px"
            path={`saddle-schema-${pathId}.json`}
            defaultLanguage="json"
            theme="vs"
            value={str}
            onChange={handleEditorChange}
            onMount={handleMount}
          />
        </div>
      )}
      {tab === "form" &&
        (formValue ? (
          <JsonSchemaQuickForm value={formValue} onChange={handleFormChange} t={t} />
        ) : (
          <p className="schema-form-fallback">{t.schemaFormParseError}</p>
        ))}
      {err && tab === "monaco" && <div className="schema-err">{err}</div>}
    </div>
  );
}
