#!/bin/bash
STAGING_DIR="/opt/flc/tmp"
REPORT_DIR="/opt/flc/reports"
BACKUP_DIR="/opt/flc/backups"

cp -f "$REPORT_DIR"/*.txt "$STAGING_DIR"/ 2>/dev/null

cd "$STAGING_DIR" || exit 1
/bin/tar czf "$BACKUP_DIR/convoy-archive-$(/bin/date +%s).tar.gz" * >> /var/log/convoy-archive.log 2>&1

rm -f "$STAGING_DIR"/*.txt 2>/dev/null