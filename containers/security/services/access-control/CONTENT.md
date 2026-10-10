# CONTENT MAP — where every narrative string lives

| What the player sees | File |
|---|---|
| Animated login sequence (header, handshake, progress bar) | `access_control_terminal/rootfs/opt/station/bin/stationboot` (mechanics, not prose) |
| controlsvc recovery banner | `access_control_terminal/login/banner_controlsvc.txt` (tokenised, `{mon}` = ORACLE line) |
| gh0st hijack message (80% stall) | `access_control_terminal/login/hijack_gh0st.txt` (tokenised) |
| zonectl hint (sudo misconfig) | `.../rootfs/opt/station/modules/access_control/recovery_notes.txt` |
| Chronicler hint (PATH hijack) | `.../rootfs/opt/station/modules/chronicler/duty_log.txt` |
| Subsystem map | `.../rootfs/opt/station/modules/README`, `.../access_control/README`, `.../chronicler/README` |
| Decoy | `.../rootfs/opt/station/modules/_legacy/deprecated_acl.cfg` |

## Names: soft vs hard

**Soft** (plain text, edit freely — use the dev bind-mount, no rebuild needed):
all note/README wording under `/opt/station/`.

**Rebuild-needed text** (correct wording, but NOT under the `/opt/station`
bind-mount): the login banners `login/banner_controlsvc.txt` and
`login/hijack_gh0st.txt` live at `/etc/erebus/` (group-locked per account), so
editing them needs an image rebuild. `stationboot` reads them by `{token}`.

**Hard** (baked at image build — changing these needs `docker-compose up -d --build`):
- Account usernames `gh0st` / `controlsvc` / `y.wu` / `labctl` — crew/system from `station_accounts.sh`, `labctl` from
  `access_control_terminal/Dockerfile`, and the sudoers file
  `access_control_terminal/rootfs/etc/sudoers.d/90-recovery-access`.
- Passwords — crew/system in `access_control_terminal/station_accounts.sh`
  (the shared canon file); `labctl` has no password (non-login).
- Hostname `erebus` — `docker-compose.yml`.
- `/opt/station/modules/access_control/bin/zonectl`,
  `/opt/station/modules/research_lab/bin/run-diagnostics.sh`, `.../research_lab/bin/sensor-status` — these ARE the mechanics, not narrative text;
  changing them changes the challenge.

## Rebuild-free text iteration (dev)

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
# edit any text under access_control_terminal/rootfs/opt/station/ , then:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart access_control_terminal
```
