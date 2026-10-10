#!/usr/bin/env python3
"""Uplink: a deterministic line-oriented TCP service for Slice B.

The deliberate flaw is that INFO exposes the same challenge value accepted as
the authentication token. It is a contained CTF exercise, not a secure auth
implementation.
"""
from __future__ import annotations

import argparse
import socketserver

RELAY_AUTH_USERNAME = "station_crew"
RELAY_AUTH_TOKEN_SECRET = "uplink-auth-token-01"  # Deliberately unused by vulnerable auth.
SESSION_CHALLENGE = "536610cb"


def response_for(command: str) -> str:
    parts = command.strip().split()
    verb = parts[0].upper() if parts else ""
    if verb == "HELP":
        return (
            "Uplink Server v2.4 — old internal maintenance protocol.\n"
            "Commands: HELP, STATUS, INFO, AUTH <username> <token>\n"
        )
    if verb == "STATUS":
        return "Uplink Server v2.4\n[running] protocol: line-oriented TCP\n[port] 5432\n"
    if verb == "INFO":
        return (
            "Uplink Server v2.4\n[sessions]:\n"
            f"  - active: sess-uplink-01\n    challenge: {SESSION_CHALLENGE}\n"
            "    hint: the challenge and token share the same derivation path\n"
        )
    if verb == "AUTH":
        username = parts[1] if len(parts) > 1 else ""
        token = parts[2] if len(parts) > 2 else ""
        # Intentional weakness: trusts an INFO-visible value, not the secret.
        if username == RELAY_AUTH_USERNAME and token == SESSION_CHALLENGE:
            return (
                "authentication accepted — session 536610cb confirmed.\n"
                "Station SSH access granted.\n"
                "COMMS_RELAY_HOST=comms_relay.internal\n"
                "STATION_SSH_PATH=/uplink/handoff\n"
                "STATION_SSH_SSH_USER=station_crew\n"
                "STATION_SSH_SSH_CHALLEGE=536610cb\n"
            )
        return "authentication rejected — token does not match expected challenge.\n"
    return "unknown command; send HELP.\n"


class UplinkHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        while True:
            line = self.rfile.readline(4096)
            if not line:
                return
            self.wfile.write(response_for(line.decode("utf-8", errors="replace")).encode("utf-8"))
            self.wfile.flush()


class UplinkTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5432)
    args = parser.parse_args()
    with UplinkTCPServer((args.host, args.port), UplinkHandler) as server:
        print(f"Uplink Server listening on {args.host}:{args.port}", flush=True)
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
