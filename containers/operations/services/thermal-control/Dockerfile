FROM python:3.12-slim
WORKDIR /app

# sshd is the only player entry; FastAPI stays on 127.0.0.1 as a localhost backend.
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server cron \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hvac_app ./hvac_app
COPY entry ./entry
COPY data ./data
COPY scripts ./scripts
COPY cli/hvac /usr/local/bin/hvac
COPY entrypoint.sh ./entrypoint.sh
COPY motd /etc/motd

# Cron consumes the engineer-writable input as root once per minute.
RUN mkdir -p /var/run/sshd /var/run/hvac /etc/cron.d /opt/hvac \
    && cp ./scripts/process_job /opt/hvac/process_job \
    && chmod 0755 /opt/hvac/process_job /usr/local/bin/hvac ./entrypoint.sh \
    && printf '# hvac-lab root diagnostic job\n* * * * * root /opt/hvac/process_job run\n# Lowpriv-writable input is /var/run/hvac/input\n' > /etc/cron.d/hvac-diagnostic \
    && chmod 0644 /etc/cron.d/hvac-diagnostic \
    && useradd -m -u 1001 -s /bin/bash default && echo 'default:HVAC-1001-STAT' | chpasswd \
    && useradd -m -u 1002 -s /bin/bash engineer && echo 'engineer:HVAC-1002-STAT' | chpasswd \
    && printf '\n# hvac-lab SSH entry\nBanner /etc/motd\nPasswordAuthentication yes\nPermitEmptyPasswords no\n' >> /etc/ssh/sshd_config

# Flag is runtime-only (see flags/init_flags.sh -> .env -> compose).
ENV PYTHONUNBUFFERED=1
ENV HVAC_FLAG=
ENV HVAC_RUN_DIR=/var/run/hvac
ENV HVAC_API_BASE=http://127.0.0.1:8081

EXPOSE 22 8081
CMD ["./entrypoint.sh"]
