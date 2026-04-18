---
description: Saddle plugin help and environment check
---

You are helping the user verify the **Saddle** Claude Code plugin.

**Requirements**

1. **`saddle serve`** must be running in the project (default `http://127.0.0.1:1995`).
2. Optional env vars (shell or `.env` next to this plugin): `SADDLE_BASE_URL`, `SADDLE_GROUP_ID`, `SADDLE_USER_ID`. Set `SADDLE_DISABLE=1` to turn hooks off.

**Check health**

```bash
curl -s "${SADDLE_BASE_URL:-http://127.0.0.1:1995}/health"
```

Explain that this plugin stores conversation snippets in the local Saddle Memory API (`POST /api/v1/memories`) and retrieves them on submit (`POST /api/v1/memories/search`). For HTTP details see the Saddle repo `docs/PLUGIN_HTTP.md`.

**Slash commands**

- `/saddle:help` — this help
- `/saddle:modes` — list mode names from the API
- `/saddle:validate` — validate the `default` mode (requires `python -m saddle` on PATH)
- `/saddle:run` — run the default pipeline (**`saddle run`**) via **`POST /api/v1/pipeline/run`** (requires **`saddle serve`**); see `commands/run.md`

Present a short status: if `curl` fails, tell the user to start `python -m saddle serve` from the project root.
