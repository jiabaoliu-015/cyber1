#!/bin/bash
cd /opt/flc/reports || exit 1
/usr/bin/find . -maxdepth 1 -type f -exec /usr/bin/wc -l {} + > /var/log/inventory-check.log 2>&1