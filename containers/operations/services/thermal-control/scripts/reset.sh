#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if command -v docker >/dev/null 2>&1 && docker compose -f "$ROOT/docker-compose.yml" ps -q hvac | grep -q .; then
  docker compose -f "$ROOT/docker-compose.yml" exec -T hvac sh -c 'printf "\n" > /var/run/hvac/input; rm -f /var/run/hvac/maintenance_report.txt'
  echo "HVAC lab reset complete (input cleared, report removed; runtime flag retained)."
else
  echo "HVAC lab container is not running; nothing to reset." >&2
  exit 1
fi
