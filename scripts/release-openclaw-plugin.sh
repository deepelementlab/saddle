#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/plugins/openclaw-plugin"

npm pack
echo "Packed openclaw plugin tarball. Use npm publish if ready."
