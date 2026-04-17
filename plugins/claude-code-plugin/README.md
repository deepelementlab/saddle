# Saddle Claude Code Plugin

Hooks-based memory integration for Claude Code.

## Hook Flow

- `SessionStart` -> load recent memory context
- `UserPromptSubmit` -> retrieve related memories and inject prompt
- `Stop` -> extract transcript turn and save to memory API
- `SessionEnd` -> save local session summary

## Local Install

```bash
claude plugin install /absolute/path/to/saddle/plugins/claude-code-plugin --scope user
```

Default backend: `http://127.0.0.1:1995` via `SADDLE_BASE_URL`.
