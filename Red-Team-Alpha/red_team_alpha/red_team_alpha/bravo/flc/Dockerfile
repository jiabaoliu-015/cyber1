FROM python:3.12-slim

WORKDIR /opt/flc

COPY . /srv/flc/app

ENV FLAG="FLAG{W0FK8S02MD}"
ARG ROOT_FLAG_BUILD="FLAG{0EN38FBQE1}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cron \
        util-linux && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -r /srv/flc/app/requirements.txt

RUN mkdir -p \
    /opt/flc/reports \
    /opt/flc/scratch \
    /opt/flc/tmp \
    /opt/flc/scripts \
    /opt/flc/tools \
    /opt/flc/logs/archive \
    /opt/flc/backups \
    /opt/flc/root/secrets
 
    
# The six scheduled scripts
RUN cp /srv/flc/app/scripts/svc-01-notice.sh   /opt/flc/scripts/svc-01-notice.sh && \
    cp /srv/flc/app/scripts/svc-02-audit.sh    /opt/flc/scripts/svc-02-audit.sh && \
    cp /srv/flc/app/scripts/svc-03-sync.sh     /opt/flc/scripts/svc-03-sync.sh && \
    cp /srv/flc/app/scripts/svc-04-purge.sh    /opt/flc/scripts/svc-04-purge.sh && \
    cp /srv/flc/app/scripts/svc-05-collect.sh  /opt/flc/scripts/svc-05-collect.sh && \
    cp /srv/flc/app/scripts/svc-06-archive.sh  /opt/flc/scripts/svc-06-archive.sh && \
    cp /srv/flc/app/scripts/svc-07-health.sh /opt/flc/scripts/svc-07-health.sh

RUN sed -i 's/\r$//' /opt/flc/scripts/*.sh
RUN chmod 755 /opt/flc/scripts
RUN chmod 755 /opt/flc/scripts/*.sh
RUN chown root:root /opt/flc/scripts /opt/flc/scripts/*.sh


# Cron table
RUN cp /srv/flc/app/cron/flc-cron /etc/cron.d/flc-cron && \
    sed -i 's/\r$//' /etc/cron.d/flc-cron && \
    printf '\n' >> /etc/cron.d/flc-cron
RUN chmod 644 /etc/cron.d/flc-cron
RUN chown root:root /etc/cron.d/flc-cron
 

# Logs 
RUN touch /var/log/svc-02.log /var/log/svc-03.log /var/log/svc-05.log /var/log/svc-06.log /var/log/svc-07.log
RUN chmod 600 /var/log/svc-02.log /var/log/svc-03.log /var/log/svc-05.log /var/log/svc-06.log /var/log/svc-07.log
RUN chown root:root /var/log/svc-02.log /var/log/svc-03.log /var/log/svc-05.log /var/log/svc-06.log /var/log/svc-07.log
 
RUN chmod 750 /var/log
RUN chown root:root /var/log 

RUN chmod 700 /opt/flc/backups
RUN chown root:root /opt/flc/backups
 

# Writable attacker-controlled directories 
RUN chown root:root /opt/flc/reports && \
    chmod 1777 /opt/flc/reports && \
    chown -R www-data:www-data /opt/flc/scratch /opt/flc/tmp && \
    chmod 755 /opt/flc/scratch /opt/flc/tmp

RUN printf '%s\n' \
    'Fleet Readiness Report' \
    'Operational: 24/25 vehicles' \
    'Availability: 96%' \
    > /opt/flc/reports/vehicle_status.txt && \
    printf '%s\n' \
    'Fuel Distribution Manifest' \
    'Sector B Allocation: 18,000 L' \
    'Priority: Convoy Operations' \
    > /opt/flc/reports/fuel_manifest.txt && \
    printf '%s\n' \
    'Convoy Delta Movement Log' \
    'Departure: 07:30 UTC' \
    'Destination: Checkpoint Echo' \
    > /opt/flc/reports/convoy_delta.txt && \
    printf '%s\n' \
    'Quarterly Inventory Audit' \
    'Status: Complete' \
    'Discrepancies: None' \
    > /opt/flc/reports/inventory_2026.txt && \
    printf '%s\n' \
    'Communications Status' \
    'Relay Network: Operational' \
    'Backup Channel: Available' \
    > /opt/flc/reports/communications_status.txt && \
    printf '%s\n' \
    'Maintenance Schedule' \
    'Depot Window: Wednesday 2200 UTC' \
    > /opt/flc/reports/maintenance_schedule.txt && \
    printf '%s\n' \
    'Personnel Duty Roster' \
    'Rotation Updated' \
    'Shift Alpha: Active' \
    > /opt/flc/reports/personnel_roster.txt && \
    chmod 644 /opt/flc/reports/*.txt


RUN cp /usr/bin/true /opt/flc/tools/maint-diag
RUN chown root:root /opt/flc/tools/maint-diag
RUN chmod 4755 /opt/flc/tools/maint-diag
RUN chmod 755 /opt/flc/tools
RUN chown root:root /opt/flc/tools
 

RUN cp /srv/flc/app/tools/generate_report.sh /opt/flc/tools/generate_report.sh && \
    sed -i 's/\r$//' /opt/flc/tools/generate_report.sh && \
    chmod 755 /opt/flc/tools/generate_report.sh && \
    chown root:root /opt/flc/tools/generate_report.sh

RUN printf '%s\n' \
    'Delta-4 Migration Bulletin' \
    '' \
    'Version 3.1 Maintenance Migration' \
    '' \
    '• Scheduled maintenance tasks migrated from systemd timers to cron.d.' \
    '• Maintenance automation remains active during depot operations.' \
    '• Archive destination relocated to protected storage.' \
    '• Several legacy maintenance scripts retained pending platform retirement.' \
    '• CVE-2019-14287 patched during migration.' \
    > /opt/flc/logs/archive/patch-notes.txt

RUN chmod 755 /opt/flc/logs /opt/flc/logs/archive
RUN chmod 644 /opt/flc/logs/archive/patch-notes.txt
RUN chown -R root:root /opt/flc/logs
 

# Archive history
RUN printf '%s\n' \
    'Delta-4 Maintenance History' \
    'Generated: 2026-09-18 08:20 UTC' \
    '' \
    'Recent maintenance activity' \
    '' \
    '2026-09-18 08:10  svc-01-notice.sh   completed' \
    '2026-09-18 08:12  svc-02-audit.sh    completed' \
    '2026-09-18 08:14  svc-03-sync.sh     completed' \
    '2026-09-18 08:16  svc-04-purge.sh    completed' \
    '2026-09-18 08:18  svc-05-collect.sh  completed' \
    '2026-09-18 08:20  svc-06-archive.sh  completed' \
    '2026-09-18 08:22  svc-07-health.sh   completed' \
    '' \
    'Historical maintenance records retained for operational auditing.' \
    > /opt/flc/logs/archive/archive-history.txt && \
    chmod 644 /opt/flc/logs/archive/archive-history.txt && \
    chown root:root /opt/flc/logs/archive/archive-history.txt
 

# Root flag 
RUN echo "$ROOT_FLAG_BUILD" > /opt/flc/root/secrets/launch_authorization.txt
RUN chmod 600 /opt/flc/root/secrets/launch_authorization.txt
RUN chown -R root:root /opt/flc/root
RUN chmod 700 /opt/flc/root
 

RUN chown -R root:www-data /srv/flc/app && \
    find /srv/flc/app -type f -exec chmod 640 {} \; && \
    find /srv/flc/app -type d -exec chmod 750 {} \;
 

# Entrypoint 
COPY entrypoint.sh /usr/local/bin/flc-entrypoint

RUN sed -i 's/\r$//' /usr/local/bin/flc-entrypoint && \
    chmod 700 /usr/local/bin/flc-entrypoint && \
    chown root:root /usr/local/bin/flc-entrypoint


EXPOSE 5006
CMD ["/usr/local/bin/flc-entrypoint"]