#!/usr/bin/env python3
"""Owned Erebus medical-officer access challenge → RE-03 medbay lab.

Deliberately vulnerable isolated CTF service. Bind only to loopback on the host.
"""
from __future__ import annotations

import base64
import hmac
import json
import os
import secrets
import threading
import subprocess
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ARTIFACT = Path(os.environ.get("MEDBAY_ARTIFACT", HERE / "artifact3_binary"))
MID_FLAG = os.environ.get("MEDBAY_MID_FLAG", "CTF{medbay_wyan_last_seen_034217}")
HARD_FLAG = os.environ.get("MEDBAY_HARD_FLAG", "CTF{medbay_failsafe_reused_credential}")
OFFICER_USERNAME = "y.nassar"
RECOVERY_CODE = secrets.token_urlsafe(20)
RECOVERY_SPENT = False
ACCESS_LOCK = threading.Lock()
EXPORT_TOKEN = secrets.token_urlsafe(20)
SESSIONS: dict[str, dict] = {}
OFFICER_PASSWORD = secrets.token_urlsafe(24)  # resettable via the flawed access-control API


def safe_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


class Handler(BaseHTTPRequestHandler):
    server_version = "StationTerminal/0.1"

    def log_message(self, format: str, *args: object) -> None:
        # Do not record cookies, submitted passwords, recovery codes or flags.
        pass

    def send(self, status: int, payload: object, content_type: str = "application/json") -> None:
        if content_type == "application/json":
            body = json.dumps(payload).encode()
        elif isinstance(payload, bytes):
            body = payload
        else:
            body = str(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def session(self) -> dict | None:
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except Exception:
            return None
        token = cookie.get("medbay_session")
        with ACCESS_LOCK:
            return SESSIONS.get(token.value) if token else None

    def require(self, officer: bool = False) -> dict | None:
        session = self.session()
        if not session:
            self.send(HTTPStatus.UNAUTHORIZED, {"error": "login required"})
            return None
        if officer and session["user"] != OFFICER_USERNAME:
            self.send(HTTPStatus.FORBIDDEN, {"error": "medical-officer access required"})
            return None
        return session

    def body(self) -> dict | None:
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 0 or size > 4096:
                raise ValueError("invalid body size")
            value = json.loads(self.rfile.read(size))
            if not isinstance(value, dict):
                raise ValueError("object required")
            return value
        except (ValueError, json.JSONDecodeError):
            self.send(HTTPStatus.BAD_REQUEST, {"error": "expected a small JSON object"})
            return None

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.send(200, {"status": "ready", "service": "medbay"})
        elif path == "/":
            self.send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/static/app.js":
            self.send(200, (HERE / "app.js").read_bytes(), "text/javascript; charset=utf-8")
        elif path == "/api/me":
            session = self.require()
            if session:
                self.send(200, {"user": session["user"], "role": "medical-officer" if session["user"] == OFFICER_USERNAME else "crew"})
        elif path == "/api/access/grants":
            session = self.require()
            if session:
                self.send(200, {"grants": [{"id": 1, "subject": "crew", "purpose": "routine access"}], "directory_hint": "Legacy grant IDs are sequential."})
        elif path.startswith("/api/access/grants/"):
            session = self.require()
            if not session:
                return
            grant_id = path.removeprefix("/api/access/grants/")
            if grant_id == "1":
                self.send(200, {"id": 1, "subject": "crew", "purpose": "routine access"})
            elif grant_id == "2":
                # INTENTIONAL: authenticated caller is not checked against grant owner.
                with ACCESS_LOCK:
                    grant = {"id": 2, "subject": OFFICER_USERNAME, "role": "medical-officer",
                             "purpose": "emergency account recovery", "recovery_code": RECOVERY_CODE,
                             "state": "used" if RECOVERY_SPENT else "available"}
                self.send(200, grant)
            else:
                self.send(404, {"error": "grant not found"})
        elif path == "/api/medbay":
            session = self.require(officer=True)
            if session:
                self.send(200, {"station": "Erebus", "operator": "Tallis Group", "officer": "Yara Nassar",
                                "message": "Routine queue restored. ORACLE's post-blackout audit export is unresolved.",
                                "artifact": "/api/medbay/artifact", "audit_submission": "/api/medbay/reconcile",
                                "hint": "Trace the recovered selector's actual route; decoy references do not reach the live archive."})
        elif path == "/api/medbay/artifact":
            session = self.require(officer=True)
            if session:
                if not ARTIFACT.is_file():
                    self.send(503, {"error": "audit selector not built"})
                else:
                    self.send(200, ARTIFACT.read_bytes(), "application/octet-stream")
        elif path == "/api/failsafe/config":
            session = self.require(officer=True)
            if not session:
                return
            auth = self.headers.get("Authorization", "")
            try:
                decoded = base64.b64decode(auth.removeprefix("Basic "), validate=True).decode()
            except (ValueError, UnicodeError):
                decoded = ""
            if not auth.startswith("Basic ") or not safe_equal(decoded, "medbay_sync:" + EXPORT_TOKEN):
                self.send(403, {"error": "station configuration credential required"})
                return
            self.send(200, {"panel": "FS-02", "location": "medbay physical bypass panel",
                            "warning": "The Chronicle entry gives the safe local mode. Remote activation is blocked."})
        else:
            self.send(404, {"error": "not found"})

    def do_POST(self) -> None:
        global OFFICER_PASSWORD, RECOVERY_SPENT
        path = urlparse(self.path).path
        body = self.body()
        if body is None:
            return
        if path == "/api/login":
            username, password = str(body.get("username", "")), str(body.get("password", ""))
            if not ((username == "crew" and safe_equal(password, "station-brief")) or
                    (username == OFFICER_USERNAME and safe_equal(password, OFFICER_PASSWORD))):
                self.send(401, {"error": "invalid credentials"})
                return
            token = secrets.token_urlsafe(32)
            with ACCESS_LOCK:
                SESSIONS[token] = {"user": username, "unlocked": False, "mid_solved": False}
            self.send_response(200)
            data = json.dumps({"user": username}).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", f"medbay_session={token}; HttpOnly; SameSite=Strict; Path=/")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif path == "/api/access/recover":
            session = self.require()
            if not session:
                return
            candidate, replacement = str(body.get("recovery_code", "")), str(body.get("new_password", ""))
            if len(replacement) < 8 or len(replacement) > 128:
                self.send(403, {"error": "recovery denied"})
                return
            # INTENTIONAL: the grant read above lacks object-level ownership checks.
            # Recovery itself accepts the leaked bearer code, but consumes it once.
            with ACCESS_LOCK:
                if RECOVERY_SPENT or not safe_equal(candidate, RECOVERY_CODE):
                    self.send(403, {"error": "recovery denied"})
                    return
                OFFICER_PASSWORD = replacement
                RECOVERY_SPENT = True
                # Reset invalidates previously issued officer cookies. Crew can log in again.
                for token, record in list(SESSIONS.items()):
                    if record["user"] == OFFICER_USERNAME:
                        del SESSIONS[token]
            self.send(200, {"status": "medical-officer account recovered"})
        elif path == "/api/medbay/reconcile":
            session = self.require(officer=True)
            if not session:
                return
            candidate = str(body.get("audit_reference", ""))
            if len(candidate) > 128 or not ARTIFACT.is_file():
                self.send(400, {"error": "invalid or unavailable reference"})
                return
            try:
                result = subprocess.run([str(ARTIFACT), "--verify", candidate], capture_output=True, timeout=2, check=False)
            except (OSError, subprocess.TimeoutExpired):
                self.send(503, {"error": "audit selector unavailable"})
                return
            if result.returncode != 0:
                self.send(403, {"error": "decoy audit reference"})
                return
            session["unlocked"] = True
            self.send(200, {"receipt": "THREAD_03", "station": "Erebus", "case": "Wu Yan",
                            "dispensing_ledger": [
                                "2026-09-21 03:16Z: ORACLE automated fatality entry for Wu Yan; unsigned and marked UNVERIFIED",
                                "03:21Z: oxygen stabiliser dispensed for Wu Yan; Yara Nassar signed the clinician entry",
                                "03:38Z: ambulatory transfer kit issued for Wu Yan's research-lab return"],
                            "clinical_notes": [
                                "Yara Nassar: Wu Yan is conscious and responsive. ORACLE's unsigned fatality entry is not a clinical assessment.",
                                "Wu Yan departed medbay alive. Confirm the last sighting with the Chronicle; final fate is unknown.",
                                "Access log: Yara Nassar's last badge-in was medbay; no subsequent movement is confirmed."],
                            "chronicler": [
                                "2026-09-21 03:42:17Z: Wu Yan seen responsive at research lab entry; w.yan badge accepted; lab then sealed from inside. No later verified sighting.",
                                "FS-02 bypass procedure: local-manual only; remote activation disabled."],
                            "recovered_config": {"account": "medbay_sync", "credential": EXPORT_TOKEN,
                                                 "note": "The same export credential was reused by the station failsafe config service."}})
        elif path == "/api/medbay/submit":
            session = self.require(officer=True)
            if not session:
                return
            if not session["unlocked"]:
                self.send(403, {"error": "authenticate the genuine audit first"})
                return
            fate = " ".join(str(body.get("fate", "")).lower().split())
            timestamp = str(body.get("timestamp", "")).strip().upper()
            if fate != "last seen alive" or timestamp != "03:42:17Z":
                self.send(400, {"error": "case conclusion not supported by the records"})
                return
            session["mid_solved"] = True
            self.send(200, {"result": "Wu Yan's last verified status recorded; final fate remains unknown", "flag": MID_FLAG})
        elif path == "/api/failsafe/isolate":
            session = self.require(officer=True)
            if not session:
                return
            if not session["mid_solved"]:
                self.send(403, {"error": "complete the medbay case first"})
                return
            auth = self.headers.get("Authorization", "")
            try:
                decoded = base64.b64decode(auth.removeprefix("Basic "), validate=True).decode()
            except (ValueError, UnicodeError):
                decoded = ""
            if not auth.startswith("Basic ") or not safe_equal(decoded, "medbay_sync:" + EXPORT_TOKEN):
                self.send(403, {"error": "configuration credential required"})
                return
            if body.get("panel") != "FS-02" or body.get("mode") != "local-manual":
                self.send(400, {"error": "unsafe or incorrect failsafe instruction"})
                return
            self.send(200, {"result": "simulated bypass evidence recovered; no physical control changed", "flag": HARD_FLAG})
        else:
            self.send(404, {"error": "not found"})


if __name__ == "__main__":
    bind = os.environ.get("MEDBAY_BIND", "127.0.0.1")
    port = int(os.environ.get("MEDBAY_PORT", "8080"))
    server = ThreadingHTTPServer((bind, port), Handler)
    print(f"READY port={server.server_port}", flush=True)
    server.serve_forever()
