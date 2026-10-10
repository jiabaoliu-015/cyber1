# Flag and handoff ledger

This is a maintainer ledger. It deliberately names artefacts and reset paths without reproducing raw flag values in player-facing documentation.

| Stage | Evidence / handoff ID | Location or producer | Prerequisite | Reset / verification | Human owner |
|---|---|---|---|---|---|
| A | Web Application SQLi archive evidence | `GET /api/search` hidden archive record | Web Application recovery login | `containers/gateway/scripts/reset.sh`; Web Lab acceptance | Unassigned |
| A | Web Application stored-XSS moderation proof | feedback queue → `/moderation/queue` | Web Application recovery login | `containers/gateway/scripts/reset.sh`; browser + Web Lab acceptance | Unassigned |
| A | Web Application profile horizontal evidence | `GET /api/profiles/mira.chen` | Web Application recovery login | `containers/gateway/scripts/reset.sh`; Web Lab acceptance | Unassigned |
| A | Web Application backup horizontal evidence | `GET /api/backups/3` | Web Application recovery login | `containers/gateway/scripts/reset.sh`; Web Lab acceptance | Unassigned |
| A | Web Application IDOR evidence + Network Service handoff | Web Application research fixture | Entry image / Web Application login | `containers/comms/scripts/reset.sh`; Network Lab health check | Unassigned |
| B | Handoff `lab user` handoff | Authentication Service `INFO` then flawed `AUTH` | Web Lab handoff | `containers/comms/scripts/reset.sh`; Network Lab health check | Unassigned |
| C | Root proof and post-root recovery pack | SUID route, scheduled-job route, or local-root-service route | Handoff foothold | `tools/reset_full_campaign.sh`; full harness | Unassigned |
| D | ARTEFACT 1–3 outputs | `containers/critical/offline-artifacts/` binaries/solvers | Post-root recovery pack | Route tests/build scripts; ARTEFACT 1 limitation noted in checklist | Unassigned |
| D | Crypto Lab recovery record (`THREAD_02`) | `containers/critical/offline-artifacts/solvers/crypto_solver.py` | Post-root recovery pack | `tools/reset_late_campaign.sh`; late-campaign/full harness | Unassigned |
| D | Oracle Lab oracle result | `containers/critical/offline-artifacts/source/oracle_lab/` and solver | Post-root recovery pack | `containers/critical/offline-artifacts/tests/test_offline_artefacts.py` | Unassigned |
| E | Completion Check final evidence / final flag | `challenges/completion/` evidence assembly | THREAD_01–04 including Crypto Lab THREAD_02 | `tests/integration/test_late_campaign.py`; full harness | Unassigned |

## Handling rule

- Keep literal flags in challenge fixtures and test assertions only where needed for deterministic local verification.
- Do not copy literal flags into public reports, player guides, screenshots, or this ledger.
- Before submission, replace every `Unassigned` field with the responsible team member and add the related commit and reviewer to `CONTRIBUTIONS.md`.
