#!/usr/bin/env python3
"""
My route's web surface (AEROSPACE COMMAND).

Two public-facing parts + the authenticated portal:

  /                      NETWORK OPERATIONS briefing / dispatch page. This is
                         where the shared hub's "Network" team tile lands. It
                         frames the mission and HANDS OVER the packet capture
                         (the start of the route). Public, no login -- you need
                         the capture to get a credential in the first place.
  /download/...pcap      serves the intercepted capture.
  /login                 OPERATIONS RECORDS PORTAL login (use the sniffed creds).
  /console, /document/<id>   the portal itself -- horizontal PE via IDOR.

Renamed from "Operator Console" to "Operations Records Portal" so it isn't
confused with the shared operator dashboard the SQLi lands on.

The vulnerability is still one missing line: the ownership check in
serve_document(), left commented so I can point at it in the demo.
"""
import os
import sys

from flask import (Flask, redirect, render_template_string, request,
                   send_file, session, url_for)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
import aerospace  # noqa: E402

app = Flask(__name__)
app.secret_key = "acc-records-portal-demo-key"  # demo only; not part of the game

# ---- locate the capture to hand out (works in Docker and when run locally) ----
def _find_pcap():
    here = os.path.dirname(__file__)
    for p in (os.environ.get("PCAP_PATH", ""),
              os.path.join(here, "capture.pcap"),
              os.path.join(here, "..", "step1-packet-capture", "capture.pcap")):
        if p and os.path.exists(p):
            return os.path.abspath(p)
    return None

PCAP_PATH = _find_pcap()


def _find_notes():
    here = os.path.dirname(__file__)
    for p in (os.environ.get("NOTES_PATH", ""),
              os.path.join(here, "intercept-notes.txt"),
              os.path.join(here, "..", "step1-packet-capture", "intercept-notes.txt")):
        if p and os.path.exists(p):
            return os.path.abspath(p)
    return None

NOTES_PATH = _find_notes()

OPERATORS = {
    "k.reyes":   {"code": "R3yes!ops2027", "role": "FLIGHT OPS", "clearance": "TIER-2"},
    "m.okonkwo": {"code": "!not-sniffable", "role": "NETOPS",     "clearance": "TIER-2"},
    "a.vance":   {"code": "!not-sniffable", "role": "TELEMETRY",  "clearance": "TIER-2"},
}

# Per-stage flags (rotate via env). The NETWORK flag is shown on the portal
# dashboard once you log in with the sniffed credential (reward for the packet
# capture stage). The HORIZONTAL flag lives inside the config record you can only
# reach via the IDOR (reward for the horizontal-PE stage).
NETWORK_FLAG    = os.environ.get("NETWORK_FLAG",    "CITS3006{l4A5p3MGYr}")
HORIZONTAL_FLAG = os.environ.get("HORIZONTAL_FLAG", "CITS3006{2cXVYDsVXj}")

ROUTER_CONFIG_EXPORT = """\
! ==============================================================
!  ACC-RTR-01   //   NETWORK SEGMENT CONTROLLER
!  configuration export  (maintenance snapshot)
! ==============================================================
hostname             ACC-RTR-01
segment              warhead-bus/3
!
mgmt.telnet.enabled  = true
mgmt.telnet.port     = 23
mgmt.telnet.user     = support
mgmt.telnet.pass_enc = HDs2OWo0eSguKHtoaA==
mgmt.telnet.enc      = xor0x5a+base64
!
snmp.community       = ****redacted****
ntp.server           = 10.44.0.2
!  cross-team access token (horizontal): %s
! end of export
""" % HORIZONTAL_FLAG

# NOTE ON THE DESIGN: the player's OWN records (4021, 4022) are mundane and do
# NOT contain the pointer to the router config. The breadcrumb lives in a NEARBY
# record they do NOT own (4023), so they only find it by actually doing the IDOR
# (decode their id -> it's a number -> try the neighbours -> land on someone
# else's record). That record then names the far-off config record (48879).
DOCUMENTS = {
    4021: {"owner": "k.reyes", "cls": "INTERNAL", "title": "Shift handover log, Bay 3",
           "body": "Nominal shift. Coolant loop A back within tolerance at 0340Z.\n"
                   "Handover acknowledged by k.reyes."},
    4022: {"owner": "k.reyes", "cls": "INTERNAL", "title": "Telemetry export request",
           "body": "Raised request for 24h telemetry on segment warhead-bus/3.\n"
                   "Escalated to NetOps for the current device settings; awaiting\n"
                   "their export. Will follow up if it isn't filed by end of shift."},
    # ---- the breadcrumb: another operator's record, reached only via IDOR ----
    4023: {"owner": "m.okonkwo", "cls": "RESTRICTED", "title": "Re: segment router settings",
           "body": "Actioning the flight-ops telemetry request. The router's full\n"
                   "maintenance snapshot (device export) is on file under NetOps\n"
                   "record #48879. Settings can be pulled from there.\n"
                   "Reminder: that export is meant to stay NetOps-only."},
    4024: {"owner": "a.vance", "cls": "INTERNAL", "title": "Downlink schedule (wk 38)",
           "body": "Pass windows unchanged. See ops calendar."},
    4025: {"owner": "m.okonkwo", "cls": "RESTRICTED", "title": "Firewall change record",
           "body": "Opened tcp/23 from jump host to ACC-RTR-01 for maintenance.\n"
                   "NOTE: revert after window. (not reverted)"},
    4026: {"owner": "a.vance", "cls": "INTERNAL", "title": "Sensor calibration notes",
           "body": "Recalibrated strain gauges on pylon 2. Drift < 0.4%."},
    48879: {"owner": "m.okonkwo", "cls": "CONFIDENTIAL", "title": "Maintenance snapshot: device export",
            "body": ROUTER_CONFIG_EXPORT},
}


# Record IDs in the URL are the record number's decimal STRING, hex-encoded
# (e.g. 4021 -> "4021" -> bytes 34 30 32 31 -> "34303231").  So a player must
# hex-DECODE one of their own to learn the scheme, and hex-ENCODE the target
# number (48879, from the breadcrumb) to build its URL -- a real CyberChef
# From-Hex / To-Hex round trip, not a character nudge.
def enc_id(n: int) -> str:
    return str(n).encode().hex()


def dec_id(s: str):
    try:
        return int(bytes.fromhex(s).decode())
    except (ValueError, UnicodeDecodeError):
        return None


CSS = aerospace.css()


def page(title, inner):
    return render_template_string(
        """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title><style>{{css|safe}}</style></head>
<body>{{inner|safe}}</body></html>""",
        title=title, css=CSS, inner=inner)


# ============================================================ BRIEFING (route entry)
@app.route("/")
def briefing():
    dl = ('<a class="btn" style="display:inline-block;width:auto;padding:10px 18px" '
          'href="/download/intercepted-traffic.pcap">&#8681;&nbsp; intercepted-traffic.pcap</a>'
          if PCAP_PATH else
          '<span class="msg err">capture unavailable — check PCAP_PATH</span>')
    notes_dl = ('<a class="btn" style="display:inline-block;width:auto;padding:10px 18px;'
                'margin-left:8px;background:transparent;color:var(--text);'
                'border:1px solid var(--line)" '
                'href="/download/intercept-notes.txt">&#8681;&nbsp; intercept-notes.txt</a>'
                if NOTES_PATH else '')
    inner = f'<div class="wrap">' + aerospace.topbar("AEROSPACE COMMAND", "Network Operations") + f"""
<div class="panel" style="margin-bottom:18px">
  <div class="phead"><span>Segment warhead-bus/3</span>
       <span style="color:var(--alert)">&#9888; SEGMENT: ARMED</span></div>
  <div class="pbody">
    <p style="line-height:1.7;color:var(--text);margin:0 0 14px">
      This segment is controlled by network gear you don't hold credentials for
      yet. Recon intercepted an operator's session on the ops network and saved
      it below. Pull what you need out of that traffic, use it to reach the
      operations portal, and work inward to the <b>segment router</b>. Compromise
      it to recover this segment's disarm code.
    </p>
  </div>
</div>

<div class="panel" style="margin-bottom:18px">
  <div class="phead"><span>Intercepted Capture</span><span>evidence</span></div>
  <div class="pbody">
    {dl}
    {notes_dl}
    <div class="note">A packet capture (.pcap) pulled off the ops network. Recon left
    their capture-review notes alongside it (<b>intercept-notes.txt</b>); worth a read
    before you start.</div>
  </div>
</div>

<a class="btn" href="/login" style="display:block;text-align:center">ACCESS OPERATIONS PORTAL &rarr;</a>
{aerospace.footer("NET-DISPATCH")}</div>"""
    return page("Aerospace Command // Network Operations", inner)


@app.route("/download/intercepted-traffic.pcap")
def download_pcap():
    if not PCAP_PATH:
        return "capture unavailable", 404
    return send_file(PCAP_PATH, as_attachment=True,
                     download_name="intercepted-traffic.pcap",
                     mimetype="application/vnd.tcpdump.pcap")


@app.route("/download/intercept-notes.txt")
def download_notes():
    if not NOTES_PATH:
        return "notes unavailable", 404
    return send_file(NOTES_PATH, as_attachment=True,
                     download_name="intercept-notes.txt",
                     mimetype="text/plain")


# ============================================================ PORTAL LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("op"):
        return redirect(url_for("dashboard"))
    msg = ""
    if request.method == "POST":
        op = (request.form.get("operator") or "").strip()
        code = request.form.get("code") or ""
        rec = OPERATORS.get(op)
        if rec and code == rec["code"]:
            session["op"] = op
            return redirect(url_for("dashboard"))
        msg = '<div class="msg err">ACCESS DENIED: INVALID OPERATOR ID OR ACCESS CODE</div>'
    inner = aerospace.jet_svg() + f"""
<div class="auth">
  <div class="card">
    <div class="kicker">Aerospace Command</div>
    <h1>SECURE<br>ACCESS</h1>
    <div class="tagline">Operations Records Portal</div>
    {msg}
    <form method="post" action="/login">
      <div class="field">
        <label>Operator ID</label>
        <input type="text" name="operator" placeholder="Enter operator ID"
               autocomplete="off" spellcheck="false" autofocus>
      </div>
      <div class="field">
        <label>Access Code</label>
        <input type="password" name="code" placeholder="Enter access code" autocomplete="off">
      </div>
      <button type="submit">Authenticate</button>
    </form>
    <div class="statusline">
      System status: <b>Online</b><br>
      Clearance system: <b>Active</b>
    </div>
    <div style="margin-top:14px"><a href="/" class="label">&#8592; BACK TO BRIEFING</a></div>
  </div>
</div>"""
    return page("Aerospace Command // Secure Access", inner)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/console")
def dashboard():
    op = session.get("op")
    if not op:
        return redirect(url_for("login"))
    rec = OPERATORS[op]
    mine = [(i, d) for i, d in sorted(DOCUMENTS.items()) if d["owner"] == op]
    rows = ""
    for i, d in mine:
        rows += f"""
<tr>
  <td class="mono"><a href="/document/{enc_id(i)}">{enc_id(i)}</a></td>
  <td>{d['title']}</td>
  <td><span class="pill">{d['cls']}</span></td>
  <td><span class="pill you">YOU</span></td>
</tr>"""
    inner = f'<div class="wrap">' + aerospace.topbar("AEROSPACE COMMAND", "Operations Records Portal") + f"""
<div class="panel" style="margin-bottom:18px">
  <div class="phead"><span>Session</span><span>{op}</span></div>
  <div class="pbody">
    <table>
      <tr><td class="label">Operator</td><td class="val">{op}</td>
          <td class="label">Role</td><td class="val">{rec['role']}</td></tr>
      <tr><td class="label">Clearance</td><td class="val">{rec['clearance']}</td>
          <td class="label">Segment</td><td class="val">warhead-bus/3</td></tr>
    </table>
    <div class="note" style="margin-top:12px">Recovered-access confirmation
    (packet-capture stage flag): <span class="mono">{NETWORK_FLAG}</span></div>
  </div>
</div>

<div class="panel">
  <div class="phead"><span>Document Records</span><span>Access scoped to your clearance</span></div>
  <div class="pbody" style="padding:0">
    <table>
      <tr><th>RECORD</th><th>TITLE</th><th>CLASSIFICATION</th><th>OWNER</th></tr>
      {rows}
    </table>
  </div>
  <div class="pbody" style="padding-top:0">
    <div class="note">Records are addressed individually at /document/&lt;ref&gt;.
    The ref is an encoded form of the internal record number. Your clearance sets
    which records are listed for you here.</div>
  </div>
</div>
<div style="margin-top:16px"><a href="/logout" class="label">&#8592; END SESSION</a></div>
{aerospace.footer("OPS-RECORDS-1")}</div>"""
    return page("Aerospace Command // Operations Records Portal", inner)


@app.route("/document/<doc_enc>")
def serve_document(doc_enc):
    op = session.get("op")
    if not op:
        return redirect(url_for("login"))

    # the encoded id is the only 'protection' -- and encoding isn't authorization
    doc_id = dec_id(doc_enc)
    doc = DOCUMENTS.get(doc_id) if doc_id is not None else None
    if not doc:
        inner = f'<div class="wrap">' + aerospace.topbar("AEROSPACE COMMAND", "Operations Records Portal") + f"""
<div class="panel"><div class="phead"><span>Record {doc_enc}</span><span>NOT FOUND</span></div>
<div class="pbody"><div class="msg err">NO RECORD {doc_enc} ON FILE</div>
<a href="/console" class="label">&#8592; BACK TO PORTAL</a></div></div></div>"""
        return page("Aerospace Command // Record", inner), 404

    # --- THE BUG (horizontal PE) ---------------------------------------------
    # No check that this record belongs to the logged-in operator. The fix would
    # be right here, deliberately disabled:
    #
    #     if doc["owner"] != op:
    #         return "403 FORBIDDEN — NOT YOUR RECORD", 403
    #
    # Missing -> any authenticated operator can read ANY record by id,
    # including m.okonkwo's device export at record 48879.
    # -------------------------------------------------------------------------

    yours = doc["owner"] == op
    owner_pill = '<span class="pill you">YOU</span>' if yours else f'<span class="pill">{doc["owner"]}</span>'
    inner = f'<div class="wrap">' + aerospace.topbar("AEROSPACE COMMAND", "Operations Records Portal") + f"""
<div class="panel">
  <div class="phead"><span>Record {doc_enc}</span><span>{doc['cls']}</span></div>
  <div class="pbody">
    <table style="margin-bottom:16px">
      <tr><td class="label">Title</td><td class="val">{doc['title']}</td></tr>
      <tr><td class="label">Owner</td><td>{owner_pill}</td></tr>
    </table>
    <pre class="readout">{doc['body']}</pre>
  </div>
</div>
<div style="margin-top:16px"><a href="/console" class="label">&#8592; BACK TO PORTAL</a></div>
{aerospace.footer("OPS-RECORDS-1")}</div>"""
    return page(f"Aerospace Command // Record {doc_enc}", inner)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8090"))
    app.run(host="0.0.0.0", port=port)
