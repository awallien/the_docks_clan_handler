#!/usr/bin/env bash
set -euo pipefail

write_info() {
    printf '\033[36m%s\033[0m\n' "$1"
}

write_error() {
    printf '\033[31m%s\033[0m\n' "$1" >&2
}

write_success() {
    printf '\033[32m%s\033[0m\n' "$1"
}

if [ "$#" -eq 0 ]; then
    write_error "Usage: ./run.sh --cli, --bot, or both"
    printf 'Example: ./run.sh --cli --bot\n'
    exit 1
fi

PYTHON_BIN="${PYTHON:-python3}"
PYTHON_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [ "$PYTHON_VERSION" != "3.11" ]; then
    write_error "Python3.11 is required, but ${PYTHON_BIN} is Python ${PYTHON_VERSION}."
    write_error "Set PYTHON=/path/to/python3.11 or update your python3 executable."
    exit 1
fi

write_info "Auto-generating python files..."
if ! "$PYTHON_BIN" "util/osrs_api/hiscore_mdata_autogen.py"; then
    write_error "Error running hiscore_mdata_autogen.py. Exiting."
    exit 1
fi

write_info "Running main.py with arguments: $*"
"$PYTHON_BIN" "main.py" "$@"

write_success "All tasks completed successfully."