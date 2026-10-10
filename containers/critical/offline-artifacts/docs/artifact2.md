# ARTEFACT 2 — Custom Key Validator

## Challenge card

- **Goal:** recover the 16-character recovery key accepted by `artifact2_binary`.
- **Narrative output:** accepted validation grants the player a synthetic `THREAD_02` recovery record and the ARTEFACT 2 flag.
- **Learning objective:** reverse a bounded per-byte validator and invert rotate/XOR operations; distinguish validation logic from guessing.
- **Discovery:** read `entry/validator_inversion_clue.txt`, run the binary, then use `strings`, `objdump -d` or equivalent to locate the fixed-length check, per-byte salt, rotate count and expected transformed bytes.
- **Prerequisite:** a local copy of the binary and ordinary C/reversing tooling. No network access is used.

## Intended solve

The validator requires exactly 16 characters and checks, for each index `i`:

```text
expected[i] = rotl8(candidate[i] XOR salt[i], (i mod 5) + 1)
```

Invert the operation:

```text
candidate[i] = rotr8(expected[i], (i mod 5) + 1) XOR salt[i]
```

The reference implementation is `solvers/validator_inversion_solver.py`. Build and test:

```bash
./scripts/build_validator_inversion.sh
python3 tests/test_validator_inversion.py
```

For a manual reference solve:

```bash
key=$(python3 solvers/validator_inversion_solver.py | sed -n 's/^Derived recovery key: //p')
printf '%s\n' "$key" | ./artifact2_binary
```

## Reset

```bash
./scripts/reset_validator_inversion.sh
./scripts/build_validator_inversion.sh
```

The reset removes only the generated binary. Source, clue and solver remain source-controlled, so a rebuild is deterministic.

## Mitigation

Real recovery keys should not be protected by a reversible client-side transformation. Store password verifiers using a slow, salted password-hashing scheme and perform verification server-side. Do not ship validation constants and logic that let an attacker derive the secret offline.

## Fairness / unintended shortcuts

- The accepted key and flag are not printable strings in the compiled binary.
- `strings` may reveal UI text but not the answer.
- The challenge intentionally remains solvable via normal control-flow and data-flow analysis, without brute force, anti-debugging or packing.
- The maintainer source is for reproducible builds and should not be placed in the player-only deployment directory.
