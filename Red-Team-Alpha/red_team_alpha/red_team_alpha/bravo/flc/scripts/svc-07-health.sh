#!/bin/bash

{
    echo "=== Depot Health Snapshot ==="
    echo "Time: $(/bin/date -u)"
    echo "Host: $(/bin/hostname)"
    echo "Reports: $(/usr/bin/find /opt/flc/reports -maxdepth 1 -type f | /usr/bin/wc -l)"
    echo "Scratch: $(/usr/bin/find /opt/flc/scratch -maxdepth 1 -type f | /usr/bin/wc -l)"
} > /var/log/svc-07.log 2>/dev/null