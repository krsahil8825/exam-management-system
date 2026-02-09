# runserver_prodlike.ps1
# Run Django in production-like mode for local testing

$ErrorActionPreference = "Stop"

$env:DEBUG = "False"
$env:ENV = "development"

uv run python manage.py runserver --insecure --noreload
