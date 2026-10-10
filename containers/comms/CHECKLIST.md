# Comms owner checklist — NET-01..03 and shared integration

**Owner:** Comms/network-lab maintainer (fill in a named student before implementation)
**Status:** scoped backlog; this checklist is not evidence that the target topology or all routes are implemented.
**Scope:** NET-01 service discovery, NET-02 relay authentication, NET-03 internal handoff/trust boundary, and integration of the verified Comms relay into the five-domain layout. Keep existing IDs and receipt bytes stable. Never put raw flags, credentials, private keys, or reusable secrets in this checklist, test output, or committed evidence.

## Current verified state and constraints

- `containers/comms/docker-compose.yml` currently defines **three** services: `webapp` (built from `../gateway`), `comms_relay_uplink` (TCP Uplink built from `network_service/`), and `station_ssh` (an Ubuntu placeholder). This is not a five-container topology.
- The webapp and Uplink currently publish loopback host ports 8080 and 5432. All three are attached to one `web-lab` network; no narrow per-boundary network or verified comms-to-five-container routing plan exists.
- `network_service/auth_server.py` is a runnable line-oriented TCP service. `HELP`, `STATUS`, `INFO`, and `AUTH` are implemented; `INFO` exposes the value accepted by the deliberately weak auth check, and successful auth returns handoff metadata. NET-01/02 therefore have a real service basis, but the existing test has hard-coded assumptions and should not be treated as independent-route or topology proof.
- The handoff configuration exists at `data/handoff.conf`. The `station_ssh` service is explicitly a placeholder: it has no SSH server, account provisioning, authorized-key flow, or tested SSH login. Do not describe it as a working SSH foothold. NET-03's real, contained trust-boundary behavior and a live handoff remain incomplete until implemented and independently exercised.
- `services/comms-relay/README.md` is a target-slot note; it is not a separate implemented service. `infra/compose.yml` and `docs/architecture/network-layout.md` record that service aggregation and five-container runtime are deferred/unspecified. Repository migration evidence also says the layout move does not prove five running containers.
- The current auth implementation contains demo values in source. Do not copy them into new docs or output. During any cleanup, preserve the intended educational flaw and existing challenge/receipt compatibility; avoid unrelated flag or receipt edits.

## Ordered work and measurable definition of done

Check an item only after its evidence exists in the repository or has been recorded below with exact command, result, and environment. If design approval or another owner is required, leave it unchecked and name the dependency.

### 1. Freeze contracts and map the topology (prerequisite)

- [ ] Inventory the authoritative challenge IDs, receipt-producing code, current service definitions, reset scripts, and references before editing. Preserve `NET-01`, `NET-02`, `NET-03` exactly and preserve existing receipt bytes byte-for-byte; compare before/after with a deterministic test or hash.
- [ ] Record the existing service/owner matrix in `docs/architecture/network-layout.md`: Gateway webapp, Comms TCP relay, three independently isolated Operations routes, Critical offline artifacts, and Security support placeholder. List actual Compose keys and network/port policy from source; do not equate five domain directories with five processes or invent services for a target count.
- [ ] Produce a service-to-container/network diagram covering **only verified runnable services**. Distinguish Compose service count from `docker compose ps` running-container count; mark Comms' `station_ssh` as a nonfunctional Ubuntu placeholder, not an SSH daemon.
- [ ] Request integration-owner review before moving a service across Compose files or changing shared networks, published ports, or receipt contracts; document that dependency without blocking Comms-only tests and docs.

**DoD:** architecture docs enumerate the actual implemented service keys and placeholders separately, each with an owner and explicit network/port policy; a reviewer can identify NET-01/02 relay and NET-03 configuration handoff without inference.

### 2. NET-01 — enumeration on the real relay

- [ ] Define the intended player-visible entry point, protocol, host/port from the player’s actual network namespace, and expected enumeration evidence. Document why that endpoint is reachable and all unintended endpoints are not.
- [ ] Test from the intended player-side container/network (not just host localhost): resolve the documented service name, connect to the documented TCP port, and use the documented safe commands to identify the Uplink protocol. Test from an unrelated service/network and confirm the relay is unreachable unless the approved design requires access.
- [ ] Make the service bind/configuration deterministic and ensure startup fails visibly on invalid port/configuration rather than silently claiming health.
- [ ] Keep `containers/comms/docs/challenges/comms_relay.md` and its intended solution aligned with observed behavior, including prerequisites, expected evidence, and a clean-reset reproduction path. Do not include secrets or raw flags.

**DoD:** an automated integration check from the designated player-side network resolves and connects to the relay, recognizes the expected protocol, and rejects/records unexpected exposure; independent tester reproduces NET-01 from reset using only challenge instructions. Save exact command/output (redacted of sensitive values) under `containers/comms/docs/verification/`.

### 3. NET-02 — relay/auth TCP behavior

- [ ] Specify and test the line protocol: command grammar, newline framing, max line length, malformed/empty input behavior, connection close/reconnect behavior, timeouts, and deterministic responses. Bound input and prevent one client from blocking service health or other tests.
- [ ] Keep the intended authentication weakness explicit and isolated as a CTF behavior. Add positive and negative cases: discover the documented clue, demonstrate the intended flaw, reject a wrong user/token, reject malformed/oversized requests, and verify no unrelated command authenticates.
- [ ] Replace brittle source-text assertions and fixed-value assumptions in `containers/comms/tests/test_network_lab.py` with protocol-level behavioral assertions where practical. Test parsing and `response_for()` without requiring a pre-existing host service, then test the real container through its network endpoint.
- [ ] Avoid embedding production-like credentials. If configuration is moved to environment or fixture data, commit only clearly non-secret examples, validate required settings, and keep the lab isolated. Never print accepted auth material in CI evidence.
- [ ] Ensure auth success issues only the intended handoff metadata/receipt, not a fictional interactive SSH session. Preserve existing IDs and receipt bytes.

**DoD:** unit tests cover each valid command and at least five negative/boundary cases; an end-to-end TCP test proves the documented NET-02 path and a rejected control case from clean state; repeated runs produce stable non-secret evidence. `python3 containers/comms/tests/test_network_lab.py` (or the replacement documented command) exits 0 against an explicitly started stack and fails clearly when the service is absent.

### 4. NET-03 — handoff and SSH boundary (do not overclaim)

- [ ] Keep `NET-03` as the existing `data/handoff.conf` configuration/trust-boundary proof. Document the exact metadata handoff and player perspective. Do not conflate receipt of handoff metadata with a live SSH session.
- [ ] Remove any claimed SSH-login success from player/architecture docs and tests; `station_ssh` is an inert Ubuntu placeholder and must remain labeled as such in this task. A real SSH daemon is out of scope absent a separately reviewed feature request.
- [ ] Test that only the intended relay authentication returns the handoff metadata; unauthenticated, malformed and unrelated direct inputs fail. Assert the config is readable only in its documented local context and NET-03 remains independently verifiable without SSH.

**DoD:** clean reset → relay enumeration → intended auth → NET-03 config/handoff observation succeeds, rejected control fails, and no docs/tests claim an SSH session. Actual SSH remains unimplemented and is not a blocker for the existing three NET IDs.

### 5. Integrate the verified Comms relay into the central topology

- [ ] Keep `containers/comms/docker-compose.yml` as the standalone development stack and add its **verified relay** to `infra/compose.yml` through an integration-owner-reviewed change; do not copy its `webapp` duplicate or nonfunctional `station_ssh` placeholder into the central model.
- [ ] Document standalone versus central launch commands and use consistent service names/network aliases without changing receipt IDs or bytes.
- [ ] Give the relay only required network memberships; test allowed player-to-relay traffic and denied unintended traffic. Make startup health-aware rather than relying on `depends_on` as readiness.
- [ ] Keep host relay ports internal unless a documented local player workflow needs them; any published host port binds `127.0.0.1`. Check for collisions in standalone and central modes.
- [ ] Use stable service DNS names rather than container IPs. Remove sensitive Compose literals; use safe non-secret examples and ignore real `.env` files.
- [ ] Preserve independent routes: NET handoff is not an unlock prerequisite for unrelated WEB/Operations/Critical challenges; verify reset and solve isolation.

**DoD:** standalone and central Compose config both pass; the central model includes each verified runnable component, no placeholder SSH or duplicate webapp, with documented network memberships and only loopback host bindings. Clean build/start/health and allowed/denied connectivity checks pass for Comms. Do not demand exactly five processes when route isolation requires more or offline artifacts require none.

### 6. Reset, readiness, test orchestration, and failure modes

- [ ] Update `containers/comms/scripts/reset.sh` to be location-independent, scoped to the intended Compose project, deterministic/idempotent, and safe around shared services/volumes. It must not stop or delete another project’s containers. Document any preserved state and ensure sensitive ephemeral key material is removed or regenerated.
- [ ] Update `containers/comms/scripts/healthcheck.sh` to test actual TCP/protocol readiness (not HTTP on the TCP-only relay), expected negative auth behavior, and any real SSH readiness only if SSH is implemented. Bound each probe with a timeout and return nonzero on failure.
- [ ] Add Docker healthchecks with tools available in the image, meaningful start periods/retries, and tests that distinguish process-running from protocol-ready. Ensure healthcheck commands do not reveal tokens, receipts, or flags.
- [ ] Add a single documented clean acceptance sequence: reset → build/start → wait for health → NET-01 → NET-02 → NET-03 boundary test → reset again. Each phase must stop on failure and preserve useful redacted logs.
- [ ] Test failure/recovery cases: missing config, port collision, relay unavailable, unhealthy dependency, interrupted reset, repeated reset, repeated clean startup, and test execution when Docker is absent (clear actionable failure, not misleading pass).

**DoD:** two consecutive clean reset/build/test/reset runs pass on the supported environment; all services become healthy within a documented bounded timeout; deliberate service shutdown makes health/integration checks fail nonzero; reset leaves no project-owned container/network/volume residue except explicitly documented persistent data. Capture actual output in verification evidence.

### 7. Docs, independent reproduction, QA, and sign-off

- [ ] Update `docs/labs/network-lab.md`, `containers/comms/docs/challenges/comms_relay.md`, `containers/comms/docs/solutions/slice-b.md`, `containers/comms/services/comms-relay/README.md`, Compose comments, and relevant architecture/verification docs together. Remove stale host paths, obsolete usernames/commands, purported SSH success claims, and assumed HTTP health endpoints.
- [ ] Keep implementation facts separate from target design and open work. Use explicit labels such as **Implemented and tested**, **Planned**, and **Placeholder**. Do not mark a route complete based only on a source file or Compose stanza.
- [ ] Record for each NET ID: owner, preconditions, intended route, expected non-secret evidence, exact reset/run/test commands, files implementing it, negative controls, and known limits. Preserve all existing IDs and receipts exactly.
- [ ] Have a student other than the implementer follow only player-facing instructions from a clean checkout/reset. Record OS/architecture, Docker/Compose versions, exact commands, pass/fail, timing, and sanitized output. The tester must not use undocumented source inspection or author-only credentials.
- [ ] Run comms unit/integration tests, Compose config validation, shell syntax checks, documentation link/path checks, and relevant cross-route regression tests. Review `git diff --check`; review the final diff for accidental secret/flag leakage and unrelated receipt changes.
- [ ] Obtain comms owner and integration reviewer sign-off. Record unresolved issues and a specific next owner/task; do not silently convert a failed or skipped verification to pass.

**DoD:** independent tester reproduces each claimed NET route from clean reset; every checklist completion has a command and retained result; docs match observed runtime; IDs/receipt bytes are unchanged; no raw flags/credentials in diff/evidence; cross-route tests show the comms changes do not break independent routes.

## Verification record (append real results; do not pre-fill as passed)

| Date / environment | Exact command | Result / evidence path | Owner |
|---|---|---|---|
| Pending | Pending | No new verification performed by authoring this checklist | Pending |

## AI update instructions

1. Read this checklist, `docs/architecture.md`, `docs/architecture/network-layout.md`, `docs/labs/network-lab.md`, the comms Compose/source/tests/reset/healthcheck, and current Git diff before acting.
2. Start with the earliest unchecked prerequisite. Inspect before editing; do not infer a service is implemented from its directory or name.
3. Change only files within the agreed ownership boundary. Preserve challenge IDs and receipt bytes. Do not expose flags, credentials, private keys, or sensitive runtime values in chat, committed files, or logs.
4. Run the exact relevant checks, record actual commands/results/evidence paths, and check an item only when its measurable DoD is met. Mark blocked/deferred work as such with the reason and next owner.
5. Before reporting completion, verify the final diff and confirm the integrated topology includes only verified runnable services; report the count of actually healthy processes separately from the five domain ownership directories.
