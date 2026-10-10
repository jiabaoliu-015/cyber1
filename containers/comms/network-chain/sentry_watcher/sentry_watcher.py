#!/usr/bin/env python3
"""
sentry_watcher — the station AI's liveness monitor (ORACLE's eyes on the link).

Unlike the ground side, this one is smart:
  * FRESHNESS: it only accepts a frame whose seq is strictly greater than the
    last one it accepted. A replayed / stale frame is rejected. So a plain
    replay will NOT fool it.
  * AUTHENTICATION: it only accepts frames carrying a valid MAC.

THE WEAKNESS is not the checks themselves — it's that the MAC key is a FACTORY
DEFAULT left in place (relay.key / RELAY_KEY). Anyone who recovers that default
key can forge fresh, correctly-signed frames and feed them in, so the AI keeps
seeing "NOMINAL" while it is actually being spoon-fed. That is the AI-blinding
step.

Reports accepted frames to flag_gate; the gate marks the AI blinded when it
accepts a frame beacon_relay never actually sent (i.e. a forgery).

Status for linkstat:
  STATUS -> "seq=<n> ts=<ts> fresh_ok=<bool>\n"
"""
from __future__ import annotations

import os
import socket
import sys
import threading

sys.path.insert(0, "/app/common")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import frame as F  # noqa: E402

sys.path.insert(0, "/app/flag_gate")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flag_gate"))
import gate_client as GC  # noqa: E402

HOST = "0.0.0.0"
PORT = int(os.getenv("SENTRY_PORT", "9102"))
RELAY_KEY = os.getenv("RELAY_KEY", "RELAY-FACTORY-DEFAULT")

_state = {"last_seq": -1, "ts": None}
_lock = threading.Lock()


def _serve(conn: socket.socket) -> None:
    with conn:
        conn.settimeout(5)
        try:
            data = conn.recv(8192).decode("utf-8", "replace")
        except socket.timeout:
            return
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.upper() == "STATUS":
                with _lock:
                    conn.sendall(
                        f"seq={_state['last_seq']} ts={_state['ts']} fresh_ok=True\n".encode()
                    )
                continue
            f = F.parse(line)
            if not f or f.get("seq") is None:
                continue
            # 1) must be authenticated with a valid MAC
            if not F.verify_mac(line, RELAY_KEY):
                continue  # reject: unsigned / bad MAC
            # 2) must be fresh (strictly increasing seq)
            with _lock:
                if f["seq"] <= _state["last_seq"]:
                    continue  # reject: stale / replayed
                _state.update(last_seq=f["seq"], ts=f.get("ts"))
            GC.report("SENTRY", seq=f["seq"], hash=F.frame_hash(line))


def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(64)
    print(f"[sentry_watcher] AI liveness monitor on {PORT} (freshness + MAC required)", flush=True)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=_serve, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
