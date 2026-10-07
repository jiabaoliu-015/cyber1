#!/bin/sh
# Stage the maintenance artefact the injectable `ping` can reach, then start both
# services: the telnet console (the vuln) and the OTA firmware endpoint (how
# Isaac's RE binary is handed out).
#
# ONE artefact lives in /opt/maint/rtr-01.snapshot. It holds the flag AND the
# firmware URL joined into a SINGLE whitespace-free token, so that a single
# `ping $(cat rtr-01.snapshot)` echoes BOTH back in the "unknown host" line. That
# way a player cannot grab the flag and miss the firmware: they arrive together.
# (No spaces or shell metacharacters in the value, so it substitutes cleanly.)
set -e
: "${FLAG:=CITS3006{24n4CBiT2K}}"
: "${FLAG_PATH:=/opt/maint/rtr-01.snapshot}"
: "${FW_PORT:=8081}"
: "${FW_TOKEN:=changeme}"
: "${FW_FILE:=/srv/acc-rtr01-fw.elf}"

MAINT_DIR="$(dirname "$FLAG_PATH")"
mkdir -p "$MAINT_DIR"

# flag + firmware URL in one token. ROUTER-HOST is a placeholder the player swaps
# for the address they are telnetting to.
echo "${FLAG}::ota-firmware::http://ROUTER-HOST:${FW_PORT}/fw/${FW_TOKEN}/acc-rtr01-fw.elf" \
    > "$FLAG_PATH"
chmod 644 "$FLAG_PATH"

# serve the firmware (Isaac's RE binary) at the secret path only
FW_PORT="$FW_PORT" FW_TOKEN="$FW_TOKEN" FW_FILE="$FW_FILE" \
    python3 /app/fw_server.py &

exec python3 /app/telnet_server.py
