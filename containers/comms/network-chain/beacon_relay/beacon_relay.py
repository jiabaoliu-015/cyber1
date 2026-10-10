#!/usr/bin/env python3
"""
beacon_relay — the station's status transmitter.

Internal loop: every BEACON_INTERVAL seconds it pulls the live session list
from event_svc, builds a fixed-field TM frame (format C), and transmits it on
two channels:

  * ground feed  -> landfall_link   : UNauthenticated, cleartext. Carries the
                    link token (TOK) that the capture flag rewards.
  * ai feed      -> sentry_watcher  : the SAME frame, but MAC-signed with the
                    relay key, because the AI feed is "trusted".

It also reports the true frame hash to flag_gate so the scoring backend knows
ground truth (what was really sent).

The relay signing key is a FACTORY DEFAULT left in place — that is the weakness
the AI-blinding step abuses (see RELAY_KEY / relay.key).
"""
from __future__ import annotations

import os
import socket
import sys
import time

sys.path.insert(0, "/app/common")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import frame as F  # noqa: E402

sys.path.insert(0, "/app/flag_gate")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "flag_gate"))
import gate_client as GC  # noqa: E402

LANDFALL = (os.getenv("LANDFALL_HOST", "landfall_link"), int(os.getenv("LANDFALL_PORT", "9101")))
SENTRY = (os.getenv("SENTRY_HOST", "sentry_watcher"), int(os.getenv("SENTRY_PORT", "9102")))
EVENT = (os.getenv("EVENT_HOST", "event_svc"), int(os.getenv("EVENT_PORT", "9100")))
INTERVAL = float(os.getenv("BEACON_INTERVAL", "5"))
RELAY_KEY = os.getenv("RELAY_KEY", "RELAY-FACTORY-DEFAULT")
EASY_FLAG = os.getenv("EASY_FLAG", "CTF{PLACEHOLDER_wire_capture}")


def get_sessions() -> str:
    try:
        with socket.create_connection(EVENT, timeout=2) as s:
            s.sendall(b"GET_SESSIONS\n")
            return s.recv(4096).decode("utf-8", "replace").strip()
    except OSError:
        return "unknown@offline"


def send(dest, data: str) -> None:
    try:
        with socket.create_connection(dest, timeout=2) as s:
            s.sendall((data + "\n").encode())
    except OSError:
        pass


def main() -> None:
    print(f"[beacon_relay] transmitting every {INTERVAL}s -> ground {LANDFALL} / ai {SENTRY}", flush=True)
    seq = int(os.getenv("BEACON_SEQ_START", "1400"))
    while True:
        ts = time.strftime("%H:%M:%SZ", time.gmtime())
        sessions = get_sessions()
        ground_frame = F.build(seq, ts, "NOMINAL", sessions, EASY_FLAG)
        ai_frame = F.sign(ground_frame, RELAY_KEY)

        # Register ground-truth FIRST (blocks for ack) so a watcher's
        # accept-report can never beat the truth-report to the gate.
        GC.report("TRUE", seq=seq, hash=F.frame_hash(ground_frame))
        send(LANDFALL, ground_frame)   # cleartext, unauthenticated
        send(SENTRY, ai_frame)         # MAC-signed

        print(f"[beacon_relay] TX seq={seq} ts={ts}", flush=True)
        seq += 1
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
