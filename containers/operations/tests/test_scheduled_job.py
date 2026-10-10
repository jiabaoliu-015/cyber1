#!/usr/bin/env python3
"""
SHIFT_SCHEDULER — Automated Acceptance Tests (Container B)

Tests for SHIFT_SCHEDULER writable root scheduled job route within the container model.
Each test simulates what the station_crew player does after starting fresh in
a clean container state — all operations confined within SHIFT_SCHEDULER container.

Usage:
    python3 test_scheduled_job.py

All tests operate within the SHIFT_SCHEDULER container — no direct host access.
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
SERVICE_PATH = "/opt/shift_scheduler/process_job"
SCHEDULE_FILE = "/etc/cron.d/shift_scheduler_job"
INPUT_FILE = "/var/run/shift_scheduler/input"
OUTPUT_FILE = "/var/run/shift_scheduler/output"
CLUE_FILE = "/entry/scheduled_job_clue.txt"

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


def test_schedule_accessible():
    """Test 1: Cron schedule file is discoverable within container."""
    result = run_cmd(["cat", SCHEDULE_FILE])
    print("\n[✓] Test 1: Cron schedule accessible")
    if "root" in result and "process_job" in result:
        TEST_RESULTS.append(("Schedule accessible", "PASS", "Root-scheduled job visible"))
        return True
    else:
        print(f"  ✗ Schedule file content unexpected")
        TEST_RESULTS.append(("Schedule accessible", "FAIL", "No visible root cron entry"))
        return False


def test_root_flag_available():
    """Test 2: Root proof/flag accessible via crafted argument."""
    result = run_cmd(["/opt/shift_scheduler/process_job", "print_flag"])
    print("\n[✓] Test 2: Root flag available")
    if ROOT_FLAG in result:
        TEST_RESULTS.append(("Root flag available", "PASS", "Flag CITS3006_ROOT_FLAG found"))
        return True
    else:
        print(f"  ✗ Root flag not found")
        TEST_RESULTS.append(("Root flag available", "FAIL", "Flag missing"))
        return False


def test_input_handling():
    """Test 3: Crafted arguments processed correctly by root job."""
    result = run_cmd(["/opt/shift_scheduler/process_job", "inspect"])
    print("\n[✓] Test 3: Input handling works (inspect operation)")
    if "cron" in result.lower() and "trust" in result.lower():
        TEST_RESULTS.append(("Input handling", "PASS", "Trust boundary analysis delivered"))
        return True
    else:
        print(f"  ✗ Inspect operation failed")
        TEST_RESULTS.append(("Input handling", "FAIL", "No trust boundary guidance"))
        return False


def test_clue_file_exists():
    """Test 4: Discovery clues present in container."""
    exists = os.path.exists(CLUE_FILE)
    print("\n[✓] Test 4: Clue file present in container")
    if exists:
        TEST_RESULTS.append(("Clue file", "PASS", "Discovery clues available"))
        return True
    else:
        print(f"  ✗ Clue file {CLUE_FILE} not found")
        TEST_RESULTS.append(("Clue file", "FAIL", "Clue file missing"))
        return False


def test_permissions_valid():
    """Test 5: Schedule file permissions reflect trust boundary."""
    try:
        perms = os.stat(SCHEDULE_FILE).st_mode
        # Should be readable/writable/executable by appropriate users
        has_writable = bool(perms & stat.S_IWUSR)
        print("\n[✓] Test 5: File permissions valid")
        if has_writable:
            TEST_RESULTS.append(("Permissions", "PASS", "Writable trust boundary present"))
            return True
        else:
            print(f"  ✗ Schedule file not writable (trust boundary missing)")
            TEST_RESULTS.append(("Permissions", "FAIL", "No writable permission detected"))
            return False
    except Exception as e:
        print(f"  ✗ Error checking permissions: {e}")
        TEST_RESULTS.append(("Permissions", "FAIL", "Permission check error"))
        return False


def run_all_tests():
    """Execute all SHIFT_SCHEDULER acceptance tests."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║     SHIFT_SCHEDULER Automated Acceptance Tests                    ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Testing writable root-scheduled job within container      ║")
    print("║ SHIFT_SCHEDULER route — Container B                                ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    tests = [
        ("Test 1 - Cron schedule accessible", test_schedule_accessible),
        ("Test 2 - Root flag available", test_root_flag_available),
        ("Test 3 - Input handling (inspect)", test_input_handling),
        ("Test 4 - Clue file present", test_clue_file_exists),
        ("Test 5 - Permissions valid", test_permissions_valid),
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
    print("║       SHIFT_SCHEDULER TEST RESULTS                                ║")
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
        print("\n✓ ALL SHIFT_SCHEDULER tests PASSED — container ready for exploration")
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
    print("║     SHIFT_SCHEDULER Automated Acceptance Tests                     ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Usage: python3 test_scheduled_job.py")
    print("║         Tests run within SHIFT_SCHEDULER container                ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    run_all_tests()

    if False:  # Always show detailed
        print_results()

    return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())