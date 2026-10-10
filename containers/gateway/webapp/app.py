from __future__ import annotations

import hashlib
import html
import os
import secrets
import sqlite3
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

APP_TITLE = "THE CREW_PORTAL"
DB_PATH = Path(os.getenv("CREW_PORTAL_DB", Path(__file__).resolve().parents[1] / "data" / "webapp.db"))
ENTRY_IMAGE = Path(os.getenv("ENTRY_IMAGE", Path(__file__).resolve().parents[1] / "entry" / "access_artifact.png"))

app = FastAPI(title=APP_TITLE, docs_url=None, redoc_url=None)
sessions: dict[str, int] = {}


def entry_md5() -> str:
    return hashlib.md5(ENTRY_IMAGE.read_bytes()).hexdigest()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS research (
                id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                public_bio TEXT NOT NULL,
                private_note TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS backups (
                owner_id INTEGER PRIMARY KEY,
                label TEXT NOT NULL,
                contents TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            """
        )
        if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO users(id, username, display_name, role) VALUES(?,?,?,?)",
                [
                    (1, "maint-recovery", "Maintenance Recovery", "maintenance"),
                    (2, "mira.chen", "Mira Chen", "researcher"),
                    (3, "eli.voss", "Eli Voss", "researcher"),
                ],
            )
            db.executemany(
                "INSERT INTO research(id, owner_id, title, body) VALUES(?,?,?,?)",
                [
                    (1, 1, "Recovery channel notes", "Archive migration complete. Research records imported with sequential record IDs 1–3."),
                    (2, 2, "Comms Relay handoff", "COMMS_RELAY_NODE=comms_relay.internal\nUPLINK_ENTRY=SG-41-ORBIT\nFLAG=CTF{webapp_idor_thread_01}"),
                    (3, 3, "Telemetry review", "Routine observation data. No recovery material attached."),
                    (4, 2, "Archive transfer exception", "Restricted migration manifest. FLAG=CTF{webapp_sqli_thread_01b}"),
                ],
            )
            db.executemany(
                "INSERT INTO profiles(username, owner_id, public_bio, private_note) VALUES(?,?,?,?)",
                [
                    ("maint-recovery", 1, "Legacy maintenance account.", "No private recovery note."),
                    ("mira.chen", 2, "Archive researcher.", "FLAG=CTF{webapp_profile_horizontal_01}"),
                    ("eli.voss", 3, "Telemetry researcher.", "Observation queue contact: ext-441."),
                ],
            )
            db.executemany(
                "INSERT INTO backups(owner_id, label, contents) VALUES(?,?,?)",
                [
                    (1, "maintenance-recovery.txt", "No additional recovery material."),
                    (2, "mira-archive.txt", "Archive staging notes only."),
                    (3, "eli-telemetry.txt", "FLAG=CTF{webapp_backup_horizontal_02}\nBackup transfer marked private."),
                ],
            )


@app.on_event("startup")
def startup() -> None:
    init_db()


def current_user(request: Request):
    token = request.cookies.get("webapp_session")
    uid = sessions.get(token or "")
    if not uid:
        return None
    with connect() as db:
        return db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{html.escape(title)}</title>
<style>
body{{margin:0;background:#0b111c;color:#dfe8f5;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
main{{max-width:900px;margin:60px auto;padding:24px;background:#111a29;border:1px solid #26354c;border-radius:14px}}
h1{{letter-spacing:.08em}} a{{color:#8bc6ff}} input,button{{font:inherit;padding:10px;margin:5px 0;background:#0c1421;color:#e7eef8;border:1px solid #354c6c;border-radius:7px}}
button{{cursor:pointer}} .muted{{color:#91a0b8}} .card{{background:#0c1421;padding:14px;border-radius:9px;margin:12px 0;border:1px solid #22344e}}
code,pre{{color:#b7d8ff;white-space:pre-wrap}} .warn{{color:#ffce85}}
</style></head><body><main><h1>{APP_TITLE}</h1>{body}</main></body></html>"""
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "webapp"}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user = current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return page(
        "Crew Portal Recovery",
        """
<p class='muted'>Neglected research-observation portal // recovery interface</p>
<form method='post' action='/login'>
<label>Maintenance username</label><br><input name='username' autocomplete='off'><br>
<label>Recovery proof</label><br><input name='password' autocomplete='off'><br>
<button type='submit'>OPEN RECOVERY CHANNEL</button>
</form>
<p class='muted'>Recovery proof is verified against the preserved incident artefact.</p>
""",
    )


@app.post("/login")
async def login(request: Request):
    data = parse_qs((await request.body()).decode("utf-8", "replace"))
    username = data.get("username", [""])[0]
    password = data.get("password", [""])[0]
    if username != "maint-recovery" or password.lower() != entry_md5():
        return page("Denied", "<p class='warn'>Recovery proof rejected.</p><p><a href='/'>Return</a></p>")
    token = secrets.token_urlsafe(24)
    sessions[token] = 1
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie("webapp_session", token, httponly=True, samesite="strict")
    return response


@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("webapp_session")
    if token:
        sessions.pop(token, None)
    r = RedirectResponse("/", status_code=302)
    r.delete_cookie("webapp_session")
    return r


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    body = f"""
<p>Channel opened as <b>{html.escape(user['display_name'])}</b> / {html.escape(user['role'])}</p>
<div class='card'>
<b>Your recovered research record</b>
<pre id='record'>loading…</pre>
</div>
<div class='card'>
<b>Research directory</b>
<p class='muted'>Directory visibility is not considered sensitive by this legacy system.</p>
<ul><li>#1 — Maintenance Recovery</li><li>#2 — Mira Chen</li><li>#3 — Eli Voss</li></ul>
</div>
<div class='card'>
<b>Legacy archive search</b>
<p class='muted'>Migration note: search is retained for archive compatibility.</p>
<form id='search-form'><input id='search-q' name='q' placeholder='search archive'><button>SEARCH</button></form>
<pre id='search-results'></pre>
</div>
<div class='card'>
<b>Researcher resources</b>
<p class='muted'>Legacy URLs use usernames and numeric owner IDs: <code>/api/profiles/mira.chen</code>, <code>/api/backups/3</code>.</p>
<p><a href='/moderation/queue'>maintenance moderation queue</a> — feedback endpoint: <code>POST /api/feedback</code>.</p>
</div>
<p class='muted'>Client build: archive-ui 0.8 // API migration incomplete</p>
<p><a href='/logout'>close channel</a></p>
<script>
fetch('/api/research/1').then(r=>r.json()).then(x=>{{document.getElementById('record').textContent=JSON.stringify(x,null,2)}})
document.getElementById('search-form').addEventListener('submit', e=>{{e.preventDefault(); fetch('/api/search?q='+encodeURIComponent(document.getElementById('search-q').value)).then(r=>r.json()).then(x=>{{document.getElementById('search-results').textContent=JSON.stringify(x,null,2)}})}})
</script>
"""
    return page("Crew Portal Dashboard", body)


@app.get("/api/research/{record_id}")
def research(record_id: int, request: Request):
    user = current_user(request)
    if not user:
        return JSONResponse({"error": "authentication required"}, status_code=401)
    with connect() as db:
        row = db.execute(
            "SELECT research.id, research.owner_id, users.display_name AS owner, research.title, research.body "
            "FROM research JOIN users ON users.id=research.owner_id WHERE research.id=?",
            (record_id,),
        ).fetchone()
    if not row:
        return JSONResponse({"error": "record not found"}, status_code=404)

    # INTENTIONAL CTF VULNERABILITY (Slice A):
    # Authentication is checked, but record ownership/authorization is not.
    # A maintenance user can request another researcher's record by ID.
    return dict(row)


@app.get("/api/search")
def search_research(q: str, request: Request):
    """Legacy archive search deliberately retains a SQL injection flaw for the lab."""
    if not current_user(request):
        return JSONResponse({"error": "authentication required"}, status_code=401)
    # INTENTIONAL CTF VULNERABILITY (Web 1): user input is concatenated into SQL.
    # The endpoint is authenticated and loopback-bound, but still must never be
    # implemented this way outside the isolated challenge environment.
    query = (
        "SELECT id, owner_id, title, body FROM research "
        f"WHERE title LIKE '%{q}%' OR body LIKE '%{q}%' ORDER BY id"
    )
    try:
        with connect() as db:
            rows = [dict(row) for row in db.execute(query).fetchall()]
    except sqlite3.Error:
        return JSONResponse({"error": "legacy search syntax error"}, status_code=400)
    return {"results": rows}


@app.get("/api/profiles/{username}")
def profile(username: str, request: Request):
    if not current_user(request):
        return JSONResponse({"error": "authentication required"}, status_code=401)
    with connect() as db:
        row = db.execute(
            "SELECT username, owner_id, public_bio, private_note FROM profiles WHERE username=?",
            (username,),
        ).fetchone()
    if not row:
        return JSONResponse({"error": "profile not found"}, status_code=404)
    # INTENTIONAL CTF VULNERABILITY (Horizontal 1): no ownership check before
    # returning another researcher's private profile note.
    return dict(row)


@app.get("/api/backups/{owner_id}")
def backup(owner_id: int, request: Request):
    if not current_user(request):
        return JSONResponse({"error": "authentication required"}, status_code=401)
    with connect() as db:
        row = db.execute(
            "SELECT owner_id, label, contents FROM backups WHERE owner_id=?", (owner_id,)
        ).fetchone()
    if not row:
        return JSONResponse({"error": "backup not found"}, status_code=404)
    # INTENTIONAL CTF VULNERABILITY (Horizontal 2): predictable owner IDs expose
    # another user's backup without an authorization decision.
    return dict(row)


@app.post("/api/feedback")
async def submit_feedback(request: Request):
    user = current_user(request)
    if not user:
        return JSONResponse({"error": "authentication required"}, status_code=401)
    data = parse_qs((await request.body()).decode("utf-8", "replace"))
    subject = data.get("subject", [""])[0].strip()[:120]
    message = data.get("message", [""])[0][:2000]
    if not subject or not message:
        return JSONResponse({"error": "subject and message required"}, status_code=400)
    with connect() as db:
        db.execute(
            "INSERT INTO feedback(owner_id, subject, message) VALUES(?,?,?)",
            (user["id"], subject, message),
        )
    return {"status": "queued"}


@app.get("/moderation/queue", response_class=HTMLResponse)
def moderation_queue(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/", status_code=302)
    with connect() as db:
        rows = db.execute("SELECT id, subject, message FROM feedback ORDER BY id").fetchall()
    # INTENTIONAL CTF VULNERABILITY (Web 2): stored feedback is rendered without
    # HTML escaping in the maintenance moderation queue.
    entries = "".join(
        f"<article class='card'><h2>{html.escape(row['subject'])}</h2>"
        f"<div class='feedback'>{row['message']}</div></article>"
        for row in rows
    ) or "<p class='muted'>No queued feedback.</p>"
    return page(
        "Crew Portal Moderation Queue",
        "<p class='warn'>Maintenance-only queue. Feedback is rendered by archive-ui 0.8.</p>" + entries,
    )
