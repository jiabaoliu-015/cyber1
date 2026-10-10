#!/usr/bin/env python3
"""Exercise the actually running Compose service, not an in-process mock."""
from __future__ import annotations

import base64
import http.cookiejar
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from reference_solver import reference

BASE = os.environ.get("MEDBAY_LIVE_URL", "http://127.0.0.1:18082")


def client():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def call(opener, path, data=None, headers=None, raw=False) -> tuple[int, Any]:
    request = urllib.request.Request(BASE + path,
        data=None if data is None else json.dumps(data).encode(),
        headers={"Content-Type": "application/json", **(headers or {})})
    try:
        response = opener.open(request, timeout=4)
    except urllib.error.HTTPError as error:
        response = error
    content = response.read()
    assert response.status is not None
    return response.status, content if raw else json.loads(content)


def expect(status, actual):
    if actual != status:
        raise AssertionError(f"wanted HTTP {status}, got {actual}")


def main():
    guest, crew, officer = client(), client(), client()
    for attempt in range(20):
        try:
            expect(200, call(guest, "/health")[0])
            break
        except (OSError, AssertionError):
            if attempt == 19:
                raise
            time.sleep(0.25)
    expect(401, call(guest, "/api/access/grants/2")[0])
    expect(401, call(guest, "/api/medbay/artifact", raw=True)[0])
    expect(200, call(crew, "/api/login", {"username": "crew", "password": "station-brief"})[0])
    expect(403, call(crew, "/api/medbay")[0])
    expect(401, call(guest, "/api/access/recover", {"recovery_code": "guess", "new_password": "replacement"})[0])
    expect(401, call(crew, "/api/login", {"username": "y.nassar", "password": "doNoHarm.09"})[0])
    status, grant = call(crew, "/api/access/grants/2")
    expect(200, status)
    if grant["subject"] != "y.nassar" or grant["state"] != "available":
        raise AssertionError("officer grant not discoverable")
    expect(403, call(crew, "/api/access/recover", {"recovery_code": "guess", "new_password": "replacement"})[0])
    expect(200, call(crew, "/api/access/recover", {"recovery_code": grant["recovery_code"],
                        "new_password": "test-officer-only"})[0])
    expect(403, call(crew, "/api/access/recover", {"recovery_code": grant["recovery_code"],
                        "new_password": "another-password"})[0])
    if call(crew, "/api/access/grants/2")[1]["state"] != "used":
        raise AssertionError("recovery code remains available")
    expect(200, call(officer, "/api/login", {"username": "y.nassar", "password": "test-officer-only"})[0])
    status, artifact = call(officer, "/api/medbay/artifact", raw=True)
    expect(200, status)
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder) / "selector"
        binary.write_bytes(artifact)
        binary.chmod(0o700)
        if not artifact.startswith(b"\x7fELF"):
            raise AssertionError("downloaded audit artifact is not a native ELF")
        if subprocess.run([str(binary), "--verify", reference()], capture_output=True, timeout=2).returncode != 0:
            raise AssertionError("container-built ELF did not verify its genuine route")
    expect(403, call(officer, "/api/medbay/reconcile", {"audit_reference": "DECOY"})[0])
    status, evidence = call(officer, "/api/medbay/reconcile", {"audit_reference": reference()})
    expect(200, status)
    if evidence["receipt"] != "THREAD_03":
        raise AssertionError("RE-03 receipt changed")
    if evidence["case"] != "Wu Yan" or evidence["station"] != "Erebus":
        raise AssertionError("Medbay evidence does not match crew/station canon")
    expect(400, call(officer, "/api/medbay/submit", {"fate": "deceased", "timestamp": "03:42:17Z"})[0])
    expect(400, call(officer, "/api/medbay/submit", {"fate": "evacuated alive", "timestamp": "03:42:17Z"})[0])
    status, mid = call(officer, "/api/medbay/submit", {"fate": "last seen alive", "timestamp": "03:42:17Z"})
    expect(200, status)
    if mid["flag"] != "CTF{medbay_wyan_last_seen_034217}":
        raise AssertionError("Medbay mid flag does not match revised case")
    if not mid["flag"].startswith("CTF{"):
        raise AssertionError("mid flag missing")
    credential = evidence["recovered_config"]
    auth = "Basic " + base64.b64encode((credential["account"] + ":" + credential["credential"]).encode()).decode()
    status, config = call(officer, "/api/failsafe/config", headers={"Authorization": auth})
    expect(200, status)
    expect(400, call(officer, "/api/failsafe/isolate", {"panel": config["panel"], "mode": "remote"}, {"Authorization": auth})[0])
    status, hard = call(officer, "/api/failsafe/isolate", {"panel": config["panel"], "mode": "local-manual"}, {"Authorization": auth})
    expect(200, status)
    if not hard["flag"].startswith("CTF{") or hard["flag"] == mid["flag"]:
        raise AssertionError("distinct hard flag missing")
    print("LIVE MEDBAY PATH: PASS (crew → officer → container ELF → case → failsafe; negative cases checked)")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"LIVE MEDBAY PATH: FAIL — {error}", file=sys.stderr)
        raise
