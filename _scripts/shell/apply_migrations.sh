#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "Creating migrations"
uv run python manage.py makemigrations

echo "Applying migrations"
uv run python manage.py migrate --noinput

echo "Migrations are up to date"
