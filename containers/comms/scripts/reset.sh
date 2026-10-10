#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ─── Clean slate ───────────────────────────────────────────────────────────────
# Compose bind mounts may leave a root-owned SQLite file; remove it through a
# short-lived container so reset remains usable by the non-root lab operator.
cd "${ROOT}"
docker compose down 2>/dev/null || true
docker run --rm -v "${ROOT}/../gateway/data:/data" alpine:3.20 sh -c 'rm -f /data/webapp.db' >/dev/null
rm -f "${ROOT}/data/handoff.conf.bak"

# ─── Regenerate Comms Relay/Uplink artefacts ───────────────────────────────────────
if [ -f "${ROOT}/scripts/regenerate_auth_service.py" ]; then
    python3 "${ROOT}/scripts/regenerate_auth_service.py"
fi

# Restart services via this slice's Docker Compose file.
cd "${ROOT}"
docker compose down 2>/dev/null || true
docker compose up -d --build

echo "Slice B reset complete. Services running:"
docker ps --filter "name=coriolis-(webapp|comms_relay-uplink|station_ssh)" --format "{{.Names}} {{.Status}}"