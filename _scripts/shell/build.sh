#!/bin/sh
set -e

# Sync Python dependencies
uv sync

# Apply database migrations
uv run python manage.py migrate

# Collect static files for production
uv run python manage.py collectstatic --noinput
