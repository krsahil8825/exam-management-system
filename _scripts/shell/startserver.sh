#!/bin/sh
set -e

echo "Starting ASGI server..."

uv run uvicorn exam_management_system.asgi:application \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
