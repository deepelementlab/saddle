---
description: Run the default Saddle pipeline (same as saddle run) via saddle serve API
arguments:
  - name: requirement
    description: What to implement or specify (pipeline requirement text)
    required: true
  - name: mode
    description: Optional mode name (e.g. fast, default); can use --mode instead
    required: false
---

Runs **`saddle run`** through **`POST /api/v1/pipeline/run`** on **`SADDLE_BASE_URL`** (requires **`saddle serve`**).

**Invoke**

```bash
node "${CLAUDE_PLUGIN_ROOT}/commands/scripts/run-pipeline.js" "$ARGUMENTS"
```

**Ways to pass input**

1. One string: the requirement text, with optional suffix **`--mode fast`** (or another mode name).
2. Two tokens: **`"requirement text"`** **`modeName`** (mode must be a single identifier-like token).

Examples for `$ARGUMENTS`:

- `Add login form --mode fast`
- `Refactor the API` `fast` (two arguments)

**After the command**: summarize whether the pipeline succeeded (`ok` / `result.stages`), highlight any stage failures, and suggest next steps. If the user sees HTTP errors, tell them to run **`python -m saddle serve`** from the project root and retry.

**Fallback**: the script may run **`python -m saddle run`** locally if the API is unreachable; set **`SADDLE_PYTHON`** to the correct interpreter if needed.
