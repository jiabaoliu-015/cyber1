#!/usr/bin/env bash
set -euo pipefail
DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
gcc -std=c11 -Wall -Wextra -Werror -O2 -fno-ident -o "$DIR/artifact3_binary" "$DIR/route_selector.c"
printf 'Built medbay RE-03 selector for this host architecture.\n'
