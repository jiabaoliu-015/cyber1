# Use the slim Debian image as the base
FROM debian:12-slim

# Install the necessary packages
RUN apt-get update && apt-get install sudo openssh-server findutils -y --no-install-recommends
RUN rm -rf /var/lib/apt/lists/*

# Create the fieldtech user
RUN useradd -m -s /bin/bash fieldtech
RUN usermod -p '$6$Uy/4xsATe57BrPpV$Q7fdtADJB6Z.aPNlnaijiusIROFCTh0WFg86Eb/t9qDJUdj/tvT6Dxt2210fomomkon.GtYrXKy/.UbHs0QvO0' fieldtech

# THE MISCONFIG: the field-maintenance account was granted passwordless sudo to
# run `find` as root (meant for filesystem integrity scans). find can spawn a
# shell via -exec, so this NOPASSWD rule is a full root escalation (GTFOBins).
RUN echo "fieldtech ALL=(root) NOPASSWD: /usr/bin/find" > /etc/sudoers.d/acc-maint \
 && chmod 440 /etc/sudoers.d/acc-maint \
 && visudo -cf /etc/sudoers.d/acc-maint

# final flag (root only), the column's disarm flag. rotate via FLAG build arg.
# Dropped in the technician's home dir: fieldtech can see it on login but
# cannot read it until they escalate to root.
ARG FLAG="CITS3006{xyOTpUwAhd}"
ENV FLAG=${FLAG}
RUN echo "$FLAG" > /home/fieldtech/disarm-authorization.txt \
 && chmod 600 /home/fieldtech/disarm-authorization.txt \
 && chown root:root /home/fieldtech/disarm-authorization.txt

COPY motd /etc/motd

RUN mkdir -p /run/sshd && ssh-keygen -A \
 && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config \
 && printf '\nPrintMotd yes\n' >> /etc/ssh/sshd_config \
 && sed -i 's/#Port 22/Port 2022/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 2022
CMD ["/entrypoint.sh"]
