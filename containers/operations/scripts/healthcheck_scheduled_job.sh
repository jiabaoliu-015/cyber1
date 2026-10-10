#!/usr/bin/env bash
#
# SHIFT_SCHEDULER — Healthcheck Script (Container B)
#
# Validates the SHIFT_SCHEDULER writable root scheduled job service is running correctly
# within the container environment. Checks include cron schedule existence,
# writable trust boundary, challenge accessibility, and root flag availability.
#
# All operations confined within container — no direct host access.

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
EXIT_CODE=0

check_schedule_exists(){
    if [[ -e "$SCHEDULE_FILE" ]]; then
        echo "[✓] SHIFT_SCHEDULER cron schedule file exists at $SCHEDULE_FILE"
        return 0
    else
        echo "[✗] SHIFT_SCHEDULER schedule file not found in container"
        EXIT_CODE=1
        return 1
    fi
}

test_root_flag_available(){
    local output
    output=$(/opt/shift_scheduler/process_job print_flag 2>&1 || echo "ERROR")
    echo "[✓] Test: Root flag accessible via crafted argument"
    if [[ "CITS3006_ROOT_FLAG" == "$output"* ]]; then
        echo "✓ Flag CITS3006_ROOT_FLAG found in output"
        return 0
    else
        echo "✗ Root flag not found in output"
        EXIT_CODE=1
        return 1
    fi
}

test_input_handling(){
    local result
    result=$(/opt/shift_scheduler/process_job inspect 2>&1 || echo "ERROR")
    echo "[✓] Test: Input handling (inspect operation)"
    if [[ "$result" == *"cron"* && "$result" == *"trust"* ]]; then
        echo "✓ Trust boundary analysis hint present"
        return 0
    else
        echo "✗ Inspect operation failed to provide expected guidance"
        EXIT_CODE=1
        return 1
    fi
}

test_challenge_accessible(){
    local result
    result=$(/opt/shift_scheduler/process_job --challenge 2>&1 || echo "ERROR")
    echo "[✓] Test: Challenge accessible within container"
    if [[ "$result" == *"vertical"* && "$result" == *"scheduled"* ]]; then
        echo "✓ Vertical privilege escalation route hint delivered"
        return 0
    else
        echo "✗ Challenge response missing expected information"
        EXIT_CODE=1
        return 1
    fi
}

test_clue_file_exists(){
    if [[ -f "$CLUE_FILE" ]]; then
        echo "[✓] Test: Discovery clue file present in container"
        return 0
    else
        echo "✗ Clue file $CLUE_FILE not found in container"
        EXIT_CODE=1
        return 1
    fi
}

echo "╔══════════════════════════════════════════════════════╗"
echo "║         SHIFT_SCHEDULER HEALTHCHECK (Container B)                 ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Validating writable root-scheduled job within container   ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

check_schedule_exists
echo ""
test_challenge_accessible
echo ""
test_input_handling
echo ""
test_root_flag_available
echo ""
test_clue_file_exists
echo ""

echo "╚══════════════════════════════════════════════════════╝"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}[SHIFT_SCHEDULER Healthcheck PASSED]${NC}"
    echo "✓ All checks passed — container ready for station_crew exploration"
    exit 0
else
    echo -e "${RED}[SHIFT_SCHEDULER Healthcheck FAILED]${NC}"
    echo "⚠ Review output above — issues may need container-level fixes"
    exit $EXIT_CODE
fi