#!/usr/bin/env python3
"""
MAINTENANCE_UTILITY — Regeneration Script

Regenerates the SUID privilege escalation binary within the MAINTENANCE_UTILITY container.
This script ensures the vulnerability is properly configured for the player
to discover and exploit — all scoped within the repo's container model.

Usage (within container context):
    python3 regenerate_suid_route.py
    python3 regenerate_suid_route.py --init     # Set up SUID privilege escalation
    python3 regenerate_suid_route.py --reset     # Remove vulnerability (full reset)

No direct host privilege required — all paths are container-relative.
"""

import os
import sys
import argparse
import uuid
import json
import stat

# --- Container-Scoped Configuration ---
SERVICE_PATH = "/opt/suseid/maintenance_utility"
WEBLocal_DIR = "/home/kali/Desktop/CITS3006-Project/containers/operations/implementation"
INPUT_FILE = "/var/run/suseid/input"
OUTPUT_FILE = "/var/run/suseid/output"
CLUE_FILE = "/entry/suid_route_clue.txt"
BASE_DIR = "/home/kali/Desktop/CITS3006-Project/labs/privilege-escalation-lab/routes"

ROOT_FLAG = "CITS3006_ROOT_FLAG"


def ensure_directories():
    """Ensure required directories exist (within container context)."""
    dirs = [
        "/opt/suseid",
        "/var/run/suseid",
        "/entry",
        "/srv/station_crew",
    ]
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print(f"[✓] Directory ensured: {d}")
        except PermissionError:
            print(f"[⚠] Warning: Could not create {d} — may already exist from prior runs")


def regenerate_service_file():
    """Copy service code from repo location to container service path."""
    source_path = os.path.join(WEBLocal_DIR, "suid_route.py")
    
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


def apply_suid_bit():
    """Apply SUID bit to enable privilege escalation (within container)."""
    if not os.path.exists(SERVICE_PATH):
        print(f"[✗] Cannot apply SUID bit — service file doesn't exist at {SERVICE_PATH}")
        return False

    # Set SUID bit + executable permissions
    os.chmod(SERVICE_PATH, stat.S_ISSETID | 0o750)
    print(f"[✓] SUID bit applied — {SERVICE_PATH} runs as root within container")
    return True


def verify_suid_configuration():
    """Verify the service is configured correctly within container."""
    perms = os.stat(SERVICE_PATH).st_mode
    if stat.S_ISSETID(perms):
        print(f"[✓] SUID configuration verified in container")
        return True
    else:
        print("[✗] SUID bit not set in container — verify configuration")
        return False


def clean_artifacts():
    """Remove previous exploitation artifacts from container."""
    artifacts = [OUTPUT_FILE, "/srv/station_crew/exploit_evidence"]
    for artifact in artifacts:
        if os.path.exists(artifact):
            os.remove(artifact)
            print(f"[✓] Cleaned artifact: {artifact}")


def write_clues():
    """Write initial discovery clues for the player within container."""
    clue = (
        "MAINTENANCE_UTILITY SUID-root service located at /opt/suseid/maintenance_utility\n"
        "Enumerate with: find / -perm -4000  (within container)\n"
        "SUID preserves root permissions when invoked\n"
        "Test with crafted arguments for root operations"
    )
    with open(CLUE_FILE, "w") as f:
        f.write(clue)
    print(f"[✓] Discovery clue written to {CLUE_FILE}")


def init_vulnerability():
    """Setup the MAINTENANCE_UTILITY challenge with SUID privilege escalation enabled."""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         MAINTENANCE_UTILITY Regeneration — INITIALIZE              ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Setting up SUID privilege escalation challenge within  ║")
    print("║ the MAINTENANCE_UTILITY container environment                         ║"
    print("╚══════════════════════════════════════════════════════╝")
    print()

    ensure_directories()
    regenerate_service_file()
    apply_suid_bit()
    clean_artifacts()
    write_clues()

    if not verify_suid_configuration():
        print("\n[✗] Initialization failed — configuration verification error")
        return False

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         MAINTENANCE_UTILITY INITIALIZED                            ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Status: SUID-root privilege escalation available      ║")
    print("║ Player can now explore and exploit within container  ║"
    print("╚══════════════════════════════════════════════════════╝")
    return True


def full_reset():
    """Remove all vulnerabilities from MAINTENANCE_UTILITY container."""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         MAINTENANCE_UTILITY RESET — FULL                          ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Removing SUID privilege — vulnerability reset in     ║"
    print("║ container for new discovery session                  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    reset_suid = False
    if os.path.exists(SERVICE_PATH):
        os.chmod(SERVICE_PATH, 0o755)  # Remove SUID, keep executable
        print("[✓] SUID bit removed from container service")
        reset_suid = True
    else:
        print("[✗] Service not found — cannot reset")

    clean_artifacts()
    write_clues()

    if not reset_suid:
        print("\n[✗] Reset incomplete")
        return False

    print("\n✓ MAINTENANCE_UTILITY reset complete — container ready for fresh exploration")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate MAINTENANCE_UTILITY SUID privilege escalation service within container"
    )
    parser.add_argument("--init", action="store_true",
                        help="Initialize challenge with SUID privilege escalation enabled")
    parser.add_argument("--reset", action="store_true",
                        help="Remove vulnerability and reset container to baseline")

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║        MAINTENANCE_UTILITY Regeneration Script                       ║")
    if args.reset:
        print("[RESET MODE] Removing vulnerability from container")
    else:
        print("[INIT MODE] Setting up SUID privilege escalation challenge")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    if args.reset:
        full_reset()
    else:
        init_vulnerability()

    return 0


if __name__ == "__main__":
    sys.exit(main())