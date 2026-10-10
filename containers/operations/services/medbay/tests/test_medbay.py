#!/usr/bin/env python3
"""Real HTTP acceptance: default crew → officer → RE-03 → mid → failsafe."""
from __future__ import annotations

import base64
import http.cookiejar
import importlib.util
import json
import os
import re
import select
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("medbay_ref", Path(__file__).with_name("reference_solver.py"))
assert SPEC is not None and SPEC.loader is not None
solver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(solver)


class MedbayPath(unittest.TestCase):
    def http(self, opener, path, data=None, headers=None, binary=False) -> tuple[int, Any]:
        url = self.base + path
        request = urllib.request.Request(url, data=None if data is None else json.dumps(data).encode(),
                                         headers={"Content-Type": "application/json", **(headers or {})})
        try:
            result = opener.open(request, timeout=3)
        except urllib.error.HTTPError as error:
            result = error
        content = result.read()
        assert result.status is not None
        return result.status, content if binary else json.loads(content)

    def launch(self):
        env = os.environ.copy()
        env.update(MEDBAY_ARTIFACT=str(self.binary), MEDBAY_BIND="127.0.0.1", MEDBAY_PORT="0")
        self.process = subprocess.Popen([sys.executable, "-u", str(ROOT / "app.py")], env=env,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert self.process.stdout is not None
        ready, _, _ = select.select([self.process.stdout], [], [], 8)
        self.assertTrue(ready, "server did not report readiness")
        line = self.process.stdout.readline().strip()
        self.assertTrue(line.startswith("READY port="), line)
        self.base = "http://127.0.0.1:" + line.split("=")[1]

    def stop(self):
        self.process.terminate()
        try:
            self.process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.communicate(timeout=3)

    def test_complete_player_path_and_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            self.binary = Path(folder) / "artifact3_binary"
            build = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2", "-fno-ident",
                                    "-o", str(self.binary), str(ROOT / "route_selector.c")], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            correct = solver.reference()
            self.assertNotIn(correct, subprocess.check_output(["strings", str(self.binary)], text=True))
            self.assertEqual(subprocess.run([str(self.binary), "--verify", correct], capture_output=True).returncode, 0)
            decoy = bytes(x ^ 0x5A for x in solver.ENCODED[0]).decode("ascii")
            self.assertEqual(subprocess.run([str(self.binary), "--verify", decoy], capture_output=True).returncode, 1)
            self.launch()
            try:
                guest = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
                crew = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
                officer = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
                self.assertEqual(self.http(guest, "/health")[0], 200)
                self.assertIn(b"EREBUS", self.http(guest, "/", binary=True)[1])
                self.assertEqual(self.http(guest, "/api/access/grants/2")[0], 401)
                self.assertEqual(self.http(guest, "/api/access/recover", {"recovery_code": "x", "new_password": "replacement"})[0], 401)
                self.assertEqual(self.http(guest, "/api/medbay/artifact", binary=True)[0], 401)
                self.assertEqual(self.http(crew, "/api/login", {"username": "crew", "password": "wrong"})[0], 401)
                self.assertEqual(self.http(crew, "/api/login", {"username": "crew", "password": "station-brief"})[0], 200)
                self.assertEqual(self.http(crew, "/api/access/grants")[1]["grants"][0]["id"], 1)
                self.assertEqual(self.http(crew, "/api/medbay")[0], 403)
                self.assertEqual(self.http(crew, "/api/access/recover", {"recovery_code": "guess", "new_password": "replacement"})[0], 403)
                self.assertEqual(self.http(crew, "/api/login", {"username": "y.nassar", "password": "doNoHarm.09"})[0], 401)
                status, grant = self.http(crew, "/api/access/grants/2")
                self.assertEqual(status, 200)
                recovery = grant["recovery_code"]
                self.assertEqual(grant["subject"], "y.nassar")
                self.assertEqual(grant["state"], "available")
                self.assertEqual(self.http(crew, "/api/access/recover", {"recovery_code": "wrong", "new_password": "passphrase-123"})[0], 403)
                self.assertEqual(self.http(crew, "/api/access/recover", {"recovery_code": recovery, "new_password": "passphrase-123"})[0], 200)
                self.assertEqual(self.http(crew, "/api/access/recover", {"recovery_code": recovery, "new_password": "another-password"})[0], 403)
                self.assertEqual(self.http(crew, "/api/access/grants/2")[1]["state"], "used")
                self.assertEqual(self.http(guest, "/api/login", {"username": "y.nassar", "password": "another-password"})[0], 401)
                self.assertEqual(self.http(officer, "/api/login", {"username": "y.nassar", "password": "passphrase-123"})[0], 200)
                self.assertEqual(self.http(officer, "/api/me")[1], {"user": "y.nassar", "role": "medical-officer"})
                self.assertEqual(self.http(officer, "/api/medbay")[0], 200)
                self.assertEqual(self.http(officer, "/api/medbay/artifact", binary=True)[1], self.binary.read_bytes())
                self.assertEqual(self.http(officer, "/api/medbay/submit", {"fate": "last seen alive", "timestamp": "03:42:17Z"})[0], 403)
                self.assertEqual(self.http(officer, "/api/medbay/reconcile", {"audit_reference": decoy})[0], 403)
                self.assertEqual(self.http(crew, "/api/medbay/reconcile", {"audit_reference": correct})[0], 403)
                status, archive = self.http(officer, "/api/medbay/reconcile", {"audit_reference": correct})
                self.assertEqual(status, 200)
                self.assertEqual(archive["receipt"], "THREAD_03")
                self.assertEqual(archive["case"], "Wu Yan")
                self.assertEqual(archive["station"], "Erebus")
                self.assertIn("dispensing_ledger", archive)
                self.assertIn("clinical_notes", archive)
                self.assertIn("chronicler", archive)
                self.assertIn("ORACLE", " ".join(archive["dispensing_ledger"]))
                self.assertIn("Yara Nassar", " ".join(archive["clinical_notes"]))
                self.assertIn("research lab", " ".join(archive["chronicler"]))
                self.assertNotIn("evacuat", json.dumps(archive).lower())
                self.assertEqual(self.http(officer, "/api/medbay/submit", {"fate": "deceased", "timestamp": "03:42:17Z"})[0], 400)
                self.assertEqual(self.http(officer, "/api/medbay/submit", {"fate": "evacuated alive", "timestamp": "03:42:17Z"})[0], 400)
                status, mid = self.http(officer, "/api/medbay/submit", {"fate": "last seen alive", "timestamp": "03:42:17Z"})
                self.assertEqual(status, 200)
                self.assertEqual(mid["flag"], "CTF{medbay_wyan_last_seen_034217}")
                self.assertRegex(mid["flag"], r"^CTF\{medbay_.*\}$")
                self.assertNotIn(mid["flag"].encode(), self.http(guest, "/", binary=True)[1])
                self.assertEqual(self.http(officer, "/api/failsafe/config")[0], 403)
                credential = archive["recovered_config"]
                basic = "Basic " + base64.b64encode((credential["account"] + ":" + credential["credential"]).encode()).decode()
                status, config = self.http(officer, "/api/failsafe/config", headers={"Authorization": basic})
                self.assertEqual(status, 200)
                self.assertEqual(config["panel"], "FS-02")
                self.assertEqual(self.http(officer, "/api/failsafe/isolate", {"panel": "FS-02", "mode": "remote"}, {"Authorization": basic})[0], 400)
                status, hard = self.http(officer, "/api/failsafe/isolate", {"panel": "FS-02", "mode": "local-manual"}, {"Authorization": basic})
                self.assertEqual(status, 200)
                self.assertRegex(hard["flag"], r"^CTF\{medbay_.*\}$")
                self.assertNotEqual(hard["flag"], mid["flag"])
            finally:
                self.stop()
            self.launch()
            try:
                self.assertEqual(self.http(officer, "/api/medbay")[0], 401)
                self.assertEqual(self.http(guest, "/api/login", {"username": "y.nassar", "password": "passphrase-123"})[0], 401)
                self.assertEqual(self.http(crew, "/api/access/recover", {"recovery_code": recovery, "new_password": "second-pass"})[0], 401)
            finally:
                self.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
