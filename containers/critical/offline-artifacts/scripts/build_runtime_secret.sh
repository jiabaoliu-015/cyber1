#!/usr/bin/env bash
#
# RECOVERED ARTIFACT 1 — Build Script (Runtime-Reconstructed Secret)
#
# Compiles the C source into a native binary for reverse engineering practice.
# All operations confined within the Slice D repository environment.
#
# Usage: ./build_runtime_secret.sh
#
# Prerequisites: gcc (standard C compiler)
#
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

D_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$D_DIR/source/runtime_secret"
BINARY="$D_DIR/runtime_secret_binary"

echo "╔══════════════════════════════════════════════════════╗"
echo "║    RECOVERED ARTIFACT 1 — Build Script (Runtime-Reconstructed Secret) ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Compiling C source to native binary                  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Build the binary to the correct absolute path
echo "[Building binary...]"
OUTPUT=$(gcc -Wall -Wextra -O2 -o "$BINARY" "$SOURCE_DIR/reconstruct_secret.c" 2>&1 || true)

if [[ ! -f "$BINARY" ]]; then
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║      [✗] Build failed — binary not created              ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo "$OUTPUT"
    exit 1
fi

echo "[✓] Binary compiled successfully: $BINARY"
echo ""

# Quick verification run using absolute path
echo "╔══════════════════════════════════════════════════════╗"
echo "║      Verification Run                                  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║ Running binary to verify output                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

echo "[Verifying binary output...]"
OUTPUT=$("$BINARY" 2>&1 || echo "ERROR")
echo "$OUTPUT"
echo ""

if [[ "$OUTPUT" == *"Reconstructed Secret (hex)"* ]]; then
    echo -e "${GREEN}[✓] RECOVERED ARTIFACT 1 build successful — binary runs correctly${NC}"
else
    echo -e "${RED}[✗] Unexpected output — check binary${NC}"
    echo "$OUTPUT"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║      Build Complete — Ready for reverse engineering    ║"
echo "╚══════════════════════════════════════════════════════╝"

exit 0