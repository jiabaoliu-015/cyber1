#!/usr/bin/env python3
"""
SHIFT_SCHEDULER — Regeneration Script (Container B)

Regenerates the writable root scheduled job within the SHIFT_SCHEDULER container.
This script ensures the vulnerability (root-owned, writable schedule) is properly
configured for the player to discover and exploit — all scoped within the repo's
container model with NO direct host privilege required.

Usage (within container context):
    python3 regenerate_scheduled_job.py
    python3 regenerate_scheduled_job.py --init     # Enable vulnerability (root-scheduled job)
    python3 regenerate_scheduled_job.py --reset     # Remove vulnerability

All paths are container-scoped within /home/kali/Desktop/CITS3006-Project/containers/operations/
"""

import os
import sys
import argparse
import uuid

# --- Container-Scoped Configuration ---
SERVICE_PATH = "/opt/shift_scheduler/process_job"
SCHEDULE_FILE = "/etc/cron.d/shift_scheduler_job"
INPUT_FILE = "/var/run/shift_scheduler/input"
OUTPUT_FILE = "/var/run/shift_scheduler/output"
CLUE_FILE = "/entry/scheduled_job_clue.txt"

ROOT_FLAG = "CITS3006_ROOT_FLAG"


def ensure_directories():
    """Ensure required directories exist within container."""
    dirs = ["/var/run/shift_scheduler", "/etc"]
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print(f"[✓] Directory ensured: {d}")
        except PermissionError as e:
            print(f"[⚠] Warning: {e} — May already exist from prior runs")


def regenerate_service_file():
    """Copy service code from repo location to container."""
    source_path = os.path.join(
        "/home/kali/Desktop/CITS3006-Project/containers/operations/implementation",
        "scheduled_job.py"
    )

    if not os.path.exists(source_path):
        print(f"[✗] Source service file not found at {source_path}")
        return False

    temp_path = SERVICE_PATH + ".tmp"
    with open(source_path, "r") as src:
        with open(temp_path, "w") as dst:
            dst.write(src.read())
    os.replace(temp_path, SERVICE_PATH)
    print(f"[✓] Service file regenerated at {SERVICE_PATH}")
    return True


def create_vulnerable_schedule(writable=True):
    """Create root-owned schedule with writable boundary (vulnerability setup)."""
    cron_content = f"""# SHIFT_SCHEDULER — Root Scheduled Job (vertical privilege escalation)
# Root-owned cron task that processes input
0 * * * root /opt/shift_scheduler/process_job {{}}
"""
    with open(SCHEDULE_FILE, "w") as f:
        f.write(cron_content)

    # Make schedule root-owned with writable permission (trust boundary)
    if writable:
        os.chmod(SCHEDULE_FILE, 0o644)
        print("[✓] Vulnerability enabled — writable root-scheduled job boundary")
    return True


def verify_vulnerability_exists():
    """Verify the scheduled job vulnerability is present in container."""
    exists = os.path.exists(SCHEDULE_FILE)
    if exists and os.path.getsize(SCHEDULE_FILE) > 0:
        print("[✓] Root-scheduled job vulnerability confirmed in container")
        return True
    else:
        print("[✗] Vulnerability not enabled — check container state")
        return False


def reset_vulnerability():
    """Remove vulnerability from SHIFT_SCHEDULER container."""
    if os.path.exists(SCHEDULE_FILE):
        os.chmod(SCHEDULE_FILE, 0o444)  # Remove writable permissions
        print("[✓] Vulnerability removed — writable boundary reset in container")
    else:
        print("[✗] Schedule file not found — cannot reset")
        return False

    clean_artifacts()
    write_clues()
    return True


def clean_artifacts():
    """Clean prior exploitation artifacts from container."""
    artifacts = [INPUT_FILE, OUTPUT_FILE]
    for artifact in artifacts:
        if os.path.exists(artifact):
            os.remove(artifact)
            print(f"[✓] Cleaned artifact: {artifact}")


def write_clues():
    """Write discovery clues for player within container."""
    clue = (
        "SHIFT_SCHEDULER — Root Scheduled Job at /etc/cron.d/shift_scheduler_job\n"
        "Inspect: cat /etc/cron.d/shift_scheduler_job\n"
        "Find writable trust boundary — input file influenced by station_crew\n"
        "Root job processes crafted inputs — understand before exploiting"
    )
    with open(CLUE_FILE, "w") as f:
        f.write(clue)
    print(f"[✓] Discovery clue written to {CLUE_FILE}")


def init_vulnerability():
    """Setup SHIFT_SCHEDULER challenge with writable root-scheduled job enabled."""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║        SHIFT_SCHEDULER Regeneration — INITIALIZE               ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Enabling writable root-scheduled job vulnerability    ║")
    print("║ within SHIFT_SCHEDULER container environment                     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    ensure_directories()
    regenerate_service_file()
    create_vulnerable_schedule(writable=True)
    empty_artifacts()
    write_clues()

    if not verify_vulnerability_exists():
        print("\n[✗] Initialization failed — configuration verification error")
        return False

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         SHIFT_SCHEDULER INITIALIZED                            ║")
    print("║ Status: Writable root-scheduled job available          ║")
    print("║ Container ready for station_crew exploration            ║")
    print("╚══════════════════════════════════════════════════════╝")
    return True


def empty_artifacts():
    """Clean artifacts from previous session."""
    artifacts = [INPUT_FILE, OUTPUT_FILE]
    for artifact in artifacts:
        if os.path.exists(artifact):
            os.remove(artifact)
            print(f"[✓] Cleaned previous artifact: {artifact}")


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate SHIFT_SCHEDULER writable root-scheduled job within container"
    )
    parser.add_argument("--init", action="store_true",
                        help="Enable vulnerability (writable root-scheduled job)")
    parser.add_argument("--reset", action="store_true",
                        help="Remove vulnerability from container")

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║     SHIFT_SCHEDULER Regeneration Script                          ║")
    if args.reset:
        print("[RESET MODE] Removing writable root-scheduled job")
    else:
        print("[INIT MODE] Enabling writable root-scheduled job vulnerability")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    if args.reset:
        reset_vulnerability()
    else:
        init_vulnerability()

    return 0


if __name__ == "__main__":
    sys.exit(main())