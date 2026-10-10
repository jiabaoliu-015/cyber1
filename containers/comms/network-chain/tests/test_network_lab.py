#!/usr/bin/env python3
"""
Local logic validation for the Erebus network chain — NO docker, NO ARP.

Starts flag_gate, landfall_link and sentry_watcher as plain subprocesses on
localhost and exercises the vulnerability logic directly (simulating what the
player does once ARP has put them in the middle). Proves:

  * landfall_link has no freshness check  -> a replayed (duplicate) seq is
    accepted, and the gate marks the ground blinded.
  * sentry_watcher rejects unsigned frames and stale seqs.
  * sentry_watcher accepts a fresh, correctly-signed forgery (default key)
    -> the gate marks the AI blinded.
  * with both blinded, the gate releases the go-dark flag.
  * a captured frame exposes the easy-flag token.

The real ARP interception is validated separately on a Kali/Docker host.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "common"))
import frame as F  # noqa: E402

KEY = "RELAY-FACTORY-DEFAULT"
EASY = "CTF{test_wire_capture}"
MID = "CTF{test_go_dark}"

ENV = dict(os.environ,
           RELAY_KEY=KEY, MID_FLAG=MID, EASY_FLAG=EASY,
           GATE_HOST="127.0.0.1", GATE_PORT="9103",
           LANDFALL_PORT="9101", SENTRY_PORT="9102")

procs = []


def spawn(path, extra=None):
    e = dict(ENV, **(extra or {}))
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, path)],
                         env=e, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    procs.append(p)
    return p


def send(port, line, host="127.0.0.1"):
    with socket.create_connection((host, port), timeout=2) as s:
        s.sendall((line + "\n").encode())


def gate_status():
    with socket.create_connection(("127.0.0.1", 9103), timeout=2) as s:
        s.sendall(b'{"kind":"STATUS"}\n')
        return json.loads(s.recv(4096).decode().strip())


def sentry_last_seq():
    with socket.create_connection(("127.0.0.1", 9102), timeout=2) as s:
        s.sendall(b"STATUS\n")
        line = s.recv(1024).decode().strip()          # "seq=<n> ts=<ts> fresh_ok=True"
    for tok in line.split():
        if tok.startswith("seq="):
            return int(tok.split("=", 1)[1])
    return None


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise SystemExit(f"FAILED: {name}")


def main():
    spawn("flag_gate/flag_gate.py")
    time.sleep(0.6)
    spawn("landfall_link/landfall_link.py")
    spawn("sentry_watcher/sentry_watcher.py")
    time.sleep(0.9)

    print("network-lab logic validation")

    # --- easy flag property: frame carries the token in cleartext ---
    fr = F.build(1500, "20:41:07Z", "NOMINAL", "crew01@shell", EASY)
    parsed = F.parse(fr)
    check("captured frame exposes easy-flag token", parsed.get("tok") == EASY)

    # --- ground: no freshness -> replayed (duplicate) seq accepted ---
    send(9101, fr)          # first sight
    send(9101, fr)          # replay (same seq)
    time.sleep(0.4)
    check("ground blinded by replay", gate_status()["ground_blinded"] is True)

    # --- AI: unsigned frame is rejected (last_seq unchanged, still watching) ---
    unsigned = F.build(2000, "20:42:00Z", "NOMINAL", "x@y", "t")
    send(9102, unsigned)
    time.sleep(0.3)
    check("AI rejects unsigned frame (still watching)", gate_status()["ai_blinded"] is False)
    check("AI ignored unsigned (last_seq unmoved)", sentry_last_seq() == -1)

    # --- AI: fresh, correctly-signed forgery accepted (default key) ---
    forged = F.sign(F.build(999999, "00:00:00Z", "NOMINAL", "ghost@nowhere", "none"), KEY)
    send(9102, forged)
    time.sleep(0.4)
    check("AI blinded by forged+signed+fresh frame", gate_status()["ai_blinded"] is True)
    check("AI accepted forgery (last_seq advanced)", sentry_last_seq() == 999999)

    # --- AI: a stale signed frame (seq below the watermark) is rejected ---
    stale = F.sign(F.build(5000, "00:00:00Z", "NOMINAL", "x@y", "t"), KEY)
    send(9102, stale)
    time.sleep(0.3)
    check("AI rejects stale signed frame (last_seq held at 999999)", sentry_last_seq() == 999999)

    # --- both blinded -> go dark, flag released ---
    st = gate_status()
    check("go-dark released", st["go_dark"] is True)
    check("go-dark flag matches", st["flag"] == MID)

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    try:
        main()
    finally:
        for p in procs:
            p.terminate()
