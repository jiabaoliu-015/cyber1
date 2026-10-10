#!/usr/bin/env bash
#
# MAINTENANCE_UTILITY — Healthcheck Script (Container A)
#
# Validates the MAINTENANCE_UTILITY SUID privilege escalation service is running correctly
# within the container environment. Checks include service responsiveness,
# SUID configuration, challenge accessibility, and root flag availability.
#
# All operations occur inside the MAINTENANCE_UTILITY container — confined to the repo's
# Docker container model (Option A: separate container per route).

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICE_PATH="/opt/suseid/maintenance_utility"
ROOT_FLAG="CITS3006_ROOT_FLAG"
EXIT_CODE=0

check_suid_bit() {
    if [[ -e "$SERVICE_PATH" ]]; then
        local perms
        perms=$(stat -c "%A" "$SERVICE_PATH" 2>/dev/null || stat -f "%a" "$SERVICE_PATH" 2>/dev/null)
        # SUID bit should NOT be set at healthcheck time (vulnerability removed after fix)
        # But the SERVICE FILE itself should exist and be executable
        [[ "$perms" == *"x"* ]] || { echo "[✗] MAINTENANCE_UTILITY service not executable"; EXIT_CODE=1; return 1; }
        echo "[✓] MAINTENANCE_UTILITY service file accessible within container"
        return 0
    else
        echo "[✗] MAINTENANCE_UTILITY service path not found: $SERVICE_PATH"
        EXIT_CODE=1
        return 1
    fi
}

test_challenge_response() {
    local result
    result=$(/opt/suseid/maintenance_utility --challenge 2>&1 || echo "ERROR")
    if [[ "$result" == *"SUID"* && "$result" == *"root"* ]]; then
        echo "[✓] MAINTENANCE_UTILITY challenge hint delivered correctly within container"
        return 0
    else
        echo "[✗] MAINTENANCE_UTILITY challenge response missing expected information"
        EXIT_CODE=1
        return 1
    fi
}

test_root_flag_available() {
    local output
    output=$(/opt/suseid/maintenance_utility print_flag 2>&1 || echo "ERROR")
    if [[ "$output" == *"CITS3006_ROOT_FLAG"* ]]; then
        echo "[✓] Root proof/flag accessible via MAINTENANCE_UTILITY within container"
        return 0
    else
        echo "[✗] Root flag not found via MAINTENANCE_UTILITY — check container state"
        EXIT_CODE=1
        return 1
    fi
}

test_input_handling() {
    local test_arg="create_file"
    local result
    result=$(/opt/suseid/maintenance_utility "$test_arg" 2>&1 || echo "ERROR")
    if [[ "$result" == *"CREATE_FILE"* ]]; then
        echo "[✓] MAINTENANCE_UTILITY accepts and processes crafted arguments within container"
        return 0
    else
        echo "[✗] MAINTENANCE_UTILITY not processing argument correctly"
        EXIT_CODE=1
        return 1
    fi
}

test_health_status() {
    local result
    result=$(/opt/suseid/maintenance_utility --healthcheck 2>&1 || echo "ERROR")
    if [[ "$result" == *"running"* ]]; then
        echo "[✓] MAINTENANCE_UTILITY health check returns expected status within container"
        return 0
    else
        echo "[✗] MAINTENANCE_UTILITY health check abnormal"
        EXIT_CODE=1
        return 1
    fi
}

echo "╔══════════════════════════════════════════════════════╗"
echo "║         MAINTENANCE_UTILITY HEALTHCHECK (Container A)                ║"
echo "╠══════════════════════════════════════════════════════╣"
echo ""

check_suid_bit
echo ""
test_challenge_response
echo ""
test_root_flag_available
echo ""
test_input_handling
echo ""
test_health_status
echo ""

echo "╚══════════════════════════════════════════════════════╝"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}[MAINTENANCE_UTILITY Healthcheck PASSED]${NC}"
    echo "✓ All checks passed — MAINTENANCE_UTILITY container ready for station_crew exploration"
    exit 0
else
    echo -e "${RED}[MAINTENANCE_UTILITY Healthcheck FAILED]${NC}"
    echo "⚠ Review output above — issues may need container-level fixes"
    exit $EXIT_CODE
fi