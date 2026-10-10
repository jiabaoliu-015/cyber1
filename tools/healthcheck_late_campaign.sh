#!/usr/bin/env bash
# Validate prerequisites and narrative artefacts for the local D → E segment.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
command -v python3 >/dev/null
command -v gcc >/dev/null
for f in \
  "$ROOT/containers/operations/entry/post_root_handoff.txt" \
  "$ROOT/containers/critical/offline-artifacts/entry/privilege_handoff.txt" \
  "$ROOT/containers/critical/offline-artifacts/solvers/crypto_solver.py" \
  "$ROOT/challenges/completion/evidence/THREAD_02.missing" \
  "$ROOT/challenges/completion/scripts/assemble_evidence.py"; do
  test -r "$f"
done
python3 -c 'import cryptography' >/dev/null
printf 'Late-campaign health check: PASS\n'
