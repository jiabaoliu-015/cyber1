#!/bin/bash
cd /var/log || exit 1
/bin/tar czf "/opt/flc/backups/logs-$(/bin/date +%s).tar.gz" *.log 2>/dev/null