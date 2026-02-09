#!/bin/sh
set -e

# Start the ASGI server using Uvicorn
# Exposes the application on all network interfaces
# Intended for production or containerized environments

uv run uvicorn exam_management_system.asgi:application \
    --host 0.0.0.0 \
    --port 8000
