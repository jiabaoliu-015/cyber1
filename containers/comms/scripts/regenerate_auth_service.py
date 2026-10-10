"""
Regenerate all Comms Relay/Uplink/Station SSH artefacts for Slice B.

This script ensures a clean baseline on each reset.
"""

import hashlib
import os
import sys
from datetime import datetime

ROOT = os.environ.get("SLICE_B_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(ROOT, "data")

RELAY_AUTH_USERNAME = "station_crew"
RELAY_AUTH_TOKEN_SECRET = "uplink-auth-token-01"
RELAY_AUTH_CHALLENGE_KEY = "maintenance-label"

# Generate stable challenge for Station SSH handoff
# The player will derive this correctly after noticing the auth flaw
combined = (os.environ.get("RELAY_AUTH_TOKEN_SECRET", "uplink-auth-token-01") + RELAY_AUTH_USERNAME).encode()
STATION_SSH_SSH_CHALLEGE = hashlib.sha256(combined).hexdigest()[:8]

# ─── Write Station SSH configuration ────────────────────────────────────────────────
station_ssh_conf = f"""# Station SSH baseline configuration (generated from Uplink auth fix)
STATION_SSH_HOST="{os.environ.get('STATION_SSH_HOST', 'station_ssh.internal')}"
STATION_SSH_USER={RELAY_AUTH_USERNAME!r}
STATION_SSH_SSH_CHALLEGE={STATION_SSH_SSH_CHALLEGE}
STATION_SSH_PATH="/uplink/handoff"
# Deterministic baseline: reset must not dirty a collaborator's worktree.
GENERATED_BY="scripts/regenerate_auth_service.py"
"""

with open(os.path.join(DATA_DIR, "handoff.conf"), "w") as f:
    f.write(station_ssh_conf)

print(f"Uplink artefacts regenerated. Station SSH challenge token: {STATION_SSH_SSH_CHALLEGE}")
print(f"Station SSH config written to: {DATA_DIR}/handoff.conf")