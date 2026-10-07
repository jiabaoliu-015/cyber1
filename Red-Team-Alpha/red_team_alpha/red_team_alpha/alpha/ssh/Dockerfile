# Use the latest LTS Ubuntu image as the base
FROM debian:12-slim

# Install any necessary packages
RUN apt update && apt install cron zip openssh-server -y --no-install-recommends
RUN rm -rf /var/lib/apt/lists/*

# Create a user for the RE/Crypto challenge
RUN groupadd -g 10001 test && useradd -m -r -u 10001 -g test testuser
RUN chown testuser:test /home/testuser && chmod 700 /home/testuser

# Copy the flag to the test user
COPY --chown=testuser:test research_notes.txt /home/testuser/research_notes.txt

# Create a user for the VPE challenge
RUN groupadd -g 10000 sysadmin && useradd -m -r -u 10000 -g sysadmin sysmaint
RUN usermod -p '$6$8W5ecIwcH9tWAzhR$PFEdhTxthK7M0YQXLI3mEHaUz/CZ1E6uYp.nKC9FynrvXy5Hk8KviFxeYcRAdiNgATGUTzLXbJ4yVTE0YgHS0.' sysmaint
RUN chown sysmaint:sysadmin /home/sysmaint && chmod 700 /home/sysmaint

# Copy the scripts for the cronjob
RUN mkdir -p /usr/local/sbin && mkdir -p /var/log/jobs && mkdir -p /var/job_queue/
COPY --chown=root:root archive_queue.sh /usr/local/sbin/archive_queue
COPY --chown=root:root log_queue.sh /usr/local/sbin/log_queue
RUN chmod 755 /usr/local/sbin/archive_queue /usr/local/sbin/log_queue

# Copy the cron script and start the cronjob
COPY --chown=root:root crontab /etc/cron.d/archive_jobs
RUN chmod 0644 /etc/cron.d/archive_jobs

# Copy the create_job binary to the system
COPY --chown=root:root create_job /home/sysmaint/create_job
RUN chmod 6755 /home/sysmaint/create_job
COPY --chown=root:root authorisation-key.txt /home/sysmaint/authorisation-key.txt
RUN chmod 600 /home/sysmaint/authorisation-key.txt

# Create the necessary files for SSH
RUN mkdir -p /run/sshd && ssh-keygen -A
RUN mkdir -p /home/testuser/.ssh && chown testuser:test /home/testuser/.ssh && chmod 700 /home/testuser/.ssh
COPY --chown=testuser:test public_key.pub /home/testuser/.ssh/authorized_keys
RUN chmod 600 /home/testuser/.ssh/authorized_keys

# Expose the SSH port
EXPOSE 22
CMD service cron start && /usr/sbin/sshd -D