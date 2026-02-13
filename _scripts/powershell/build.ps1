# build.ps1
# Production build script (Windows)

$ErrorActionPreference = "Stop"

Write-Host "Installing dependencies..."
uv sync

Write-Host "Building Tailwind CSS..."
uv run python manage.py tailwind build

Write-Host "Applying migrations..."
uv run python manage.py migrate

Write-Host "Collecting static files..."
uv run python manage.py collectstatic --noinput

Write-Host "Build complete."
