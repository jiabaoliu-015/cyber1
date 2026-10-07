#!/bin/bash
cd /opt/flc/scratch || exit 1
/bin/tar czf "/opt/flc/backups/scratch-$(/bin/date +%s).tar.gz" -- * 2>/dev/null