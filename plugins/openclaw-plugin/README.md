# Saddle OpenClaw Plugin (`@saddle/openclaw-plugin`)

OpenClaw **context-engine** plugin: recalls and saves conversation turns through **`saddle serve`** Memory API (`POST /api/v1/memories/search`, `POST /api/v1/memories`).

**Scope:** This mirrors the *integration style* of EverOS’s OpenClaw plugin; Saddle’s retrieval is **local keyword search**, not cloud vectors.

## Prerequisites

- **Node.js** ≥ 18  
- **Saddle** installed and **`saddle serve`** reachable (default `http://127.0.0.1:1995`)

```bash
cd /path/to/saddle
python -m pip install -e .
python -m saddle serve
# another terminal:
curl -s http://127.0.0.1:1995/health
```

## Install (local checkout)

```bash
cd saddle/plugins/openclaw-plugin
node bin/install.js
```

The installer merges `~/.openclaw/openclaw.json`: adds this folder to `plugins.load.paths`, allows plugin id **`saddle-ai-openclaw`**, sets **`plugins.slots.contextEngine`**, and writes `plugins.entries[saddle-ai-openclaw].config`.

Restart OpenClaw after install (e.g. `openclaw gateway restart`).

## Install via npx (after npm publish)

If you publish `@saddle/openclaw-plugin` to npm:

```bash
npx --yes --package @saddle/openclaw-plugin saddle-openclaw-install
```

Alternatively, global install:

```bash
npm install -g @saddle/openclaw-plugin
saddle-openclaw-install
```

## Manual `openclaw.json` snippet

See [examples/openclaw.sample.json](./examples/openclaw.sample.json). Replace the plugin `paths` entry with the **absolute path** to this package on disk.

## Run pipeline (`saddle run`) from OpenClaw

The context-engine plugin handles **memory** only. To trigger the same pipeline as **`saddle run`** without a separate terminal:

1. **HTTP (recommended)** — `POST` to **`{baseUrl}/api/v1/pipeline/run`** with JSON body `{ "requirement": "...", "mode": "fast", "project_root": "/abs/path/to/repo" }` (see [PLUGIN_HTTP.md](../../docs/PLUGIN_HTTP.md)). You can ask the agent to call this URL when `baseUrl` matches your `saddle serve` instance.

2. **CLI helper** — from any shell with the same Node version:

   ```bash
   SADDLE_PROJECT_ROOT=/abs/path/to/repo node bin/run-once.js "your requirement" fast
   ```

   Or after `npm install -g @saddle/openclaw-plugin` (if published): `saddle-run-once "your requirement" fast`.

OpenClaw does not currently register a second plugin entry for “tools” in this package; use HTTP or `run-once.js` unless your host documents `registerTool`.

## Configuration keys (`plugins.entries["saddle-ai-openclaw"].config`)

| Key | Default | Description |
|-----|---------|-------------|
| `baseUrl` | `http://127.0.0.1:1995` | `saddle serve` origin (no trailing slash) |
| `userId` | `saddle-user` | Stored on each memory row |
| `groupId` | `saddle-default-group` | Scope shared memory |
| `topK` | `5` | Max hits per assemble |
| `memoryTypes` | `["episodic_memory"]` | Types kept for forward compatibility |
| `retrieveMethod` | `hybrid` | Ignored by Saddle backend (reserved) |

## HTTP contract

[Saddle `docs/PLUGIN_HTTP.md`](../../docs/PLUGIN_HTTP.md)

## Development

```bash
npm test
```

## License

Same as the parent Saddle project (MIT unless otherwise stated).
