# Completion Check — Final Evidence Archive

## Player progression

1. Recover `THREAD_02=evidence-evidence` from Crypto Lab.
2. Read `entry/completion_locator.txt` and inspect `evidence/`; `THREAD_02.missing` explains exactly what is needed.
3. Assemble the set:

```bash
python3 scripts/assemble_evidence.py --thread-02 'THREAD_02=evidence-evidence'
```

The readout displays all four evidence fragments, then the LIABILITIES reveal and final flag.

## Thread provenance

- THREAD_01: initial Web Application/Network Service maintenance trail.
- THREAD_02: recovered from Crypto Lab’s AES-GCM nonce-reuse challenge.
- THREAD_03: authenticity established by ARTEFACT 3’s genuine execution path.
- THREAD_04: Completion Check observation log describing John’s recorded route.

## Reset and test

```bash
./scripts/reset.sh
python3 tests/test_completion.py
```

No network service, password guessing, or brute force is required. Mitigation is narrative/operational: segment evidence stores, authenticate archive access server-side, and avoid exposing recovery credentials through other vulnerable systems.
