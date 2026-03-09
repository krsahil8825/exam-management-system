#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Production build should run with an explicit non-debug profile.
export ENV="${ENV:-production}"
export DEBUG="${DEBUG:-False}"

echo "Syncing dependencies"
uv sync

echo "Running deployment checks"
uv run python manage.py check --deploy

echo "Applying migrations"
"$SCRIPT_DIR/apply_migrations.sh"

echo "Building Tailwind CSS"
uv run python manage.py tailwind build

echo "Collecting static files"
uv run python manage.py collectstatic --noinput

echo "Release build completed"
