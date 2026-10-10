#!/usr/bin/env bash
# healthcheck: sshd (player entry) + localhost backend.
set -euo pipefail

# 1. Backend health — prefer in-container probe when compose is available
#    (web is localhost-only and not host-published by design).
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  if docker compose ps --status running 2>/dev/null | grep -q hvac; then
    docker compose exec -T hvac python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=3).read().decode())'
    printf '\n'
  else
    python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=3).read().decode())'
    printf '\n'
  fi
else
  python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=3).read().decode())'
  printf '\n'
fi

# 2. SSH entry probe (host port 2223 -> container 22).
if command -v ssh-keyscan >/dev/null 2>&1; then
  ssh-keyscan -p 2223 -T 5 127.0.0.1 >/dev/null 2>&1 \
    && echo "ssh: 127.0.0.1:2223 open" \
    || { echo "ssh: 127.0.0.1:2223 not reachable (is the stack up?)" >&2; exit 1; }
elif command -v nc >/dev/null 2>&1; then
  nc -z -w 5 127.0.0.1 2223 && echo "ssh: 127.0.0.1:2223 open"
else
  echo "ssh: skipping port probe (no ssh-keyscan/nc)"
fi
