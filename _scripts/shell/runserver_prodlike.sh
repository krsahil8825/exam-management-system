#!/bin/sh
set -e

echo "Starting Django in production-like mode..."

export DEBUG=False
export ENV=development

uv run python manage.py runserver --insecure --noreload
