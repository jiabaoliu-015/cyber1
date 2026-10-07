# Step 3 image -- the segment router (Telnet command injection) + OTA firmware
# endpoint that hands out Isaac's reverse-engineering binary.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends iputils-ping \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY telnet_server.py /app/telnet_server.py
COPY fw_server.py /app/fw_server.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Isaac's RE binary, served in-world as the controller's OTA firmware image.
COPY fw/acc-rtr01-fw.elf /srv/acc-rtr01-fw.elf
RUN chmod 644 /srv/acc-rtr01-fw.elf

# Route flag (step 3, the router stage) + where it's hidden (rotate freely).
ARG FLAG="CITS3006{24n4CBiT2K}"
ENV FLAG=${FLAG}
ENV FLAG_PATH="/opt/maint/rtr-01.snapshot"

# OTA firmware endpoint. The firmware is downloadable ONLY at the secret path
# /fw/${FW_TOKEN}/acc-rtr01-fw.elf ; that URL is disclosed only inside
# /opt/maint (read via the ping injection), so the injection stays mandatory.
# Rotate FW_TOKEN freely -- it is baked into the URL the player recovers.
ENV FW_PORT="8081"
ENV FW_TOKEN="1edca15d3306"
ENV FW_FILE="/srv/acc-rtr01-fw.elf"

# Telnet backdoor creds. If you change TELNET_PASS you MUST re-scramble it and
# update mgmt.telnet.pass_enc in step 2's leaked export:
#   python3 -c "import base64;print(base64.b64encode(bytes(b^0x5A for b in b'NEWPASS')).decode())"
ENV TELNET_USER="support"
ENV TELNET_PASS_ENC="HDs2OWo0eSguKHtoaA=="

EXPOSE 23/tcp
EXPOSE 8081/tcp
CMD ["/app/entrypoint.sh"]
