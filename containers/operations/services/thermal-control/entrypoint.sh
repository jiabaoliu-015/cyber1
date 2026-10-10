#!/usr/bin/env bash
# entrypoint — start hvac-lab: sshd (player entry) + localhost FastAPI backend.
# Runtime flag comes from compose .env (see flags/init_flags.sh).
set -euo pipefail

# Host keys (ephemeral unless a volume is mounted on /etc/ssh).
ssh-keygen -A >/dev/null 2>&1 || true

mkdir -p /var/run/sshd /var/run/hvac /app/data
chown root:engineer /var/run/hvac
chmod 0710 /var/run/hvac

# Cron drops the container environment. Keep the runtime flag root-only and
# read it only in the root worker.
umask 077
printf '%s\n' "${HVAC_FLAG:?HVAC_FLAG must be set at runtime}" > /var/run/hvac/worker.env
chmod 0600 /var/run/hvac/worker.env
printf '\n' > /var/run/hvac/input
chown root:engineer /var/run/hvac/input
chmod 0660 /var/run/hvac/input
mkdir -p /etc/cron.d
printf '# hvac-lab root diagnostic job\n* * * * * root /opt/hvac/process_job run\n# Lowpriv-writable input is /var/run/hvac/input\n' > /etc/cron.d/hvac-diagnostic
chmod 0644 /etc/cron.d/hvac-diagnostic
chmod 0755 /opt/hvac/process_job

# Drop the flag from the player-facing API and all children; only cron reads
# the root-only runtime file. Cron itself does not inherit the compose flag.
unset HVAC_FLAG
export -n HVAC_FLAG
/usr/sbin/cron

/usr/sbin/sshd
echo "hvac-lab: sshd up (ssh default@localhost -p 2223), backend on 127.0.0.1:8081"

exec env -u HVAC_FLAG uvicorn hvac_app.app:app --host 127.0.0.1 --port 8081
