#!/usr/bin/env python3
"""Solve the Black Box optics portrait: recover Mid flag + RIGHT Captain Key.

Reads a portrait downloaded with `power blackbox-image` (or a live URL), finds the trailing
PWR-BLACKBOX-V1:<base64> marker, base64-decodes, XORs with the side-channel
key (default BECK-4217-K9 from data/blackbox_logs/), prints '<MID>|<RIGHT>'.

Usage:
  python3 solve_image.py /tmp/astronaut_stego.jpeg
  python3 solve_image.py /tmp/astronaut_stego.jpeg --key BECK-4217-K9
  python3 solve_image.py --url http://127.0.0.1:8082/api/blackbox/image --token PWR-3002-STAT
"""
import argparse
import base64
import sys
from pathlib import Path

MARKER = b"PWR-BLACKBOX-V1:"
DEFAULT_KEY = "BECK-4217-K9"


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def decode(raw: bytes, key: str) -> str:
    idx = raw.rfind(MARKER)
    if idx < 0:
        raise SystemExit("marker PWR-BLACKBOX-V1: not found — is this the stego portrait?")
    blob = raw[idx + len(MARKER):].strip().split()[0]
    cipher = base64.b64decode(blob)
    kb = key.encode()
    return bytes(c ^ kb[i % len(kb)] for i, c in enumerate(cipher)).decode()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image", nargs="?", default="/tmp/astronaut_stego.jpeg")
    p.add_argument("--key", default=DEFAULT_KEY)
    p.add_argument("--url", default=None)
    p.add_argument("--token", default=None)
    a = p.parse_args()
    if a.url:
        import urllib.request

        req = urllib.request.Request(a.url, headers={"X-Token": a.token or ""})
        raw = urllib.request.urlopen(req, timeout=10).read()
    else:
        raw = Path(a.image).read_bytes()
    bundle = decode(raw, a.key)
    print(bundle)
    if "|" in bundle:
        mid, right = bundle.split("|", 1)
        print(f"mid_flag: {mid}")
        print(f"right_key: {right}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
