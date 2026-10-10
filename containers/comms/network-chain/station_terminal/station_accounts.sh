#!/usr/bin/env bash
# Erebus canonical station accounts — SHARED across every campaign lab.
# Unified station identity: every crew + system login exists on every module
# host, so a credential recovered in one chain works station-wide. Each lab
# layers its own privilege/sudo/foothold on top; this only creates the LOGINS.
# Keep this file identical across labs (source of truth: crew-and-station-canon).
set -eu

add(){ useradd -m -s /bin/bash "$1" 2>/dev/null || true; echo "$1:$2" | chpasswd; }

# crew
add j.hong      'Kestrel.Rising24'   # Captain — Jin Hong
add j.becker    'deadmans.switch'    # First Officer — John Becker (backdoor: gh0st)
add h.mercer    'just_reboot_it'     # Chief Engineer — Hank Mercer
add y.nassar    'doNoHarm.09'        # Medical Officer — Yara Nassar
add y.wu        'subject.null.7'     # Researcher — Wu Yan

# system / non-crew
add controlsvc  'recovery-access'    # Tallis Group company-recovery service account
add gh0st       'w0rmh0le'           # John Becker's personal backdoor
