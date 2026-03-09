#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "Cleaning previous build"
"$SCRIPT_DIR/clean_release.sh"

echo "Running fresh release build"
"$SCRIPT_DIR/build_release.sh"