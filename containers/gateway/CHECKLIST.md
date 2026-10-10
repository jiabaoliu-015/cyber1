# Gateway owner checklist

**Owner:** Gateway / Crew Portal maintainer
**Scope:** Existing gateway web challenge and its container/scripts/tests, plus explicitly labeled station-portal and SSH placeholders.
**Status convention:** `[ ]` not done or blocked (add `BLOCKED: reason; owner/task; next action`); `[x]` complete with evidence. Never check off a task from a diagram, README claim, or intended behavior alone. Keep this file as the status ledger; append concise evidence and verification date to each completed item.
**Evidence format:** `Evidence: <command or test> — <observed result> (YYYY-MM-DD).` Do not paste raw flags, passwords, session cookies, private credentials, or secret-bearing logs. Record route/status/assertion names and redacted summaries only.
**Date convention:** Use ISO dates from the actual verification run. Do not backdate.

## 0. Baseline and coordination

- [ ] Capture starting branch/commit and dirty-tree status; do not overwrite unrelated work. Evidence: `git status --short --branch` and `git rev-parse HEAD`, summarized here.
- [ ] Read `docs/architecture/integration-contract.md` and `docs/challenge-design/migration-verification.md` before wiring gateway into other containers; confirm inventory, route/receipt ownership, Compose boundaries, and integration test expectations remain unchanged.
- [ ] Confirm the authoritative challenge IDs, routes, and receipt/flag byte contracts in `challenges/manifest.json`, relevant challenge implementations, and tests. Do not rename/merge IDs or regenerate expected bytes as part of this gateway checklist.
- [ ] Keep gateway implementation self-contained unless an integration-contract task specifically assigns a cross-container change. Treat the editable flowchart as design input only: proposed nodes/edges and names are not implemented features or acceptance evidence.
- [ ] Before handing work to another owner, record touched files, commands and outcomes, known gaps, reset state, and exact interface/dependency questions; coordinate through `docs/architecture/integration-contract.md`.

## 1. Verified baseline and current gaps

The gateway target currently has a runnable FastAPI Crew Portal under `webapp/app.py`, Docker packaging in `Dockerfile` plus `docker-compose.yml`, data/config under the target root, and a focused pytest module. Existing intentional web behaviors include authenticated research-record IDOR, SQL-injection archive search, stored-XSS moderation rendering, and horizontal profile/backup access. `docs/alternate_coverage.md` documents intended alternate paths. The service is loopback-published by Compose. Current tests assert challenge fixture values directly, so treat test output as private evidence and report only sanitized pass/fail summaries.

The current target also contains `services/web-platform/README.md` and `services/station-ssh/README.md` as target-slot documentation, not implementations. `config/README.md` is a placeholder. The existing Dockerfile copies only `webapp` and `entry`; station SSH is explicitly not verified/deployed. Do not claim a station portal or SSH service is implemented until it has runnable source/config, isolated lifecycle/reset, and tests. `containers/gateway/webapp/app.py` is the implementation for `WEB-01`–`WEB-03` and `HZ-01`–`HZ-03` in `challenges/manifest.json`; map each fixed ID to its actual route and test rather than asking whether it is assigned. Do not invent new challenge IDs or silently replace existing gateway behavior.

## 2. Inventory, contracts, and safe baseline

- [ ] Inventory every tracked gateway file and identify owners/consumers before edits: `git ls-files containers/gateway`; record expected source, docs, config, scripts, tests, and target-slot paths.
- [ ] Read `containers/gateway/README.md`, `docs/challenge_card.md`, `docs/player.md`, `docs/sample_solution.md`, `docs/alternate_coverage.md`, and `docs/verification.md`; reconcile claims against executable source and tests.
- [ ] Inspect `webapp/app.py` and map each existing challenge behavior to its stable route, auth precondition, fixture, test, and expected sanitized handoff. Preserve these route contracts unless integration owners approve a change.
- [ ] Verify the six fixed Gateway entries in `challenges/manifest.json` still point to `containers/gateway/webapp/app.py` and have independent `depends_on: []`; compare each `receipt_id` against its source/test without printing raw values.
- [ ] Verify that flag and receipt outputs are byte-for-byte unchanged for existing challenge IDs by running their authoritative tests/checkers and comparing only approved artifact hashes or sanitized expected values. Never print raw tokens in the checklist or logs attached to handover.
- [ ] Record Python, Docker/Compose availability, architecture, and starting test baseline using `python3 --version`, `docker --version`, `docker compose version`, and the test commands below; label unavailable tools as blocked rather than passed.
- [ ] Check `git diff -- containers/gateway` before edits and after each work batch; do not include unrelated files in the gateway change.

## 3. Web challenge coverage: WEB-01..03 and HZ-01..03

The manifest fixes this assignment; source and tests determine which parts are actually demonstrated. Complete one evidence row per ID below. Do not infer a new vulnerability from the diagram alone.

- [ ] **WEB-01:** Verify SQL injection in `GET /api/search`, discover the protected archive result from a fresh fixture, add a negative/control query, and document the source/test/reset/receipt evidence without publishing the receipt.
- [ ] **WEB-02:** Verify stored feedback survives `POST /api/feedback` and is rendered by `GET /moderation/queue`; add a harmless control case and a reset/isolation assertion.
- [ ] **WEB-03:** Verify unauthorised access to another owner's `GET /api/research/{record_id}`; test intended result, own-object control and unauthenticated boundary.
- [ ] **HZ-01:** Verify another user's `GET /api/profiles/{username}` private resource is exposed under the intended session; test own-object and unauthenticated controls.
- [ ] **HZ-02:** Verify another owner's `GET /api/backups/{owner_id}` contents are exposed; test expected result, own-object and unauthenticated controls.
- [ ] **HZ-03:** Verify cross-owner research resource access independently of WEB-03's same handler/record; add a distinct learner action/receipt demonstration or document honestly if the two IDs reuse one mechanic and cannot both be counted as distinct assessment evidence.
- [ ] For every assigned ID, assert unauthenticated behavior, expected authorized/unauthorized boundary, stable response schema/status, and expected challenge-specific effect; test negative inputs without leaking secrets in assertion output.
- [ ] For every intentionally vulnerable route, add an explicit source comment naming the assigned challenge ID and lab-only intent; add player/maintainer documentation explaining the isolated scope and safe local-only use.
- [ ] Preserve existing primary spine and alternate routes unless the relevant challenge owner approves a migration. Add coverage without merging independent reset or solve state.
- [ ] Verify regression isolation: solve/reset one gateway challenge and assert other gateway challenge records, challenge IDs, and receipts remain unchanged.

### Challenge evidence ledger

| Challenge ID | Manifest owner / assigned? | Route or explicit N/A | Test(s) | Result and sanitized evidence |
|---|---|---|---|---|
| WEB-01 | Gateway | `/api/search` | `test_sqli_search_reveals_hidden_archive_clue` | Pending clean-run evidence |
| WEB-02 | Gateway | `/api/feedback` → `/moderation/queue` | `test_stored_xss_is_retained_and_rendered_in_moderation_queue` | Pending clean-run evidence |
| WEB-03 | Gateway | `/api/research/{record_id}` | `test_fixture_contains_idor_target` | Pending independent-route evidence |
| HZ-01 | Gateway | `/api/profiles/{username}` | `test_horizontal_profile_and_backup_boundaries_are_broken` | Pending clean-run evidence |
| HZ-02 | Gateway | `/api/backups/{owner_id}` | `test_horizontal_profile_and_backup_boundaries_are_broken` | Pending clean-run evidence |
| HZ-03 | Gateway | `/api/research/{record_id}` | `test_horizontal_research_boundary_is_broken` | Pending distinctness evidence |

## 4. Station portal and SSH placeholder boundary

- [ ] Keep `services/station-ssh/README.md` explicit that it is a placeholder until an independently runnable SSH service is built and verified; do not describe a placeholder in another Compose stack as a deployed server.
- [ ] Treat the existing Crew Portal (`webapp/app.py`) as the station web portal; do not create a duplicate. Record its service name, loopback exposure, data owner and outbound handoff in `docs/architecture/integration-contract.md`.
- [ ] Keep Station SSH explicitly **not implemented**. `NET-03` currently maps to a Comms handoff file, not an SSH server; do not assign SSH implementation to any owner or add a new daemon under this checklist. Remove claims of a working SSH server from player docs until a separately scoped feature is implemented and tested.
- [ ] Do not create real/default reusable SSH passwords or expose credential material in docs, fixtures, logs, images, or repository history; inject lab-only credentials at runtime using the agreed secret mechanism.
- [ ] Verify the Comms NET-03 handoff/reset does not erase or mutate Crew Portal data, flags, receipts, or another service's challenge state; treat SSH isolation as a separate acceptance gate only if an SSH feature is later scoped.
- [ ] Leave unimplemented station/SSH proposals clearly marked as **not implemented** in docs and handover; do not add unrelated flowchart systems to improve apparent completeness.

## 5. Dockerfile and Compose execution

- [ ] Review `containers/gateway/Dockerfile` for reproducible base/dependency pins, minimal copied context, non-root runtime feasibility, writable data ownership, health-check strategy, and absence of build-time secrets; record each unresolved risk.
- [ ] Build the image from the gateway directory and capture the real exit status: `docker compose -f containers/gateway/docker-compose.yml build --no-cache` (run from repo root). Resolve build errors rather than treating syntax/source checks as image verification.
- [ ] Validate Compose rendering: `docker compose -f containers/gateway/docker-compose.yml config --quiet` and inspect rendered ports, volumes, environment, networks, and service count without publishing secret values.
- [ ] Start the service in an isolated test project/network; verify only the intended loopback host binding, health route, root/login/dashboard behavior, and expected service name. Do not expose this intentionally vulnerable lab service to LAN/public interfaces.
- [ ] Verify the container can write only required persistent data, that `entry/` remains read-only as configured, and that image/build context contains no `.env`, database, caches, flags, credentials, or unrelated artifacts.
- [ ] Verify restart behavior and fixture initialization from an empty data volume; ensure restart does not mint/change challenge identity, IDs, or receipt bytes.
- [ ] Stop/remove only the gateway test project after verification; prove unrelated Compose projects/containers and challenge volumes were untouched.

## 6. Config, scripts, and documentation

- [ ] Replace `config/README.md` placeholder only when there is actual gateway-owned configuration to document; describe each setting, default, validation, and secret policy, or explicitly retain and label the target slot as not implemented.
- [ ] Reconcile `.env.example` with runtime settings in `webapp/app.py` and Compose; keep it secret-free and ensure documented variables actually affect the service.
- [ ] Verify `scripts/healthcheck.sh` fails on an unavailable/non-healthy endpoint, returns nonzero on curl failure, and checks the intended service address; test both healthy and stopped-service cases.
- [ ] Verify `scripts/reset.sh` affects only the gateway's intended DB/volume and reinitializes fixtures; test reset twice and compare sanitized state to prove idempotence and independence from other challenge state.
- [ ] Review `scripts/build_entry_artifact.py` and `entry/ENTRY_MD5.txt` generation/verification for deterministic output; do not regenerate a committed artifact unless byte-level contract tests prove the expected bytes remain unchanged and the owner approves it.
- [ ] Keep `services/web-platform/README.md` consistent with actual code/build locations and runnable commands; state explicitly what remains a target slot.
- [ ] Keep player-facing docs free of raw answer values, flags, reusable credentials, session IDs, or operational secrets. Maintainer solution material must follow repository access conventions and should not be copied into public-facing checklists.
- [ ] Update `docs/verification.md` only with commands actually executed, exact scope, architecture/environment, date, and sanitized outcome; distinguish unit tests from Docker E2E.
- [ ] Document reset, local-only exposure, challenge prerequisites, expected sanitized success signal, and troubleshooting steps for each implemented gateway ID.

## 7. Tests, quality, and security gates

Run the focused test suite first, then applicable integration checks. Commands below are repository-root commands; use a project virtual environment/dependencies if available. If pytest/dependencies or Docker are unavailable, mark the corresponding checklist items blocked with the exact tool error and do not claim pass.

- [ ] Run gateway smoke tests: `PYTHONPATH=containers/gateway python3 containers/gateway/tests/test_web_lab.py` from repository root; record exit code and sanitized summary. Run `python3 -m pytest -q containers/gateway/tests` additionally only when pytest is installed and configured.
- [ ] Run syntax checks: `python3 -m compileall -q containers/gateway/webapp containers/gateway/tests containers/gateway/scripts`; record exit code.
- [ ] Run shell syntax checks: `bash -n containers/gateway/scripts/healthcheck.sh containers/gateway/scripts/reset.sh`; record exit code.
- [ ] Run Compose validation and clean image build as above; capture actual output/exit codes and platform.
- [ ] Run the official challenge/integration verification commands from `docs/challenge-design/migration-verification.md`; ensure gateway change does not alter total required/optional challenge inventory or completion checker semantics.
- [ ] Test unauthenticated route access, malformed/nonexistent identifiers, normal expected discovery, intended challenge behavior, and reset/replay using isolated temporary DB and test session state.
- [ ] Test cookie flags and session lifecycle; assess process-local session loss/restart behavior and document/resolve if it conflicts with accepted single-instance runtime.
- [ ] Review SQL construction, HTML rendering, input limits, secret-bearing errors/logging, file path configuration, and directory/DB permissions. Preserve deliberate vulnerabilities only for explicitly assigned isolated CTF behaviors; close unintended exposure without silently removing challenge-required behavior.
- [ ] Test host binding is loopback only and ensure Docker/Compose changes cannot accidentally bind `0.0.0.0` or publish SSH/web services publicly.
- [ ] Check dependency pins and known repository security conventions; avoid unreviewed dependency additions and do not run the intentionally vulnerable service against external data.
- [ ] Run `git diff --check` and inspect `git diff -- containers/gateway`; verify no secrets, raw challenge answers, generated DBs, pycache, unrelated files, or unintended binary changes are staged.
- [ ] Mark each gate independently; a passing unit suite does not imply Docker E2E, integration, security review, or handoff completion.

### Suggested verification commands

```bash
# From repository root
PYTHONPATH=containers/gateway python3 containers/gateway/tests/test_web_lab.py
python3 -m compileall -q containers/gateway/webapp containers/gateway/tests containers/gateway/scripts
bash -n containers/gateway/scripts/healthcheck.sh containers/gateway/scripts/reset.sh
docker compose -f containers/gateway/docker-compose.yml config --quiet
docker compose -f containers/gateway/docker-compose.yml build --no-cache
git diff --check
git diff -- containers/gateway
```

## 8. Independent reset/solve, receipt and integration handover

- [ ] Verify gateway reset clears/recreates only gateway-owned state and is independent of every other required challenge reset.
- [ ] Verify each assigned gateway challenge can be solved independently and repeated deterministically after reset; capture status and approved hashes/receipt metadata, never raw flag or credential bytes.
- [ ] Compare emitted receipt/flag bytes against the authoritative expected contract using the sanctioned tests/checker; do not transform, trim, re-encode, or combine receipt payloads.
- [ ] Verify gateway has no hidden dependency on another container's startup order unless the integration contract explicitly defines and tests it.
- [ ] Record inbound/outbound interfaces and dependencies (routes, ports, volumes, networks, data/receipt owner, reset owner, health check) in the integration contract through the coordinating owner; gateway-only checklist changes must not unilaterally edit another container's contract or files.
- [ ] Provide handover with exact commit, changed file paths, commands and real outcomes, test environment/architecture, challenge IDs verified, reset proof, known limitations, blocked items, and next owner/action.
- [ ] Confirm the receiving integration/assessment owner can reproduce the documented verification from a clean state without access to private secrets or undocumented local files.

## 9. Exit criteria

Gateway work is ready for handover only when every **assigned** WEB/HZ challenge has source-of-truth ownership, deterministic tests, isolated reset/solve evidence, and preserved receipt/flag bytes; web/container/docs/scripts checks are reported truthfully; station portal/SSH remain either explicitly unimplemented or separately verified under approved ownership; integration dependencies are coordinated via `docs/architecture/integration-contract.md`; and `git diff --check` plus scoped diff review show no out-of-scope changes or exposed secrets. Unassigned IDs and unavailable environment checks remain visibly pending/blocked rather than being represented as complete.
