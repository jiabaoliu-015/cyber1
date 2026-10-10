#!/usr/bin/env bash
# run-diagnostics.sh — Research Lab Equipment Controller
#
# Runs the station's environmental/sensor self-test and appends the result to
# the lab activity log. Invoked by researchers via the sudoers rule below when
# they need an ad-hoc reading outside the automated schedule.
#
#   y.wu ALL=(labctl) NOPASSWD: /opt/station/modules/research_lab/bin/run-diagnostics.sh
#
# INTENTIONAL VULNERABILITY (station Access Control chain — vertical move):
#
#   /opt/station/modules/research_lab/toolbox is a shared drop-in directory researchers are allowed to
#   add their own diagnostic plugins to (so a researcher can add a one-off
#   sensor check without waiting on Operations to touch the image). This
#   script puts that directory FIRST on PATH and then calls `sensor-status`
#   UNQUALIFIED, trusting it to resolve to the real system tool.
#
#   Because the script runs as `labctl` (via the sudo rule above) but PATH
#   resolution happens inside the script itself, a researcher (y.wu) who drops their
#   own executable named `sensor-status` into /opt/station/modules/research_lab/toolbox/ gets it run as
#   labctl instead of the real one — a classic PATH-hijack privilege jump from
#   researcher to the equipment-controller account.
set -euo pipefail

export PATH="/opt/station/modules/research_lab/toolbox:/opt/station/modules/research_lab/bin:/usr/local/bin:/usr/bin:/bin"

LOG_FILE="/opt/station/modules/research_lab/logs/logactivity.log"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "[$STAMP] diagnostics run requested by uid=$(id -u) as $(id -un)" >> "$LOG_FILE"

# BUG: unqualified call — resolves against the PATH above, toolbox first.
sensor-status --full >> "$LOG_FILE"

echo "[$STAMP] diagnostics run complete" >> "$LOG_FILE"
