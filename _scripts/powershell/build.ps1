# build.ps1
# Build steps for the Django application

$ErrorActionPreference = "Stop"

# Sync Python dependencies
uv sync

# Apply database migrations
uv run python manage.py migrate

# Collect static files for production
uv run python manage.py collectstatic --noinput
