# access_control_terminal — Erebus Access Control chain (player foothold).
# Same station identity as every other chain: the crew + system accounts are
# provisioned from the shared station_accounts.sh (source of truth:
# crew-and-station-canon), so a credential recovered in one chain works here.
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server sudo python3 bash coreutils \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Unified station identity: crew (j.hong, j.becker, h.mercer, y.nassar, y.wu)
# + system accounts (controlsvc, gh0st). controlsvc = company recovery foothold,
# gh0st = 1st Officer's backdoor; y.wu (Researcher Wu Yan) is this chain's
# horizontal-move target.
COPY station_accounts.sh /tmp/station_accounts.sh
RUN bash /tmp/station_accounts.sh && rm /tmp/station_accounts.sh \
    # labctl: chain-local lab-equipment service account (NOT campaign-wide).
    # non-login: reachable only by becoming it through the PATH hijack.
    && useradd -m -s /usr/sbin/nologin labctl \
    && mkdir -p /var/run/sshd

# the explorable station filesystem — the exploitable subsystems now live
# UNDER the module tree (/opt/station/modules/{access_control,research_lab}).
COPY rootfs/ /
RUN ln -sf /opt/station/modules/access_control/bin/zonectl /usr/local/bin/zonectl \
    # lock the station tree read-only, owned by root: players can read and
    # traverse it but cannot edit or delete any of it.
    && chown -R root:root /opt/station \
    && find /opt/station -type d -exec chmod 755 {} + \
    && find /opt/station -type f -exec chmod 444 {} + \
    # ...then restore execute on the three subsystem binaries the find just
    # stripped. toolbox/ and logs/ under research_lab get their real (runtime)
    # perms from entrypoint.sh at container start — labctl's uid only exists
    # then, and the flag must never be baked into the image.
    && chmod 0755 /opt/station/modules/access_control/bin/zonectl \
                  /opt/station/modules/research_lab/bin/run-diagnostics.sh \
                  /opt/station/modules/research_lab/bin/sensor-status \
    # stationboot is the animated login sequence (ported from the network
    # chain); it lives in the read-only station tree, restore its exec bit.
    && chmod 0555 /opt/station/bin/stationboot

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 0755 /usr/local/bin/entrypoint.sh

# animated station login (same handshake/boot as network-chain/station_terminal).
# Banner text lives OUTSIDE the browsable /opt/station tree, each group-locked
# to a single account so neither account can read the other's, and the dir
# can't be listed (0711). stationboot reads only the file for the current user;
# it runs on INTERACTIVE login only (scripted/piped SSH skips it).
COPY login/ /etc/erebus/
RUN chown root:controlsvc /etc/erebus/banner_controlsvc.txt \
    && chown root:gh0st /etc/erebus/hijack_gh0st.txt \
    && chmod 0640 /etc/erebus/banner_controlsvc.txt /etc/erebus/hijack_gh0st.txt \
    && chmod 0711 /etc/erebus \
    && for u in j.hong j.becker h.mercer y.nassar y.wu controlsvc gh0st; do \
         echo 'case $- in *i*) /opt/station/bin/stationboot ;; esac' >> "/home/$u/.bashrc"; \
       done

# the sudo misconfiguration this chain is built around
COPY rootfs/etc/sudoers.d/90-recovery-access /etc/sudoers.d/90-recovery-access
RUN chmod 0440 /etc/sudoers.d/90-recovery-access

RUN sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
