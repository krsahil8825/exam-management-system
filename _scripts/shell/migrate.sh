#!/bin/sh
set -e

echo "Creating migrations..."
uv run python manage.py makemigrations

echo "Applying migrations..."
uv run python manage.py migrate

echo "Migrations completed successfully."
