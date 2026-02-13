#!/bin/sh
set -e

echo "Cleaning migrations and SQLite databases..."

# Delete migration files (except __init__.py)
find . -path "*/migrations/[0-9]*.py" -type f -print -delete

# Delete SQLite databases
find . -name "*.sqlite3" -type f -print -delete

echo "Cleanup complete. Run migrations again."
