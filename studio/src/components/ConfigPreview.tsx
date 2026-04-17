import YAML from "yaml";
import type { ModeConfig } from "../types/mode";

interface Props {
  mode: ModeConfig;
}

export function ConfigPreview({ mode }: Props): JSX.Element {
  return (
    <div className="preview-grid">
      <section className="panel">
        <h3>JSON Preview</h3>
        <pre>{JSON.stringify(mode, null, 2)}</pre>
      </section>
      <section className="panel">
        <h3>YAML Preview</h3>
        <pre>{YAML.stringify(mode)}</pre>
      </section>
    </div>
  );
}
