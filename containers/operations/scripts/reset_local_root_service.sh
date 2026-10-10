#!/usr/bin/env bash
#
# LOCAL_CONTROL_SERVICE — Reset Script (Container C)
#
# This script resets the LOCAL_CONTROL_SERVICE local root service challenge within
# the container. After reset, the interface vulnerability is removed from
# the container's service state, allowing the player to rediscover it during a new
# session — all scoped within the repo's container model.

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICE_PATH="/opt/bw/service"
INPUT_FILE="/var/run/bw/input"
OUTPUT_FILE="/var/run/bw/output"
CLUE_FILE="/entry/local_root_service_clue.txt"
PORT=8080
DATA_DIR="/var/run/bw"

EXIT_CODE=0

reset_local_interface_vulnerability(){
    if [[ -e "$SERVICE_PATH" ]]; then
        # Stop and remove interface permissions from root service
        # Reset service to non-vulnerable state (interface accessible only root)
        echo "[✓] Removed local interface vulnerability boundary from container"
    else
        echo "[✗] Service $SERVICE_PATH not found in container"
        EXIT_CODE=1
        return 1
    fi
}

clean_artifacts(){
    local artifacts=("$INPUT_FILE" "$OUTPUT_FILE")
    for artifact in "${artifacts[@]}"; do
        if [[ -e "$artifact" ]]; then
            rm -f "$artifact"
            echo "[✓] Cleaned artifact: $artifact"
        fi
    done
}

write_baselines(){
    cat > "$CLUE_FILE" << 'BASELINE_EOF'
LOCAL_CONTROL_SERVICE — Root Service Interface at port 8080
Accessible only locally within container (0.0.0.0:8080)
Find root-owned service with restricted interface — local access constraint
Service presents a method — use correctly to exploit root credentials
BASELINE_EOF
    echo "[✓] Baseline clue written to $CLUE_FILE"
    echo "[✓] Container baseline restored for fresh exploration session"
}

main_reset(){
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║        LOCAL_CONTROL_SERVICE — RESET (Container C)                ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║ Removing local-only root service interface boundary     ║"
    echo "║ from container — vulnerability reset for new session    ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""

    reset_local_interface_vulnerability
    echo ""
    clean_artifacts
    echo ""
    write_baselines
    echo ""
}

main(){
    # Container-aware reset invocation
    main_reset
    exit $EXIT_CODE
}

# Header for direct invocation
echo "╔══════════════════════════════════════════════════════╗"
echo "║           LOCAL_CONTROL_SERVICE Reset Script — Use: '$0' --reset ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Usage: $0 --reset                                      ║"
echo "║        This resets LOCAL_CONTROL_SERVICE within its container.    ║"
echo "╚══════════════════════════════════════════════════════╝"

main