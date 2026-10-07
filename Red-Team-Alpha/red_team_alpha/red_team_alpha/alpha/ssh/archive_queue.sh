#!/bin/sh

# This script empties the job queue completely at the start of each day
# by archiving the contents of the queue and removing any job scripts.
# This operation is run by `cron` daily.

zip -r /var/log/jobs/jobs-$(date +%F).zip /var/job_queue/
rm -rf /var/job_queue/*