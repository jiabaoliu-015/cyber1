# Security owner execution checklist

**Scope:** `containers/security/` only, unless a shared-contract change is explicitly agreed with the affected owner(s) and integrated as a separate reviewed change. This checklist fixes the default boundary and prioritizes executable, evidence-backed work over creating a nominal fifth runtime.

## Fixed default decision

- [ ] Treat Security as **one ownership/container boundary**, with only two narrowly scoped responsibilities: (1) minimal access-control behavior needed to support the existing station narrative and (2) watchdog/heartbeat behavior as station narrative support.
- [ ] Keep the access-control component and watchdog/heartbeat component **inside the same Security container** by default. They are components, not independent containers or new challenge routes.
- [ ] Neither component creates a required challenge. No new manifest ID, required receipt, mandatory dependency, player gate, or exploit is added. Existing challenge routes remain independently startable, resettable, solvable, and assessable.
- [ ] Default to **narrative support, not centralized enforcement**: do not place existing authorization in the Security service, proxy all app/network traffic through it, or make the current services depend on it to start. Existing challenge targets continue to own their current authentication/authorization and intentional weaknesses.
- [ ] Preserve the narrow trust boundary: expose only the smallest local interface needed by an existing station service; no host control, Docker socket, privileged mode, host networking, broad shared mounts, unrestricted service-to-service access, or raw secrets. Prefer read-only inputs and a dedicated private Compose network if/when a runtime is approved.
- [ ] Watchdog/heartbeat is an observable station-status/narrative aid only. It must not automatically repair, restart, block, disable, hide, or change challenge targets or their evidence. Deterministic local defaults: fixed service identity, fixed heartbeat interval/timeout, bounded state, no outbound network, no wall-clock-dependent challenge result; document chosen values in service README/config before implementation.
- [ ] Do not introduce a live access-control daemon or watchdog runtime merely to claim five containers. Current `infra/compose.yml` intentionally composes only the verified web/Uplink stack; Security has no runtime until its local contract, container build, and tests are real and reviewed.
- [ ] Any proposed deviation from these defaults is a design decision requiring explicit written rationale, affected-owner review, and tests; do not silently widen scope.

## Priority and grade ROI

Work in this order; stop at the first unresolved boundary or regression.

| Priority | Deliverable | Grade/effort ROI | Exit evidence |
| --- | --- | --- | --- |
| P0 | Inventory current auth/access-control/watchdog behavior and map each item to its actual owner; confirm this boundary against current branch code. | Highest: cheap, prevents misplaced scope and accidental regressions. | Dated evidence entry with paths, observations, and known gaps; no claims based on placeholder names. |
| P0 | Record/accept the default boundary above and the cross-owner contracts below before moving code or adding Compose wiring. | Highest: low effort, prevents broken build contexts and route coupling. | Reviewed decision + owner acknowledgements or named open questions. |
| P1 | Add the smallest local access-control and watchdog/heartbeat support only if a concrete existing narrative integration requires it; otherwise document “not implemented / not needed yet.” | Medium: demonstrable architecture work without inventing rubric scope. | Executable component tests and/or evidence-backed defer decision. |
| P1 | Verify existing deliberate challenge behavior, manifest, independent routes, and exact receipt artifacts are unchanged. | Highest regression value; required even for documentation-only security changes that touch shared behavior. | Before/after diff/hash evidence where byte preservation is relevant; relevant test output. |
| P2 | Add Security runtime to shared Compose only after a real bounded service exists and owners approve its interface/network. | Lower until needed; avoid speculative orchestration. | Compose config/build/health evidence plus cross-service integration proof. |
| P2 | Improve explanatory station-status narrative and operator docs without changing challenge semantics. | Optional polish after correctness. | Copy reviewed for factual restraint; no asserted incident outcome or invented lore. |

## Ground truth and protected contracts

- [ ] Use `challenges/manifest.json` as inventory source of truth. It currently contains **17 required challenge IDs plus one optional `OPT-01`**. `COMPLETE-01` is the separate aggregate receipt checker, not another challenge.
- [ ] Keep all required IDs, lab assignments, implementation paths, `receipt_id` values, and empty `depends_on` lists unchanged unless a separately approved challenge migration requires coordinated edits. A Security task does not justify editing the manifest.
- [ ] Do not add a required vulnerability, flag, receipt, challenge card, player gate, or dependency. A watchdog “go dark” event from the story diagram is not an implemented required challenge or unlock condition.
- [ ] Preserve every existing intentional vulnerability and solver-visible behavior in its owning implementation. In particular, do not harden, normalize, proxy, or transfer authorization away from existing challenge code merely because Security is named “access-control.” Keep mitigation discussion separate from target behavior.
- [ ] Preserve the exact bytes of existing receipt/token/flag fixtures and outputs. When a proposed change could touch one, capture a before hash and compare after; never paste secret/flag bytes into this checklist, PR description, or evidence log.
- [ ] Keep the four lab paths independent: web (`WEB-01`–`WEB-03`, `HZ-01`–`HZ-03`), network (`NET-01`–`NET-03`), privilege escalation (`VRT-01`–`VRT-03`), offline artefacts (`RE-01`–`RE-03`, `ADV-01`–`ADV-02`); `OPT-01` remains optional.
- [ ] The story is an open investigation. Do not assert a cause of the incident, crew fate, culpability, or unexplained lore as fact.

## Current inventory to verify before implementing

- [ ] Read `containers/security/README.md`, `containers/security/config/README.md`, `containers/security/services/access-control/README.md`, and `containers/security/services/watchdog/README.md`. They currently mark Security, access control, and watchdog as reserved; they are not implementations or contracts.
- [ ] Confirm existing network authentication remains in `containers/comms/network_service/auth_server.py`, built by `containers/comms/network_service/Dockerfile` and tested by `containers/comms/tests/test_network_lab.py`. The current Uplink intentionally exposes/reuses a challenge value; keep that exercise in Comms and do not move or repair it under Security ownership.
- [ ] Confirm current web access-control challenges remain in `containers/gateway/webapp/app.py` and its tests/docs under `containers/gateway/`; do not centralize or repair their intentionally vulnerable authorization behavior.
- [ ] Confirm `infra/compose.yml` includes `containers/comms/docker-compose.yml` (which also builds Gateway) and does not currently include Security. The root Compose is a verified partial orchestration, not a five-container runtime contract.
- [ ] Review `docs/architecture.md`, `docs/architecture/integration-contract.md`, `docs/story/README.md`, and `docs/challenge-design/migration-verification.md` for current limitations and historical-vs-current evidence.
- [ ] Check `git status --short` and `git diff` before edits. Do not overwrite or “clean up” pre-existing untracked `labs/` or unrelated owner files.

## Proposed Security-owned file boundary

Keep changes in `containers/security/` until a cross-owner integration change is separately agreed.

- [ ] `containers/security/README.md`: make the accepted one-container boundary, implemented-vs-deferred status, local-only intent, and no-new-challenge guarantee explicit.
- [ ] `containers/security/services/access-control/README.md`: state the smallest proposed interface, caller/decision semantics, default-deny only for any newly introduced support endpoint, and explicitly state it does not enforce or replace existing challenge authorization. If no concrete caller exists, retain it as a documented placeholder.
- [ ] `containers/security/services/watchdog/README.md`: define deterministic heartbeat/status semantics, fixed defaults, bounded failure behavior, and narrative-only/no-remediation behavior. If no concrete consumer exists, retain it as a documented placeholder.
- [ ] `containers/security/config/README.md`: list only non-secret deterministic defaults and config ownership; no credentials, keys, tokens, flags, or sample secrets.
- [ ] Add implementation files, tests, Dockerfile, healthcheck, or Compose only when an actual separable behavior is approved. Put them under `containers/security/`; name exact paths in the evidence entry and update this list in the same change. Do not create empty placeholder code or a fake runnable service to satisfy a container count.
- [ ] Keep generated databases, runtime state, secrets, and mutable receipts out of source/config unless an existing contract requires them; any required state location and reset behavior must be documented and tested.

## Contracts before coding or cross-container wiring

Write down the answers in the relevant README/PR before implementation; “TBD” is a blocker to runtime integration, not permission to guess.

- [ ] **Consumer and purpose:** identify the existing service and narrative view that needs each Security behavior; if none exists, defer implementation. Gateway owns portal routes and access-control challenge behavior; Comms owns Uplink/auth challenge behavior; Operations owns its three privilege-route units; Critical owns offline artefacts; shared integration owns manifest/completion/test harness changes.
- [ ] **Interface:** specify protocol/transport, endpoint or message schema, caller identity, success/failure response, timeout, and versioning. Bind locally/private-network only; do not publish a new host port by default.
- [ ] **Trust:** identify trusted inputs, untrusted inputs, data classification, and what the component is explicitly not allowed to decide or mutate. Never accept arbitrary host paths, shell commands, container-control requests, or unbounded payloads.
- [ ] **Availability:** define whether the caller can continue when Security is absent/unhealthy. Default: Security is optional narrative support and must not block independent challenge startup or solve paths.
- [ ] **Determinism:** use fixed local configuration, bounded queues/state, explicit timeouts, and stable test fixtures. Tests must not depend on public services, random outcomes, real waiting periods, or developer-specific absolute paths.
- [ ] **Failure behavior:** return bounded, documented status; no implicit “fail open” change to an existing protected route, and no watchdog remediation. Because the support component is not authoritative for existing routes, its failure must not alter those routes.
- [ ] **Ownership:** name the source/config/test owner and any downstream consumer; obtain Gateway/Comms/Operations/Critical acknowledgement for changes they consume.
- [ ] **Security/container limits:** run as non-root where feasible; drop unnecessary capabilities; read-only filesystem where feasible; no privileged mode, host PID/network, Docker socket, broad mounts, or published port. Document any necessary exception and why.

## Execution checklist

### A. Discovery and decision

- [ ] Record branch, commit, `git status --short`, and relevant existing tests in the task evidence.
- [ ] Trace the actual access-control/authentication code and the current tests; distinguish intentional exploit surface from ordinary service boundary.
- [ ] Inspect actual Compose/build contexts; do not infer deployment from `services/` folder names.
- [ ] Mark each candidate as `existing challenge behavior`, `narrative support`, or `not implemented`. Only the second category is eligible for this Security container.
- [ ] Confirm whether a concrete existing consumer exists. If not, make the outcome “documented boundary; no runtime added.”
- [ ] Ask affected owners to review contract proposals before changing their files or shared integration files.

### B. Minimal implementation (only if justified)

- [ ] Implement only the agreed local support behavior; avoid generic IAM, user directory, policy engine, reverse proxy, centralized auth, or monitoring platform.
- [ ] Keep access-control support advisory/narrative-only with respect to existing challenge targets. Do not change intentional bypasses or solve paths.
- [ ] Keep watchdog state informational and bounded; no target restarts, process kills, route blocking, reset triggers, flag access, or exploit suppression.
- [ ] Provide deterministic configuration with safe local defaults; never commit credentials or raw secrets. Provide `.env.example` only for documented non-secret knobs, and validate required runtime secrets from the environment if any are genuinely necessary (prefer none).
- [ ] Add narrowly scoped tests for protocol/schema validation, unauthorized/untrusted inputs, timeout/unavailable behavior, bounded state, and no target mutation.
- [ ] Add a reset/healthcheck only when stateful/runnable service behavior needs one; tests must prove reset does not alter other routes or receipt fixtures.
- [ ] Ensure any future container builds solely from its documented context and does not rely on sibling files that Docker cannot access.

### C. Regression and integration

- [ ] Verify service-level tests first, then existing owner suites and catalogue/integration checks listed below.
- [ ] Prove all required manifest IDs/receipt IDs and independence constraints remain unchanged; prove optional status remains unchanged.
- [ ] Re-run the relevant intentional exploit tests and compare behavior to baseline. A security-support change that causes an existing exploit challenge to stop being exploitable is a regression unless a separate assessment-approved spec explicitly says otherwise.
- [ ] If container/Compose wiring changed, validate config and build without replacing unrelated running stacks; capture exact command output and any environment limitation.
- [ ] Test both Security-present and Security-absent modes. Existing challenge services must still start, reset, solve, and emit the same receipt bytes when Security is unavailable.
- [ ] Verify private-network reachability only for named consumers; prove no new host-published port and no access to unrelated service networks.
- [ ] Run the completion checker only using its existing documented flow; do not add Security receipts to `COMPLETE-01`.
- [ ] Review diff for accidental changes outside `containers/security/`; request a separate coordinated change/owner approval for any shared-file edits rather than slipping them into this owner task.

## Exact useful commands

Run from repository root. Commands below are grounded in checked-in files. Docker runtime commands are conditional on Docker being available and should not disrupt an already-running stack.

```bash
# Boundary / diff hygiene
git status --short --branch
git diff --check
git diff -- containers/security/

# Manifest inventory and independence regression
python3 tests/test_challenge_manifest.py
./tools/challenge validate
./tools/challenge list

# Existing Web/Gateway challenge suite (pytest-style; pytest may be needed)
PYTHONPATH=containers/gateway python3 -m pytest -q containers/gateway/tests/test_web_lab.py

# Existing Comms intentional-auth-flaw / handoff suite.
# It expects the Uplink at localhost:5432; do not accidentally test another stack.
python3 containers/comms/tests/test_network_lab.py

# Existing offline artefact regression suites
python3 containers/critical/offline-artifacts/tests/test_offline_artefacts.py
python3 containers/critical/offline-artifacts/tests/test_runtime_secret.py
python3 containers/critical/offline-artifacts/tests/test_validator_inversion.py

# Existing late-campaign/completion integration
python3 tests/integration/test_late_campaign.py

# Compose syntax for current verified orchestration (no deployment)
docker compose -f infra/compose.yml config --quiet
```

For a genuine new Security implementation, add exact test command(s) to its README and run them first. If a Dockerfile and approved Compose entry are later added, additionally run:

```bash
docker compose -f infra/compose.yml config --quiet
docker compose -f infra/compose.yml build --pull=false security
```

Use the actual Compose service key in place of `security` if the reviewed contract selects another name. Do not run `up`, full reset, or broad integration scripts against a shared machine without checking running containers and ports first. Do not use historical logs/results as proof of a current run.

**Known baseline caveats from `docs/challenge-design/migration-verification.md`:** the offline artefact aggregate test and completion unit test have documented fixture mismatches; some Operations files have pre-existing syntax errors; the full-campaign runtime test may conflict with an unrelated existing Compose stack. Report these as baseline/blocker evidence if encountered; do not “fix” unrelated owner code in this task or mislabel them as Security failures.

## Progress and evidence conventions

- [ ] Keep this checklist as the source for Security-owner execution status. Use `[ ]` not started, `[-]` in progress, `[x]` completed with evidence, and `[!]` blocked; do not check off work based on plans or a successful file write alone.
- [ ] For each completed item, add a concise evidence row to the Security PR/task description: **date (YYYY-MM-DD), commit, item, exact command/test, exit/result, artifact path, reviewer**. Use local date from the execution environment.
- [ ] Separate `PASS`, `FAIL`, `BLOCKED`, and `NOT RUN`; include reason and affected scope. A known baseline failure stays `FAIL (pre-existing)` with its source citation, not PASS or silently omitted.
- [ ] Store durable implementation-specific evidence under `containers/security/docs/verification/` only when useful and approved; otherwise keep execution logs in ignored scratch/CI artifacts. Never overwrite shared historical `tests/integration/results/` or logs as a side effect of a checklist run.
- [ ] Evidence must be reproducible: command, working directory, required non-secret environment variable names, and observed result. Redact credentials/tokens/flags and avoid raw response dumps that may contain them.
- [ ] Use before/after hashes for exact receipt/fixture byte preservation; record only relative path and hashes, never the underlying secret value.
- [ ] Record runtime context for Docker results (Compose file, service key, image/build result, health/readiness result, ports/network inspected). A successful `config` is not evidence that containers ran.
- [ ] Maintain a short blocker list with owner and next action. Do not convert a blocker to “done” because adjacent docs/tests passed.

Suggested evidence table (copy into the PR/task report; do not invent results here):

| Date | Commit | Item | Command / evidence path | Result | Reviewer / blocker |
| --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | `<sha>` | Boundary decision | `<PR link or note>` | `PASS / BLOCKED` | `<owner>` |
| YYYY-MM-DD | `<sha>` | Regression suite | `<exact command; log path>` | `PASS / FAIL / NOT RUN` | `<reviewer>` |
| YYYY-MM-DD | `<sha>` | Receipt-byte check | `<hash command; relative paths only>` | `PASS / FAIL / N/A` | `<reviewer>` |

## Shared integration handoff

- [ ] Send Gateway and Comms the proposed consumer/interface and ask them to confirm that no existing auth/access-control challenge behavior is moved, centralized, hardened, or made dependent on Security.
- [ ] Send Operations and Critical the same boundary note; confirm Security has no access to privileged route state, offline artefacts, flags, or completion receipts.
- [ ] Notify the shared integration owner before proposing any edit to `infra/compose.yml`, `challenges/manifest.json`, `challenges/completion/`, root `README.md`, or `tests/integration/`. Those files are not Security-owned.
- [ ] Handoff includes: (a) decision and rationale, (b) exact owned file list, (c) service key/endpoint/schema if implemented, (d) network and failure semantics, (e) deterministic defaults, (f) tests and actual output, (g) intentional exploit/receipt preservation evidence, (h) known baseline issues, and (i) rollback/removal procedure.
- [ ] Integration owner independently verifies Compose/network contracts and current test results; a Security README or local unit test alone does not establish five-container integration.
- [ ] Get another team member's review and approval before merging shared changes to `main`, consistent with the root repository contribution guidance.

## Definition of done

- [ ] The one-container/minimal-support default and no-new-required-challenge boundary are documented and accepted.
- [ ] Implemented behavior has a real consumer, explicit narrow contract, deterministic defaults, tests, and local-only trust boundary; otherwise it is explicitly deferred with no fake runtime.
- [ ] Existing intentional exploits, route independence, the 17-required-plus-one-optional inventory, and exact existing receipt bytes remain intact.
- [ ] The relevant commands were actually run and results recorded; baseline failures and skipped runtime checks remain explicit.
- [ ] Only Security-owned files changed in the Security owner patch; shared integration changes have separate owner review/evidence.
- [ ] Handoff is complete and reviewed; no raw secrets are present in source, config, logs, or report.
