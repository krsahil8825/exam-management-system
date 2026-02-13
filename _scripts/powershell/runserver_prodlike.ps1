# runserver_prodlike.ps1
# Run Django in production-like mode (Windows)

$ErrorActionPreference = "Stop"

Write-Host "Starting Django in production-like mode..."

$env:DEBUG = "False"
$env:ENV = "development"

uv run python manage.py runserver --insecure --noreload
