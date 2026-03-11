#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

if [ "${1:-}" != "--yes" ]; then
	echo "Refusing to run without confirmation"
	echo "Usage: _scripts/shell/reset_dev_data.sh --yes"
	exit 1
fi

if [ "${ENV:-development}" = "production" ] || [ "${DB_ENGINE:-sqlite}" = "mysql" ]; then
	echo "Refusing to reset data in production/mysql mode"
	exit 1
fi

echo "Deleting app migration files"
find accounts communication errors exams workflow -type f -path "*/migrations/[0-9]*.py" -print -delete

if [ -d "_data" ]; then
	echo "Deleting local sqlite data"
	find _data -type f -name "*.sqlite3" -print -delete
fi

echo "Deleting media files except .gitkeep"
find media -type f ! -name ".gitkeep" -delete

echo "Deleting folders inside media"
find media -mindepth 1 -type d -empty -delete

echo "Reset complete"