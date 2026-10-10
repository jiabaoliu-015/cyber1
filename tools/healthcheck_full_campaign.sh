#!/usr/bin/env bash
# Runtime health surface for the complete local A→E demonstration path.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
"$ROOT/containers/comms/scripts/healthcheck.sh"
for item in 'compose-shift_scheduler-1 SHIFT_SCHEDULER' 'compose-local_control_service-1 LOCAL_CONTROL_SERVICE'; do
  set -- $item
  for _ in $(seq 1 15); do
    status=$(docker inspect -f '{{.State.Health.Status}}' "$1" 2>/dev/null || true)
    [ "$status" = healthy ] && break
    sleep 1
  done
  test "$status" = healthy || { echo "$2 container is not healthy" >&2; exit 1; }
done
docker run --rm --entrypoint /opt/suseid/maintenance_utility cits3006-maintenance_utility-handoff --healthcheck >/dev/null
"$ROOT/tools/healthcheck_late_campaign.sh"
printf 'Full campaign health check: PASS\n'
