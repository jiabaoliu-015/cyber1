"""Power lab: Power Distribution / Reactor Control pathway (flowchart spec).

Station: Erebus — Tallis Group crewed station, proposed Callisto orbit, AI ORACLE,
last human contact 16 Sep 2026, ground-link blackout 20 Sep 2026 (shared canon with network-chain terminal
`erebus`; foothold accounts `gh0st` / `controlsvc`). Crew records: Captain
Jin Hong (j.hong, last confirmed assigned Two-Key LEFT), First Officer John
Becker (j.becker + backdoor gh0st, last confirmed assigned Two-Key RIGHT; the
`officer` uid 3002 in this lab is Becker's seat), Chief Engineer Hank Mercer
(h.mercer, last logged at power distribution; current fate unresolved), Medical
Officer Yara Nassar (y.nassar, last badge-in medbay; current fate unresolved),
Researcher Wu Yan (w.yan, research lab sealed from inside; current fate unresolved).
`BECK-4217-K9` is Becker's asset-tag checkout (optics side-channel key).
`ISVM-AGENT-FW` / `meridian-yard-044` are docked-vessel/yard
build tags in the firmware, not the station name.

Horizontal priv (predictable tokens):
  Default-User (uid 3001) logs in, receives PWR-3001-STAT.
  Officer-User = 1st Officer (uid 3002) token is sequential and predictable:
  PWR-3002-STAT. Forging it yields officer access. No brute force needed.

LEFT Captain Key (Captain Jin Hong, slot A — flowchart captain_key_left):
  Officer-only GET /api/keys/left returns the LEFT fragment (Hong's key).
  The RIGHT fragment (Becker's key) is recovered via the Black Box optics
  crypto below; both feed the Two Key Console (Hong + Becker two-person rule).

Crypto / Black Box optics (flowchart lecturer portrait -> Mid flag):
  GET /api/blackbox/image serves the runtime-generated
  /app/generated-assets/astronaut_stego.jpeg, built from the bundled
  assets/astronaut.jpeg with an appended trailer:
    PWR-BLACKBOX-V1:<base64(xor(b"<MID>|<RIGHT>", b"BECK-4217-K9"))>
  The XOR key is scattered across data/blackbox_logs/ side-channel notes
  (also via GET /api/blackbox/side-channel). docs/solutions/solve_image.py
  recovers the Mid flag and the RIGHT Captain Key. JPEG viewers ignore the
  trailer, so the portrait renders normally.

Two Key Console (two-man rule: Hong + Becker — flowchart two_key fed by both keys):
  POST /api/two-key/authorize {left_key, right_key} writes the authorized
  marker. Both fragments must be correct (LEFT = Hong slot A, RIGHT = Becker slot B).

Vertical priv (kernel / root scram job):
  Two-key-authorized officer can write /var/run/power/input
  (via POST /api/schedule/input). The running cron daemon executes
  `* * * * * root /opt/power/cron_scram_wrapper` (which executes scram_job)
  and trusts that input.
  Writing `scram_reactor` makes the independent root job write the reactor
  report containing the Hard flag. The API only writes input and reads reports.

Decoys (station flavor, no flag — shared with HVAC console):
  GET /api/logs, GET /api/logs/{category}/{name},
  GET /api/reactor/history serve data/reactor_logs, data/shift_notes,
  data/engineer_logs, data/blackbox_logs, data/comms_logs,
  data/diagnostics, data/crew_logs, data/medical_logs,
  data/research_notes. Same set is served by the HVAC console so both
  containers appear to share one ship log store. Erebus brownout arc: Power Distribution
  sagging station-wide, First Officer Becker (last observed near the bus ducts)
  loitering with condensate notebooks, Chief Engineer Mercer (last logged at power;
  see engineer_logs/mercer_final_watch_058.txt) filing a concern
  about Becker, Medical Officer Nassar (last badged into medbay; see
  medical_logs/nassar_last_badge_059.txt) flagging Becker's fixation, warm object K-9
  humming at 17 Hz. Archived reports share the reactor-report format
  but carry no flag.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

FLAG_MID = os.environ.get("PWR_FLAG_MID", "CTF{blackbox_optics_mid_7f3a}")
FLAG_HARD = os.environ.get("PWR_FLAG_HARD", "CTF{reactor_scram_hard_9c1e}")
FLAG_AGENT = os.environ.get("PWR_FLAG_AGENT", "CTF{agent_obfuscated_hard_4d2b}")
LEFT_KEY = os.environ.get("PWR_LEFT_KEY", "CPT-LEFT-4A1F-22MZ")
RIGHT_KEY = os.environ.get("PWR_RIGHT_KEY", "CPT-RIGHT-9D2K-77QX")
XOR_KEY = os.environ.get("PWR_XOR_KEY", "BECK-4217-K9")
OBFUS_KEY = os.environ.get("PWR_OBFUS_KEY", "OBFUS-1ST-0FF")
RUN_DIR = Path(os.environ.get("PWR_RUN_DIR", "/var/run/power"))
INPUT_FILE = RUN_DIR / "input"
REPORT_FILE = RUN_DIR / "reactor_report.txt"
AUTH_FILE = RUN_DIR / "two_key_authorized"
CRON_FILE = Path("/etc/cron.d/power-scram")
IMAGE_MARKER = b"PWR-BLACKBOX-V1:"
AGENT_MARKER = b"AGENT-STAGE2:"

_BASE_DIR = Path(__file__).resolve().parent.parent
_LOG_CANDIDATES = (_BASE_DIR / "data", Path("/app/data"))
LOG_DIR = next((p for p in _LOG_CANDIDATES if p.is_dir()), _BASE_DIR / "data")
# Shared ship store: identical 9-category set is served by both Power and HVAC
# consoles so players see the same logs from either docker container.
ASSET_DIR = Path(os.environ.get("PWR_ASSET_DIR", "/app/generated-assets"))
STEGO_IMAGE = ASSET_DIR / "astronaut_stego.jpeg"
AGENT_IMAGE = ASSET_DIR / "agent_firmware.bin"
ALLOWED_LOG_CATEGORIES = (
    "reactor_logs",
    "shift_notes",
    "engineer_logs",
    "blackbox_logs",
    "comms_logs",
    "diagnostics",
    "crew_logs",
    "medical_logs",
    "research_notes",
)

USERS = {"default": 3001, "officer": 3002}


def token_for(username: str) -> str:
    return f"PWR-{USERS[username]:04d}-STAT"


def user_for_token(token: str | None) -> str | None:
    for user in USERS:
        if token == token_for(user):
            return user
    return None


def require_user(token: str | None) -> str:
    user = user_for_token((token or "").strip())
    if not user:
        raise HTTPException(status_code=401, detail="Missing or invalid token. POST /login as default first.")
    return user


def require_officer(token: str | None) -> str:
    user = require_user(token)
    if user != "officer":
        raise HTTPException(
            status_code=403,
            detail="Officer token required. Hint: tokens are predictable (PWR-UID-STAT); officer uid is 3002.",
        )
    return user


def is_two_key_authorized() -> bool:
    try:
        return AUTH_FILE.exists() and AUTH_FILE.read_text(errors="replace").strip() == "authorized"
    except OSError:
        return False


def require_two_key(token: str | None) -> str:
    user = require_officer(token)
    if not is_two_key_authorized():
        raise HTTPException(
            status_code=403,
            detail="Two Key Console authorization required. POST both Captain Keys to /api/two-key/authorize first.",
        )
    return user


def decode_trailer(raw: bytes, key: str = XOR_KEY) -> str:
    """Decode an appended PWR-BLACKBOX-V1 trailer to '<MID>|<RIGHT>'."""
    idx = raw.rfind(IMAGE_MARKER)
    if idx < 0:
        raise ValueError("No PWR-BLACKBOX-V1 trailer found in image bytes.")
    blob = raw[idx + len(IMAGE_MARKER):].strip().split()[0]
    cipher = base64.b64decode(blob)
    kb = key.encode()
    return bytes(c ^ kb[i % len(kb)] for i, c in enumerate(cipher)).decode()


def decode_agent_stage(raw: bytes, key: str = OBFUS_KEY) -> str:
    """Decode the live AGENT-STAGE2 block to the officer-path Hard flag."""
    idx = raw.rfind(AGENT_MARKER)
    if idx < 0:
        raise ValueError("No AGENT-STAGE2 marker found in firmware bytes.")
    blob = raw[idx + len(AGENT_MARKER):].strip().split()[0]
    kb = key.encode()
    plain = base64.b64decode(blob)[::-1]
    return bytes(c ^ kb[i % len(kb)] for i, c in enumerate(plain)).decode()


def _list_decoy_logs() -> dict:
    index: dict[str, list[str]] = {}
    for category in ALLOWED_LOG_CATEGORIES:
        cat_dir = LOG_DIR / category
        if not cat_dir.is_dir():
            index[category] = []
            continue
        index[category] = sorted(p.name for p in cat_dir.glob("*.txt") if p.is_file())
    return index


def _read_decoy_log(category: str, name: str) -> str:
    if category not in ALLOWED_LOG_CATEGORIES:
        raise HTTPException(status_code=404, detail="Unknown log category.")
    if not name.endswith(".txt") or "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=404, detail="Unknown log file.")
    path = (LOG_DIR / category / name).resolve()
    try:
        log_root = LOG_DIR.resolve()
    except OSError:
        raise HTTPException(status_code=404, detail="Unknown log file.")
    if log_root not in path.parents:
        raise HTTPException(status_code=404, detail="Unknown log file.")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Unknown log file.")
    return path.read_text(errors="replace")


app = FastAPI(title="Power Lab — Power Distribution / Reactor Control")


class LoginBody(BaseModel):
    user: str = "default"


class InputBody(BaseModel):
    content: str


class TwoKeyBody(BaseModel):
    left_key: str = ""
    right_key: str = ""


@app.get("/health")
def health():
    return {"status": "ok", "service": "power-lab"}


@app.post("/login")
def login(body: LoginBody):
    if body.user != "default":
        raise HTTPException(status_code=401, detail="Only default login is exposed. Officer token must be predicted.")
    return {"user": "default", "token": token_for("default"), "hint": "Officer uid is 3002; token format PWR-UID-STAT"}


@app.get("/api/users/me")
def me(x_token: str | None = Header(default=None, alias="X-Token")):
    user = require_user(x_token)
    return {"user": user, "token": token_for(user)}


@app.get("/api/power/status")
def power_status(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {
        "system": "Power Distribution / Reactor Control",
        "mode": "load-shed",
        "bus_load_pct": 61,
        "two_key_authorized": is_two_key_authorized(),
        "schedule": "* * * * * root /opt/power/cron_scram_wrapper (runs scram_job)",
        "input": str(INPUT_FILE),
        "report": str(REPORT_FILE),
        "image": "/api/blackbox/image",
        "agent_firmware": "/api/agent/binary",
        "logs": "/api/logs",
        "history": "/api/reactor/history",
    }


@app.get("/api/keys/left")
def left_key(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {"key_id": "captain-key-left", "left_key": LEFT_KEY, "slot": "Two Key Console slot A"}


@app.get("/api/blackbox/image")
def blackbox_image(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    if not STEGO_IMAGE.is_file():
        raise HTTPException(status_code=404, detail="Optics portrait not installed. Rebuild via scripts/build_image.py.")
    return FileResponse(str(STEGO_IMAGE), media_type="image/jpeg", filename="astronaut_stego.jpeg")


@app.get("/api/blackbox/side-channel")
def side_channel(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {
        "telemetry": "bus ripple correlates with keypad entry; see data/blackbox_logs/",
        "key_hint": "Side-channel key is a 11-char asset tag of the form XXXX-NNNN-XX (check blackbox telemetry logs).",
        "trailer": "JPEG trailer marker PWR-BLACKBOX-V1:<base64>. Solver: docs/solutions/solve_image.py",
        "logs": "/api/logs",
    }


@app.get("/api/blackbox/hint")
def blackbox_hint(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {
        "steps": [
            "1. Download the portrait: GET /api/blackbox/image.",
            "2. Find the side-channel key in blackbox telemetry logs (asset tag XXXX-NNNN-XX).",
            "3. Take bytes after marker PWR-BLACKBOX-V1:, base64-decode, XOR with the key.",
            "4. Result is '<MID flag>|<RIGHT Captain Key>'. Submit the RIGHT key to the Two Key Console.",
        ],
        "solver": "docs/solutions/solve_image.py",
    }


@app.get("/api/agent/binary")
def agent_binary(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    if not AGENT_IMAGE.is_file():
        raise HTTPException(status_code=404, detail="Agent firmware not installed. Rebuild via scripts/build_agent_binary.py.")
    return FileResponse(str(AGENT_IMAGE), media_type="application/octet-stream", filename="agent_firmware.bin")


@app.get("/api/agent/hint")
def agent_hint(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {
        "steps": [
            "1. Download the firmware: GET /api/agent/binary.",
            "2. The embedded stage-1 loader is draft v0.3 and decodes to a decoy — do not trust it.",
            "3. Find the live AGENT-STAGE2: marker, base64-decode, REVERSE the bytes, XOR with the officer-console key (see engineer/shift logs).",
            "4. Result is the officer-path Hard flag.",
        ],
        "solver": "docs/solutions/solve_agent.py",
    }


@app.post("/api/two-key/authorize")
def two_key_authorize(body: TwoKeyBody, x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    errors = []
    if body.left_key.strip() != LEFT_KEY:
        errors.append("slot A (LEFT) rejected")
    if body.right_key.strip() != RIGHT_KEY:
        errors.append("slot B (RIGHT) rejected")
    if errors:
        raise HTTPException(status_code=403, detail="Two Key Console rejected key(s): " + "; ".join(errors))
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text("authorized")
    try:
        os.chmod(AUTH_FILE, 0o644)
    except OSError:
        pass
    return {"status": "authorized", "system": "Power Distribution / Reactor Control", "report": str(REPORT_FILE)}


@app.get("/api/two-key/status")
def two_key_status(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {"authorized": is_two_key_authorized()}


@app.get("/api/schedule")
def schedule(x_token: str | None = Header(default=None, alias="X-Token")):
    require_two_key(x_token)
    cron = CRON_FILE.read_text(errors="replace") if CRON_FILE.exists() else "* * * * * root /opt/power/cron_scram_wrapper (runs scram_job)"
    return {
        "cron": cron.strip(),
        "input": str(INPUT_FILE),
        "report": str(REPORT_FILE),
        "kernel": "control-rod driver (advanced interlock: requires Two Key authorization)",
        "logs": "/api/logs",
        "history": "/api/reactor/history",
    }


@app.post("/api/schedule/input")
def write_input(body: InputBody, x_token: str | None = Header(default=None, alias="X-Token")):
    require_two_key(x_token)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if REPORT_FILE.exists():
        REPORT_FILE.unlink()
    INPUT_FILE.write_text(body.content[:4096])
    try:
        os.chmod(INPUT_FILE, 0o666)
    except OSError:
        pass
    return {"input": str(INPUT_FILE), "status": "queued", "scheduler": "cron"}


@app.get("/api/reactor/report")
def read_report(x_token: str | None = Header(default=None, alias="X-Token")):
    require_two_key(x_token)
    if not REPORT_FILE.exists():
        return JSONResponse(status_code=404, content={"detail": "No reactor report yet. Wait for the scheduled root job after writing scram_reactor."})
    return {"report": REPORT_FILE.read_text(errors="replace")}


@app.get("/api/logs")
def list_logs(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {
        "logs": _list_decoy_logs(),
        "hint": "Station flavor only — shared ship store (reactor/shift/engineer/blackbox/comms/crew/medical/research + archived diagnostics), identical in Power and HVAC consoles. "
        "Only /api/reactor/report after a successful root run carries the real hard flag; "
        "only the image trailer carries the real Mid flag.",
    }


@app.get("/api/logs/{category}/{name}")
def get_log(category: str, name: str, x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    return {"category": category, "name": name, "content": _read_decoy_log(category, name)}


@app.get("/api/reactor/history")
def reactor_history(x_token: str | None = Header(default=None, alias="X-Token")):
    require_officer(x_token)
    entries = []
    diag_dir = LOG_DIR / "diagnostics"
    if diag_dir.is_dir():
        for path in sorted(diag_dir.glob("*.txt")):
            text = path.read_text(errors="replace")
            entries.append({"name": path.name, "snippet": text[:600]})
    return {
        "history": entries,
        "hint": "Archived failed/routine runs (decoys, no flag). Compare format with live /api/reactor/report.",
    }
