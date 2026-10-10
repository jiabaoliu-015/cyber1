# ARTEFACT 2 local verification — 19 September 2026

Host architecture: ARM64 (`aarch64`)

Command run from the repository root:

```bash
python3 containers/critical/offline-artifacts/tests/test_validator_inversion.py
```

Observed result:

```text
ARTEFACT 2 portable acceptance checks: PASS
```

The acceptance test performs a clean reset, native GCC build, reference-solver
derivation, invalid-key rejection, derived-key acceptance, printable-string
leakage checks for both the key and flag, and a second reset. AMD64 is not yet
verified and needs a teammate/CI run before assessment sign-off.