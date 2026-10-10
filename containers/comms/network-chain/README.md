# Erebus — Network Chain (self-contained lab)

The station's status link to ground, and the two watchers on it. The player
lands on a reclaimed link-maintenance account and works the segment:
**ARP MITM → replay (blind ground) → default-key forge (blind the AI) → go dark.**

This stack **replaces** the committed app-layer comms lab (NET-01..03). It is
built standalone so integrating/replacing is a deliberate step, not an
overwrite.

## Vulnerabilities (3 network)

| # | Vuln | Where | Player action |
|---|------|-------|---------------|
| 1 | Unauthenticated L2 status link (ARP MITM) | the `station_lan` segment | ARP-spoof between `beacon_relay` and `landfall_link` |
| 2 | Replay / missing freshness | `landfall_link` (ground) | resend a captured frame — ground accepts the stale seq |
| 3 | Default signing key | `sentry_watcher` (AI) + `relay.d/relay.key` | forge a fresh, correctly-signed frame with the unrotated key |

Flags: **easy** = the `TOK:` value carried in a captured frame; **mid** = the
go-dark token, released only when *both* watchers are blinded. Both are
runtime-only (generated per build, not in source — see `flags/init_flags.sh`).

## Layout

```
station_terminal ─ station_lan ─ beacon_relay ─► landfall_link  (ground: no auth, no freshness)
 (erebus)
                           │              └► sentry_watcher  (AI: freshness + MAC required)
                           └► event_svc (session source) · flag_gate (scoring, token-authed, not attackable)
```

## Run it (on Kali / native-Linux Docker)

```bash
./flags/init_flags.sh                 # generate fresh flag tokens -> .env
docker compose up -d --build
```

Two ways in (both land on the Erebus station terminal):

```bash
ssh controlsvc@localhost -p 2222      # official (company-reclaimed) — password: recovery-access
ssh gh0st@localhost      -p 2222      # backdoor (1st Officer's)      — password: w0rmh0le
```

Both accounts run an animated station login sequence (`/opt/station/bin/stationboot`,
interactive logins only). `controlsvc` gets the company control-services banner
plus a `handover.txt` pointing you to investigate; `gh0st`'s banner decrypt is
hijacked by the 1st Officer's implant, whose message points at the shared notes.
Either way, explore the station:

```bash
cd /opt/station/modules       # subsystem map: comms_relay, ground_link, sentry, event_log (+ decoys)
cat link_maint.txt            # maint troubleshooting note (how the link is wired)
cat /opt/station/notes/known_issues.txt   # 1st Officer's log (method, in gripe-list disguise)
cat */*.conf                  # each subsystem's settings (auth / freshness / key policy)
cat comms_relay/relay.key     # the unrotated factory key
cat /opt/station/logs/keymgmt.log         # key audit: relay.key never rotated
linkstat                      # link visibility + integrity readout
```

Then perform the attack (see `solution/SOLUTION.md`). `linkstat` shows
`STATION DARK` + the mid flag once both watchers are blinded.

## ARP inside Docker — validated

The L2 ARP interception between containers was the known reproducibility risk;
it is **confirmed working on Kali + Docker (compose v1 & buildkit)**. The
`station_terminal` container is set up so an *unprivileged* player can do it
with no root steps:

- `cap_add: [NET_ADMIN, NET_RAW]` on the container (compose),
- `setcap cap_net_raw,cap_net_admin+eip` on `tcpdump` / `arpspoof` / `ettercap`
  / `python3` in the Dockerfile (so the normal user can use raw sockets),
- `sysctls: net.ipv4.ip_forward=1` (transparent MITM so the link stays up).

Quick confirm from inside the terminal (`ssh gh0st@localhost -p 2222`):

```bash
getent hosts beacon_relay landfall_link          # note the two IPs
arpspoof -i eth0 -t <beacon_ip>   <landfall_ip> >/dev/null 2>&1 &
arpspoof -i eth0 -t <landfall_ip> <beacon_ip>   >/dev/null 2>&1 &
tcpdump -i eth0 -nn -A 'tcp port 9101'           # TM|...|TOK:CTF{...} = easy flag
```

## Integrity / hardening

- **flag_gate is not attackable from the player segment.** It only *observes*
  (ground-truth from the relay, accepted-frame reports from the two watchers)
  and releases the mid flag when both are blinded. Report messages must carry a
  shared `GATE_TOKEN` that lives only in the service containers' env — never on
  the terminal, never in a readable file — so a player cannot forge reports to
  fake a go-dark. `STATUS` (what `linkstat` reads) is open and read-only.
- **The station tree is read-only.** `/opt/station/**` is `root:root`, dirs
  `755`, files `444` (binaries `555`) — players can read and traverse it but
  cannot edit or delete any config, key, log, note or tool.
- **Least privilege on tooling.** Only `tcpdump` / `arpspoof` / `ettercap` carry
  `cap_net_raw` (so the unprivileged user can sniff/ARP without root). `python3`
  is intentionally *not* capped — the replay/forge use plain TCP sockets.
- **netcat** (`netcat-traditional`) is installed for the replay step.

## Test (no Docker needed)

```bash
python3 tests/test_network_lab.py     # validates the vuln + scoring logic
```

## Decoys (bait — see `decoys/`)

Plausible in-world decoys (look real, grade wrong):
`relay_selftest.py` (canned sample frame token `CTF{relay_selftest_ok}`),
`journal.1.log` (archived status tokens `CTF{link_nominal_0992}` /
`CTF{ground_ack_0994}`), `link_legacy.cfg` (dead endpoint).

Troll bait for the grep-first crowd (obvious human-left files):
`/opt/station/flags.txt` → `CTF{nice_try_though}`,
`/opt/station/logs/recovered_notes.txt` → `CTF{not_going_to_be_that_easy}`.

Submitting any decoy token fails — the graded flags are the runtime `.env`
tokens only (on the wire / from `linkstat`), never in a file.

## Reset

`docker compose down && ./flags/init_flags.sh && docker compose up -d --build`.

## Editing text / naming

All narrative text lives in plain files (banners, notes, `linkstat` labels). See
`CONTENT.md` for the string-to-file map and the soft-name (edit freely) vs
hard-name (`gh0st`/`controlsvc`/`erebus`, need a `--build`) split. For
rebuild-free wording iteration, use the dev bind-mount:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
# edit any text under station_terminal/rootfs/opt/station/ then:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart station_terminal
```

`Erebus` / `ORACLE` are WIP placeholders; no mechanic depends on them.
