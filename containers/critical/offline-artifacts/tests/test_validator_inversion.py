#!/usr/bin/env python3
"""Portable acceptance checks for RECOVERED ARTIFACT 2."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SLICE_DIR = Path(__file__).resolve().parents[1]
BUILD = SLICE_DIR / 'scripts' / 'build_validator_inversion.sh'
RESET = SLICE_DIR / 'scripts' / 'reset_validator_inversion.sh'
BINARY = SLICE_DIR / 'artifact2_binary'
SOLVER = SLICE_DIR / 'solvers' / 'validator_inversion_solver.py'
EXPECTED_FLAG = 'CTF{egg2_validator_path}'


def run(args: list[str], input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, input=input_text, text=True, capture_output=True, check=False)


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(detail)


def main() -> int:
    reset = run([str(RESET)])
    require(reset.returncode == 0 and not BINARY.exists(), 'reset did not remove generated binary')

    build = run([str(BUILD)])
    require(build.returncode == 0 and BINARY.exists(), 'build failed: ' + build.stderr)

    solver = run([sys.executable, str(SOLVER)])
    require(solver.returncode == 0, 'solver failed')
    key = solver.stdout.split('Derived recovery key:', 1)[1].splitlines()[0].strip()
    require(len(key) == 16, 'solver did not derive a 16-byte key')

    rejected = run([str(BINARY)], 'wrong-key\n')
    require(rejected.returncode == 1 and 'remains sealed' in rejected.stdout, 'invalid key was not rejected')

    accepted = run([str(BINARY)], key + '\n')
    require(accepted.returncode == 0, 'derived key was not accepted')
    require(EXPECTED_FLAG in accepted.stdout, 'expected flag missing after valid key')

    string_scan = run(['strings', str(BINARY)])
    require(key not in string_scan.stdout, 'valid key leaked through strings')
    require(EXPECTED_FLAG not in string_scan.stdout, 'flag leaked through strings')

    reset_again = run([str(RESET)])
    require(reset_again.returncode == 0 and not BINARY.exists(), 'second reset did not restore baseline')
    print('RECOVERED ARTIFACT 2 portable acceptance checks: PASS')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (AssertionError, IndexError) as error:
        print('RECOVERED ARTIFACT 2 portable acceptance checks: FAIL —', error, file=sys.stderr)
        raise SystemExit(1)
