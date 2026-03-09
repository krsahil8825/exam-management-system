#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export SECRET_KEY="${SECRET_KEY:-dev-only-insecure-key}"
export DEBUG="${DEBUG:-True}"
export ENV="${ENV:-development}"
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-127.0.0.1,localhost}"
export DB_ENGINE="${DB_ENGINE:-sqlite}"
export EMAIL_BACKEND="${EMAIL_BACKEND:-django.core.mail.backends.console.EmailBackend}"
export DEFAULT_FROM_EMAIL="${DEFAULT_FROM_EMAIL:-noreply@localhost}"

PORT="${PORT:-8000}"
HOST="${HOST:-localhost}"

echo "Starting development server on ${HOST}:${PORT}"
exec uv run python manage.py runserver "${HOST}:${PORT}"
