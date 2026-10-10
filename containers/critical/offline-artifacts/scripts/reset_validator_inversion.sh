#!/usr/bin/env bash
# Reset RECOVERED ARTIFACT 2 to its source-controlled baseline.
set -euo pipefail

SLICE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
rm -f "$SLICE_DIR/artifact2_binary"
printf 'RECOVERED ARTIFACT 2 reset: removed generated binary. Run scripts/build_validator_inversion.sh to rebuild.\n'
