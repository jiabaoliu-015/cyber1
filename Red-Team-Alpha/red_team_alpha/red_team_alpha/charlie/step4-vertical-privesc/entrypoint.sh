#!/bin/sh
# Refresh the flag from the env (so it can be rotated at run time) and start sshd.
set -e
: "${FLAG:=CITS3006{xyOTpUwAhd}}"
echo "$FLAG" > /home/fieldtech/disarm-authorization.txt
chmod 600 /home/fieldtech/disarm-authorization.txt
chown root:root /home/fieldtech/disarm-authorization.txt
exec /usr/sbin/sshd -D -e
