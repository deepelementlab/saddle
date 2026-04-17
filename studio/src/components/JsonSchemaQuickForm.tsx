import type { Lang } from "../i18n";
import type { text } from "../i18n";

const JSON_TYPES = ["object", "array", "string", "number", "integer", "boolean", "null"] as const;

type JsonType = (typeof JSON_TYPES)[number];

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null && !Array.isArray(x);
}

function nextPropKey(existing: Record<string, unknown>): string {
  let n = 1;
  let k = `field_${n}`;
  while (k in existing) {
    n += 1;
    k = `field_${n}`;
  }
  return k;
}

interface Props {
  value: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
  t: (typeof text)[Lang];
}

export function JsonSchemaQuickForm({ value, onChange, t }: Props): JSX.Element {
  if (!isRecord(value)) {
    return <p className="schema-form-fallback">{t.schemaFormNeedObject}</p>;
  }

  const typeRaw = value.type;
  const typeStr: JsonType = JSON_TYPES.includes(typeRaw as JsonType) ? (typeRaw as JsonType) : "object";
  const title = typeof value.title === "string" ? value.title : "";
  const description = typeof value.description === "string" ? value.description : "";
  const propsObj =
    isRecord(value.properties) && typeStr === "object" ? (value.properties as Record<string, unknown>) : {};
  const propEntries = Object.entries(propsObj);

  const setField = (patch: Record<string, unknown>): void => {
    onChange({ ...value, ...patch });
  };

  const addProperty = (): void => {
    const k = nextPropKey(propsObj);
    setField({
      properties: { ...propsObj, [k]: { type: "string" } },
      type: "object",
    });
  };

  const removeProperty = (key: string): void => {
    const nextProps = { ...propsObj };
    delete nextProps[key];
    setField({ properties: nextProps });
  };

  return (
    <div className="schema-quick-form">
      <p className="schema-form-hint">{t.schemaFormHint}</p>
      <div className="schema-form-grid">
        <label className="schema-form-label">
          {t.schemaFormType}
          <select
            value={typeStr}
            onChange={(e) => {
              const nt = e.target.value as JsonType;
              if (nt === "object") {
                onChange({
                  ...value,
                  type: "object",
                  properties: isRecord(value.properties) ? value.properties : {},
                });
              } else {
                const { properties: _p, required: _r, additionalProperties: _a, ...rest } = value;
                onChange({ ...rest, type: nt });
              }
            }}
          >
            {JSON_TYPES.map((x) => (
              <option key={x} value={x}>
                {x}
              </option>
            ))}
          </select>
        </label>
        <label className="schema-form-label">
          {t.schemaFormTitle}
          <input value={title} onChange={(e) => setField({ title: e.target.value || undefined })} />
        </label>
        <label className="schema-form-label schema-form-span2">
          {t.schemaFormDescription}
          <textarea
            rows={2}
            value={description}
            onChange={(e) => setField({ description: e.target.value || undefined })}
          />
        </label>
      </div>

      {typeStr === "object" && (
        <>
          <label className="schema-form-check">
            <input
              type="checkbox"
              checked={value.additionalProperties === true}
              onChange={(e) =>
                setField({
                  additionalProperties: e.target.checked ? true : false,
                })
              }
            />
            {t.schemaFormAdditionalProps}
          </label>
          <div className="schema-form-props-head">
            <span>{t.schemaFormProperties}</span>
            <button type="button" className="btn btn-secondary btn-compact" onClick={addProperty}>
              {t.schemaFormAddProperty}
            </button>
          </div>
          {propEntries.length === 0 && <p className="schema-form-empty">{t.schemaFormNoProperties}</p>}
          {propEntries.map(([key, raw]) => {
            const sub = isRecord(raw) ? raw : { type: "string" };
            const st = typeof sub.type === "string" && JSON_TYPES.includes(sub.type as JsonType) ? sub.type : "string";
            return (
              <div key={key} className="schema-prop-row">
                <input
                  className="schema-prop-key"
                  value={key}
                  onChange={(e) => {
                    const nk = e.target.value;
                    const nextProps = { ...propsObj };
                    delete nextProps[key];
                    nextProps[nk] = sub;
                    setField({ properties: nextProps });
                  }}
                />
                <select
                  value={st}
                  onChange={(e) => {
                    const nextProps = { ...propsObj };
                    nextProps[key] = { ...sub, type: e.target.value };
                    setField({ properties: nextProps });
                  }}
                >
                  {JSON_TYPES.map((x) => (
                    <option key={x} value={x}>
                      {x}
                    </option>
                  ))}
                </select>
                <button type="button" className="btn btn-secondary btn-compact" onClick={() => removeProperty(key)}>
                  ×
                </button>
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}
