#!/usr/bin/env python3
"""Solve the obfuscated agent firmware: recover the officer-path Hard flag.

The firmware's embedded loader stub is a decoy (wrong key -> decoy output).
The live stage: find marker AGENT-STAGE2:, base64-decode, REVERSE the bytes,
XOR with the officer-console key (default OBFUS-1ST-0FF, hinted in
data/engineer_logs/ + data/shift_notes/), print the flag.

Usage:
  python3 solve_agent.py /tmp/agent_firmware.bin
  python3 solve_agent.py /tmp/agent_firmware.bin --key OBFUS-1ST-0FF
  python3 solve_agent.py --url http://127.0.0.1:8082/api/agent/binary --token PWR-3002-STAT
"""
import argparse
import base64
from pathlib import Path

MARKER = b"AGENT-STAGE2:"
DEFAULT_KEY = "OBFUS-1ST-0FF"


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def decode(raw: bytes, key: str) -> str:
    idx = raw.rfind(MARKER)
    if idx < 0:
        raise SystemExit("marker AGENT-STAGE2: not found — is this the firmware image?")
    blob = raw[idx + len(MARKER):].strip().split()[0]
    return xor_bytes(base64.b64decode(blob)[::-1], key.encode()).decode()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image", nargs="?", default="/tmp/agent_firmware.bin")
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
    flag = decode(raw, a.key)
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
