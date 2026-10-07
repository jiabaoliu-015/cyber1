from flask import Flask, render_template, request, redirect, session, make_response, jsonify, url_for
from urllib.parse import quote, unquote, urlparse
import sqlite3
import os
import base64
import json
import secrets
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me-in-production")

DB_NAME = "database.db"

def run_query(query):
    """Runs whatever query text it's given. Shared, intentionally
    vulnerable execution path — reachable from either /login/guest or
    /login/operator whenever a ?query= parameter is present."""
    print("\n--- SQL QUERY ---")
    print(query)
    print("-----------------\n")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        print("DATABASE RESULT:", user)
    except sqlite3.Error as error:
        print("SQL Error:", error)
        user = None
    conn.close()
    return user


def build_query(username, password):
    return f"SELECT username, role, clearance FROM users WHERE username = '{username}' AND password = '{password}'"


@app.route("/")
def home():
    return render_template("portal.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if not session.get("stage_one_complete"):
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    query = f"""
        SELECT username, role, clearance
        FROM users
        WHERE username = '{username}' AND password = '{password}'
    """

    print("\n--- SQL QUERY ---")
    print(query)
    print("-----------------\n")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        print("DATABASE RESULT:", user)
    except sqlite3.Error as error:
        print("SQL Error:", error)
        user = None

    conn.close()

    if user:
        session["stage_two_complete"] = True
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("stage_two_complete"):
        return redirect("/")
    return render_template("dashboard.html")

def handle_reflected_query():
    query_param = request.args.get("query")

    if not query_param:
        return None
    
    query = unquote(query_param)
    user = run_query(query)
    if user and user[0] == "guest":
        return _maintenance_page()

    if user:
        session["stage_one_complete"] = True
        return redirect("/login")
    return render_template(
        "guest_login.html",
        action_url="/login/guest"
    )


@app.route("/login/guest", methods=["GET", "POST"])
def login_guest():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        query = build_query(username, password)
        return redirect(f"/login/guest?query={quote(query)}")

    reflected = handle_reflected_query()
    if reflected is not None:
        return reflected
    return render_template("guest_login.html", action_url="/login/guest")


@app.route("/login/operator", methods=["GET", "POST"])
def login_operator():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, role, clearance FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            return _granted_page(user)
        return render_template(
            "login.html",
            action_url="/login"
        )

    reflected = handle_reflected_query()
    if reflected is not None:
        return reflected
    return render_template("operator_login.html", action_url="/login/operator")


def _granted_page(user):
    is_escalation = user[0] != "guest"
    handoff = """
        <br>
        <p style="color:#9fe0b8; font-size: 12px; letter-spacing:1px;">STAGE ONE COMPLETE.</p>
        <a href="/login" style="color:#d9dee3; text-decoration:underline;">PROCEED TO SECURE OPERATOR TERMINAL →</a>
    """ if is_escalation else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Access Granted</title>
        <style>
            body {{ background: #05070a; color: white; font-family: Arial, sans-serif; text-align: center; padding-top: 100px; }}
            .box {{ display: inline-block; padding: 40px; background: #0d1117; border: 1px solid #444; }}
            h1 {{ letter-spacing: 3px; }}
            p {{ color: #aeb7c0; }}
            a {{ color: white; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ACCESS GRANTED</h1>
            <p>Welcome, {user[0]}</p>
            <p>Role: {user[1]}</p>
            <p>Clearance: {user[2]}</p>
            {handoff}
            <br><br>
            <a href="/">Return to Login</a>
        </div>
    </body>
    </html>
    """


def _maintenance_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Access Granted</title>
        <style>
            body { background: #05070a; color: white; font-family: Arial, sans-serif; text-align: center; padding-top: 100px; }
            .box { display: inline-block; padding: 40px; background: #0d1117; border: 1px solid #444; }
            h1 { letter-spacing: 3px; }
            p { color: #aeb7c0; }
            a { color: white; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>ACCESS GRANTED</h1>
            <p>Welcome, guest</p>
            <br>
            <p style="color:#697581; font-size: 12px; letter-spacing:1px;">
                SYSTEM CURRENTLY UNDER MAINTENANCE.<br>
                Guest-tier systems are temporarily unavailable.
            </p>
            <br>
            <a href="/">Return to Login</a>
        </div>
    </body>
    </html>
    """


@app.route("/login/team-alpha")
def team_alpha():
    return render_template(
        "branch1_01.html"
    )

ALPHA_VAULT_PASSWORD = os.environ.get("ALPHA_VAULT_PASSWORD", "AS!@DJshjdb@#aksjA^&%SJDBka*sbdjkas")

@app.route("/login/team-alpha/vault", methods=["GET", "POST"])
def team_alpha_vault():
    if request.method == "POST":
        supplied = request.form.get("password", "")
        if secrets.compare_digest(supplied, ALPHA_VAULT_PASSWORD):
            session["alpha_vault_unlocked"] = True
            return redirect(url_for("team_alpha_vault"))
        return render_template(
            "alpha_branch_vaultRE.html",
            unlocked=False,
            error="ACCESS DENIED — INCORRECT PASSPHRASE."
        )

    return render_template(
        "alpha_branch_vaultRE.html",
        unlocked=session.get("alpha_vault_unlocked", False),
        error=None
    )

BRAVO_ACCOUNTS = {
    "castillo": {
        "name": "R. Castillo",
        "notes": [
            "FLAG{1*8ja&^@IHj}",
            "Approved fuel allocation for Bravo flight line, Q3.",
            "Reminder: J. Okafor still hasn't submitted the maintenance sign-off from last week.",
            "I typed something somewhere in the browser and somehow my account got changed to J. Okafor. Remember to tell IT"
        ]
    },
    "okafor": {
        "name": "J. Okafor",
        "notes": [
            "FLAG{U1H!@SDBAI}",
            "Maintenance sign-off attached separately — sent it to the wrong inbox twice, sorry.",
            "Note to self: stop leaving my session logged in on the shared terminal.",
            "SIGN-IN DETAILS — username: jsmith | password: warehouse#123"
        ]
    }
}

BRAVO_VOSS_NOTES = [
    {
        "title": "IT — session behavior",
        "text": 'Noticed the "current level" shown up top is just... whatever the session says it is? Nobody\'s ever explained what actually decides that or where it\'s checked.'
    },
    {
        "title": "re: console access last week",
        "text": "Had the technician over to look at my terminal — he was messing with something in the Application and somehow ended up logged into R. Castillo's account. Meant to report it, kept forgetting."
    },
    {
        "title": "reminder",
        "text": "Team lunch moved to Friday. Bring your own badge this time, front desk ran out of visitor passes again."
    },
    {
        "title": "reminder",
        "text": "Printer on the 3rd floor is out of toner. Already submitted a ticket, don't submit a second one."
    }
]


def _bravo_b64url_encode(value):
    raw = json.dumps(value, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _bravo_b64url_decode(segment):
    padded = segment + ("=" * (-len(segment) % 4))
    raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    return json.loads(raw.decode("utf-8"))


def make_bravo_token(user, level):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user": user,
        "level": level,
        "exp": int(time.time() * 1000) + (24 * 60 * 60 * 1000)
    }

    fake_signature = secrets.token_hex(22)[:43]

    return (
        f"{_bravo_b64url_encode(header)}."
        f"{_bravo_b64url_encode(payload)}."
        f"{fake_signature}"
    )


def read_bravo_token():
    token = request.cookies.get("bravo_token")
    if not token:
        return None

    parts = token.split(".")
    if len(parts) != 3:
        return None

    try:
        payload = _bravo_b64url_decode(parts[1])

        if payload.get("exp") and payload["exp"] < int(time.time() * 1000):
            return None

        return payload
    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def _bravo_context(view="selector", error_castillo=None, error_okafor=None):
    payload = read_bravo_token()
    level = payload.get("level") if payload else None

    active_account = request.cookies.get("bravo_account")
    if not active_account and payload:
        active_account = payload.get("user")

    account = None
    if view == "account" and active_account in BRAVO_ACCOUNTS:
        account = BRAVO_ACCOUNTS[active_account]

    raw_token = request.cookies.get("bravo_token")
    token_parts = raw_token.split(".") if raw_token and raw_token.count(".") == 2 else None

    return {
        "view": view,
        "level": level,
        "current_id": active_account,
        "account": account,
        "voss_notes": BRAVO_VOSS_NOTES,
        "raw_token": raw_token,
        "token_parts": token_parts,
        "error_castillo": error_castillo,
        "error_okafor": error_okafor,
    }


@app.route("/login/team-bravo")
def team_bravo():
    if not session.get("stage_two_complete"):
        return redirect("/")

    return render_template(
        "branch2_01_M.html",
        **_bravo_context(view="selector")
    )


@app.route("/login/team-bravo/voss")
def team_bravo_voss():
    if not session.get("stage_two_complete"):
        return redirect("/")

    response = make_response(
        redirect(url_for("team_bravo_dashboard"))
    )
    response.set_cookie(
        "bravo_token",
        make_bravo_token("voss", "admin-lvl1"),
        max_age=24 * 60 * 60,
        path="/",
        samesite="Lax",
        httponly=False,
    )
    response.set_cookie(
        "bravo_account",
        "voss",
        max_age=24 * 60 * 60,
        path="/",
        samesite="Lax",
        httponly=False,
    )
    return response


@app.route("/login/team-bravo/dashboard")
def team_bravo_dashboard():
    if not session.get("stage_two_complete"):
        return redirect("/")

    payload = read_bravo_token()
    if not payload:
        return redirect(url_for("team_bravo"))

    return render_template(
        "branch2_01_M.html",
        **_bravo_context(view="dashboard")
    )


@app.route("/login/team-bravo/castillo")
def team_bravo_castillo():
    if not session.get("stage_two_complete"):
        return redirect("/")

    payload = read_bravo_token()

    if not payload or payload.get("level") != "admin-lvl2":
        return render_template(
            "branch2_01_M.html",
            **_bravo_context(
                view="selector",
                error_castillo="ACCESS DENIED — ADMIN-LVL2 REQUIRED."
            )
        )

    response = make_response(
        redirect(url_for("team_bravo_account"))
    )
    response.set_cookie(
        "bravo_account",
        "castillo",
        max_age=24 * 60 * 60,
        path="/",
        samesite="Lax",
        httponly=False,
    )
    return response


@app.route("/login/team-bravo/okafor")
def team_bravo_okafor():
    if not session.get("stage_two_complete"):
        return redirect("/")

    return render_template(
        "branch2_01_M.html",
        **_bravo_context(
            view="selector",
            error_okafor="ACCOUNT NOT SIGNED IN."
        )
    )


@app.route("/login/team-bravo/account")
def team_bravo_account():
    if not session.get("stage_two_complete"):
        return redirect("/")

    payload = read_bravo_token()
    if not payload or payload.get("level") != "admin-lvl2":
        return redirect(url_for("team_bravo"))

    account_id = request.cookies.get("bravo_account")
    if account_id not in BRAVO_ACCOUNTS:
        return redirect(url_for("team_bravo"))

    return render_template(
        "branch2_01_M.html",
        **_bravo_context(view="account")
    )


@app.route("/login/team-bravo/api/switch-account", methods=["POST"])
def team_bravo_switch_account():
    if not session.get("stage_two_complete"):
        return jsonify({"ok": False, "error": "Stage two required."}), 403

    payload = read_bravo_token()
    if not payload or payload.get("level") != "admin-lvl2":
        return jsonify({"ok": False, "error": "ADMIN-LVL2 required."}), 403

    data = request.get_json(silent=True) or {}
    account_id = str(data.get("id", "")).lower().strip()

    if account_id not in BRAVO_ACCOUNTS:
        return jsonify({"ok": False, "error": "No such account."}), 404

    response = make_response(jsonify({"ok": True, "account": account_id}))
    response.set_cookie(
        "bravo_account",
        account_id,
        max_age=24 * 60 * 60,
        path="/",
        samesite="Lax",
        httponly=False,
    )
    return response


@app.route("/login/team-charlie")
def team_charlie():
    return redirect(f"http://{urlparse(request.base_url).hostname}:8090/")


@app.route("/reset-all")
def reset_all():
    session.clear()

    response = redirect("/")

    response.delete_cookie("bravo_token", path="/")
    response.delete_cookie("bravo_account", path="/")

    response.delete_cookie("challenge_token", path="/")

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=False, use_reloader=False)
