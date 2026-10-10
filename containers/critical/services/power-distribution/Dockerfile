FROM python:3.12-slim
WORKDIR /app

# sshd is the only player entry; FastAPI stays on 127.0.0.1 as a localhost backend.
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server cron \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY power_app ./power_app
COPY entry ./entry
COPY data ./data
COPY assets/astronaut.jpeg ./assets/astronaut.jpeg
COPY scripts ./scripts
COPY cli/power /usr/local/bin/power
COPY entrypoint.sh ./entrypoint.sh
COPY motd /etc/motd

# Lab accounts: predictable-password horizontal privesc (mirrors old token vuln).
# default password is documented; officer password must be predicted (uid 3002).
RUN useradd -m -u 3001 -s /bin/bash default && echo 'default:PWR-3001-STAT' | chpasswd \
    && useradd -m -u 3002 -s /bin/bash officer && echo 'officer:PWR-3002-STAT' | chpasswd \
    && mkdir -p /app/data /app/generated-assets /var/run/power /opt/power /etc/cron.d \
    && cp ./scripts/scram_job /opt/power/scram_job \
    && chmod +x /opt/power/scram_job \
    && chmod +x /usr/local/bin/power ./entrypoint.sh scripts/build_image.py scripts/build_agent_binary.py \
    && printf 'SHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n* * * * * root /opt/power/cron_scram_wrapper\n' > /etc/cron.d/power-scram \
    && chmod 0644 /etc/cron.d/power-scram \
    && printf '#!/bin/sh\nset -a\n. /run/power-runtime.env\nset +a\nexec /opt/power/scram_job run\n' > /opt/power/cron_scram_wrapper \
    && chmod 0755 /opt/power/cron_scram_wrapper \
    && printf '\n# power-lab SSH entry\nBanner /etc/motd\nPasswordAuthentication yes\nPermitEmptyPasswords no\n' >> /etc/ssh/sshd_config

# Flags are runtime-only (see flags/init_flags.sh -> .env -> compose).
# Fail closed if operators omit the .env rather than emit placeholder receipts.
ENV PYTHONUNBUFFERED=1
ENV PWR_RUN_DIR=/var/run/power
ENV PWR_ASSET_DIR=/app/generated-assets
ENV PWR_API_BASE=http://127.0.0.1:8082

EXPOSE 22 8082
CMD ["./entrypoint.sh"]
