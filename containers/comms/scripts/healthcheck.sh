#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "============================================"
echo "Slice B Healthcheck - Comms Relay / Uplink / Station SSH"
echo "============================================"

# 1. Crew Portal health check (Slice A prerequisite)
echo ""
echo "[1/3] Checking Crew Portal service..."
CREW_PORTAL_STATUS="FAILED"
for _ in $(seq 1 15); do
    if CREW_PORTAL_STATUS=$(curl -fsS http://127.0.0.1:8080/health 2>/dev/null); then
        break
    fi
    sleep 1
done
echo "Crew Portal status: $CREW_PORTAL_STATUS"

if [ "$CREW_PORTAL_STATUS" = '{"status":"ok","service":"webapp"}' ]; then
    echo "✓ Crew Portal healthy"
else
    echo "✗ Crew Portal failed"
    exit 1
fi

# 2. Uplink TCP service health check
echo ""
echo "[2/3] Checking Uplink service (Comms Relay)..."

if python3 -c "import socket; socket.create_connection(('localhost', 5432)); print('LISTENING')" >/dev/null 2>&1; then
    echo "✓ Uplink TCP service is listening on port 5432"
    
    echo ""
    echo "[3/3] Testing Uplink auth state..."
    
    RESPONSE=$(python3 -c "
import socket, re
with socket.create_connection(('localhost', 5432)) as sock:
    sock.send(b'INFO\n')
    resp = sock.recv(4096).decode()
    challenge_present = 'challenge:' in resp and 'token' in resp.lower()
    match = re.search(r'challenge:\s*([a-f0-9]+)', resp)
    challenge = match.group(1) if match else 'simulated'
    
    sock.send(f'AUTH station_crew {challenge}\n'.encode())
    result = sock.recv(4096).decode()
    auth_success = 'authentication accepted' in result
    station_ssh_present = 'Station SSH' in result
    
    if auth_success and station_ssh_present:
        print('Auth FLAW confirmed: station_ssh material delivered')
    else:
        print('Auth test FAILED')
        print('INFO response excerpt:', resp[:300])
        print('AUTH result excerpt:', result[:300])
" 2>&1)
    
    echo "$RESPONSE"
    
    if echo "$RESPONSE" | grep -q "Auth FLAW confirmed"; then
        echo "✓ Uplink auth state confirmed - vulnerability present and exploitable"
        echo ""
        echo "============================================"
        echo "✓ All health checks PASSED"
        echo "============================================"
        exit 0
    else
        echo "✗ Uplink auth state issue detected"
        exit 1
    fi
else
    echo "✗ Uplink service not responding on port 5432"
    echo "Restart: docker compose up -d"
    exit 1
fi