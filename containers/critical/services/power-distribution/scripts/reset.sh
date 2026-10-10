#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v docker >/dev/null 2>&1; then
  cd "$ROOT"
  if docker compose version >/dev/null 2>&1; then
    docker compose run --rm --no-deps --entrypoint sh power -c 'rm -f /var/run/power/input /var/run/power/reactor_report.txt /var/run/power/two_key_authorized' >/dev/null || true
    docker compose restart power >/dev/null || true
  else
    docker run --rm -v power-run:/var/run/power busybox sh -c 'rm -f /var/run/power/input /var/run/power/reactor_report.txt /var/run/power/two_key_authorized' >/dev/null || true
  fi
  echo "Power lab reset complete."
else
  rm -f /var/run/power/input /var/run/power/reactor_report.txt /var/run/power/two_key_authorized 2>/dev/null || true
  echo "Power state cleared. Restart the power service to recreate fixtures."
fi
