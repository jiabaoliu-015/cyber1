#!/usr/bin/env bash
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
rm -f "$ROOT/evidence/assembly.log"
printf 'INCIDENT ARCHIVE reset complete: THREAD_02 remains absent until supplied to the assembler.\n'
