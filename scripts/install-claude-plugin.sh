#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$ROOT_DIR/plugins/claude-code-plugin"

echo "Installing Saddle Claude Code plugin from: $PLUGIN_DIR"
if ! command -v claude >/dev/null 2>&1; then
  echo "claude command not found. Install Claude Code CLI first."
  exit 1
fi

claude plugin install "$PLUGIN_DIR" --scope user || true
echo "Done. Set SADDLE_BASE_URL if needed (default http://127.0.0.1:1995)."
