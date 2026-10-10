#!/usr/bin/env bash
#
# MAINTENANCE_UTILITY — Reset Script (Container A)
#
# This script resets the MAINTENANCE_UTILITY SUID privilege escalation challenge within
# the container. After reset, the vulnerability is removed from the
# container's state, allowing the player to rediscover it during a new
# session.
#
# All operations occur inside the MAINTENANCE_UTILITY container — no direct host system access.

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICE_PATH="/opt/suseid/maintenance_utility"
OUTPUT_FILE="/var/run/suseid/output"
ARTIFACT_FILE="/srv/station_crew/exploit_evidence"
CLUE_FILE="/entry/suid_route_clue.txt"

EXIT_CODE=0

reset_suid_bit(){
    if [[ -e "$SERVICE_PATH" ]]; then
        # Remove SUID bit — this is the vulnerability itself
        chmod -s "$SERVICE_PATH"
        echo "[✓] Removed SUID-root privilege — vulnerability reset in container"
    else
        echo "[✗] Container missing service at $SERVICE_PATH"
        EXIT_CODE=1
        return 1
    fi
}

clean_artifacts(){
    local artifacts=("$OUTPUT_FILE" "$ARTIFACT_FILE")
    for artifact in "${artifacts[@]}"; do
        if [[ -e "$artifact" ]]; then
            rm -f "$artifact"
            echo "[✓] Cleaned artifact: $artifact"
        fi
    done
}

write_baselines(){
    # Ensure baseline files exist for new session
    cat > "$CLUE_FILE" << 'BASELINE_EOF'
MAINTENANCE_UTILITY SUID-root service located at /opt/suseid/maintenance_utility
Enumerate with: find / -perm -4000
SUID preserves root permissions when invoked by station_crew
Test with arguments to trigger root operations
BASELINE_EOF
    echo "[✓] Baseline clue written to $CLUE_FILE"
    echo "[✓] Baseline state restored for new discovery session"
}

main_reset(){
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║         MAINTENANCE_UTILITY — RESET (Container A)                      ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo ""

    # Step 1: Remove vulnerability (SUID bit)
    reset_suid_bit
    echo ""

    # Step 2: Clean prior exploitation artifacts
    clean_artifacts
    echo ""

    # Step 3: Restore baseline
    write_baselines

    echo ""
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
}

# Override with container-aware reset
main(){
    # In container context, we run reset as the service user
    main_reset
    exit $EXIT_CODE
}

# Header for direct invocation
echo "╔══════════════════════════════════════════════════════╗"
echo "║          MAINTENANCE_UTILITY Reset Script — Use: '$0' --reset       ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Usage: $0 --reset                                      ║"
echo "║        This resets MAINTENANCE_UTILITY within its container.            ║"
echo "╚══════════════════════════════════════════════════════╝"

main