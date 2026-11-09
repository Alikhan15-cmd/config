#!/usr/bin/env bash
set -e

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ $# -eq 0 ]; then
    "$PYTHON_BIN" -m src.main --config config.json
elif [ "$1" = "test" ]; then
    "$PYTHON_BIN" -m unittest discover -s tests -p "test_*.py" -v
else
    "$PYTHON_BIN" "$@"
fi
