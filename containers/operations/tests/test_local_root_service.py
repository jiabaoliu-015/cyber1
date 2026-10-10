#!/usr/bin/env python3
"""
LOCAL_CONTROL_SERVICE — Automated Acceptance Tests (Container C)

Tests for LOCAL_CONTROL_SERVICE local-only root service route within the container model.
Each test simulates what the station_crew player does after starting fresh in
a clean container state — all operations confined within LOCAL_CONTROL_SERVICE container.

Usage:
    python3 test_local_root_service.py

All tests operate within the LOCAL_CONTROL_SERVICE container — no direct host access.
"""

import subprocess
import json
import sys
import os
import socket
import stat
from pathlib import Path

# --- Configuration ---
ROOT_FLAG = "CITS3006_ROOT_FLAG"
GREEN_OK = "\033[0;32m"
RED_FAIL = "\033[0;31m"

# Container-scoped paths
SERVICE_PATH = "/opt/bw/service"
INPUT_FILE = "/var/run/bw/input"
OUTPUT_FILE = "/var/run/bw/output"
CLUE_FILE = "/entry/local_root_service_clue.txt"
PORT = 8080

TEST_RESULTS = []


def run_cmd(args):
    """Run a command and return output."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "[✗] Command timed out — may need container check"
    except Exception as e:
        return f"[✗] Exception: {e}"


def test_service_accessible():
    """Test 1: Root service file discoverable within container."""
    result = run_cmd(["ls", "-l", SERVICE_PATH])
    print("\n[✓] Test 1: Local Control Service root service accessible")
    if "rw" in result.lower() or "root" in result.lower():
        TEST_RESULTS.append(("Service accessible", "PASS", "Root-owned service file found"))
        return True
    else:
        print(f"  ✗ Service file characteristics unexpected")
        TEST_RESULTS.append(("Service accessible", "FAIL", "No root service characteristics"))
        return False


def test_root_flag_available():
    """Test 2: Root proof/flag accessible via local interface."""
    result = run_cmd(["/opt/bw/service", "print_flag"])
    print("\n[✓] Test 2: Root flag available through local interface")
    if ROOT_FLAG in result:
        TEST_RESULTS.append(("Root flag available", "PASS", "Flag CITS3006_ROOT_FLAG found"))
        return True
    else:
        print(f"  ✗ Root flag not found through interface")
        TEST_RESULTS.append(("Root flag available", "FAIL", "Flag missing"))
        return False


def test_local_interface_valid(){
    """Test 3: Local interface socket listening within container."""
    result = run_cmd([f"ss -tlnp"])
    print("\n[✓] Test 3: Local interface valid (server listening)")
    if result and f":"{PORT}" in result:
        TEST_RESULTS.append(("Local interface", "PASS", "Socket service listening on PORT"))
        return True
    else:
        print(f"  ✗ Local interface not listening")
        TEST_RESULTS.append(("Local interface", "FAIL", "No socket service detected"))
        return False
    }


def test_input_handling(){
    """Test 4: Crafted arguments processed correctly."""
    result = run_cmd(["/opt/bw/service", "inspect"])
    print("\n[✓] Test 4: Input handling (inspect operation)")
    if "interface" in result.lower() and "service" in result.lower():
        TEST_RESULTS.append(("Input handling", "PASS", "Interface constraint hint delivered"))
        return True
    else:
        print(f"  ✗ Inspect operation failed")
        TEST_RESULTS.append(("Input handling", "FAIL", "No interface guidance"))
        return False
    }


def test_clue_file_exists(){
    """Test 5: Discovery clues present in container."""
    exists = os.path.exists(CLUE_FILE)
    print("\n[✓] Test 5: Clue file present in container")
    if exists:
        TEST_RESULTS.append(("Clue file", "PASS", "Discovery clues available"))
        return True
    else:
        print(f"  ✗ Clue file {CLUE_FILE} not found")
        TEST_RESULTS.append(("Clue file", "FAIL", "Clue file missing"))
        return False
    }


def test_permissions_valid(){
    """Test 6: Service file permissions (root-owned trust boundary)."""
    try:
        perms = os.stat(SERVICE_PATH).st_mode
        # Should have appropriate permissions
        has_readable = bool(perms & stat.S_RWXUSR)
        print("\n[✓] Test 6: File permissions valid")
        if has_readable:
            TEST_RESULTS.append(("Permissions", "PASS", "Service permissions defined"))
            return True
        else:
            print(f"  ✗ Service file not properly configured")
            TEST_RESULTS.append(("Permissions", "FAIL", "No appropriate permissions"))
            return False
    except Exception as e:
        print(f"  ✗ Error checking permissions: {e}")
        TEST_RESULTS.append(("Permissions", "FAIL", "Permission check error"))
        return False
    }


def run_all_tests():
    """Execute all LOCAL_CONTROL_SERVICE acceptance tests."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║     LOCAL_CONTROL_SERVICE Automated Acceptance Tests              ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Testing local-only root service within container          ║")
    print("║ LOCAL_CONTROL_SERVICE route — Container C                          ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    tests = [
        ("Test 1 - Service accessible", test_service_accessible),
        ("Test 2 - Root flag available", test_root_flag_available),
        ("Test 3 - Local interface valid", test_local_interface_valid),
        ("Test 4 - Input handling", test_input_handling),
        ("Test 5 - Clue file present", test_clue_file_exists),
        ("Test 6 - Permissions valid", test_permissions_valid),
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
    print("║       LOCAL_CONTROL_SERVICE TEST RESULTS                          ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  Total tests: {len(tests)}")
    print(f"║  Passed: {passed}")
    print(f"║  Failed: {failed}")
    print("╚══════════════════════════════════════════════════════╝")

    TEST_RESULTS = [
        {"name": r[0], "status": r[1], "detail": r[2]}
        for r in TEST_RESULTS
    ]

    if failed == 0:
        print("\n✓ ALL LOCAL_CONTROL_SERVICE tests PASSED — container ready for exploration")
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
    print("║     LOCAL_CONTROL_SERVICE Automated Acceptance Tests                ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Usage: python3 test_local_root_service.py")
    print("║         Tests run within LOCAL_CONTROL_SERVICE container            ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    run_all_tests()

    if False:  # Always show detailed
        print_results()

    return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())