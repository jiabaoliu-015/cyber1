#!/usr/bin/env python3
"""Deterministic INCIDENT ARCHIVE evidence assembler. Synthetic CTF data only."""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "evidence"
EXPECTED = "THREAD_02=evidence-evidence"
FINAL_FLAG = "CTF{the_web_marks_john_liability}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble recovered INCIDENT ARCHIVE evidence.")
    parser.add_argument("--thread-02", required=True, help="Recovered THREAD_02 record from Uplink Vault")
    args = parser.parse_args()
    if args.thread_02 != EXPECTED:
        print("INCIDENT ARCHIVE: THREAD_02 verification failed; archive remains incomplete.")
        return 1

    print("INCIDENT ARCHIVE: THREAD_02 accepted. Evidence set complete.\n")
    for name in ("THREAD_01.txt", "THREAD_02.txt", "THREAD_03.txt", "THREAD_04.txt"):
        print(f"===== {name} =====")
        print((ARCHIVE / name).read_text(encoding="utf-8").rstrip())
        print()
    print("===== INCIDENT ARCHIVE SYSTEM NOTICE =====")
    print("Recovery path correlation complete. Station incident records indexed for review.")
    print("Observation status: ACTIVE. Every recovered thread was recorded.")
    print(f"Final evidence flag: {FINAL_FLAG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
