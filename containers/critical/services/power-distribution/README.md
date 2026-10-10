# Power Lab service (flowchart: Power Distribution / Reactor Control — Station Erebus)

Station `Erebus` — Tallis Group crewed station, proposed Callisto orbit; station AI ORACLE;
last human contact 16 Sep 2026; ground-link blackout 20 Sep 2026 (shared canon;
foothold accounts `gh0st` / `controlsvc` live on the network-chain terminal `erebus`).
Crew records are provisional: Jin Hong was last confirmed assigned Two-Key LEFT;
John Becker (j.becker + backdoor gh0st) was last confirmed assigned Two-Key RIGHT;
Hank Mercer was last logged at power distribution; Yara Nassar last badged into
medbay; Wu Yan's research lab was sealed from inside. Current fates are unresolved.
Lab mapping: `officer` (uid `3002`) = Becker's 1st-Officer seat; `BECK-4217-K9`
is Becker's asset-tag checkout (side-channel key).

SSH entry only (pure SSH, no web login). FastAPI stays on container-localhost
`127.0.0.1:8082` as a backend for the `power` CLI:

```bash
./flags/init_flags.sh                 # runtime flags -> .env (like network-chain)
docker compose up -d --build
ssh default@localhost -p 2222        # password: PWR-3001-STAT
su officer                            # password: PWR-3002-STAT (predictable, uid 3002)
```

- Horizontal: predictable SSH passwords (`PWR-UID-STAT`, 1st Officer `3002`)
- LEFT Captain Key (officer): `power left-key`
- Officer-path RE (Agent System firmware): `power agent-binary -o /tmp/fw.bin` serves
  `agent_firmware.bin`; the draft stage-1 loader is a decoy, the live
  `AGENT-STAGE2:` block (base64, reversed, XOR `OBFUS-1ST-0FF` from
  engineer/shift logs) yields the officer-path Hard flag.
  Solver: `docs/solutions/solve_agent.py`.
- Crypto (Black Box optics): `power blackbox-image -o /tmp/portrait.jpeg` serves the
  `astronaut_stego.jpeg` portrait (rebuilt at container start from runtime
  `PWR_FLAG_MID` via `scripts/build_image.py`);
  trailing `PWR-BLACKBOX-V1:` payload XORs to `MID flag | RIGHT Captain Key`.
  Key material (`BECK-4217-K9`) is scattered across `data/blackbox_logs/`
  side-channel notes. Solver: `docs/solutions/solve_image.py`.
- Two Key Console: `power two-key --left ... --right ...`
  (flowchart `Two Key Console` fed by both Captain Keys)
- Vertical (kernel/root): the running root cron job trusts writable
  `/var/run/power/input` -> reactor report hard flag. `power schedule`
  advertises the cron; after Two Key authorization,
  `power schedule-input --content scram_reactor` queues input. Cron runs once per minute; poll
  `power reactor-report` for the asynchronous report.
- Flavor: `power logs`, `power log --category X --name Y`,
  `power history` serve station decoys from `data/`
  (reactor logs, shift notes, engineer logs, blackbox side-channel,
  comms logs, archived diagnostics — all decoys, no flag).
- Flags are runtime-only (`flags/init_flags.sh` -> `.env` -> compose),
  mirroring `network-chain`. Never commit `.env` or generated artifact binaries.
