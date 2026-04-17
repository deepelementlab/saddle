$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python -m pip install -e .

Write-Host "Starting Saddle memory API on http://127.0.0.1:1995 ..."
Start-Process -FilePath "python" -ArgumentList "-m","uvicorn","saddle.memory_api.server:app","--host","127.0.0.1","--port","1995" -WindowStyle Hidden
Start-Sleep -Seconds 2

Invoke-RestMethod "http://127.0.0.1:1995/health" | Out-Null
Write-Host "Health check passed."
Write-Host "Next:"
Write-Host "  .\scripts\install-claude-plugin.ps1"
Write-Host "  .\scripts\install-openclaw-plugin.ps1"
