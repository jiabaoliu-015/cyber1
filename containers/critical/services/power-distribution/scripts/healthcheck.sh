#!/usr/bin/env bash
# healthcheck: sshd (player entry) + localhost backend.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
probe_backend() {
  python3 -c 'import json,urllib.request; r=urllib.request.urlopen("http://127.0.0.1:8082/health", timeout=4); data=json.load(r); assert r.status == 200 and data.get("status") == "ok", data; print(json.dumps(data))'
}

# 1. Backend health — prefer in-container probe when compose is available
#    (web is localhost-only and not host-published by design).
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  if (cd "$ROOT" && docker compose ps --status running 2>/dev/null | grep -q power); then
    (cd "$ROOT" && docker compose exec -T power python3 -c 'import json,urllib.request; r=urllib.request.urlopen("http://127.0.0.1:8082/health", timeout=4); data=json.load(r); assert r.status == 200 and data.get("status") == "ok", data; print(json.dumps(data))')
  else
    probe_backend
  fi
else
  probe_backend
fi

# 2. SSH entry probe (host port 2222 -> container 22).
if command -v ssh-keyscan >/dev/null 2>&1; then
  ssh-keyscan -p 2222 -T 5 127.0.0.1 >/dev/null 2>&1 \
    && echo "ssh: 127.0.0.1:2222 open" \
    || { echo "ssh: 127.0.0.1:2222 not reachable (is the stack up?)" >&2; exit 1; }
elif command -v nc >/dev/null 2>&1; then
  nc -z -w 5 127.0.0.1 2222 && echo "ssh: 127.0.0.1:2222 open"
else
  echo "ssh: skipping port probe (no ssh-keyscan/nc)"
fi
