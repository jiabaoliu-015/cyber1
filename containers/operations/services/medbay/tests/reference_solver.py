#!/usr/bin/env python3
"""Maintainer-only reference for the RE-03 data/control-flow route."""
from __future__ import annotations

ENCODED = [
    bytes.fromhex("17 1f 1e 77 6d 1c 68 19 77 63 18 62 6b 77 69 6e 6b 6a 77 1b 6f 1c 68"),
    bytes.fromhex("17 1f 1e 77 63 1b 6b 1e 77 6c 6d 1f 1c 77 6a 62 68 18 77 19 69 63 6a"),
    bytes.fromhex("17 1f 1e 77 6e 19 6c 6d 77 1e 6b 69 1f 77 6f 1b 68 6a 77 18 62 1c 6b"),
]


def reference() -> str:
    state = 0x6D
    for i, step in enumerate((0x31, 0xA4, 0x07, 0xD2)):
        state = ((state ^ step) + i * 19) & 0xFF
    return bytes(byte ^ 0x5A for byte in ENCODED[state % 3]).decode("ascii")


if __name__ == "__main__":
    print(reference())
