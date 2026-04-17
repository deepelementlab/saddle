#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/plugins/claude-code-plugin"

npm pack
echo "Packed claude plugin tarball. Publish through your GitHub/marketplace flow."
