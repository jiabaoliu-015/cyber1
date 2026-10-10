#!/usr/bin/env python3
"""
landfall_link — the ground-side receiver (the company / "mission-control").

THE VULNERABILITY: it accepts any well-formed TM frame with NO freshness check
and NO authentication. A stale or replayed frame is accepted exactly like a
fresh one. It only logs "last status seen". This is what makes the replay
attack blind the ground side.

It reports every accepted frame to flag_gate; the gate notices when a seq is
accepted twice (a replay got through) and marks the ground blinded.

Also exposes a read-only status line so linkstat can show what ground last saw:
  STATUS -> "seq=<n> ts=<ts> hs=<status>\n"
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
PORT = int(os.getenv("LANDFALL_PORT", "9101"))

_last = {"seq": None, "ts": None, "hs": None}
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
                        f"seq={_last['seq']} ts={_last['ts']} hs={_last['hs']}\n".encode()
                    )
                continue
            f = F.parse(line)
            if not f or f.get("seq") is None:
                continue
            # NO freshness check, NO auth check -> accept it.
            with _lock:
                _last.update(seq=f["seq"], ts=f.get("ts"), hs=f.get("hs"))
            GC.report("LANDFALL", seq=f["seq"], hash=F.frame_hash(line))


def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(64)
    print(f"[landfall_link] ground receiver on {PORT} (no freshness / no auth)", flush=True)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=_serve, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
