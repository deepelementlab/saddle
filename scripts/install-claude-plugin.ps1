$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$plugin = Join-Path $root "plugins\claude-code-plugin"

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  throw "claude command not found. Install Claude Code CLI first."
}

Write-Host "Installing Saddle Claude plugin from $plugin"
claude plugin install $plugin --scope user
Write-Host "Done. Default SADDLE_BASE_URL is http://127.0.0.1:1995"
