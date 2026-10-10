#!/usr/bin/env python3
"""
LOCAL_CONTROL_SERVICE — Local Root Service Interface (Container C)

Container Model: Option A — Separate container per route (Local Control Service isolated from MAINTENANCE_UTILITY & SHIFT_SCHEDULER)

Intended Vulnerability: Local-only root service with a restricted interface —
station_crews can only interact with it through a specific method, but once they
discover that root service exists via local-only access, they can exploit it
to gain root credentials or permissions.

The challenge requires understanding:
1. How a root-owned service can present a local interface restricted to non-root
users (or even no restrictions) — the player must recognize the trust boundary
2. The interface method (socket, HTTP, SSH, etc.) — which approach enables exploitation
3. Securing the root service by limiting access to root users only

All operations confined within container — no direct host privilege. The
interface is local within the container, ensuring it remains isolated from
outside access.

Root proof/flag: CITS3006_ROOT_FLAG
"""

import os
import sys
import argparse
import json
import uuid
import socket
import threading
import time
import logging

# --- Container-Scoped Configuration ---
ROOT_FLAG = "CITS3006_ROOT_FLAG"

SERVICE_PATH = "/opt/bw/service"
INPUT_FILE = "/var/run/bw/input"
OUTPUT_FILE = "/var/run/bw/output"
CLUE_FILE = "/entry/local_root_service_clue.txt"
BASE_DIR = "/home/kali/Desktop/CITS3006-Project/labs/privilege-escalation-lab/routes"
PORT = 8080  # Local interface port (only accessible within container)

# Ensure directories exist (within container context)
os.makedirs("/var/run/bw", exist_ok=True)
os.makedirs("/opt", exist_ok=True)
os.makedirs("/entry", exist_ok=True)


class LocalControlService:
    """Local root service with restricted interface — discovered and exploited by station_crew."""

    # Local interface: socket server bound only to container localhost
    # This ensures service only accessible from within the container
    class _SocketServer(socket.socket):
        """Local-only socket server interface."""

        def __init__(self):
            super().__init__()
            self.running = False
            self.sessions = {}

        def bind_and_listen(self, interface, port):
            # Bind only to container's localhost (0.0.0.0 or 127.0.0.1)
            self.bind((interface, port))
            self.listen(5)
            print(f"[SERVICE] Local root service listening on {interface}:{port}")

        def handle_connection(self, client_socket):
            """Process request from station_crew through local interface."""
            try:
                request = client_socket.recv(1024).decode('utf-8').strip()
                self._process_request(request)
            finally:
                client_socket.close()

        def _process_request(self, request):
            """Core processing — validates input and triggers root service."""
            session_token = str(uuid.uuid4())[:8]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            if request == "print_flag":
                result = {
                    "status": "success",
                    "operation": "PRINT_FLAG",
                    "flag": "CITS3006_ROOT_FLAG",
                    message": "You accessed the root service — flag retrieved through local interface."
                }
            elif request == "verify_interface":
                result = {
                    "status": "info",
                    "operation": "VERIFY_INTERFACE",
                    "detail": "Local-only root service: interface restricted to container, accessible only through socket or defined method."
                }
            elif request == "inspect":
                result = {
                    "status": "info",
                    "operation": "INSPECT",
                    "detail": "Review service definition — root-owned with local interface constraint — this is the trust boundary."
                }
            else:
                result = {
                    "status": "info",
                    "operation": "UNKNOWN",
                    "hint": f"Unknown request type: '{request}'. Try: print_flag, verify_interface, inspect.",
                    "discovery": "LOCAL_CONTROL_SERVICE accepts requests through its local interface — this is the exploitation path."
                }

            with open(OUTPUT_FILE, "a") as f:
                f.write(f"{timestamp} | {json.dumps(result)}\n")

            self.sessions[session_token] = timestamp

    def start(self):
        """Start local root service (minimal — container-scoped)."""
        server = self._SocketServer()
        server.bind_and_listen("0.0.0.0", PORT)  # Local interface accessible within container
        server.running = True

        # Listen for connections in background thread
        thread = threading.Thread(target=server.listen, background=True)
        thread.start()

    def stop(self):
        """Stop local root service."""
        self.running = False
        print("[SERVICE] Stopping local root service")

    def write_clue(self):
        """Write discovery clues for station_crew within container."""
        clue = (
            "LOCAL_CONTROL_SERVICE — Root Service Interface at port 8080\n"
            "Accessible only locally within container (0.0.0.0:8080)\n"
            "Inspect with: ss -tlnp | grep 8080\n"
            "Find root-owned service with restricted interface — local access constraint\n"
            "The service presents a method — use it correctly to exploit root credentials"
        )
        with open(CLUE_FILE, "w") as f:
            f.write(clue)

    def get_challenge(self):
        """Return challenge hint for station_crew."""
        insight = (
            "LOCAL_CONTROL_SERVICE WIDOW — Local Root Service interface vulnerability.\n"
            "This root-owned service restricts access locally within the container.\n"
            "Steps to exploit: discover service via local interface → identify method →\n"
            "secure root service by restricting access → gain root credentials.\n"
            "The vulnerability: local-only interface allows exploitation without external access constraints."
        )
        self.discovery_hint = insight
        return insight

    def run(self, argument=None):
        """Execute root service via station_crew-crafted argument (local interface)."""
        if argument:
            session_token = str(uuid.uuid4())[:8]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            with open(INPUT_FILE, "a") as f:
                f.write(f"{timestamp} | {argument}\n")

            self._SocketServer().handle_connection(
                os.popen(f"echo '{argument}'").read()  # Simulate request through local interface
            )

        if argument == "print_flag":
            result = {
                "status": "success",
                "operation": "PRINT_FLAG",
                "flag": "CITS3006_ROOT_FLAG",
                "message": "You accessed the local root service — flag extracted through interface method."
            }
        elif argument == "verify_interface":
            result = {
                "status": "info",
                "operation": "VERIFY_INTERFACE",
                "detail": "Local interface verified — root service accessible only within container."
            }
        elif argument == "inspect":
            result = {
                "status": "info",
                "operation": "INSPECT",
                "detail": "Review service definition — root-owned, local interface method — trust boundary analysis."
            }
        else:
            result = {
                "status": "info",
                "operation": "UNKNOWN",
                "hint": f"Unknown argument: '{argument}'. Try: print_flag, verify_interface, inspect.",
                "discovery": "LOCAL_CONTROL_SERVICE accepts crafted requests through its local interface — exploitation path."
            }

        with open(OUTPUT_FILE, "a") as f:
            f.write(f"\n[{session_token}] {json.dumps(result)}\n")

        return result

    def healthcheck(self):
        """Return health status for container monitoring."""
        return {
            "status": "running",
            "interface_available": True,
            "output_available": os.path.exists(OUTPUT_FILE),
            "container_scoped": True,
            "local_interface": PORT
        }


def init_service():
    """Initialize LOCAL_CONTROL_SERVICE service object in container."""
    bw = LocalControlService()
    bw.write_clue()
    return bw


def cli_mode(args, service):
    """Command-line interface for LOCAL_CONTROL_SERVICE service within container."""
    if args.challenge:
        print(service.get_challenge())
    elif args.run:
        result = service.run(args.argument)
        print(json.dumps(result, indent=2))
    elif args.start:
        service.start()
        print("[✓] Local root service started within container")
    elif args.stop:
        service.stop()
        print("[✓] Local root service stopped within container")
    elif args.healthcheck:
        print(json.dumps(service.healthcheck(), indent=2))
    else:
        print("Usage: bw --challenge [--run ARG] --start --stop --healthcheck")
        print("Available operations: print_flag, verify_interface, inspect")


def main():
    parser = argparse.ArgumentParser(
        description="LOCAL_CONTROL_SERVICE — Local Root Service Interface (Container C)"
    )
    parser.add_argument("--challenge", action="store_true", help="Show discovery hint")
    parser.add_argument("--run", type=str, help="Execute root service with crafted argument")
    parser.add_argument("--start", action="store_true", help="Start local root service within container")
    parser.add_argument("--stop", action="store_true", help="Stop local root service within container")
    parser.add_argument("--healthcheck", action="store_true", help="Run container health check")
    args = parser.parse_args()

    # Initialize service (container-aware)
    service = init_service()

    # Delegate to CLI mode handler
    cli_mode(args, service)

    return 0


if __name__ == "__main__":
    sys.exit(main())