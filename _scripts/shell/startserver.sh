# runserver.ps1
# Start the ASGI server using Uvicorn

$ErrorActionPreference = "Stop"

uv run uvicorn exam_management_system.asgi:application `
    --host 127.0.0.1 `
    --port 8000
