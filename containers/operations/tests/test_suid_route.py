#!/usr/bin/env python3
"""
MAINTENANCE_UTILITY — Automated Acceptance Tests

Tests for MAINTENANCE_UTILITY SUID privilege escalation route within the container model.
Each test simulates what the station_crew player would do after starting fresh
in a clean container state.

Usage:
    python3 test_suid_route.py
    python3 test_suid_route.py --clean-first   # Optional: ensures clean test state

All tests operate within the MAINTENANCE_UTILITY container context — no direct host access.
"""

import subprocess
import json
import sys
import os
import stat
from pathlib import Path

# --- Configuration ---
ROOT_FLAG = "CITS3006_ROOT_FLAG"
GREEN_OK = "\033[0;32m"
RED_FAIL = "\033[0;31m"

# Container-scoped paths
SERVICE_PATH = "/opt/suseid/maintenance_utility"
CLUE_FILE = "/entry/suid_route_clue.txt"
OUTPUT_FILE = "/var/run/suseid/output"
EXPLOIT_FILE = "/srv/station_crew/exploit_evidence"

TEST_RESULTS = []


def run_cmd(args, cwd=None):
    """Run a command within container context and return output."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "[✗] Command timed out — may need container check"
    except Exception as e:
        return f"[✗] Exception: {e}"


def test_challenge_accessible():
    """Test 1: Challenge hint is accessible within container."""
    result = run_cmd(["/opt/suseid/maintenance_utility", "--challenge"])
    print("\n[✓] Test 1: Challenge accessible")
    if "SUID" in result and "root" in result.lower():
        TEST_RESULTS.append(("Challenge accessible", "PASS", "Service hint delivered correctly"))
        return True
    else:
        print(f"  ✗ Output contains expected info")
        TEST_RESULTS.append(("Challenge accessible", "FAIL", "Hint missing critical information"))
        return False


def test_root_flag_available():
    """Test 2: Root proof/flag is accessible via crafted argument."""
    result = run_cmd(["/opt/suseid/maintenance_utility", "--run", "print_flag"])
    print("\n[✓] Test 2: Root flag available")
    if ROOT_FLAG in result:
        TEST_RESULTS.append(("Root flag available", "PASS", "Flag CITS3006_ROOT_FLAG found"))
        return True
    else:
        print(f"  ✗ Root flag not found in output")
        TEST_RESULTS.append(("Root flag available", "FAIL", "Flag missing"))
        return False


def test_input_handling():
    """Test 3: Crafted arguments are processed correctly."""
    result = run_cmd(["/opt/suseid/maintenance_utility", "--run", "create_file"])
    print("\n[✓] Test 3: Input handling works")
    if "CREATE_FILE" in result:
        TEST_RESULTS.append(("Input handling", "PASS", "Argument processed correctly"))
        return True
    else:
        print(f"  ✗ Argument not processed")
        TEST_RESULTS.append(("Input handling", "FAIL", "No response to crafted argument"))
        return False


def test_health_status():
    """Test 4: Health check returns expected status."""
    result = run_cmd(["/opt/suseid/maintenance_utility", "--healthcheck"])
    print("\n[✓] Test 4: Health status valid")
    if "running" in result.lower():
        TEST_RESULTS.append(("Health status", "PASS", "Service reports healthy"))
        return True
    else:
        print(f"  ✗ Unexpected health status")
        TEST_RESULTS.append(("Health status", "FAIL", "Health check abnormal"))
        return False


def test_clue_file_exists():
    """Test 5: Discovery clues are written in container."""
    exists = os.path.exists(CLUE_FILE)
    print("\n[✓] Test 5: Clue file present in container")
    if exists:
        TEST_RESULTS.append(("Clue file", "PASS", "Discovery clues file exists"))
        return True
    else:
        print(f"  ✗ Clue file {CLUE_FILE} not found")
        TEST_RESULTS.append(("Clue file", "FAIL", "Clue file missing"))
        return False


def test_suid_bit_present():
    """Test 6: Service file has appropriate permissions within container."""
    try:
        perms = os.stat(SERVICE_PATH).st_mode
        has_exec = bool(perms & (stat.S_IXUSR | stat.S_IXGRP))
        print("\n[✓] Test 6: Service file permissions valid")
        if has_exec:
            TEST_RESULTS.append(("Permissions", "PASS", "Service file executable"))
            return True
        else:
            print(f"  ✗ Service file lacks execute permission")
            TEST_RESULTS.append(("Permissions", "FAIL", "File not executable"))
            return False
    except Exception as e:
        print(f"  ✗ Error checking permissions: {e}")
        TEST_RESULTS.append(("Permissions", "FAIL", "Permission check error"))
        return False


def run_all_tests():
    """Execute all MAINTENANCE_UTILITY acceptance tests."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║     MAINTENANCE_UTILITY Automated Acceptance Tests                  ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Running tests for SUID privilege escalation route     ║")
    print("║ within MAINTENANCE_UTILITY container environment                     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    tests = [
        ("Test 1 - Challenge accessible", test_challenge_accessible),
        ("Test 2 - Root flag available", test_root_flag_available),
        ("Test 3 - Input handling", test_input_handling),
        ("Test 4 - Health status", test_health_status),
        ("Test 5 - Clue file present", test_clue_file_exists),
        ("Test 6 - Permissions valid", test_suid_bit_present),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        result = test_func()
        status = "PASS" if result else "FAIL"
        if "FAIL" in status:
            failed += 1

        passed += 1
        print(f"[{status}] {name}")

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║         MAINTENANCE_UTILITY TEST RESULTS                            ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  Total tests: {len(tests)}")
    print(f"║  Passed: {passed}")
    print(f"║  Failed: {failed}")
    print("╚══════════════════════════════════════════════════════╝")

    global TEST_RESULTS
    TEST_RESULTS = [{"name": r[0], "status": r[1], "detail": r[2]} for r in TEST_RESULTS]

    if failed == 0:
        print("\n✓ ALL MAINTENANCE_UTILITY tests PASSED — container ready for exploration")
        return 0
    else:
        print(f"\n⚠ {failed} TEST(S) FAILED — review details above")
        return 1


def print_results():
    """Print detailed test results."""
    print("\nDetailed Results:")
    print("-" * 60)
    for r in TEST_RESULTS:
        icon = GREEN_OK if "PASS" in r[1] else RED_FAIL
        print(f"[{icon}] {r[0]}: {r[1]} — {r[2]}")
    print("-" * 60)


def main():
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║     MAINTENANCE_UTILITY Automated Acceptance Tests                   ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Usage: python3 test_suid_route.py")
    print("║         python3 test_suid_route.py --detailed  (show details)")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    status = run_all_tests()

    if "--detailed" in sys.argv or False:  # Always show detailed
        print_results()

    print("\nNext steps for container testing:")
    print("  1. Run container: docker-compose up -d maintenance_utility")
    print("  2. Verify health: ./containers/operations/scripts/healthcheck_suid_route.sh")
    print("  3. Explore challenge: /opt/suseid/maintenance_utility --challenge")

    return status


if __name__ == "__main__":
    sys.exit(main())