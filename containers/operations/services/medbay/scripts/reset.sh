#!/usr/bin/env bash
set -euo pipefail
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
  docker compose -p medbay-standalone -f "$DIR/compose.yml" down
fi
rm -f "$DIR/artifact3_binary"
printf 'Medbay standalone state reset (sessions and recovery codes reset on next start).\n'
