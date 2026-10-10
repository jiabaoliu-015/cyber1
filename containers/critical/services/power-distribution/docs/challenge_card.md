# Power Lab — Power Distribution / Reactor Control (Station Erebus)

Flowchart path: `Default-User -> Predictable SSH passwords (horizontal) -> Officer-User -> LEFT Captain Key + Black Box optics portrait (crypto, Mid flag + RIGHT Captain Key) -> Two Key Console -> Kernel interlock / Scheduled scram (vertical) -> Reactor Control -> Hard flag in scram report`.

SSH is the only player entry (`ssh default@localhost -p 2222`, password
`PWR-3001-STAT`). FastAPI stays on container-localhost `127.0.0.1:8082` as
a backend for the `power` CLI, which maps the Unix user to its token.

Shared campaign canon: station `Erebus` — Tallis Group crewed station, proposed Callisto orbit,
AI ORACLE, last human contact 16 Sep 2026, ground-link blackout 20 Sep 2026
(network-chain terminal `erebus`).
Foothold accounts (network-chain): `gh0st` (1st Officer Becker's backdoor) and
`controlsvc` (company-issued). Crew records are provisional: Jin Hong (j.hong) was
last confirmed assigned Two-Key LEFT slot A; John Becker (j.becker) was last
confirmed assigned Two-Key RIGHT slot B (the `officer` uid `3002` in this lab);
Hank Mercer was last logged at power distribution (see
`data/engineer_logs/mercer_final_watch_058.txt`); Yara Nassar last badged into
medbay (see `data/medical_logs/nassar_last_badge_059.txt`); Wu Yan's research lab
was sealed from inside. Current fates are unresolved.
The `BECK-4217-K9` asset tag is keyed to Becker's checkout (optics side-channel key);
`ISVM-AGENT-FW` / `meridian-yard-044` in the agent firmware are the
docked-vessel/yard build tags, not the station name.

## Horizontal priv (predictable SSH passwords)
1. `ssh default@localhost -p 2222` (password `PWR-3001-STAT`).
2. Password format is `PWR-{uid:04d}-STAT`; officer uid is `3002`.
3. `su officer` with `PWR-3002-STAT`; `power status` now succeeds.
4. As default, `power status` gets `403`; as officer it succeeds.

## LEFT Captain Key (Captain Jin Hong, slot A)
- As officer: `power left-key` -> `CPT-LEFT-4A1F-22MZ`
  (flowchart `captain_key_left`, slot A of the Two Key Console — Hong's key;
  slot B / RIGHT is Becker's key, recovered via the optics crypto below.
  Two-man rule: Hong + Becker.)

## Reverse — Agent System firmware (officer-path Hard flag)
Flowchart path: `1st Officer -> objdump/strings -> agent_bin -> obfus -> Hard flag`.
1. As officer: `power agent-binary -o /tmp/fw.bin` -> `agent_firmware.bin`
   (Automated Agent System Module firmware dump).
2. `strings` shows decoy flags (`CTF{agent_decoy_dead00/01}`), a draft
   stage-1 loader and a draft key (`AGENT-00`) — all decoys. The loader
   decodes to a decoy; do not trust or blindly run it.
3. The live block is `AGENT-STAGE2:<base64>`; base64-decode, REVERSE the
   bytes, XOR with the officer-console key `OBFUS-1ST-0FF` (stenciled tag
   in `data/engineer_logs/agent_firmware_note_053.txt` and
   `data/shift_notes/shift_zeta_057.txt`).
4. Result is `CTF{agent_obfuscated_hard_4d2b}`.
5. Solver: `python3 docs/solutions/solve_agent.py assets/agent_firmware.bin`.
6. Rebuild: `python3 scripts/build_agent_binary.py`.

## Crypto — Black Box optics portrait (Mid flag + RIGHT key)
1. As officer: `power blackbox-image -o /tmp/portrait.jpeg` -> `astronaut_stego.jpeg`
   (portrait rebuilt at container start from runtime `PWR_FLAG_MID`; renders normally).
2. `power blackbox-sidechannel` + `data/blackbox_logs/` give the
   11-char side-channel key `BECK-4217-K9` (asset-tag form `XXXX-NNNN-XX`).
3. Take bytes after marker `PWR-BLACKBOX-V1:`, base64-decode, XOR with the key:
   result is `<MID flag>|<RIGHT Captain Key>`, e.g.
   `CTF{blackbox_optics_mid_7f3a}|CPT-RIGHT-9D2K-77QX`.
4. Solver: `python3 docs/solutions/solve_image.py assets/astronaut_stego.jpeg`
   (or pass `--url http://127.0.0.1:8082/api/blackbox/image --token <officer>`).

## Two Key Console
- `power two-key --left CPT-LEFT-... --right CPT-RIGHT-...`
  (officer only). Wrong fragments get `403` per slot.
- `power two-key-status` shows authorization. Authorization gates
  `power schedule*` and `power reactor-report`.

## Vertical priv (kernel / root scram job)
1. Authorized officer: `power schedule` shows
   `* * * * * root /opt/power/cron_scram_wrapper` (executes `scram_job run`),
   input `/var/run/power/input`.
2. `power schedule-input --content scram_reactor` queues input in the writable
   trust boundary; it does not execute the job.
3. The real root cron daemon runs once per minute and writes
   `/var/run/power/reactor_report.txt` containing
   the runtime `PWR_FLAG_HARD`.
4. `power reactor-report` reads the flag. Cron requires the two-key
   authorization marker and the `scram_reactor` input.

## Station flavor / decoys (no flag — shared ship store with HVAC console)
- `power logs` indexes `data/reactor_logs`, `data/shift_notes`,
  `data/engineer_logs`, `data/blackbox_logs`, `data/comms_logs`, `data/diagnostics`,
  `data/crew_logs`, `data/medical_logs`, `data/research_notes` — identical set served by the HVAC console so both docker containers appear to share one log store.
- `power log --category <cat> --name <file>` reads one decoy file (traversal-safe, `.txt` only).
- `power history` lists archived failed/routine diagnostics (all decoys, no flag).
- Story arc (Erebus brownouts): Power Distribution sagging station-wide
  (bus 61%, load-shed on decks C/D, lighting flicker), First Officer John Becker
  (paranoid-and-right, now Unaccounted for — see
  `data/shift_notes/becker_unaccounted_058.txt`) loitering near bus ducts with
  condensate notebooks before vanishing, Chief Engineer Hank Mercer (Deceased at power —
  see `data/engineer_logs/mercer_final_watch_058.txt`) having filed a concern about
  Becker, Medical Officer Yara Nassar (Missing from medbay — see
  `data/medical_logs/nassar_last_badge_059.txt`) flagging Becker's fixation,
  warm object K-9 in aft hold driving temps + 17 Hz hum on the power bus.
- Decoy reports deliberately share the scram-report format so players must
  distinguish the live `/api/reactor/report` (root job, `status: success`) from
  archived failures. Engineer/blackbox logs contain red herrings (wrong keys like
  `BECK-4217-K8`, wrong markers, old paths) — trust `/api/blackbox/side-channel`
  and the solver, not stray notes.

## Ops
- Runtime flags: `./flags/init_flags.sh` (writes `.env`, like network-chain) before first run.
- Build optics: entrypoint builds from bundled `assets/astronaut.jpeg` into
  `/app/generated-assets` at boot using runtime flags; do not commit generated flags.
- Run: `docker compose up --build -d`, `./scripts/healthcheck.sh`
  (checks `http://127.0.0.1:8082/health` with Python stdlib +
  `ssh-keyscan -p 2222`; curl is not installed).
- SSH entry: `ssh default@localhost -p 2222` (`PWR-3001-STAT`), `su officer` (`PWR-3002-STAT`).
- Reset: `./scripts/reset.sh` (clears input + report + two-key authorization)
- No brute force; SSH on loopback `127.0.0.1:2222`, web backend on container-localhost only.

## Mitigations
- Horizontal: random per-session tokens, server-side session store, enforce authz per user.
- Crypto: never hide secrets in trailing image bytes; use authenticated encryption with
  per-recipient keys; treat side-channel telemetry as sensitive.
- Two Key: require independent authenticated principals per key, not bearer fragments
  over one channel; log both insertions.
- Vertical: root job must not trust lowpriv-writable input; drop privileges, validate
  allow-listed commands, write reports to root-only paths.
