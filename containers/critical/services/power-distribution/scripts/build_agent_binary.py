#!/usr/bin/env python3
"""Build runtime agent firmware into a writable generated-assets directory."""
import argparse
import base64
import os
from pathlib import Path

DEFAULT_OUTPUT = Path(os.environ.get("PWR_ASSET_DIR", str(Path(__file__).resolve().parent.parent / "generated-assets"))) / "agent_firmware.bin"
MARKER = b"AGENT-STAGE2:"


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def build(output: Path) -> Path:
    flag = os.environ.get("PWR_FLAG_AGENT")
    if not flag:
        raise ValueError("PWR_FLAG_AGENT must be supplied at runtime")
    key = os.environ.get("PWR_OBFUS_KEY", "OBFUS-1ST-0FF")
    blob = base64.b64encode(xor_bytes(flag.encode(), key.encode())[::-1]).decode()
    body = "\n".join([
        "ISVM-AGENT-FW/2.3 Automated Agent System Module — firmware dump",
        "build: meridian-yard-044 | rod-driver interlock: PRESENT",
        "note: field loader below is from draft v0.3 and is KNOWN-BROKEN",
        "loader: b64decode(stage1) then xor with key AGENT-00 then run",
        "CTF{agent_decoy_dead00}",
        "stage1: VFUxTlUxSlJQVEk9 (draft marker, do not trust)",
        "key: AGENT-00 (draft key, wrong)",
        f"{MARKER.decode()}{blob}",
        "trailer: checksum 0x17hz-ok | object K-9 thermal nominal",
        "CTF{agent_decoy_dead01}",
        "",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(body.encode())
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"wrote {build(args.output)}")
