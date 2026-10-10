#!/usr/bin/env bash
#
# CITS3006-Project — Integration Test Runner
#
# This script orchestrates and reports on the full integration test suite
# covering all three routes (MAINTENANCE_UTILITY, SHIFT_SCHEDULER, LOCAL_CONTROL_SERVICE).
#
# Usage:
#   ./tests/integration/run_integration.sh
#
# All tests are container-aware and scoped within containers/operations/
# No direct host privilege required.

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INTEGRATION_DIR="$PROJECT_ROOT/tests/integration"
RESULTS_DIR="$PROJECT_ROOT/tests/integration/results"
LOGS_DIR="$PROJECT_ROOT/tests/integration/logs"

# Ensure directories exist
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

# ==========================================
# Header
# ==========================================
echo "╔══════════════════════════════════════════════════════╗"
echo "║         CITS3006-PROJECT INTEGRATION TESTS             ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Full validation across ALL THREE routes:                ║"
echo "║   • MAINTENANCE_UTILITY          — SUID Root Service (Container A)       ║"
echo "║   • SHIFT_SCHEDULER          — Writable Root Schedule (Container B) ║"
echo "║   • LOCAL_CONTROL_SERVICE   — Local Root Service (Container C)    ║"
echo "║                                                          ║"
echo "║ All tests container-aware — NO direct host privilege     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ==========================================
# Run Integration Tests
# ==========================================
echo "╔══════════════════════════════════════════════════════╗"
echo "║   RUNNING INTEGRATION TESTS                            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Run the Python integration test
python3 "$INTEGRATION_DIR/test_integration.py" 2>&1 | tee "$LOGS_DIR/integration_test_output.log"

# ==========================================
# Result Summary
# ==========================================
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         TEST SUMMARY                                    ║"
echo "╠══════════════════════════════════════════════════════╣"

# Check if results were generated
if [ -f "$RESULTS_DIR/integration_test_results.json" ]; then
    echo "✓ Results file generated:"
    echo "  $RESULTS_DIR/integration_test_results.json"
    echo ""

    # Parse results - calculate statistics
    TOTAL_TESTS=$(python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    all_tests = data.get('all_test_results', [])
    print(len(all_tests))
")

    PASSED_TESTS=$(python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    all_tests = data.get('all_test_results', [])
    passed = sum(1 for r in all_tests if r['status'] == 'PASS')
    print(passed)
")

    # Calculate success rate safely
    SUCCESS_RATE=$(python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    all_tests = data.get('all_test_results', [])
    passed = sum(1 for r in all_tests if r['status'] == 'PASS')
    total = len(all_tests)
    rate = (passed / total * 100) if total > 0 else 0
    print(f'{rate:.2f}')
")

    echo "Summary Statistics:"
    echo "  Total tests executed: $TOTAL_TESTS"
    echo "  Tests passed: $PASSED_TESTS"
    echo "  Success rate: $SUCCESS_RATE%"
    echo ""

    # Route breakdown
    echo "Route Breakdown:"
    python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    route_stats = {}
    for result in data['all_test_results']:
        route = result['route']
        if route not in route_stats:
            route_stats[route] = {'passed': 0, 'total': 0}
        route_stats[route]['total'] += 1
        if result['status'] == 'PASS':
            route_stats[route]['passed'] += 1
    for route in ['MAINTENANCE_UTILITY', 'SHIFT_SCHEDULER', 'LOCAL_CONTROL_SERVICE']:
        stats = route_stats.get(route, {'passed': 0, 'total': 0})
        status = '✓' if stats['passed'] == stats['total'] else '✗'
        print(f\"  {route}: {stats['passed']}/{stats['total']} passed ({status})\")
"
    echo ""

    # Verification checks
    CROSS_ROUTE=$(python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    results = data.get('all_test_results', [])
    passed_count = sum(1 for t in results if t['test_name'].startswith('CrossRoute') and t['status']=='PASS')
    total_tests = len(results)
    print(f'{passed_count}/{total_tests}')
")
    FLAG_CONSISTENCY=$(python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    results = data.get('all_test_results', [])
    passed = sum(1 for t in results if t['test_name'].startswith('RootFlagConsistent') and t['status']=='PASS')
    total = len([t for t in results if t['test_name'].startswith('RootFlagConsistent')])
    print(f'{passed}/{total}')
")
    FILE_STRUCTURE=$(python3 -c "
import json
with open('$RESULTS_DIR/integration_test_results.json') as f:
    data = json.load(f)
    results = data.get('all_test_results', [])
    passed = sum(1 for t in results if t['test_name'].startswith('FileStructure') and t['status']=='PASS')
    total = len([t for t in results if t['test_name'].startswith('FileStructure')])
    print(f'{passed}/{total}')
")

    echo "Verification Checks:"
    echo "  Cross-route isolation: $CROSS_ROUTE"
    echo "  Root flag consistency: $FLAG_CONSISTENCY"
    echo "  File structure completeness: $FILE_STRUCTURE"
    echo ""

    # Verdict - based on pass ratio
    PASS_RATIO=$(echo "$PASSED_TESTS" "/" "$TOTAL_TESTS" | bc 2>/dev/null || echo "0.0")

    if [ "$PASSED_TESTS" -eq "$TOTAL_TESTS" ]; then
        VERDICT="✓ ALL TESTS PASSED"
    elif [ "$(echo "$PASS_RATIO >= 0.9" | bc)" = "1" ] 2>/dev/null || [ "$PASSED_TESTS" -ge $((TOTAL_TESTS * 9 / 10)) ]; then
        VERDICT="✓ MOST TESTS PASSED"
    else
        VERDICT="✗ TEST FAILURES DETECTED"
    fi

    echo "Final Verdict: $VERDICT"
else
    echo "✗ NO RESULTS FILE - INTEGRATION TESTS MAY NOT HAVE RAN"
    echo "Check logs/integration_test_output.log for details"
    exit 1
fi

echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   FILES GENERATED                                      ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "  • Results: $RESULTS_DIR/integration_test_results.json"
echo "  • Output Log: $LOGS_DIR/integration_test_output.log"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         END OF INTEGRATION TEST REPORT                  ║"
echo "╚══════════════════════════════════════════════════════╝"

# Ensure success_rate_percent is calculated if missing
python3 -c "
import json
import sys

results_file = '$RESULTS_DIR/integration_test_results.json'
try:
    with open(results_file) as f:
        data = json.load(f)
    
    all_tests = data.get('all_test_results', [])
    passed = sum(1 for r in all_tests if r['status'] == 'PASS')
    total = len(all_tests)
    rate = (passed / total * 100) if total > 0 else 0
    
    # Update the JSON with success rate if missing
    if 'success_rate_percent' not in data['integration_test_run']:
        data['integration_test_run']['success_rate_percent'] = round(rate, 2)
        with open(results_file, 'w') as f:
            json.dump(data, f, indent=2)
    
except Exception as e:
    print(f'ERROR updating results: {e}')
    sys.exit(1)
"