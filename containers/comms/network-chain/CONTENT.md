# CONTENT MAP — where every narrative string lives

All player-facing text is in plain files so wording can be changed without
touching mechanics. Edit the file, then rebuild (`docker-compose up -d --build`)
or, for rebuild-free iteration, use the dev bind-mount (see bottom).

## Narrative text

| What the player sees | File |
|----------------------|------|
| Login boot sequence (structural lines, `[ OK ]`/`[ WARN ]`, colours) | `station_terminal/rootfs/opt/station/bin/stationboot` |
| controlsvc login banner (the box) | `station_terminal/login/banner_controlsvc.txt` → installed at `/etc/erebus/` (root:controlsvc 0640) |
| "ORACLE is watching the link" / "OFFLINE" monitor line | `stationboot` (the `MON=` lines) |
| gh0st hijack message | `station_terminal/login/hijack_gh0st.txt` → installed at `/etc/erebus/` (root:gh0st 0640) |
| 1st Officer note (method, gripe-list disguise) | `station_terminal/rootfs/opt/station/notes/known_issues.txt` |
| Maint / engineer troubleshooting note | `station_terminal/rootfs/opt/station/modules/link_maint.txt` |
| controlsvc handover note | `station_terminal/home/controlsvc/handover.txt` |
| Subsystem map / README | `station_terminal/rootfs/opt/station/modules/README` |
| Per-subsystem config flavour | `station_terminal/rootfs/opt/station/modules/*/*.conf` |
| `linkstat` labels + `LINK INTEGRITY` words (`LIVE`/`STALE`, `VERIFIED`/`UNVERIFIED`, `STATION DARK`) | `station_terminal/rootfs/opt/station/bin/linkstat` |

Colour tokens usable in the `etc/*.txt` files: `{g}` green, `{a}` amber, `{r}` red,
`{c}` cyan, `{d}` dim, `{b}` bold, `{x}` reset. `banner_controlsvc.txt` also has a
`{mon}` placeholder that `stationboot` fills with the live monitor line.

## Decoys / flags

| What | File |
|------|------|
| Real flag tokens (generated per build) | `flags/init_flags.sh` |
| Plausible decoys (grade wrong) | `logs/journal.1.log`, `modules/_selftest/relay_selftest.py` |
| Troll bait | `rootfs/opt/station/flags.txt`, `logs/recovered_notes.txt` |

## Names: soft vs hard

**Soft** (plain text — edit freely, no `--build` needed with the dev mount):
- Station display name `EREBUS` / `Erebus`, AI name `ORACLE`, signoff `unsigned`
- all note / banner / message wording

**Hard** (baked at image build — changing these needs `docker-compose up -d --build`):
- Account usernames `gh0st` / `controlsvc` — `station_terminal/Dockerfile` (`useradd`,
  `chpasswd`) **and** the `case "$who"` branch in `stationboot`, plus docs
- Account passwords — `station_terminal/Dockerfile`
- Hostname `erebus` — `docker-compose.yml` (`hostname:`)
- Service names `beacon_relay` / `landfall_link` / `sentry_watcher` / `flag_gate` /
  `event_svc` — `docker-compose.yml` service names + the `*.conf` references

When you sync crew/station names with the team: do the soft ones live, and batch
the hard ones into one `--build`.

## Rebuild-free text iteration (dev)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
# edit any text under station_terminal/rootfs/opt/station/ , then:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart station_terminal
```

`docker-compose.dev.yml` bind-mounts the station tree read-only, so host edits
show up on restart. It's opt-in: the plain `docker-compose up` (what graders run)
bakes everything into the image and does **not** use the mount, so the shipped
lab stays self-contained.
