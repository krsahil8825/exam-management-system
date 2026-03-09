#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "Cleaning collected static files"
uv run python manage.py collectstatic --clear --noinput

echo "Removing Tailwind build cache"
if [ -d "theme/static/css/dist" ]; then
	rm -rf theme/static/css/dist
fi

if [ -d "theme/static_src/node_modules" ]; then
	rm -rf theme/static_src/node_modules
fi

echo "Removing Python cache files"
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "Cleaning temporary files"
if [ -d ".pytest_cache" ]; then
	rm -rf .pytest_cache
fi

if [ -d ".mypy_cache" ]; then
	rm -rf .mypy_cache
fi

echo "Removing staticfiles directory if it exists"
if [ -d "staticfiles" ]; then
    rm -rf staticfiles
fi

echo "Release cleanup completed"