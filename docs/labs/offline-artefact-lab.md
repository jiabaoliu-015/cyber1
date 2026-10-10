# Offline Artefact Lab

RE-01/02 and ADV-01/02 live in `containers/critical/offline-artifacts/`. RE-03 is now the standalone Medbay Terminal path in `containers/operations/services/medbay/`; its native selector remains independently buildable through the legacy offline-artifact script for compatibility.

| ID | Primary requirement | Artefact area |
| --- | --- | --- |
| RE-01 | Runtime-reconstructed secret | `runtime-secret/` |
| RE-02 | Validator inversion | `source/validator_inversion/` |
| RE-03 | Real-versus-decoy medical audit path | `containers/operations/services/medbay/route_selector.c` |
| ADV-01 | Cryptographic nonce reuse | `data/` and `solvers/crypto_solver.py` |
| ADV-02 | Non-time-based oracle | `source/oracle_lab/` |

`OPT-01` is optional and is not counted in the required inventory. Use the Critical reset/build scripts for the other artifacts, and the [Medbay standalone instructions](../../containers/operations/services/medbay/README.md) for RE-03. Consult `./tools/challenge show <ID>` for the inventory.
