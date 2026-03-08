#!/bin/sh
set -e

echo "Cleaning migrations and SQLite databases..."

# Delete migration files (except __init__.py) and ignore .venv
find . -type f -path "*/migrations/[0-9]*.py" -not -path "./.venv/*" -print -delete

# Delete SQLite databases and ignore .venv
find . -type f -name "*.sqlite3" -not -path "./.venv/*" -print -delete

echo "Cleanup complete. Run migrations again."