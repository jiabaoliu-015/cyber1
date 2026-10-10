#!/usr/bin/env python3
"""
event_svc — the station's session/access ledger.

Runs continuously, holding recent session/access events. beacon_relay pulls
the current session list from here each cycle to build its status frame, so the
captured downlink carries real, live station activity (that is the NET-01
"read the transmission" payload).

Protocol (newline text on TCP):
  GET_SESSIONS  -> "crew01@shell,med@medbay,...\n"
"""
from __future__ import annotations

import os
import socket
import threading
import time

HOST = "0.0.0.0"
PORT = int(os.getenv("EVENT_PORT", "9100"))

# Seed of "who is currently active" — beacon reports these to ground.
# In a live box this list would churn; kept static here for reproducibility.
_SESSIONS = [
    "crew01@shell",
    "med@medbay",
    "sci@lab",
    "linkmaint@relay",
]


def _serve(conn: socket.socket) -> None:
    with conn:
        conn.settimeout(5)
        try:
            req = conn.recv(256).decode("utf-8", "replace").strip()
        except socket.timeout:
            return
        if req.upper().startswith("GET_SESSIONS"):
            conn.sendall((",".join(_SESSIONS) + "\n").encode())


def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(32)
    print(f"[event_svc] session ledger on {PORT}", flush=True)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=_serve, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    # touch time import so linters keep it; also a heartbeat log
    _ = time.time()
    main()
