#!/usr/bin/env bash
# Start the real cron daemon, localhost API backend, and player-facing sshd.
set -euo pipefail

ssh-keygen -A >/dev/null 2>&1 || true
mkdir -p /var/run/sshd /var/run/power /app/data "${PWR_ASSET_DIR:-/app/generated-assets}"

# Debian cron does not inherit container environment; expose only the hard flag
# required by the root cron job through a root-readable runtime file.
umask 077
printf 'PWR_FLAG_HARD=%s\nPWR_RUN_DIR=%s\n' "${PWR_FLAG_HARD:?PWR_FLAG_HARD is required}" "${PWR_RUN_DIR:-/var/run/power}" > /run/power-runtime.env
chmod 0600 /run/power-runtime.env
chown root:root /run/power-runtime.env
chmod 0755 /var/run/power

# Build per-container artifacts from bundled source into writable storage.
python3 scripts/build_image.py --output "${PWR_ASSET_DIR:-/app/generated-assets}/astronaut_stego.jpeg"
python3 scripts/build_agent_binary.py --output "${PWR_ASSET_DIR:-/app/generated-assets}/agent_firmware.bin"

# cron reads /etc/cron.d on startup; explicitly start it rather than simulating
# its job from an HTTP request handler.
cron
/usr/sbin/sshd
echo "power-lab: sshd and cron up; backend on 127.0.0.1:8082"
exec uvicorn power_app.app:app --host 127.0.0.1 --port 8082
