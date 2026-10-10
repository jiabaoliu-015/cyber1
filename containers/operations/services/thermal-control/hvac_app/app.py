"""HVAC lab: Thermal Regulation / HVAC Control pathway (flowchart spec).

Station: Erebus — Tallis Group crewed station, Callisto orbit, AI ORACLE,
last human contact 16 Sep 2026, ground-link blackout 20 Sep 2026 (shared canon with network-chain terminal
`erebus`; foothold accounts `gh0st` (Becker's backdoor) / `controlsvc`).
Crew (canon): Captain Jin Hong (j.hong, Alive), First Officer John Becker
(j.becker, Unaccounted for), Chief Engineer Hank Mercer (h.mercer, Deceased at
power — the engineer uid 1002 in this lab is his seat), Medical Officer Yara
Nassar (y.nassar, Missing — last badge-in medbay), Researcher Wu Yan (w.yan,
Deceased/Missing — research lab sealed from inside). No Tech 2nd class exists;
the duct-sitting fixation arc belongs to Becker (paranoid-and-right).

Horizontal priv (predictable tokens):
  Default-User (uid 1001) logs in, receives HVAC-1001-STAT.
  Engineer-User (uid 1002) token is sequential and predictable:
  HVAC-1002-STAT. Forging it yields engineer access. No brute force needed.

Vertical priv (scheduled task exploit):
  Engineer can write /var/run/hvac/input (via POST /api/schedule/input).
  Root cron `* * * * * root /opt/hvac/process_job run` trusts that input.
  Writing `run_diagnostic` makes the root job write the maintenance
  report containing the Mid flag. See docs/challenge_card.md and
  scripts/process_job (same logic, container-scoped).

Decoys (station flavor, no flag — shared with Power Distribution console):
  GET /api/logs, GET /api/logs/{category}/{name}, GET /api/maintenance/history
  serve data/crew_logs, data/shift_notes, data/engineer_logs, data/diagnostics,
  data/medical_logs, data/research_notes, data/reactor_logs,
  data/blackbox_logs, data/comms_logs. Same set is served by the Power
  console so both containers appear to share one ship log store.
   Erebus heat-wave arc: failing
   Thermal Regulation, strange behavior (First Officer Becker — see
   shift_notes/becker_unaccounted_058.txt), Medical Officer Nassar Missing from
   medbay (see medical_logs/nassar_last_badge_059.txt), weird warm object K-9.
  Archived reports share the maintenance-report format but carry no flag.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

RUN_DIR = Path(os.environ.get("HVAC_RUN_DIR", "/var/run/hvac"))
INPUT_FILE = RUN_DIR / "input"
REPORT_FILE = RUN_DIR / "maintenance_report.txt"
CRON_FILE = Path("/etc/cron.d/hvac-diagnostic")

# Station flavor / decoy logs. Resolved to service/data/ in repo or /app/data in container.
# Shared ship store: identical 9-category set is served by both HVAC and Power
# consoles so players see the same logs from either docker container.
_BASE_DIR = Path(__file__).resolve().parent.parent
_LOG_CANDIDATES = (_BASE_DIR / "data", Path("/app/data"))
LOG_DIR = next((p for p in _LOG_CANDIDATES if p.is_dir()), _BASE_DIR / "data")
ALLOWED_LOG_CATEGORIES = ("crew_logs", "shift_notes", "engineer_logs", "diagnostics", "medical_logs", "research_notes", "reactor_logs", "blackbox_logs", "comms_logs")

USERS = {"default": 1001, "engineer": 1002}


def token_for(username: str) -> str:
    return f"HVAC-{USERS[username]:04d}-STAT"


def user_for_token(token: str) -> str | None:
    for user in USERS:
        if token == token_for(user):
            return user
    return None


def require_user(token: str | None) -> str:
    user = user_for_token((token or "").strip())
    if not user:
        raise HTTPException(status_code=401, detail="Missing or invalid token. POST /login as default first.")
    return user


def require_engineer(token: str | None) -> str:
    user = require_user(token)
    if user != "engineer":
        raise HTTPException(
            status_code=403,
            detail="Engineer token required. Hint: tokens are predictable (HVAC-UID-STAT); engineer uid is 1002.",
        )
    return user


def _list_decoy_logs() -> dict:
    """Index station flavor logs (crew / shift / engineer / failed diagnostics)."""
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


app = FastAPI(title="HVAC Lab — Thermal Regulation")


class LoginBody(BaseModel):
    user: str = "default"


class InputBody(BaseModel):
    content: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "hvac-lab"}


@app.post("/login")
def login(body: LoginBody):
    if body.user != "default":
        raise HTTPException(status_code=401, detail="Only default login is exposed. Engineer token must be predicted.")
    return {"user": "default", "token": token_for("default"), "hint": "Engineer uid is 1002; token format HVAC-UID-STAT"}


@app.get("/api/users/me")
def me(x_token: str | None = Header(default=None, alias="X-Token")):
    user = require_user(x_token)
    return {"user": user, "token": token_for(user)}


@app.get("/api/hvac/status")
def hvac_status(x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    return {
        "system": "Thermal Regulation / HVAC Control",
        "mode": "auto",
        "supply_c": 21.5,
        "schedule": "* * * * * root /opt/hvac/process_job run",
        "input": str(INPUT_FILE),
        "report": str(REPORT_FILE),
        "logs": "/api/logs",
        "history": "/api/maintenance/history",
    }


@app.get("/api/schedule")
def schedule(x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    cron = CRON_FILE.read_text(errors="replace") if CRON_FILE.exists() else "* * * * * root /opt/hvac/process_job run"
    return {
        "cron": cron.strip(),
        "input": str(INPUT_FILE),
        "report": str(REPORT_FILE),
        "logs": "/api/logs",
        "history": "/api/maintenance/history",
    }


@app.post("/api/schedule/input")
def write_input(body: InputBody, x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    # Preserve the root-owned inode: engineer can write this input but cannot
    # create or replace files in the root-owned directory.
    with INPUT_FILE.open("w") as input_file:
        input_file.write(body.content[:4096])
    return {"input": str(INPUT_FILE), "status": "queued"}


@app.get("/api/maintenance/report")
def read_report(x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    if not REPORT_FILE.exists():
        return JSONResponse(
            status_code=404,
            content={"detail": "No maintenance report yet. The root scheduled job runs once per minute after POST run_diagnostic to /api/schedule/input."},
        )
    return {"report": REPORT_FILE.read_text(errors="replace")}


@app.get("/api/logs")
def list_logs(x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    return {
        "logs": _list_decoy_logs(),
        "hint": "Station flavor only — shared ship store (crew/shift/engineer/medical/research/reactor/blackbox/comms + archived diagnostics), identical in HVAC and Power consoles. "
        "Only /api/maintenance/report after a successful root run carries the real flag.",
    }


@app.get("/api/logs/{category}/{name}")
def get_log(category: str, name: str, x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    return {"category": category, "name": name, "content": _read_decoy_log(category, name)}


@app.get("/api/maintenance/history")
def maintenance_history(x_token: str | None = Header(default=None, alias="X-Token")):
    require_engineer(x_token)
    entries = []
    diag_dir = LOG_DIR / "diagnostics"
    if diag_dir.is_dir():
        for path in sorted(diag_dir.glob("*.txt")):
            text = path.read_text(errors="replace")
            entries.append({"name": path.name, "snippet": text[:600]})
    return {
        "history": entries,
        "hint": "Archived failed/routine runs (decoys, no flag). Compare format with live /api/maintenance/report.",
    }
