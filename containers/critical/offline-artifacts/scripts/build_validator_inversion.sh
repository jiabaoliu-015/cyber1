#!/usr/bin/env bash
# Build RECOVERED ARTIFACT 2 reproducibly relative to this repository checkout.
set -euo pipefail

SLICE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
SOURCE="$SLICE_DIR/source/validator_inversion/key_validator.c"
BINARY="$SLICE_DIR/artifact2_binary"

command -v gcc >/dev/null || { echo "gcc is required" >&2; exit 1; }
gcc -std=c11 -Wall -Wextra -Werror -O2 -fno-ident -o "$BINARY" "$SOURCE"
printf 'Built %s\n' "$BINARY"
