#!/usr/bin/env python3
"""
MAINTENANCE_UTILITY — SUID Privilege Escalation Service (Inside Container A)

Container Model: Option A — Separate container per route (MAINTENANCE_UTILITY, SHIFT_SCHEDULER, LOCAL_CONTROL_SERVICE)

Intended Vulnerability: SUID-root program within the MAINTENANCE_UTILITY container accepts
user input and performs root-level operations that the station_crew player must
discover and exploit.

The vulnerability is NOT simply that the program runs as root — the player
must understand:
1. Why SUID preserves root permissions regardless of caller
2. What input the program expects to trigger root operations
3. How to craft arguments to exploit the privilege escalation

All operations occur inside the MAINTENANCE_UTILITY container. No direct host system access.

Root proof/flag: CITS3006_ROOT_FLAG
"""

import os
import sys
import argparse
import json
import uuid
import time
import logging

# --- Container-Scoped Configuration ---
SERVICE_PATH = "/opt/suseid/maintenance_utility"
INPUT_FILE = "/var/run/suseid/input"
OUTPUT_FILE = "/var/run/suseid/output"
CLUE_FILE = "/entry/suid_route_clue.txt"
BASE_DIR = "/home/kali/Desktop/CITS3006-Project/labs/privilege-escalation-lab/routes"

# Ensure directories exist (within container context)
os.makedirs("/opt/suseid", exist_ok=True)
os.makedirs("/var/run/suseid", exist_ok=True)
os.makedirs("/entry", exist_ok=True)
os.makedirs("/srv/station_crew", exist_ok=True)


class MaintenanceUtilityService:
    """SUID privilege escalation service — designed for container-scoped testing."""

    def __init__(self):
        self.logged_in = False
        self.discovery_hint = None

    def check_suid(self):
        """Verify the program runs with SUID privilege boundary within container."""
        return os.access(SERVICE_PATH, os.X_OK) and os.geteuid() == 0

    def write_clue(self):
        """Write a discovery hint for the player to find clues."""
        clue = (
            "MAINTENANCE_UTILITY SUID-root service located at /opt/suseid/maintenance_utility.\n"
            "Enumerate with: find / -perm -4000\n"
            "SUID preserves root permissions when invoked by station_crew.\n"
            "Test with arguments to trigger root operations."
        )
        with open(CLUE_FILE, "w") as f:
            f.write(clue)

    def get_challenge(self):
        """Return a challenge hint for the player."""
        hint = (
            "MAINTENANCE_UTILITY SUID-root service discovered via Linux enumeration within the container.\n"
            "This program runs as root regardless of who invokes it.\n"
            "To exploit it: understand that SUID preserves elevated permissions, "
            "then craft the appropriate argument to trigger the root operation and obtain the flag."
        )
        self.discovery_hint = hint
        return hint

    def run(self, argument=None):
        """Execute the SUID program's root operation.

        All operations occur within the MAINTENANCE_UTILITY container — station_crew interacts
        with the service via arguments passed through the container's entrypoint.

        Args:
            argument: Crafted input provided by the station_crew player

        Returns:
            dict with operation result and flag
        """
        session_token = str(uuid.uuid4())[:8]

        # Validate and process argument
        arg_lower = argument.strip().lower() if argument else ""

        if arg_lower == "create_file":
            output_path = "/srv/station_crew/exploit_evidence"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(f"{session_token}\n")
            result = {
                "status": "success",
                "operation": "CREATE_FILE",
                "file": output_path,
                "detail": "File created with elevated content — demonstrating privilege escalation works."
            }

        elif arg_lower == "print_flag":
            result = {
                "status": "success",
                "operation": "PRINT_FLAG",
                "flag": "CITS3006_ROOT_FLAG",
                "message": "You triggered the root operation. The root proof/flag is revealed."
            }

        elif arg_lower == "verify_priv":
            result = {
                "status": "info",
                "operation": "VERIFY_PRIV",
                "detail": "SUID preserves root permissions. The vulnerability is in accepting unvalidated input — understanding this is key to exploitation."
            }

        else:
            result = {
                "status": "info",
                "operation": "UNKNOWN",
                "hint": f"Unknown argument: '{argument}'. Try: create_file, print_flag, or verify_priv.",
                "discovery": "The SUID-root service accepts crafted arguments — this is the exploitation path."
            }

        # Write output for player verification (within container)
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"\n[MAINTENANCE_UTILITY-{session_token}] {json.dumps(result)}\n")

        return result

    def healthcheck(self):
        """Return health check status for monitoring within container."""
        return {
            "status": "running",
            "suid": self.check_suid(),
            "path": SERVICE_PATH,
            "version": "1.0",
            "container_scoped": True
        }


def write_clue_file():
    """Write initial clue file for the container environment."""
    MaintenanceUtilityService().write_clue()


def cli_mode(args):
    """Command-line interface for direct invocation within container."""
    service = MaintenanceUtilityService()

    if args.challenge:
        print(service.get_challenge())
    elif args.run:
        result = service.run(args.run)
        print(json.dumps(result, indent=2))
    elif args.healthcheck:
        print(json.dumps(service.healthcheck(), indent=2))
    elif args.status:
        print(json.dumps(service.healthcheck(), indent=2))
    else:
        print("Usage: maintenance_utility [--challenge] [--run ARG] [--healthcheck] [--status]")
        print("Available operations: create_file, print_flag, verify_priv")


def main():
    parser = argparse.ArgumentParser(description="MAINTENANCE_UTILITY — SUID Privilege Escalation Service (Container A)")
    parser.add_argument("--challenge", action="store_true", help="Show discovery hint")
    parser.add_argument("--run", type=str, help="Execute root operation with crafted argument")
    parser.add_argument("--healthcheck", action="store_true", help="Run health check")
    parser.add_argument("--status", action="store_true", help="Show service status")
    args = parser.parse_args()

    write_clue_file()

    service = MaintenanceUtilityService()

    if args.challenge:
        print(service.get_challenge())
    elif args.run:
        result = service.run(args.run)
        print(json.dumps(result, indent=2))
    elif args.healthcheck or args.status:
        print(json.dumps(service.healthcheck(), indent=2))
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())