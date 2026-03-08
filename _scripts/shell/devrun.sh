#!/bin/sh
set -e

echo "Starting Django development server..."

export SECRET_KEY=dev-secret-key-change-me
export DEBUG=True
export ENV=development
export ALLOWED_HOSTS=127.0.0.1,localhost
export DB_ENGINE=sqlite
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
export DEFAULT_FROM_EMAIL=noreply@localhost

uv run python manage.py runserver localhost:8000
