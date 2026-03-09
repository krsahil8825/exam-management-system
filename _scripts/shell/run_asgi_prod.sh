#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export ENV="${ENV:-production}"
export DEBUG="${DEBUG:-False}"

# if OS is windows use 127.0.0.1 and if linux use 0.0.0.0 as default host
if [ "$(uname -s)" = "Linux" ]; then
  echo "Running on Linux"
  export HOST="${HOST:-0.0.0.0}"
else
  echo "Running on non-Linux OS"
  export HOST="${HOST:-127.0.0.1}"
fi
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-4}"

echo "Starting ASGI server on ${HOST}:${PORT} (workers=${WORKERS})"
exec uv run uvicorn exam_management_system.asgi:application \
  --host "$HOST" \
  --port "$PORT" \
  --workers "$WORKERS" \
  --proxy-headers
