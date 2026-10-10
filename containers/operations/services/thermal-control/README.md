# HVAC Lab service (flowchart: Thermal Regulation / HVAC Control — Station Erebus)

> **Integration status:** standalone lab boundary only. Callisto/campaign fates are provisional here; coordinate shared canon and a composed player-route test with the network-chain and Power labs before calling this campaign-ready.

Station `Erebus` — Tallis Group crewed station, Callisto orbit; station AI ORACLE;
last human contact 16 Sep 2026; ground-link blackout 20 Sep 2026 (shared canon; foothold accounts `gh0st`
(Becker's backdoor) / `controlsvc` live on the network-chain terminal `erebus`).
Crew (canon): Captain Jin Hong (j.hong, Alive), First Officer John Becker (j.becker,
Unaccounted for — see `data/shift_notes/becker_unaccounted_058.txt`), Chief Engineer
Hank Mercer (h.mercer, Deceased at power — engineer seat `uid 1002` in this lab is
his seat), Medical Officer Yara Nassar (y.nassar, Missing — last badge-in medbay,
see `data/medical_logs/nassar_last_badge_059.txt`), Researcher Wu Yan (w.yan,
Deceased/Missing — research lab sealed from inside).

SSH entry only (pure SSH, no web login). FastAPI stays on container-localhost
`127.0.0.1:8081` as a backend for the `hvac` CLI:

```bash
./flags/init_flags.sh                 # runtime flag -> .env (like network-chain)
docker compose up -d --build
ssh default@localhost -p 2223        # password: HVAC-1001-STAT
su engineer                           # password: HVAC-1002-STAT (predictable, uid 1002)
```

- Cron runs the worker once per minute; the API only queues input and reads an asynchronous report.
- Horizontal: predictable SSH passwords (`HVAC-UID-STAT`, engineer `1002`)
- Vertical: root `process_job` trusts writable `/var/run/hvac/input` -> maintenance report flag
  (`hvac schedule`, `hvac schedule-input --content run_diagnostic`, `hvac report`)
- Flavor: `hvac logs`, `hvac log --category X --name Y`, `hvac history`
  serve station decoys from `data/` (crew logs, shift notes, engineer logs,
  failed/routine diagnostics — all decoys, no flag).
- Flag is runtime-only (`flags/init_flags.sh` -> `.env` -> compose),
  mirroring `network-chain`. Never commit `.env`.
