#!/bin/sh
set -e

echo "Installing dependencies..."
uv sync

echo "Building Tailwind CSS..."
uv run python manage.py tailwind build

echo "Applying migrations..."
uv run python manage.py migrate

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Build complete."
