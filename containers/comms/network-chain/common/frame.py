"""
Shared telemetry-frame (TM) format for the Erebus status link.

Wire format (fixed-field, pipe-delimited — "format C"):

    TM|<seq>|<ts>|HS:<status>|SES:<sessions>|TOK:<token>|CRC:<crc16>

- seq     monotonically increasing sequence number (freshness marker)
- ts      station clock, HH:MM:SSZ
- HS      health-and-status word (NOMINAL / DEGRADED / ...)
- SES     comma-separated active sessions (user@node)
- TOK     a link auth token carried in cleartext on the ground feed
          (this is the exposed value the capture flag rewards)
- CRC     crc16 over the preceding fields

Authenticated frames (the internal AI feed to sentry_watcher) append:

    ...|CRC:<crc16>|MAC:<hmac-sha256-hex-truncated>

The ground feed (to landfall_link) is NOT authenticated and NOT freshness-
checked — that is the point. The AI feed IS authenticated + freshness-checked.
"""
from __future__ import annotations

import hashlib
import hmac


def crc16(data: str) -> str:
    crc = 0xFFFF
    for ch in data.encode("utf-8", "replace"):
        crc ^= ch << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def build(seq: int, ts: str, status: str, sessions: str, token: str) -> str:
    body = f"TM|{seq}|{ts}|HS:{status}|SES:{sessions}|TOK:{token}"
    return f"{body}|CRC:{crc16(body)}"


def sign(frame: str, key: str) -> str:
    """Append a MAC field, keyed with `key` (the AI feed is authenticated)."""
    mac = hmac.new(key.encode(), frame.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{frame}|MAC:{mac}"


def verify_mac(frame: str, key: str) -> bool:
    if "|MAC:" not in frame:
        return False
    base, _, mac = frame.rpartition("|MAC:")
    expect = hmac.new(key.encode(), base.encode(), hashlib.sha256).hexdigest()[:16]
    return hmac.compare_digest(mac.strip(), expect)


def parse(frame: str) -> dict:
    """Parse a frame into a dict. Tolerant; returns {} on obvious garbage."""
    frame = frame.strip()
    parts = frame.split("|")
    if not parts or parts[0] != "TM":
        return {}
    out: dict = {"raw": frame, "seq": None, "ts": None}
    try:
        out["seq"] = int(parts[1])
        out["ts"] = parts[2]
    except (IndexError, ValueError):
        return {}
    for p in parts[3:]:
        if ":" in p:
            k, _, v = p.partition(":")
            out[k.lower()] = v
    return out


def frame_hash(frame: str) -> str:
    """Stable identity of a frame's *content* (excludes the MAC field)."""
    base = frame.split("|MAC:")[0]
    return hashlib.sha256(base.encode()).hexdigest()[:12]
