# Operations owner checklist — VRT-01–03

**Separate Medbay RE-03 slice:** `services/medbay/` now has a standalone, synthetic medical-officer recovery → RE-03 audit → scientist case → failsafe evidence path. It does **not** replace any of the three independent VRT routes below and is not part of `infra/compose.yml` yet. Its own [README](services/medbay/README.md) lists reset/build/solve, boundaries and limitations. Verified locally on Linux/aarch64: `tests/test_medbay.py`, `tests/test_live.py` against a healthy loopback-only Compose container, `tests/test_challenge_manifest.py` and `tests/integration/test_late_campaign.py` passed. Pending: non-author solve, agreed crew canon, leader's actual officer identity/session handoff, and team review before merge. The old combined Critical test remains red from its unrelated pre-existing crypto expectation mismatch.

**Owner:** Operations container/domain owner

**Scope:** The three independent station-crew-to-root routes currently named `MAINTENANCE_UTILITY` (VRT-01/SUID utility), `SHIFT_SCHEDULER` (VRT-02/scheduled job), and `LOCAL_CONTROL_SERVICE` (VRT-03/local root service).
**Status rule:** Check a box only after recording the command, result, and (for manual checks) evidence location in the PR or `CONTRIBUTIONS.md`. This is a work checklist, not a claim that unchecked work exists or has passed.

## 1. Guardrails and interfaces

- [ ] Preserve the three routes as **independent alternatives**: each is reachable from the documented low-privilege station context, can be solved without solving either other VRT, and has its own reset, health check, tests, clue and post-root handoff. Do not turn them into sequential locks.
- [ ] Keep the five-container target: Operations is one domain/container owner among Gateway, Comms, Operations, Security and Critical. This does **not** imply merging the three VRTs into one challenge path or claiming all five runtime containers are already implemented.
- [ ] Keep all intentionally vulnerable privilege boundaries inside the Operations runtime container(s); never grant host root, mount the host Docker socket, expose a privilege-bearing service to the public network, or put real credentials/flags in source, docs, logs or evidence. Use synthetic challenge markers and the repository’s established flag handling.
- [ ] Confirm ownership boundaries before editing shared integration files. Operations owns `containers/operations/**`; coordinate edits to root `infra/compose.yml`, root `tools/reset_full_campaign.sh`, `tools/healthcheck_full_campaign.sh`, `tests/integration/**`, campaign story, and `CONTRIBUTIONS.md` with their respective owners. Avoid changing other domains’ files in an Operations-only change.
- [ ] Record interfaces with other domains: Gateway/Comms provide the documented station-crew entry context; Operations consumes that context without depending on a specific upstream exploit having been solved. Each successful route writes or exposes the documented root handoff for the later Critical/recovery campaign. Coordinate exact mount/path/identity and handoff contract with the relevant owners; do not invent a new dependency or claim integration until exercised.
- [ ] Keep the Operations local compose files usable during migration until the agreed parent integration demonstrates equivalent build/start/reset/health/test behavior. Do not remove route isolation just to reduce compose-file count.

## 2. Inventory and baseline (do before refactoring)

- [ ] Review `containers/operations/docs/design.md`, all current Operations compose/Dockerfiles, implementations, route clues, reset/regenerate/health scripts, and tests. Confirm actual image names, contexts, entrypoints, users, volumes, exposed ports, privilege settings, and generated artifacts from the files—not from old design comments.
- [ ] Capture baseline behavior separately for each route. From repository root, run:

  ```bash
  docker compose -f containers/operations/compose/compose.yml config
  docker compose -f containers/operations/compose/compose_scheduled_job.yml config
  docker compose -f containers/operations/compose/compose_local_root_service.yml config
  python3 -m py_compile containers/operations/implementation/*.py containers/operations/scripts/*.py containers/operations/tests/*.py
  ```

  Then, for each route, record the existing documented build/start, `tests/test_<route>.py`, `scripts/healthcheck_<route>.sh`, and `scripts/reset_<route>.sh` outcomes. Use the exact compose invocation/flags that the files support; do not mark a failure as a regression until compared with baseline. Save logs without secrets.
- [ ] Make an issue list from reproducible findings. Classify syntax/import/runtime/behavior/test defects separately. A parser error blocks all downstream behavioral claims for that file.

## 3. Maintain three isolated Operations route models

- [ ] Keep one authoritative Operations source tree and a route/service inventory under `containers/operations/`. Retain route-specific implementation, tests, clues, resets, and build inputs; remove stale duplicates only after repository-wide reference searches and tests prove they are unused.
- [ ] Retain the three route-specific Dockerfiles and Compose definitions while they protect privilege isolation; correct their build contexts, paths and health behavior rather than forcing one image/process. Document canonical per-route commands in `containers/operations/docs/design.md`. Consolidate shared non-privileged boilerplate only if tests prove the three independent users, filesystems, startup behaviors, vulnerabilities and resets stay unchanged.
- [ ] Make relative paths robust to invocation from repository root and from the compose directory (use Compose project directory/path semantics deliberately); do not depend on the developer’s absolute checkout path. Resolve conflicting legacy paths such as `/home/kali/Desktop/CITS3006-Project/...` against the actual container layout and update code, docs and tests consistently.
- [ ] Keep container/service names, target names and integration hooks stable or coordinate changes with the parent integration owner. Document the canonical commands and route-to-service mapping in `containers/operations/README.md` if created, or `containers/operations/docs/design.md`.
- [ ] Validate all three route-specific Compose models separately (`compose.yml`, `compose_scheduled_job.yml`, `compose_local_root_service.yml`) and then the reviewed central `infra/compose.yml` integration. Verify each route starts independently and no host privilege or unintended port exposure was introduced.
- [ ] Search the repository for references to renamed/removed compose files, services, scripts, artifacts and paths before deletion; update references only in owned files or coordinate with owners.

## 4. VRT acceptance contracts

Apply this contract independently to VRT-01, VRT-02 and VRT-03. Preserve the intended learning objective, not merely a command that prints a marker.

### VRT-01 — MAINTENANCE_UTILITY (SUID route)

- [ ] Record the intended vulnerable baseline: the intended utility/permission boundary is discoverable to `station_crew`, produces the documented root proof, and does not depend on host privilege. Verify generated binary permissions/ownership and reproducible build inputs.
- [ ] Verify the clue at `containers/operations/entry/suid_route_clue.txt` gives fair discovery without directly disclosing the solution; verify the route’s post-root handoff is available at the documented location.
- [ ] Exercise the actual player path from the intended low-privilege identity, capture the decisive observation and root proof, and verify the route remains independent from VRT-02/VRT-03.
- [ ] Exercise reset and regenerate in both directions; verify reset restores the intended baseline and removes stale output/state without damaging another route or other campaign data.

### VRT-02 — SHIFT_SCHEDULER (scheduled-job route)

- [ ] Implement the existing `/etc/cron.d/shift_scheduler_job` contract with an installed cron daemon running foreground in `Dockerfile_shift_scheduler` (the current image merely tails `/dev/null` and does not schedule jobs). Ensure the generated schedule is loaded with correct ownership/permissions and invokes the existing root-side processor; test the station_crew-writable input, one-minute scheduling window with bounded retries, and documented root proof inside the container. Keep the same clue and receipt bytes.
- [ ] Verify the intended writable-job/config boundary and controlled execution as root inside the container, then demonstrate the player path and documented root proof from `station_crew`.
- [ ] Check the clue at `containers/operations/entry/scheduled_job_clue.txt`, timing/retry behavior, logs and post-root handoff. Keep tests bounded and avoid flaky sleep-based success criteria where a deterministic trigger/status check is possible.
- [ ] Exercise route-only reset/regeneration, including removal/recreation of scheduled entries, permissions and generated artifacts. Confirm VRT-01/VRT-03 state is unchanged.

### VRT-03 — LOCAL_CONTROL_SERVICE (local root service route)

- [ ] Specify the real interface and trust boundary (socket or TCP, bind address, port/path, protocol, caller identity and permissions) consistently across implementation, image, clue and player instructions. The current code comments/design mention both local-only access and `0.0.0.0:8080`; resolve this explicitly and test network reachability rather than relying on comments.
- [ ] Verify the root service is a persistent, functioning process (not a one-shot CLI simulation); it accepts the intended request, handles malformed/disconnected clients safely, and produces the documented root proof only through the intended challenge mechanic.
- [ ] Verify clue `containers/operations/entry/local_root_service_clue.txt`, health behavior and post-root handoff agree with the actual interface. Ensure health checks do not accidentally exploit the route or disclose a raw secret.
- [ ] Exercise route-only reset/regeneration, confirm service lifecycle is clean and stale sockets/state are removed, and verify VRT-01/VRT-02 remain unchanged.

## 5. Targeted syntax and correctness repairs

- [ ] Fix and regression-test the known parser error in `containers/operations/implementation/service.py` (the malformed `message` dictionary key near the `print_flag` response). Then run `python3 -m py_compile containers/operations/implementation/*.py` and the focused VRT-03 tests before broader tests.
- [ ] Inspect all route implementation, test, regeneration and script files for further syntax/import issues, including `containers/operations/implementation/local_root_service.py`, `scheduled_job.py`, `suid_route.py`, and every `containers/operations/scripts/*.py`. Fix only findings supported by reproduced errors; do not infer more defects from the first failure.
- [ ] For every fix, add or update a focused regression assertion that would fail before the fix. Run it and record actual output. Keep challenge behavior, route independence, reset safety and synthetic-only secret handling intact.
- [ ] Remove compile-generated `__pycache__`/`.pyc` artifacts if produced and ensure they are ignored/untracked; keep generated build outputs out of commits unless explicitly required.

## 6. Reset, health, build and test gates

- [ ] Define a route matrix in the Operations docs: route/service, build command, start command, low-privilege test command, health command, reset command, expected baseline, expected root proof/handoff, and evidence location.
- [ ] Build every Operations service from a clean state using the canonical compose model. Verify all three routes build independently and together; include the target architectures required by the project and report unsupported architecture/runtime limitations explicitly.
- [ ] Run each route’s focused acceptance test in its actual runtime context:

  ```bash
  python3 containers/operations/tests/test_suid_route.py
  python3 containers/operations/tests/test_scheduled_job.py
  python3 containers/operations/tests/test_local_root_service.py
  ```

  If a test requires a running container, use its documented compose `run`/`exec` path; do not count host-only mocks as container acceptance evidence.
- [ ] Run each route health check against the started service and assert a nonzero exit/failure for an intentionally stopped or misconfigured service. Health should test readiness of the real route-specific process/interface, not merely file existence or an unconditional `status: ok`.
- [ ] Verify reset idempotence: reset twice, then rebuild/reinitialize; both resets succeed, baseline is restored, and no unrelated route or shared campaign state is modified. Test reset from both a solved state and a partial initialization where practical.
- [ ] Exercise the Operations build → health → each independent exploit acceptance → route reset → health sequence from a clean checkout or documented clean state. Record commands, platform, commit, exit statuses and concise outputs.
- [ ] Run the parent integration checks after Operations changes, coordinated with the parent owner. At minimum discover and execute the currently applicable root reset/health and integration commands documented by `README.md`, `tools/`, `infra/compose.yml` and `tests/integration/`. Do not report parent campaign success if any route is skipped or a command is unavailable.
- [ ] Scan diff for accidental raw credentials/flags and host-escape surfaces; verify host-published ports are loopback-only when publication is needed and route-local interfaces are not unintentionally reachable across routes.

## 7. Coriolis station-story placeholders and evidence

- [ ] Keep technical truth primary: story text must reflect the actual service, account, interface, timing, reset behavior and handoff. Coordinate story edits with campaign/story owners; do not edit their files as an Operations-only change.
- [ ] Replace operationally vague text in owned clue/handoff files with reviewed, consistent Coriolis station placeholders where needed: service/station identifier, responsible subsystem or crew role, observed anomaly, actionable discovery hint, expected next handoff identifier, and a neutral `[STORY OWNER: ...]` placeholder when narrative facts await approval. No real secrets or raw flag values in placeholders.
- [ ] Ensure VRT-01, VRT-02 and VRT-03 clues each stand alone, identify the relevant station subsystem without naming the exploit, and lead to the matching post-root handoff. Do not make one route’s clue a prerequisite for another route.
- [ ] Confirm all three route success artifacts/handoffs have stable identifiers and exact paths agreed with downstream Critical/recovery owners. Record placeholders explicitly if the receiving story/artifact is not implemented; do not describe it as live.
- [ ] Request a non-author solve and maintainer review for each route; retain timestamped or commit-linked evidence, anonymized if needed. Record confusing clue points and resolve them before marking the story acceptance complete.

## 8. Measurable Definition of Done (DoD)

An Operations owner may mark this work complete only when **all** criteria below have evidence:

1. **Scope:** Exactly the three VRT route contracts above are mapped to canonical Operations files and services; each route can be started, tested, reset and solved independently (3/3).
2. **Build:** Clean builds pass for every supported target architecture and all three route images/services (3/3); build commands and commit/platform are recorded.
3. **Syntax/tests:** All Operations Python implementation, script and test files pass `py_compile`; all three focused route acceptance suites pass against their intended runtime contexts (3/3); parent integration tests relevant to the change pass.
4. **Mechanics:** A non-author operator using the supplied station context reproduces the intended privilege escalation and correct route-specific root proof/handoff on each route, without solving another route (3/3); no host-root or host escape is used.
5. **Reset:** Each route resets successfully twice in succession after a solve, returns to its documented vulnerable baseline, preserves its clue, and leaves the other two routes unchanged (3/3; verify pairwise isolation).
6. **Health:** Each route’s health check passes when ready and fails nonzero when its required process/interface is absent (3/3).
7. **Compose:** The canonical Compose config validates; every service’s build context, startup, identity, mounts, ports, health and reset ownership are documented; any intentionally retained extra compose/Dockerfile has a written isolation/reproducibility rationale.
8. **Story/handoffs:** Three reviewed clues and three matching stable handoff artifacts exist or are explicitly marked as owner-approved placeholders; downstream receiver and exact integration paths are confirmed with domain owners.
9. **Safety/quality:** Diff contains no raw secrets, no unintended public exposure, and no host privilege escalation; `git diff --check` is clean; generated caches/build debris are absent.
10. **Ownership/evidence:** Operations changes are committed with accurate owner/reviewer attribution in the agreed contribution record; checklist boxes cite commands/results or evidence references. No unchecked or unrun requirement is represented as passed.

## 9. Completion record (fill in; never fabricate)

- Commit/PR:
- Owner / reviewer:
- Date and tested architecture(s):
- Canonical build command + result:
- Syntax command + result:
- VRT-01 test / health / reset evidence:
- VRT-02 test / health / reset evidence:
- VRT-03 test / health / reset evidence:
- Parent integration command + result:
- Non-author solve evidence (3/3 or outstanding routes):
- Known limitations / deferred work:

## 10. Priority by grade return

| Priority | Work | Grade-return rationale |
|---|---|---|
| **P0 — blocker / high** | Repair reproducible syntax failures; make each of 3 VRTs build, solve, health-check and reset independently; prove intended privilege boundary and no host escape; preserve the three alternatives. | Directly protects required vertical-escalation coverage and a working demonstrable campaign; one broken route can cost a whole coverage item. |
| **P1 — high** | Consolidate duplicated code/Compose only where route isolation remains; add deterministic scheduler/service readiness; clean-checkout/architecture and parent integration tests; obtain 3/3 non-author reproductions. | Improves reproducibility, fairness and demo confidence; catches regressions hidden by author-only runs. |
| **P2 — medium** | Align Coriolis clue/handoff placeholders, route matrix, design docs and downstream interface contracts; improve diagnostics and failure-mode assertions. | Makes the campaign coherent and maintainable, but must not displace route correctness or independent solveability. |
| **P3 — conditional / lower** | Cosmetic refactors, broad abstraction, merging images/compose files without a measured benefit, or narrative expansion beyond actionable route evidence. | Limited direct coverage return and carries regression risk; defer until P0/P1 are evidenced. |
