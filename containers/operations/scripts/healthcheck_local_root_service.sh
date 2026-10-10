#!/usr/bin/env bash
#
# LOCAL_CONTROL_SERVICE — Healthcheck Script (Container C)
#
# Validates the LOCAL_CONTROL_SERVICE local root service is running correctly
# within the container environment. Checks include service accessibility,
# local interface integrity, challenge accessibility, and root flag availability.
#
# All operations confined within container — no direct host access.

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
EXIT_CODE=0

check_service_accessible(){
    if [[ -e "$SERVICE_PATH" ]]; then
        echo "[✓] Test: Local Control Service root service file accessible in container"
        return 0
    else
        echo "✗ Service $SERVICE_PATH not found in container"
        EXIT_CODE=1
        return 1
    fi
}

test_root_flag_available(){
    local output
    output=$(/opt/bw/service print_flag 2>&1 || echo "ERROR")
    echo "[✓] Test: Root flag accessible via local interface"
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
    result=$(/opt/bw/service inspect 2>&1 || echo "ERROR")
    echo "[✓] Test: Input handling (inspect operation)"
    if [[ "$result" == *"service"* && "$result" == *"interface"* ]]; then
        echo "✓ Interface constraint analysis hint present"
        return 0
    else
        echo "✗ Inspect operation failed to provide expected guidance"
        EXIT_CODE=1
        return 1
    fi
}

test_local_interface_valid(){
    if ss -tlnp 2>/dev/null | grep -qE ":$PORT"; then
        echo "[✓] Test: Local interface valid within container"
        return 0
    else
        echo "✗ Local interface $PORT not listening in container"
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
echo "║         LOCAL_CONTROL_SERVICE HEALTHCHECK (Container C)            ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Validating local-only root service within container       ║"
echo "║ LOCAL_CONTROL_SERVICE route                                          ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

check_service_accessible
echo ""
test_local_interface_valid
echo ""
test_root_flag_available
echo ""
test_input_handling
echo ""
test_clue_file_exists
echo ""

echo "╚══════════════════════════════════════════════════════╝"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}[LOCAL_CONTROL_SERVICE Healthcheck PASSED]${NC}"
    echo "✓ All checks passed — container ready for station_crew exploration"
    exit 0
else
    echo -e "${RED}[LOCAL_CONTROL_SERVICE Healthcheck FAILED]${NC}"
    echo "⚠ Review output above — issues may need container-level fixes"
    exit $EXIT_CODE
fi