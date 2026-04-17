#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python -m pip install -e .

echo "Starting Saddle memory API on http://127.0.0.1:1995 ..."
nohup saddle serve --host 127.0.0.1 --port 1995 >/tmp/saddle-api.log 2>&1 &
sleep 1

curl -fsS http://127.0.0.1:1995/health || (echo "health check failed" && exit 1)

echo "Install plugins:"
echo "  bash scripts/install-claude-plugin.sh"
echo "  bash scripts/install-openclaw-plugin.sh"
