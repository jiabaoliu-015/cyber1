#!/usr/bin/env bash
#
# RECOVERED ARTIFACT 1 — Reset Script (Runtime-Reconstructed Secret)
#
# Ensures the challenge returns to its clean state after play/testing.
# All operations scoped within the Slice D repository environment.
#
# Usage: ./reset_runtime_secret.sh
#
# This reset:
#   1. Removes compiled binary (player rebuilds if needed)
#   2. Cleans runtime artifacts
#   3. Restores baseline clue file
#
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

D_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BINARY="$D_DIR/runtime_secret_binary"
CLUE_FILE="$D_DIR/entry/runtime_secret_clue.txt"

EXIT_CODE=0

write_clues(){
    cat > "$CLUE_FILE" << 'BASELINE_EOF'
RECOVERED ARTIFACT 1 — Runtime-Reconstructed Secret

A secret/credential has been reconstructed at runtime via mathematical operations.
Strings alone will NOT reveal the answer — you must reverse-engineer the algorithm.

CLUES for the solver:
1. The binary takes 5 integer parameters and transforms them
2. Operations include: multiply by 7, XOR with 0xFF, multiply by 3,
   bit-reversal of a byte, addition, subtraction with modulo adjustment
3. Output is a 4-character hexadecimal digest
4. Tools: strings, objdump, readelf, nm — find the constants and reconstruct
5. The formula: ((param1*7)+(param2^0xFF))*3 + reverse_byte(param3) + param4 - ((param5%3)*2)

Hint: Run the binary, then disassemble. What is computed at runtime?
BASELINE_EOF
    echo "[✓] Clue file written to $CLUE_FILE"
}

main_reset(){
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║      RECOVERED ARTIFACT 1 — Reset                                      ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║ Restoring clean state for runtime-reconstructed secret  ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""

    if [[ -f "$BINARY" ]]; then
        rm -f "$BINARY"
        echo "[✓] Removed compiled binary: $BINARY"
    else
        echo "[ℹ] Binary not found — no action needed"
    fi

    echo ""
    clean_artifacts
    echo ""
    write_clues
    echo ""
}

clean_artifacts(){
    # Remove any accumulated temporary files
    local temp_files=("$D_DIR/artifact1_output.txt" "$D_DIR/artifact1_debug.log")
    for artifact in "${temp_files[@]}"; do
        if [[ -e "$artifact" ]]; then
            rm -f "$artifact"
            echo "[✓] Cleaned artifact: $artifact"
        fi
    done
}

main(){
    main_reset
    exit $EXIT_CODE
}

# Header for direct invocation
echo "╔══════════════════════════════════════════════════════╗"
echo "║           RECOVERED ARTIFACT 1 Reset Script — Use: '$0'              ║"
echo "╚══════════════════════════════════════════════════════╝"

main