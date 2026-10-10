#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Python 3.9 or newer is required.' >&2
    exit 1
fi
exec python3 -B "$ROOT/web/app.py" "$@"
