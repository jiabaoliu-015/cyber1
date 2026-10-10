FROM python:3.11-slim

WORKDIR /opt/suseid

# MAINTENANCE_UTILITY is a deliberately container-scoped challenge service.
COPY implementation/suid_route.py /opt/suseid/maintenance_utility
COPY entry/ /entry/

RUN mkdir -p /var/run/suseid /srv/station_crew \
    && chmod 0755 /opt/suseid/maintenance_utility

ENV SERVICE_NAME=maintenance_utility \
    ROOT_FLAG=CITS3006_ROOT_FLAG \
    PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD ["/opt/suseid/maintenance_utility", "--healthcheck"]

CMD ["/opt/suseid/maintenance_utility", "--healthcheck"]
