#!/usr/bin/env bash
set -euo pipefail
D=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO=$(CDPATH= cd -- "$D/../../.." && pwd)
gcc -std=c11 -Wall -Wextra -Werror -O2 -fno-ident -o "$D/artifact3_binary" "$REPO/containers/operations/services/medbay/route_selector.c"
python3 "$D/scripts/reset_crypto_lab.py"
printf 'Built RECOVERED ARTIFACT 3 and reset Uplink Vault fixtures.\n'
