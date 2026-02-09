#!/bin/sh

# Delete Django migration files that start with digits (e.g. 0001_*.py)
# This script preserves __init__.py and only targets migration files.

find . -path "*/migrations/[0-9]*.py" -type f -print -delete
