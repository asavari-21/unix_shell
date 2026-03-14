#!/bin/sh
#
# Use this script to run your program LOCALLY.
#
# Note: Changing this script WILL NOT affect how CodeCrafters runs your program.
#
# Learn more: https://codecrafters.io/program-interface

set -e # Exit on failure
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

exec uv run --quiet -m app.main "$@"
