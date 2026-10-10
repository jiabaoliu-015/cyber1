# CITS3006 CTF Project — Team Execution Checklist

**Goal:** Build, document, solve and demonstrate a reproducible, story-led CTF campaign: **IF YOU’RE READING THIS: The Web**.

**Non-negotiable:** AI may help scaffold, test, organise and critique. Every team member must personally understand and be able to reproduce/explain their assigned work during Task 3; unexplained AI-generated work does not count.

---

## 0. Assessment gates

- [ ] Group has five members (or coordinator approval for 4/6) and confirmed AMD + ARM access.
- [ ] Group registration and leader confirmation completed in Teams.
- [ ] A private Git repository exists; all members have access.
- [ ] `CONTRIBUTIONS.md` records owner, date, commit/artefact, review and demo responsibility for every meaningful contribution.
- [ ] Agree a target environment: isolated Docker/internal network, no exposure to public internet, reproducible on a clean machine.
- [ ] Confirm Task 1 LMS deadline, Task 2 portal/deadline, and Week 12 demo booking in Teams.

## 0.1 `poc` branch implementation snapshot — 19 September 2026

**Reviewed commit:** `809d005` clean-clone verification on a separate gaming-PC environment. This is an evidence-based implementation snapshot, not a claim that human review or assessment submission is complete.

- [x] Private project repository and a project `README.md` exist.
- [x] Slice A source, Compose configuration, player/maintainer documents, reset/health-check scripts and fixture tests exist. Compose now publishes only `127.0.0.1:8080`; a real host health request returned `{"status":"ok","service":"webapp"}`, and the entry/IDOR fixture check passed inside its runtime image.
- [x] Slice B’s corrected Compose stack launches Crew Portal plus Comms Relay Uplink on loopback only. The Uplink socket acceptance flow (`INFO` challenge leak → `AUTH station_crew <challenge>`) and all Slice B checks pass against the live container.

- [x] Slice C is implemented: MAINTENANCE_UTILITY, SHIFT_SCHEDULER and LOCAL_CONTROL_SERVICE now have container-backed route artefacts. MAINTENANCE_UTILITY, SHIFT_SCHEDULER and LOCAL_CONTROL_SERVICE image builds, health checks and in-container root-proof runs pass. Each live route includes `/entry/post_root_handoff.txt`. The unified A→E harness includes all three routes.
- [x] Slice D has RECOVERED ARTIFACT 1–3, Uplink Vault and Station Audit artefacts. RECOVERED ARTIFACT 2's portable acceptance test passed locally on ARM64: reset → build → derive via validator inversion → reject invalid key → accept derived key → verify `strings` does not leak the key/flag → reset. The combined RECOVERED ARTIFACT 3/Uplink Vault/Station Audit acceptance test passes locally. A post-root recovery handoff identifies Uplink Vault’s `THREAD_02=...` output as the INCIDENT ARCHIVE completion record. RECOVERED ARTIFACT 1 remains path-dependent and has not been made portable.
- [x] Slice E has a deterministic INCIDENT ARCHIVE archive, THREAD_01–04 evidence readout, Uplink Vault THREAD_02 validation, LIABILITIES reveal, final flag and reset script. `tests/integration/test_late_campaign.py` proves the local recovery segment; `tests/integration/test_full_campaign.py` now runs the clean A→B→C→D→E runtime spine.
- [x] Root `tools/reset_full_campaign.sh`, `tools/healthcheck_full_campaign.sh`, and `tests/integration/test_full_campaign.py` provide an exercised full integration path. `.env.example`, `docs/architecture.md`, `docs/flag-ledger.md`, and the factual `CONTRIBUTIONS.md` template are present. The full runtime proof passed from a fresh clone on a separate gaming-PC environment. Human ownership/reviewer fields remain to be completed truthfully.

**Immediate build priority:** obtain non-author team reproduction evidence and complete truthful ownership/reviewer/demo attribution; then assemble the Task 1 submission package.

## 1. Approved campaign spine

### Premise
John receives a dead-man’s-switch email from his missing friend. An untouched photograph hides maintenance access to **The Web**, the company’s neglected-but-deliberately interconnected internal infrastructure. The friend left evidence of corporate money laundering; every system John touches both advances the investigation and alerts whoever controls the Web.

**Core line:** *Pull one thread and another moves.*

### Final reveal
`INCIDENT ARCHIVE` contains `THREAD_01`, `THREAD_03`, `THREAD_04`; `THREAD_02` is the missing evidence page. The completed evidence identifies John as a **LIABILITY**. The Web reports that his recovery path has been observed.

- [ ] Team agrees this is the final narrative direction, or records deviations here.
- [ ] Team defines a single flag format, e.g. `CTF{...}`.
- [ ] Every challenge produces either a flag, a credential, a host/service clue, a decryption key, or a final-evidence fragment.
- [ ] No clue requires guessing or brute force.

## 2. Campaign / exploit map

```text
Dead-man email + original image
        │  (metadata/stego + MD5-derived recovery credential)
        ▼
THE CREW_PORTAL — public research / observation portal
  ├─ SQLi  ──────────────────────────┐
  ├─ Stored XSS ─────────────────────┼─► COMMS_RELAY clue / access material
  └─ IDOR ───────────────────────────┘
                                      ▼
COMMS_RELAY — forgotten internal network node
  ├─ exposed custom Uplink service
  ├─ flawed authentication
  └─ insecure internal trust boundary ─► STATION_SSH
                                      ▼
STATION_SSH — low-privilege `station_crew` foothold
  ├─ MAINTENANCE_UTILITY: SUID route ───────────────┐
  ├─ SHIFT_SCHEDULER: writable root scheduled job┼─► root (three independent routes)
  └─ LOCAL_CONTROL_SERVICE: local root service ┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
RECOVERED STATION ARTIFACTS            UPLINK VAULT
  ├─ runtime secret             └─ modern crypto misuse
  ├─ custom validation              (e.g. nonce reuse)
  └─ real-vs-decoy logic                  │
          └──────────┬────────────────────┘
                     ▼
STATION AUDIT — non-time-based side-channel (e.g. padding oracle)
                     │
                     ▼
AUTOMATED AGENT — optional indirect prompt-injection branch
                     │
                     ▼
INCIDENT ARCHIVE — Threads/evidence + final flag + station incident readout
```

**Design rule:** the three web, network and root vulnerabilities are coverage branches/alternatives where practical—not a 15-lock mandatory linear grind. All branches must be independently reproducible and documented.

## 3. Coverage ledger (assign owners before implementation)

| Requirement | Challenge / implementation | Owner | Evidence/acceptance test | Status |
|---|---|---|---|---|
| Network 1 | Comms Relay exposed Uplink service | | Scan reveals only intended service; documented route | [ ] |
| Network 2 | Uplink flawed authentication | | Credential/logic is recoverable from prior clue | [ ] |
| Network 3 | Internal trust abuse | | Forged/relayed authorised request reaches intended boundary | [ ] |
| Web 1 | Crew Portal SQLi | Unassigned | `containers/gateway/tests/test_web_lab.py`: injected archive search returns hidden record | [x] automated local verification; non-author reproduction still required |
| Web 2 | Crew Portal stored XSS | Unassigned | `containers/gateway/tests/test_web_lab.py`: feedback is stored and returned unescaped by moderation queue | [x] automated local verification; non-author browser reproduction still required |
| Web 3 | Crew Portal IDOR | Unassigned | `containers/gateway/tests/test_web_lab.py`: record 2 is returned to maintenance user | [x] automated local verification; non-author reproduction still required |
| Horizontal 1 | Another researcher profile/resource | Unassigned | `containers/gateway/tests/test_web_lab.py`: Mira profile private note is exposed | [x] automated local verification; non-author reproduction still required |
| Horizontal 2 | Another user backup/evidence | Unassigned | `containers/gateway/tests/test_web_lab.py`: Eli backup is exposed | [x] automated local verification; non-author reproduction still required |
| Horizontal 3 | Another research resource | Unassigned | `containers/gateway/tests/test_web_lab.py`: Mira research record is exposed | [x] automated local verification; non-author reproduction still required |
| Vertical 1 | MaintenanceUtility SUID | | `station_crew`→root route works and resets | [ ] |
| Vertical 2 | ShiftScheduler writable root job | | `station_crew`→root route works and resets | [ ] |
| Vertical 3 | Local Control Service local root service | | `station_crew`→root route works and resets | [ ] |
| RE 1 | Recovered Artifact 1: runtime-reconstructed secret | | `strings` alone is insufficient; intended solve works | [ ] |
| RE 2 | Recovered Artifact 2: custom key validator | Unassigned | `python3 containers/critical/offline-artifacts/tests/test_validator_inversion.py` passes: derived key accepted, invalid key rejected, and `strings` leakage checks pass | [x] local ARM64 verification; non-author reproduction still required |
| RE 3 | Recovered Artifact 3: real vs decoy path | Unassigned | `python3 containers/critical/offline-artifacts/tests/test_offline_artefacts.py` passes | [x] automated local verification; non-author reproduction still required |
| Advanced 1 | Uplink Vault modern crypto flaw | Unassigned | `python3 containers/critical/offline-artifacts/tests/test_offline_artefacts.py` passes and emits THREAD_02 | [x] automated local verification; non-author reproduction still required |
| Advanced 2 | Station Audit side-channel | Unassigned | `python3 containers/critical/offline-artifacts/tests/test_offline_artefacts.py` passes | [x] automated local verification; non-author reproduction still required |
| Optional advanced | Automated Agent indirect prompt injection | | Untrusted document causes bounded, intended disclosure | [ ] |

## 4. Repository and environment foundation

- [x] `README.md`: campaign summary, quick start, supported platform, safety boundary.
- [x] Documented equivalent to root Compose: root reset/health scripts coordinate slice-specific Compose files.
- [x] `.env.example`; no runtime secrets are required by the verified harness.
- [x] Root reset/health scripts restore and verify the full campaign baseline.
- [x] Host-published lab services are loopback-only; Slice C services are container-scoped.
- [x] `docs/architecture.md` with service diagram, ports, trust boundaries and owner placeholders.
- [x] `docs/flag-ledger.md` with handoff ID, location, prerequisite, owner placeholder and reset method; raw flags excluded.
- [x] `.gitignore` covers common secrets/build/test artefacts.
- [x] Clean clone → reset → health → full runtime proof, including a separate gaming-PC environment.

## 5. Build order: vertical slices

### Slice A — playable entry
- [ ] Implement Crew Portal with harmless seed data and narrative entry artefact.
- [ ] Implement one intended web route end-to-end.
- [ ] Produce a clue that reaches Comms Relay.
- [ ] Write the player-facing text and maintainer sample solution.
- [ ] Fresh tester completes it without author intervention.

### Slice B — network transition
- [ ] Implement Comms Relay service and one safe internal-only network challenge.
- [ ] Add enumeration evidence, clue chain and reset support.
- [ ] Independent tester reaches Station SSH from a clean reset.

### Slice C — privilege escalation
- [ ] Implement each root path separately; do not let one broken route invalidate the others.
- [ ] For each route: baseline permissions → intended exploitation → root proof/flag → reset test.
- [ ] Record why it is a vertical escalation vulnerability and how it is discovered.

### Slice D — advanced/reversing branches
- [ ] Build RE binaries with source, build instructions and deterministic output.
- [ ] Build Uplink Vault with the intended modern-crypto misuse and a verified solver.
- [ ] Build Station Audit with bounded/reliable oracle behaviour and a verified solver.
- [ ] Only add the Automated Agent branch after the required two advanced challenges work end-to-end.

### Slice E — convergence and polish
- [ ] Implement the Incident Archive, `THREAD_02`, evidence assembly and final flag.
- [ ] Ensure every route/clue points somewhere unambiguously.
- [ ] Write enough story to create atmosphere, not enough to hide technical instructions.
- [ ] Conduct a reset-and-playthrough test of every route.

## 6. Per-challenge definition of done

For **every** row in the coverage ledger:

- [ ] Owner writes a concise challenge card: goal, prerequisite, target, intended vulnerability, hint, flag/clue, reset method.
- [ ] Owner writes a step-by-step sample solution with expected observations—not just commands.
- [ ] Owner demonstrates the vulnerability from a clean environment.
- [ ] A non-author team member reproduces it using only the supplied player material and reasonable enumeration.
- [ ] Team records runtime, failure modes and any flaky behaviour.
- [ ] Challenge has no accidental alternate path that bypasses its intended learning objective.
- [ ] Owner can explain the underlying vulnerability, exploitation mechanics, mitigation, and why the design is fair.
- [ ] Commit, issue/task link, and reviewer are recorded in `CONTRIBUTIONS.md`.

## 7. Quality / difficulty review

- [ ] Difficulty comes from discovery, enumeration, analysis and chaining—not hidden errors, arbitrary filters or brute force.
- [ ] Challenges are solvable without unauthorised activity outside the lab.
- [ ] Every provided solution works after a full reset.
- [ ] Every service is reachable as documented on AMD and ARM, or architecture-specific limitations are explicit and tested.
- [ ] At least one full playthrough is performed by a teammate who did not author the route.
- [ ] Fix all blockers, flaky timing, missing dependencies and undocumented manual steps.
- [ ] Run a demo rehearsal with an intentionally fresh setup.

## 8. Task 1 submission package

- [ ] Group report includes: campaign overview, exploit map, every required category, advanced challenges, intended difficulty, and sample solutions.
- [ ] Report explicitly maps every coverage-ledger requirement to a challenge.
- [ ] Report names individual contributions clearly and truthfully.
- [ ] Setup instruction PDF: prerequisites, safe network isolation, start, reset, health check, known limitations and teardown.
- [ ] Challenge files/repository link are accessible to the coordinator.
- [ ] Group leader submits report to LMS by Week 10 Wednesday 11:59pm.
- [ ] Group leader emails/shares challenge files and setup PDF as instructed.
- [ ] Team books Week 12 demo slot in Teams.
- [ ] Final independent clean-machine reproduction completed before submission.

## 9. Task 2: solve other groups’ CTFs

- [ ] Assign live-session roles: enumeration, web, network, notes/flag submission, coordination.
- [ ] Attend the Week 11 live lecture CTF with the group.
- [ ] Keep a factual per-target log: target, observation, hypothesis, technique, result, flag/no flag, contributor.
- [ ] Complete remaining available challenges before the Friday 11:59pm deadline.
- [ ] Submit all discovered flags to the official portal.
- [ ] Write the findings report: flags, vulnerabilities, tools/techniques, obstacles, unsolved attempts, individual contributions, and most-fun vote rationale.
- [ ] Do not claim a technique or contribution that was not actually performed/understood by the named person.

## 10. Task 3: live demo and Q&A

- [ ] Reconfirm booking, room, equipment, adapters and internet/local environment.
- [ ] Prepare one clean, resettable demo environment plus an offline fallback recording/screenshots only if course rules permit.
- [ ] Time-box the one-hour flow: opening/story → created challenge demonstration → exploit/solution → Task 2 solving evidence → each member’s contribution → Q&A buffer.
- [ ] Every member demonstrates a substantial contribution and can explain at least the overall campaign/exploit map.
- [ ] Rehearse all commands from a clean state; record exact recovery steps if a demo target fails.
- [ ] During Q&A, explain mechanics and evidence honestly; never bluff beyond what the team understands.

## 11. Final archive

- [ ] Tag the final submitted commit.
- [ ] Export final report, setup PDF, source/challenge bundle, contribution ledger and demo run sheet.
- [ ] Preserve all source, build instructions and versions needed for reproduction.
- [ ] Record retrospective: what was built, who built/reviewed it, what worked, what should change.

---

# AI-agent handoff prompt (bounded, review-first)

> You are a development assistant supporting a **student team** building the CITS3006 CTF campaign **“IF YOU’RE READING THIS: The Web.”** Read `CITS3006_CTF_PROJECT_EXECUTION_CHECKLIST.md` before acting.
>
> Your job is to help with **scaffolding, isolated lab implementation, tests, documentation templates, reproducibility checks, and issue tracking**. Do not submit work, impersonate a student, fabricate contribution records, or mark an item complete without tool output proving it. Do not work outside the explicitly isolated CTF repository/network.
>
> Work one vertical slice at a time:
> 1. Inspect the repository and identify the next unchecked task with a named human owner.
> 2. Propose a minimal implementation plus acceptance tests.
> 3. Implement only after the responsible student confirms the technical design and has read/understood it.
> 4. Run the exact verification commands; preserve outputs in `docs/verification/`.
> 5. Update the checklist/status only with evidence and leave a concise handoff: changed files, commands run, results, unresolved risks, and what the owner must be able to explain in the demo.
>
> Architecture constraints: internal-only Docker/host-only lab networking; no public exposure; no real targets, credentials, malware or data; deterministic reset; every required challenge has a documented intended solution and independent reproduction test.
>
> Story design: a company brief leads the player through Coriolis crew records, comms, station operations and recovered artifacts to investigate the crew's fate. The Incident Archive aggregates evidence; the diagram's captain keys, reactor and black box are proposals, not implemented services. The current required challenges remain independent, and the Station SSH foothold is a placeholder. Keep `THREAD_02` and other existing receipts stable until the known completion-fixture discrepancy is fixed; do not add scope until required coverage is working and team-reviewed.
>
> At the start of each work session, return: **next task, owner, acceptance test, risk, and exact commands to verify.** At the end, return: **evidence, changed files, test output, and human explanation checklist.**
