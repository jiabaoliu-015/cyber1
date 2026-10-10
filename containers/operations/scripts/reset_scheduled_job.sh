#!/usr/bin/env bash
#
# SHIFT_SCHEDULER — Reset Script (Container B)
#
# This script resets the SHIFT_SCHEDULER writable root scheduled job challenge within
# the container. After reset, the vulnerability is removed from the
# container's cron state, allowing the player to rediscover it during a new
# session — all scoped within the repo's container model.

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICE_PATH="/opt/shift_scheduler/process_job"
SCHEDULE_FILE="/etc/cron.d/shift_scheduler_job"
INPUT_FILE="/var/run/shift_scheduler/input"
OUTPUT_FILE="/var/run/shift_scheduler/output"
CLUE_FILE="/entry/scheduled_job_clue.txt"
DATA_DIR="/var/run/shift_scheduler"

EXIT_CODE=0

reset_schedule_vulnerability(){
    if [[ -e "$SCHEDULE_FILE" ]]; then
        # Remove root-owned schedule and set default permissions
        chmod 0o644 "$SCHEDULE_FILE" 2>/dev/null || true
        echo "[✓] Removed writable root-scheduled job boundary from container"
    else
        echo "[✗] Schedule file $SCHEDULE_FILE not found in container"
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
SHIFT_SCHEDULER — Root Scheduled Job located at /etc/cron.d/shift_scheduler_job
Inspect with: cat /etc/cron.d/shift_scheduler_job
Find the writable trust boundary — input file influenced by station_crew
Root job processes crafted inputs — understand before exploiting
BASELINE_EOF
    echo "[✓] Baseline clue written to $CLUE_FILE"
    echo "[✓] Container baseline restored for fresh exploration session"
}

main_reset(){
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║         SHIFT_SCHEDULER — RESET (Container B)                       ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║ Removing writable root-scheduled job boundary from      ║"
    echo "║ container — vulnerability reset for new session         ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""

    reset_schedule_vulnerability
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
echo "║           SHIFT_SCHEDULER Reset Script — Use: '$0' --reset      ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Usage: $0 --reset                                      ║"
echo "║        This resets SHIFT_SCHEDULER within its container.           ║"
echo "╚══════════════════════════════════════════════════════╝"

main