# startserver.ps1
# Start ASGI server using Uvicorn

$ErrorActionPreference = "Stop"

Write-Host "Starting ASGI server..."

uv run uvicorn exam_management_system.asgi:application `
    --host 127.0.0.1 `
    --port 8000 `
    --workers 4
