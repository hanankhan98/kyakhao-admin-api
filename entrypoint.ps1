#Requires -Version 5.1
# Windows PowerShell equivalent of entrypoint.sh

$ErrorActionPreference = "Stop"

# Set PYTHONPATH to include Admin_api
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$adminApiPath = Join-Path $scriptDir "Admin_api"
$env:PYTHONPATH = "$adminApiPath;$env:PYTHONPATH"

Write-Host "Running migrations..." -ForegroundColor Cyan
python -m alembic upgrade head

Write-Host "Starting server..." -ForegroundColor Green
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
