#!/usr/bin/env python3
"""Build the per-container optics artifact from the bundled source JPEG."""
import argparse
import base64
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "assets" / "astronaut.jpeg"
DEFAULT_OUTPUT = Path(os.environ.get("PWR_ASSET_DIR", str(ROOT / "generated-assets"))) / "astronaut_stego.jpeg"
MARKER = b"PWR-BLACKBOX-V1:"


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def build(source: Path, output: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(f"source image not found: {source}")
    raw = source.read_bytes()
    if not raw.startswith(b"\xff\xd8"):
        raise ValueError(f"source does not look like a JPEG: {source}")
    mid = os.environ.get("PWR_FLAG_MID")
    if not mid:
        raise ValueError("PWR_FLAG_MID must be supplied at runtime")
    right = os.environ.get("PWR_RIGHT_KEY", "CPT-RIGHT-9D2K-77QX")
    key = os.environ.get("PWR_XOR_KEY", "BECK-4217-K9").encode()
    idx = raw.rfind(MARKER)
    if idx >= 0:
        raw = raw[:idx].rstrip(b"\n")
    blob = base64.b64encode(xor_bytes(f"{mid}|{right}".encode(), key))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raw + b"\n" + MARKER + blob + b"\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"wrote {build(args.source, args.output)}")
