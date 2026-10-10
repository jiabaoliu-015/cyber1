# Remaining Offline Artefact Lab challenges

## ARTEFACT 3 — real versus decoy path
Build with `scripts/build_remaining_d.sh` (which uses the canonical source in `containers/operations/services/medbay/`), trace `route()` through the three XOR-masked records, then submit the authentic candidate with `artifact3_binary --verify <candidate>`. RE-03 now also opens the officer-only Medbay Terminal archive; its `THREAD_03` receipt remains corroborating evidence for the separate Completion Check, not a mandatory final lock. Mitigation: authenticate records and avoid routing sensitive data based on client-visible logic.

## Crypto Lab — AES-GCM nonce reuse
`data/uplink_vault.json` contains a known plaintext/ciphertext and a target ciphertext produced with the same AES-GCM key and nonce. `solvers/crypto_solver.py` XORs the known pair to recover the reused CTR keystream and decrypts the target. Its exact `THREAD_02=...` output is the required Completion Check completion record; pass it to `../challenges/completion/scripts/assemble_evidence.py --thread-02 '<record>'`. Mitigation: generate a unique nonce per AES-GCM encryption and reject nonce reuse.

## Oracle Lab — deterministic oracle
`source/oracle_lab/oracle.py` binds only to `127.0.0.1:8091`. It returns 202 for a correct prefix, 403 otherwise, and 200 only for the full token. `solvers/oracle_solver.py` recovers it incrementally without timing measurements. It is corroborating evidence, not required to assemble Completion Check. Mitigation: return indistinguishable errors and use constant-work validation.

Run all three: `python3 tests/test_offline_artefacts.py`.
