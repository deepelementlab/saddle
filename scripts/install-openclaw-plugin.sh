#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$ROOT_DIR/plugins/openclaw-plugin"

echo "Installing Saddle OpenClaw plugin from: $PLUGIN_DIR"
if ! command -v node >/dev/null 2>&1; then
  echo "node not found"
  exit 1
fi

node "$PLUGIN_DIR/bin/install.js"
echo "Then run: openclaw gateway restart"
