#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v docker >/dev/null 2>&1; then
  cd "$ROOT"
  # The container creates SQLite fixtures as root; remove them from a short-lived
  # project container so reset is repeatable for an unprivileged host user.
  docker compose run --rm --no-deps --entrypoint sh webapp -c 'rm -f /app/data/webapp.db' >/dev/null
  docker compose restart webapp >/dev/null
  echo "Slice A reset complete."
else
  rm -f "$ROOT/data/webapp.db"
  echo "Database removed. Restart the Crew Portal app to recreate fixtures."
fi
