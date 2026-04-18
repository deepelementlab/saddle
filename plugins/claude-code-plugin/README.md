# Saddle Claude Code Plugin

Hooks-based integration with the **Saddle Memory API** running on **`saddle serve`** (default `http://127.0.0.1:1995`). No cloud API key: storage is local JSONL under `SADDLE_MEMORY_DIR` (see server docs).

## What it does

| Hook | Behavior |
|------|----------|
| `SessionStart` | Health check + brief memory count for this project (`group_id` derived from cwd) |
| `UserPromptSubmit` | Keyword search → inject `additionalContext` for the model |
| `Stop` | Read latest transcript turn → batch `POST /api/v1/memories` |
| `SessionEnd` | No-op (persistence happens on **Stop**) |

Slash commands (if supported by your Claude Code build): **`/saddle:help`**, **`/saddle:modes`**, **`/saddle:validate`**, **`/saddle:run`** — see `commands/*.md`.

## Run pipeline (`saddle run`)

**`/saddle:run`** runs the same default pipeline as **`python -m saddle run`**, via **`POST /api/v1/pipeline/run`** (see [PLUGIN_HTTP.md](../../docs/PLUGIN_HTTP.md)). It uses **`CLAUDE_PROJECT_DIR`** / **`SADDLE_CWD`** (or cwd) as **`project_root`**. If the API is unreachable, the script may fall back to **`python -m saddle run`** (set **`SADDLE_PYTHON`** if needed).

## Prerequisites

1. **Node.js** ≥ 18 (hooks run as `node …` scripts).
2. **`saddle serve`** running while you use the plugin, from a directory that matches how you develop (API uses `cwd` of the server for modes; memory file lives under `SADDLE_MEMORY_DIR`, usually `\<cwd\>/.saddle/memory`).

```bash
cd yourRepo   # contains .saddle/modes if you use modes
python -m saddle serve
```

## Environment (optional)

| Variable | Purpose |
|----------|---------|
| `SADDLE_BASE_URL` | Default `http://127.0.0.1:1995` |
| `SADDLE_USER_ID` | Default `saddle-user` |
| `SADDLE_GROUP_ID` | Override group; default is `claude-code:<normalized cwd>` |
| `SADDLE_DISABLE` | Set to `1` to skip hooks |
| `SADDLE_DEBUG` | Set to `1` for stderr debug lines |

You can also place a `.env` file beside `plugin.json` (plugin root) with the same keys.

## Install — local path

```bash
claude plugin install /absolute/path/to/saddle/plugins/claude-code-plugin --scope user
```

## Install — Git marketplace (after you push this repo)

Replace `OWNER/REPO` and subtree path if the plugin lives under `saddle/plugins/claude-code-plugin`:

```bash
claude plugin marketplace add https://github.com/OWNER/REPO
claude plugin install saddle@saddle --scope user
```

Exact marketplace identifier follows Anthropic’s docs; align `plugin.json` `name` (**`saddle`**) with the marketplace package name.

## Verify

```bash
curl -s "${SADDLE_BASE_URL:-http://127.0.0.1:1995}/health"
```

Re-run **`/saddle:help`** inside Claude Code.

## HTTP contract

[Saddle `docs/PLUGIN_HTTP.md`](../../docs/PLUGIN_HTTP.md)

## Development

```bash
cd saddle/plugins/claude-code-plugin
npm test
```

## npm pack (artifact)

```bash
npm pack
# produces saddle-claude-code-0.1.0.tgz — optional distribution
```

## License

Same as the parent Saddle project (MIT unless otherwise stated).
