#!/usr/bin/env bash
# entrypoint.sh — per-run provisioning (root). Runs once at container start,
# then execs sshd. Keeps the flag out of the image (runtime-only, like the
# network chain's EASY_FLAG/MID_FLAG).
#
# The exploitable subsystems now live under the station module tree:
#   /opt/station/modules/access_control   (acctld / zonectl)
#   /opt/station/modules/research_lab      (lab equipment / run-diagnostics.sh)
set -euo pipefail

MID_FLAG="${MID_FLAG:-CTF{PLACEHOLDER_not_set}}"

LAB="/opt/station/modules/research_lab"
ACC="/opt/station/modules/access_control"

install -d -m 0750 -o labctl -g labctl "$LAB/logs"
printf '%s\n' "${MID_FLAG}" > "$LAB/logs/.mid_flag"
chown labctl:labctl "$LAB/logs/.mid_flag"
chmod 0400 "$LAB/logs/.mid_flag"

# logactivity.log itself must stay writable by labctl (run-diagnostics.sh
# writes to it whether or not it's been hijacked) and readable by y.wu
# (so they can see the run they triggered), but not writable by y.wu —
# the log is the evidence trail, not something they should be able to edit.
: > "$LAB/logs/logactivity.log"
chown labctl:y.wu "$LAB/logs/logactivity.log"
chmod 0640 "$LAB/logs/logactivity.log"

# toolbox: the self-service drop-in directory. Writable by the y.wu
# (researcher) account specifically — this is the misconfiguration, not a
# mistake in this entrypoint script.
install -d -m 0755 -o y.wu -g y.wu "$LAB/toolbox"

# zone_audit.log: acctld's own audit trail, world-readable so any crew account
# can confirm what zonectl has done (the daemon's transparency, not the bug).
install -d -m 0755 "$ACC/logs"
: > "$ACC/logs/zone_audit.log"
chmod 0644 "$ACC/logs/zone_audit.log"

mkdir -p /var/run/sshd
exec /usr/sbin/sshd -D -e
