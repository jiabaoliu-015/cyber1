#!/usr/bin/env bash
# Deterministic local reset for the complete A→E demonstration path.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
# Slice A and B deliberately use the same Crew Portal container name. Remove a
# focused Slice A run before starting the combined Slice B stack.
docker compose -f "$ROOT/containers/gateway/docker-compose.yml" down --remove-orphans >/dev/null 2>&1 || true
docker compose -f "$ROOT/containers/comms/docker-compose.yml" down --remove-orphans >/dev/null 2>&1 || true
docker rm -f coriolis-webapp coriolis-crew_portal coriolis-comms_relay-uplink coriolis-station_ssh >/dev/null 2>&1 || true
"$ROOT/containers/comms/scripts/reset.sh"
docker build -t cits3006-maintenance_utility-handoff -f "$ROOT/containers/operations/compose/Dockerfile" "$ROOT/containers/operations"
docker compose -f "$ROOT/containers/operations/compose/compose_scheduled_job.yml" down -v --remove-orphans >/dev/null 2>&1 || true
docker compose -f "$ROOT/containers/operations/compose/compose_local_root_service.yml" down -v --remove-orphans >/dev/null 2>&1 || true
docker compose -f "$ROOT/containers/operations/compose/compose_scheduled_job.yml" up -d --build
docker compose -f "$ROOT/containers/operations/compose/compose_local_root_service.yml" up -d --build
a="$ROOT/tools/reset_late_campaign.sh"
"$a"
printf 'Full campaign reset complete: A/B, SHIFT_SCHEDULER, LOCAL_CONTROL_SERVICE and D/E fixtures are clean.\n'
