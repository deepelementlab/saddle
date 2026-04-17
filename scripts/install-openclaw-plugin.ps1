$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$plugin = Join-Path $root "plugins\openclaw-plugin"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "node not found"
}

node (Join-Path $plugin "bin\install.js")
Write-Host "Then run: openclaw gateway restart"
