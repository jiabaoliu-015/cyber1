#!/usr/bin/env python3
"""
flag_gate — scoring backend for the Erebus link chain.

NOT part of the attack surface. Players never interact with it directly; it
only observes ground truth and what each watcher accepted, and releases the
GO-DARK (mid) token when BOTH conditions hold:

  * ground blinded  -> landfall_link accepted a frame whose seq it had
                       already seen (a replay was accepted).
  * ai blinded      -> sentry_watcher accepted a frame that beacon_relay
                       never actually sent (a forged frame passed).

Reports arrive as newline JSON on TCP:
  {"kind":"TRUE",    "seq":N, "hash":H}          from beacon_relay (ground truth)
  {"kind":"LANDFALL","seq":N, "hash":H}          from landfall_link (accepted)
  {"kind":"SENTRY",  "seq":N, "hash":H}          from sentry_watcher (accepted)

Status query:
  {"kind":"STATUS"}  -> {"ground_blinded":bool,"ai_blinded":bool,
                         "go_dark":bool,"flag":<token or null>}
"""
from __future__ import annotations

import json
import os
import socket
import threading

HOST = "0.0.0.0"
PORT = int(os.getenv("GATE_PORT", "9103"))
MID_FLAG = os.getenv("MID_FLAG", "CTF{PLACEHOLDER_go_dark}")
# Shared secret the trusted services attach to their reports. Set only in the
# service containers' env — never on the player terminal and never in any file
# the player can read. STATUS needs no token (read-only). When unset (local
# logic test), auth is skipped so the test still runs.
GATE_TOKEN = os.getenv("GATE_TOKEN", "")

_lock = threading.Lock()
_true_hashes: set[str] = set()          # frames beacon really sent
_landfall_seen: set[int] = set()        # seqs landfall has accepted
_state = {"ground_blinded": False, "ai_blinded": False}


def _handle(msg: dict) -> dict | None:
    kind = msg.get("kind")
    # Report kinds must carry the shared secret; a forged report from the
    # player segment (no token) is dropped. STATUS is open (read-only).
    if kind in ("TRUE", "LANDFALL", "SENTRY") and GATE_TOKEN:
        if msg.get("token") != GATE_TOKEN:
            return None
    with _lock:
        if kind == "TRUE":
            _true_hashes.add(msg.get("hash", ""))
            return {"ok": True}   # ack so the relay can order truth-before-send
        if kind == "LANDFALL":
            seq = msg.get("seq")
            if seq in _landfall_seen:
                # a seq accepted twice => a replay got through
                _state["ground_blinded"] = True
            else:
                _landfall_seen.add(seq)
            return None
        if kind == "SENTRY":
            h = msg.get("hash", "")
            if h and h not in _true_hashes:
                # sentry accepted something beacon never sent => forged
                _state["ai_blinded"] = True
            return None
        if kind == "STATUS":
            go = _state["ground_blinded"] and _state["ai_blinded"]
            return {
                "ground_blinded": _state["ground_blinded"],
                "ai_blinded": _state["ai_blinded"],
                "go_dark": go,
                "flag": MID_FLAG if go else None,
            }
    return None


def _serve(conn: socket.socket) -> None:
    with conn:
        buf = b""
        conn.settimeout(5)
        try:
            data = conn.recv(65536)
        except socket.timeout:
            return
        buf += data
        for line in buf.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line.decode())
            except (ValueError, UnicodeDecodeError):
                continue
            reply = _handle(msg)
            if reply is not None:
                conn.sendall((json.dumps(reply) + "\n").encode())


def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(64)
    print(f"[flag_gate] scoring backend on {PORT}", flush=True)
    while True:
        conn, _ = s.accept()
        threading.Thread(target=_serve, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
