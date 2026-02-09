#!/bin/sh
set -e

# Run Django in production-like mode for local testing
# - DEBUG disabled
# - Development environment
# - Static files served via --insecure
# - Auto-reload disabled

export DEBUG=False
export ENV=development

uv run python manage.py runserver --insecure --noreload
