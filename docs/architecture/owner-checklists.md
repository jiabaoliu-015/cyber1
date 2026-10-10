# Five-container owner checklist contract

These are execution trackers, **not claims that five runtime containers or all diagram services exist**. Each owner updates their own checklist after a verified change. Source of truth for current challenges: `challenges/manifest.json` (17 required, one optional, separate `COMPLETE-01`); narrative design: `docs/story/README.md`. The official 2026 S2 project brief is `~/uni/CITS3006/external/uwacyber-cits3006/cits3006-assessments/project.md` on `origin/2026s2`; the brief prioritises required vulnerability coverage, three distinct working root paths, two advanced challenges, real difficulty, reproducible setup/solutions, independent research, and every member's ability to explain and demonstrate the work. No speculative station module earns credit merely because its directory exists.

## Ownership and progress update protocol

- [Gateway](../../containers/gateway/CHECKLIST.md) — portal, web and horizontal challenges, entry artifact.
- [Comms](../../containers/comms/CHECKLIST.md) — relay, network challenges, handoff and internal network.
- [Security](../../containers/security/CHECKLIST.md) — currently empty boundary; bounded access-control/watchdog support, not additional required challenge claims.
- [Operations](../../containers/operations/CHECKLIST.md) — three distinct root-route challenges plus the standalone Medbay RE-03 investigation.
- [Critical](../../containers/critical/CHECKLIST.md) — currently houses RE-01/02 pending allocation of one elsewhere, plus two advanced challenges and a legacy RE-03 compatibility build; completion remains separate.

For every checklist item: leave `[ ]` until its stated acceptance command/observation passes **from a clean reset**; then set `[x]` and add a terse dated evidence line with commit/PR, command, result, and sanitized log path or review link. Never mark complete from a proposed file, a prior run, or a different checkout. If blocked, keep `[ ]`, add `BLOCKED: reason; dependency owner/task ID; next executable action`. Do not place flag values, passwords, private tokens, or connection material in public checklist evidence. Prefer one small PR per independent milestone; obtain a different team member's review and approval before any merge into `main`.

## Fixed implementation boundaries (no new design vote required)

1. Retain all current required/optional IDs, deliberately vulnerable mechanics and independent start/reset/solve; `COMPLETE-01` stays separate. Do not turn diagram arrows into mandatory unlocks.
2. Keep host exposure loopback-only (`127.0.0.1`); internal services use a private Compose network. Never expose exercise services on a public/LAN interface by default.
3. Use the five directory names as ownership boundaries. Do **not** force exactly five Docker processes by merging unrelated privilege boundaries: if consolidation prevents three genuinely distinct root paths or breaks reproducibility, keep isolated route containers and document the deviation. The central `infra/compose.yml` must orchestrate each **verified** runtime component and declare its interface, while empty proposed modules remain explicitly not implemented.
4. `containers/gateway/` owns the web app, `containers/comms/` the existing TCP auth relay, `containers/operations/` the three root routes and standalone Medbay RE-03 service, and `containers/critical/` the remaining offline artifacts. `containers/security/` may add the smallest deterministic station access-control/watchdog *support* service after integration tests specify its boundary; it must not suppress intended vulnerabilities or be counted as an extra required challenge.
5. Preserve challenge and receipt IDs and existing opaque flag bytes during structural work. The known crypto/completion fixture mismatch is an exception requiring an **explicit test-backed reconciliation** of fixture, solver, checker, and player instructions; do not silently change the final flag or present the currently failing tests as green.
6. Do not present the flowchart's open crew mystery, culprit, captain-key progression, reactor or black-box exploit as settled canon. The standalone Medbay case follows Erebus/Yara Nassar/Wu Yan; its **21 September last-sighting timestamp is a reviewable local evidence detail**, not proof of Wu Yan's ultimate fate. Other destinations remain story/design candidates unless implemented, independently tested, and documented within assessed scope.

## Acceptance for the layout/retheme/handoff PR

This PR moves files into five **ownership domains**, rethemes existing names and player copy, and supplies execution checklists. It does **not** promise a finished playable campaign or five live Docker processes. It is review-ready when: (1) manifest references and README/checklist links resolve; (2) moved services still pass the applicable focused tests and Compose config checks that passed at baseline; (3) the diff contains no unexplained changes to IDs, receipt/flag bytes, route mechanics or host exposure; (4) every placeholder is explicitly labeled as such; and (5) known baseline failures, skipped runtime checks and follow-up owner tasks are disclosed in the PR. A failing test introduced by the move/retheme is a regression to fix on this branch. Another team member must review and approve before merge.

## Campaign completion gate (future owner work, not PR #4's scope)

- [ ] Every required category has its prescribed number of distinct reproducible vulnerabilities; at least three **different** working root methods and two working advanced challenges are demonstrated. Evidence links live in each owner's checklist and `challenges/manifest.json`.
- [ ] A fresh clone on an intended host can set up, reset, discover, solve, and verify every claimed route and the separate completion check using documented commands; no existing containers or developer-local paths are prerequisites. A second member reproduces each owner's path.
- [ ] Existing red offline/completion tests and four Operations syntax errors are fixed and verified; they are disclosed as existing baseline failures in the layout PR, not silently marked as passing.
- [ ] `infra/compose.yml` accurately reflects runnable services, no host ports are broadly exposed, and container image/health checks plus integration tests pass on clean state. The README and architecture docs describe actual topology rather than promised services.
- [ ] Every counted challenge has a marker-only sample solution, vulnerability mechanism and mitigation explanation, reset/acceptance test, report-section handoff, demo observation and individual-contribution record. Player release excludes solutions and secrets. Each owner can explain their work **and** give a high-level explanation of the full challenge set.

The existing checklist boxes are a living handoff to subsequent owner PRs. They are not all prerequisites for review or merge of the narrower layout/retheme PR. Do not merge that PR if its structural changes caused new failures, if its scope is misrepresented, or without another team member's approval.
