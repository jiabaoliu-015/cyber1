# Five-container layout migration verification

Branch: `refactor/five-container-layout` from `origin/main` at `bb6023d2164779f80ec91950ddc1b505f3ea4b24`.

## Passed after migration

- `python3 tests/test_challenge_manifest.py` — 4/4 passed; all 19 manifest implementation paths exist.
- Gateway: six `test_*` functions in `containers/gateway/tests/test_web_lab.py` passed using host `PYTHONPATH=containers/gateway` (the file is pytest-style; pytest is not installed here).
- `python3 containers/comms/tests/test_network_lab.py` — 4/4 passed against the already-running local Silk/Webling stack; this proves test/source path repair, but the running containers are from an earlier `/tmp` checkout, not the new Compose deployment.
- `python3 containers/critical/offline-artifacts/tests/test_runtime_secret.py` — 4/4 passed after making local build/reset paths relocation-safe.
- `python3 containers/critical/offline-artifacts/tests/test_validator_inversion.py` — passed.
- `python3 tests/integration/test_late_campaign.py` — passed, including reset, source-relative references, solver-to-completion flow and final reset.
- `python3 tests/integration/test_integration.py` — exit 0, all route checks passed after repairing a pre-existing syntax typo in the test runner. Its generated result/log files were not retained as source changes.
- `docker compose -f infra/compose.yml config --quiet` and all five existing service Compose files — valid.
- `docker compose -f infra/compose.yml build --pull=false` — gateway and comms images built from their new locations.
- Operations: standalone FANG Docker build plus scheduled-job and local-service Compose builds passed; FANG and scheduled-job image health commands passed, and the local-service Python entry compiled inside its image.
- Shell syntax checks and Git whitespace checks passed.

## Not green at baseline; deliberately not reworked as part of this move

Historical baseline below describes the layout migration, not the later Medbay branch. The latter repairs the short known-plaintext fixture and truncated checker contract; verify its current focused tests before calling it green.

- `containers/critical/offline-artifacts/tests/test_offline_artefacts.py` fails because its expected crypto record differs from the fixture/solver output; it failed identically before the move.
- `challenges/completion/tests/test_completion.py` fails on its hard-coded expected record; it failed identically before the move. The end-to-end late-campaign test uses the solver's actual record and passes.
- Full `compileall` reports four Python syntax errors in the operations implementation/regeneration/acceptance files (`implementation/service.py`, `scripts/regenerate_local_root_service.py`, `scripts/regenerate_suid_route.py`, `tests/test_local_root_service.py`). Compiling the corresponding files directly from `HEAD` proved all four syntax errors existed before migration. They were not rewritten in this layout-only pass.
- `tests/integration/test_full_campaign.py` and the full reset/healthcheck were not run: the current Webling/Silk/Trapdoor containers belong to a different `/tmp` Compose project, share fixed names/loopback ports, and the reset script would remove them. We validated the new Compose config and built new images without stopping or replacing the existing stack.

## Remaining integration boundary

`infra/compose.yml` intentionally includes only the verified combined comms (which also launches gateway and Trapdoor) stack; operations keeps three independent Compose routes; security has no identifiable separate service; critical offline artifacts have no standalone Docker service. Exactly five *running containers* and a unified network are deferred rather than fabricated. Current Compose definitions publish web/network ports only on loopback. The layout and the running service count are different concepts.

The pre-existing hard-coded `/home/kali/Desktop/CITS3006-Project` paths in some operations regeneration/implementation files remain unresolved, as do their baseline syntax errors; these are explicitly outside the narrow relocation edits and should be addressed in a separate functionality repair. The untracked baseline `labs/offline-artefact-lab/challenges/egg3_binary` remains in the old lab location; it is a generated build output, not a tracked source file, and was not discarded.
