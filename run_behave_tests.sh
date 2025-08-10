#!/usr/bin/env bash
set -e

# Install test dependencies
pip install -r requirements-test.txt

# Always set PYTHONPATH to the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$PROJECT_ROOT"

# Run behave tests with any arguments
behave "$@"
