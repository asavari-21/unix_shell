#!/bin/sh
#
# This script is used to run your program on CodeCrafters
#
# This runs after .codecrafters/compile.sh
#
# Learn more: https://codecrafters.io/program-interface

set -e # Exit on failure
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

exec uv run --quiet -m app.main "$@"