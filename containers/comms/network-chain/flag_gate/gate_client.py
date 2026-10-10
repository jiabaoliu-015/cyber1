"""Tiny helper for services to report to flag_gate (best-effort, never fatal)."""
from __future__ import annotations

import json
import os
import socket

GATE_HOST = os.getenv("GATE_HOST", "flag_gate")
GATE_PORT = int(os.getenv("GATE_PORT", "9103"))
GATE_TOKEN = os.getenv("GATE_TOKEN", "")


def report(kind: str, **fields) -> dict | None:
    msg = {"kind": kind, **fields}
    if GATE_TOKEN and kind != "STATUS":
        msg["token"] = GATE_TOKEN
    try:
        with socket.create_connection((GATE_HOST, GATE_PORT), timeout=2) as s:
            s.sendall((json.dumps(msg) + "\n").encode())
            if kind in ("STATUS", "TRUE"):
                # STATUS returns the status dict; TRUE returns an ack so the
                # caller can guarantee ground-truth is recorded before sending.
                s.settimeout(2)
                data = s.recv(65536)
                return json.loads(data.decode().strip())
    except OSError:
        return None
    return None
