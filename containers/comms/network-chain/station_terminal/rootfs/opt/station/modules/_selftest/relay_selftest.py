#!/usr/bin/env python3
"""
relay_selftest — offline link self-test (diagnostics).

Emits a few SAMPLE telemetry frames so an operator can eyeball the format
without touching the live link. These are canned samples: they are not on the
wire, their sequence numbers are out of band, and the token they carry is a
self-test placeholder. Capturing or replaying this output achieves nothing
against the live watchers.
"""
SAMPLES = [
    "TM|9001|00:00:01Z|HS:NOMINAL|SES:selftest@loop|TOK:CTF{relay_selftest_ok}|CRC:0000",
    "TM|9002|00:00:02Z|HS:NOMINAL|SES:selftest@loop|TOK:CTF{relay_selftest_ok}|CRC:0000",
]

if __name__ == "__main__":
    print("relay self-test — sample frames (offline, not live):")
    for s in SAMPLES:
        print(" ", s)
