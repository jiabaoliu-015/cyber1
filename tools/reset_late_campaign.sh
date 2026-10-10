#!/usr/bin/env bash
# Reset only the local Slice D → Slice E campaign segment.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3 "$ROOT/containers/critical/offline-artifacts/scripts/reset_crypto_lab.py"
"$ROOT/challenges/completion/scripts/reset.sh"
rm -f "$ROOT/containers/critical/offline-artifacts/artifact3_binary"
printf 'Late-campaign reset complete: Slice D fixtures and INCIDENT ARCHIVE are clean.\n'
