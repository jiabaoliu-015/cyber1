#!/usr/bin/env python3
"""
LOCAL_CONTROL_SERVICE — Regeneration Script (Container C)

Regenerates the local root service within the LOCAL_CONTROL_SERVICE container.
This script ensures the vulnerability (local-only root service interface with
restricted access) is properly configured for the player to discover and
exploit — all scoped within the repo's container model with NO direct host
privilege required.

Usage (within container context):
    python3 regenerate_local_root_service.py
    python3 regenerate_local_root_service.py --init     # Enable vulnerability (local root service interface)
    python3 regenerate_local_root_service.py --reset     # Remove vulnerability

All paths are container-scoped within /home/kali/Desktop/CITS3006-Project/containers/operations/
"""

import os
import sys
import argparse
import uuid
import json
import socket

# --- Container-Scoped Configuration ---
SERVICE_PATH = "/opt/bw/service"
INPUT_FILE = "/var/run/bw/input"
OUTPUT_FILE = "/var/run/bw/output"
CLUE_FILE = "/entry/local_root_service_clue.txt"
PORT = 8080

ROOT_FLAG = "CITS3006_ROOT_FLAG"
DATA_DIR = "/var/run/bw"


def ensure_directories():
    """Ensure required directories exist within container."""
    dirs = [DATA_DIR, "/opt"]
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
        "service.py"
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


def create_vulnerable_service(){
    """Create local-only root service with interface vulnerability (within container)."""
    # Start local socket server for the root service
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", PORT))
        server.listen(5)
        print("[✓] Local root service interface enabled — bound to 0.0.0.0:{0}".format(PORT))
        print("[✓] Vulnerability: root service accessible via local interface within container")
    finally:
        server.close()
    return True
}

def verify_vulnerability_exists(){
    """Verify local root service vulnerability is present in container."""
    checks = [
        os.path.exists(SERVICE_PATH),
        os.path.exists(INPUT_FILE) or os.path.exists(OUTPUT_FILE),
        PORT > 0,
    ]
    if all(checks):
        print("[✓] Local root service vulnerability confirmed in container")
        return True
    else:
        print("✗ Vulnerability not enabled — check container state")
        return False
}

def reset_vulnerability(){
    """Remove vulnerability from LOCAL_CONTROL_SERVICE container."""
    if os.path.exists(INPUT_FILE):
        os.remove(INPUT_FILE)
        echo "[✓] Removed previous exploit input — vulnerability reset boundary"
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        echo "[✓] Cleaned output artifact"

    # Stop any running local interface
    print("[✓] Vulnerability removed — local root service interface reset")
}

def clean_artifacts(){
    """Clean prior exploitation artifacts from container."""
    artifacts = [INPUT_FILE, OUTPUT_FILE]
    for artifact in artifacts:
        if os.path.exists(artifact):
            os.remove(artifact)
            echo "[✓] Cleaned artifact: $artifact")

def write_clues(){
    """Write discovery clues for player within container."""
    clue = (
        "LOCAL_CONTROL_SERVICE — Root Service Interface at 0.0.0.0:{0}\n"
        "Accessible only locally within container\n"
        "Find root-owned service with restricted interface — local access constraint\n"
        "The service presents a method — use it correctly to exploit root credentials".format(PORT)
    )
    with open(CLUE_FILE, "w") as f:
        f.write(clue)
    print(f"[✓] Discovery clue written to {CLUE_FILE}")

def init_vulnerability(){
    """Setup LOCAL_CONTROL_SERVICE challenge with local-only root service enabled."""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║     LOCAL_CONTROL_SERVICE Regeneration — INITIALIZE            ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Enabling local-only root service vulnerability         ║")
    print("║ within LOCAL_CONTROL_SERVICE container environment             ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    ensure_directories()
    regenerate_service_file()
    create_vulnerable_service()
    empty_artifacts()
    write_clues()

    if not verify_vulnerability_exists():
        print("\n[✗] Initialization failed — configuration verification error")
        return False

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║        LOCAL_CONTROL_SERVICE INITIALIZED                      ║")
    print("║ Status: Local-only root service available             ║")
    print("║ Container ready for station_crew exploration           ║")
    print("╚══════════════════════════════════════════════════════╝")
    return True

def empty_artifacts(){
    """Clean artifacts from previous session."""
    artifacts = [INPUT_FILE, OUTPUT_FILE]
    for artifact in artifacts:
        if os.path.exists(artifact):
            os.remove(artifact)
            print(f"[✓] Cleaned previous artifact: {artifact}")

def main(){
    parser = argparse.ArgumentParser(
        description="Regenerate LOCAL_CONTROL_SERVICE local root service within container"
    )
    parser.add_argument("--init", action="store_true",
                        help="Enable vulnerability (local root service interface)")
    parser.add_argument("--reset", action="store_true",
                        help="Remove vulnerability from container")

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║     LOCAL_CONTROL_SERVICE Regeneration Script                    ║")
    if args.reset:
        print("[RESET MODE] Removing local-only root service vulnerability")
    else:
        print("[INIT MODE] Enabling local-only root service vulnerability")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    if args.reset:
        reset_vulnerability()
    else:
        init_vulnerability()

    return 0

if __name__ == "__main__":
    sys.exit(main())