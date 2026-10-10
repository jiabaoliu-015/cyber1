# HVAC Lab — Thermal Regulation / HVAC Control (Station Erebus)

> **Integration status:** standalone boundary only. Callisto/campaign fates remain provisional pending cross-lab canon review and an integrated route test; this challenge card does not assert campaign-ready integration.

Flowchart path: `Default-User -> Predictable SSH passwords (horizontal) -> Engineer-User -> Scheduled tasks Module -> Scheduled Task Exploit (vertical) -> HVAC Control -> Mid flag in maintenance report`.

SSH is the only player entry (`ssh default@localhost -p 2223`, password
`HVAC-1001-STAT`). FastAPI stays on container-localhost `127.0.0.1:8081` as
a backend for the `hvac` CLI, which maps the Unix user to its token.

Shared campaign canon: station `Erebus` — Tallis Group crewed station, Callisto orbit,
AI ORACLE, last human contact 16 Sep 2026, ground-link blackout 20 Sep 2026
(network-chain terminal `erebus`).
Foothold accounts (network-chain): `gh0st` (1st Officer Becker's backdoor) and
`controlsvc` (company-issued). Crew (canon): Captain Jin Hong (j.hong, Alive),
1st Officer John Becker (j.becker, Unaccounted for — see
`data/shift_notes/becker_unaccounted_058.txt`), Chief Engineer Hank Mercer
(h.mercer, Deceased at power — the engineer uid `1002` in this lab is his seat),
Medical Officer Yara Nassar (y.nassar, Missing — last badge-in medbay, see
`data/medical_logs/nassar_last_badge_059.txt`), Researcher Wu Yan (w.yan,
Deceased/Missing — research lab sealed from inside). No Tech 2nd class exists;
the duct-sitting fixation arc belongs to Becker.

## Horizontal priv (predictable SSH passwords)
1. `ssh default@localhost -p 2223` (password `HVAC-1001-STAT`).
2. Password format is `HVAC-{uid:04d}-STAT`; engineer uid is `1002`.
3. `su engineer` with `HVAC-1002-STAT`; `hvac status` now succeeds.
4. As default, `hvac status` gets `403`; as engineer it succeeds.

## Vertical priv
1. As engineer: `hvac schedule` shows `* * * * * root /opt/hvac/process_job run`, input `/var/run/hvac/input`.
2. `hvac schedule-input --content run_diagnostic` (engineer only); API returns queued.
3. Wait for the next once-per-minute root cron tick; it writes `/var/run/hvac/maintenance_report.txt` containing the runtime `HVAC_FLAG`.
4. `hvac report` (engineer only) reads the flag.

## Station flavor / decoys (no flag — shared ship store with Power console)
- `hvac logs` (engineer only) indexes `data/crew_logs`, `data/shift_notes`, `data/engineer_logs`, `data/diagnostics`, `data/medical_logs`, `data/research_notes`, `data/reactor_logs`, `data/blackbox_logs`, `data/comms_logs` — identical set served by the Power console so both docker containers appear to share one log store.
- `hvac log --category <cat> --name <file>` reads one decoy file (traversal-safe, `.txt` only).
- `hvac history` lists archived failed/routine diagnostics (all decoys, no flag).
- Story arc (Erebus heat wave): Thermal Regulation failing station-wide
  (supply 21.5C lost, returns 27-28C, filter 90%+), crew too hot to sleep/work,
  First Officer John Becker (paranoid-and-right, now Unaccounted for)
  behaving strangely (missed check-ins, duct-sitting, stethoscope,
  condensate notebooks — see `data/engineer_logs/becker_duct_run_044.txt` and
  `data/engineer_logs/mercer_concern_memo_becker.txt`), Medical Officer Nassar
  Missing from medbay, weird warm object K-9 in aft hold driving temps + 17 Hz hum.
- Decoy reports deliberately share the maintenance-report format so players must
  distinguish the live `/api/maintenance/report` (root job, `status: success`) from
  archived failures. Engineer logs contain red herrings (wrong phrases like
  `diagnostic_run`, wrong case, old paths) — trust `GET /api/schedule`, not old notes.

## Ops
- Runtime flag: `./flags/init_flags.sh` (writes `.env`, like network-chain) before first run.
- Run: `docker compose up --build -d`, `./scripts/healthcheck.sh`
  (checks backend in-container + `ssh-keyscan -p 2223`).
- SSH entry: `ssh default@localhost -p 2223` (`HVAC-1001-STAT`), `su engineer` (`HVAC-1002-STAT`).
- Reset: `./scripts/reset.sh` (clears input + report)
- No brute force; SSH on loopback `127.0.0.1:2223`, web backend on container-localhost only.

## Mitigations
- Horizontal: random per-session tokens, server-side session store, enforce authz per user.
- Vertical: root job must not trust lowpriv-writable input; drop privileges, validate allow-listed commands, write reports to root-only paths.
