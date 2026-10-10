# station_terminal — the Erebus station terminal (player foothold).
# Kali base so the standard recon + L2 tooling is present and point-and-shoot.
FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        iproute2 iputils-ping net-tools nmap \
        tcpdump dsniff ettercap-text-only netcat-traditional \
        python3 python3-scapy \
        libcap2-bin \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Unified station identity: every crew + system account is a valid login here
# (shared across all labs via station_accounts.sh). controlsvc = company foothold,
# gh0st = 1st Officer's backdoor; the five crew logins exist campaign-wide.
COPY station_terminal/station_accounts.sh /tmp/station_accounts.sh
RUN bash /tmp/station_accounts.sh && rm /tmp/station_accounts.sh \
    && mkdir -p /var/run/sshd

# the explorable station filesystem (/opt/station/...)
COPY station_terminal/rootfs/ /
RUN ln -sf /opt/station/bin/linkstat /usr/local/bin/linkstat \
    # lock the station tree read-only, owned by root: players can read and
    # traverse it but cannot edit or delete any of it (dirs are not writable
    # by non-root, so files can't be removed either).
    && chown -R root:root /opt/station \
    && find /opt/station -type d -exec chmod 755 {} + \
    && find /opt/station -type f -exec chmod 444 {} + \
    && chmod 555 /opt/station/bin/linkstat /opt/station/bin/stationboot /opt/station/modules/_selftest/relay_selftest.py

# per-account homes + login sequence.
# controlsvc keeps a company-voice handover note; gh0st's home is bare (its
# story is delivered by the login hijack). Both accounts run the station login
# sequence on INTERACTIVE login only (scripted/piped SSH skips it).
COPY station_terminal/home/controlsvc/ /home/controlsvc/
RUN chown -R controlsvc:controlsvc /home/controlsvc \
    && chmod 0444 /home/controlsvc/handover.txt \
    && for u in j.hong j.becker h.mercer y.nassar y.wu controlsvc gh0st; do \
         echo 'case $- in *i*) /opt/station/bin/stationboot ;; esac' >> "/home/$u/.bashrc"; \
       done

# login banners live OUTSIDE the browsable /opt/station tree, each group-locked
# to a single account so neither account can read the other's, and the dir
# can't be listed (0711). stationboot reads only the file for the current user.
COPY station_terminal/login/ /etc/erebus/
RUN chown root:controlsvc /etc/erebus/banner_controlsvc.txt \
    && chown root:gh0st /etc/erebus/hijack_gh0st.txt \
    && chmod 0640 /etc/erebus/banner_controlsvc.txt /etc/erebus/hijack_gh0st.txt \
    && chmod 0711 /etc/erebus

# grant ONLY the diagnostic/recon tools raw-socket capability so the
# UNPRIVILEGED user can run them without root (container cap_add makes the caps
# available; file capabilities pass them to the normal user).
#
# python3 is deliberately NOT capped: the replay/forge steps use plain TCP
# sockets (no caps needed), and leaving the interpreter uncapped keeps a broad
# raw-socket primitive out of the player's hands. ARP is done with arpspoof.
RUN for b in tcpdump arpspoof ettercap; do \
        p="$(command -v "$b" 2>/dev/null)"; \
        [ -n "$p" ] && setcap cap_net_raw,cap_net_admin+eip "$p" 2>/dev/null || true; \
    done

RUN sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
