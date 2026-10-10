# Slice D — Recovered Station Artifacts

This directory contains isolated advanced/reverse-engineering challenge artefacts.

## Implemented

- **RECOVERED ARTIFACT 1 — Runtime-reconstructed secret:** `source/runtime_secret/`, `runtime_secret_binary`, `solvers/runtime_secret_solver.py`.
- **RECOVERED ARTIFACT 2 — Custom key validator:** `source/validator_inversion/`, `scripts/build_validator_inversion.sh`, `scripts/reset_validator_inversion.sh`, `solvers/validator_inversion_solver.py`, `tests/test_validator_inversion.py`, and `docs/artifact2.md`.

## RECOVERED ARTIFACT 2 quick verification

```bash
cd containers/critical/offline-artifacts
python3 tests/test_validator_inversion.py
```

The test performs reset → deterministic build → solver derivation → rejection of an invalid key → acceptance of the derived key → `strings` leakage check → reset.

RECOVERED ARTIFACT 3's authoritative source and playable chain now live in the [Medbay Terminal](../../operations/services/medbay/README.md); the local artifact build remains for legacy compatibility. Uplink Vault and Station Audit remain here. The
post-root recovery pack identifies Uplink Vault's `THREAD_02` output as the Incident Archive
completion record, and `tests/integration/test_full_campaign.py` exercises the A→E
runtime spine. RECOVERED ARTIFACT 1 remains path-dependent; see the root checklist for the stated
limitation and remaining human reproduction work.
