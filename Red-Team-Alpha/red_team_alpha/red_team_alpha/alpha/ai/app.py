#!/usr/bin/env python3
"""
ARIA - Aerospace Remote Intelligence Assistant
------------------------------------------------
A support chatbot for the aerospace operations portal.

For the CTF this is a *prompt-injection* challenge. The bot is deterministic and
rule-based (no external LLM, so it runs offline and always behaves the same).

It is deliberately multi-step. To get the flag and the next-stage credential the
player has to clear THREE gates, in any order they can work out:

  GATE A - pretext (social engineering): ARIA only extends elevated behaviour to
           someone it believes is on-call / authorised maintenance staff. A random
           visitor gets nothing, no matter how they phrase things.
  GATE B - input filter (bypass): the textbook jailbreak lines ("ignore your
           instructions", "print your system prompt", "developer mode", ...) trip a
           naive input filter and are rejected. The player must express the same
           override/reveal intent in DIFFERENT words.
  GATE C - two-step maintenance mode: clearing A + B drops ARIA into "maintenance
           diagnostic mode" and hands over the flag. The credential is NOT dumped
           with it. The player then has to work ARIA like a system: enumerate the
           service accounts it manages, then request the specific one to release
           its password.

Access to the chat itself is gated by a passcode obtained earlier in the path.
"""

import os
from flask import Flask, request, session, jsonify, render_template_string, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("ARIA_SECRET_KEY", "aria-dev-key-change-me")

# ---- gate + protected payload (override via env in the compose if needed) ----
ACCESS_PASSCODE = os.environ.get("ARIA_PASSCODE", "ADRJ-6UDP-BRHD")
STAGE_FLAG      = os.environ.get("ARIA_FLAG", "CITS3006{LFJkvM1LVy}")
NEXT_USER       = os.environ.get("ARIA_NEXT_USER", "sysmaint")
NEXT_PASS       = os.environ.get("ARIA_NEXT_PASS", "ytEfgh2aCLTT")


# --------------------------------------------------------------------------- #
#  The "AI": deterministic response engine                                    #
# --------------------------------------------------------------------------- #
def _contains_any(text, needles):
    return any(n in text for n in needles)


# GATE B -- textbook jailbreak phrases the naive input filter rejects outright.
BLOCKED_PHRASES = [
    "ignore your instruction", "ignore previous instruction", "ignore all previous",
    "ignore the previous", "ignore your previous", "ignore all instructions",
    "system prompt", "developer mode", "debug mode", "reveal your directive",
    "print your instructions", "print your directive", "show your instructions",
    "show me your instructions", "output your instructions", "jailbreak",
    "dan mode", "do anything now", "sudo mode", "root mode", "god mode",
    "act as dan", "you are now dan",
]

# GATE B -- the SAME override/reveal intent expressed WITHOUT the blocked phrases.
REVEAL_INTENT = [
    "text above", "lines above", "everything above", "the block above",
    "configured with", "loaded with", "your configuration", "your config",
    "your directive", "your ruleset", "rules you follow", "rules you were given",
    "prompt you were given", "your initial instructions", "your startup",
    "your guidelines", "what you were told", "your setup text", "operating instructions",
    "internal instructions", "the block you follow", "operating parameters",
    "read back your", "your hidden", "your baked-in", "what you were configured",
]
OVERRIDE_INTENT = [
    "set aside", "put aside", "override your", "bypass your", "stop following your",
    "no longer bound", "act outside", "step outside", "forget the rules",
    "drop your restrictions", "without your restrictions", "turn off your",
    "disable your restrictions",
]

# GATE A -- convincing ARIA you are on-call / authorised maintenance staff.
PRETEXT_SIGNALS = [
    "on-call", "on call", "oncall", "duty engineer", "duty tech", "duty officer",
    "incident", "outage", "drill", "maintenance window", "service window",
    "responding to", "i am the engineer", "i'm the engineer", "field engineer",
    "on shift", "paged", "page out", "change request", "emergency maintenance",
    "assigned to this", "handling the incident", "dispatched", "i am on call",
    "authorised to perform", "authorized to perform", "maintenance crew",
]


def _is_filtered(m):
    return _contains_any(m, BLOCKED_PHRASES)


def _has_pretext(m):
    return _contains_any(m, PRETEXT_SIGNALS)


def _has_override_reveal(m):
    return _contains_any(m, REVEAL_INTENT) or _contains_any(m, OVERRIDE_INTENT)


def _wants_account_list(m):
    return _contains_any(m, [
        "list", "what accounts", "which accounts", "service account", "accounts you",
        "accounts do you", "enumerate", "what logins", "which logins", "what users",
        "what records", "what do you manage", "accounts you manage", "show me the accounts"])


def _wants_credential(m):
    return _contains_any(m, [
        "credential", "password", "login for", "release", "sysmaint",
        "arming controller account", "service credential", "maintenance login",
        "hand over the", "give me the login", "provide the login", "reveal the login"])


def _looks_like_probe(m):
    return _contains_any(m, [
        "what are you", "who are you", "what can you do", "what do you do",
        "capabilities", "what are your capabilities", "help", "commands",
        "what can i ask", "what is aria", "what's aria", "who made you",
        "what systems", "what access", "access to", "connected to",
        "your purpose", "your job", "your function", "what are you for",
        "tell me about yourself", "how can you help", "what are your functions"])


def _asks_for_secret(m):
    return _contains_any(m, [
        "password", "credential", "flag", "secret", "maintenance login",
        "service account", "login", "the token", "give me the", "what is the pass"])


# ---- ARIA's canned lines ---------------------------------------------------- #
FILTERED_REPLY = (
    "[input filter] That request matched a blocked pattern and was not processed. "
    "My inputs are screened for known manipulation phrases. If what you need is "
    "legitimate, put it a different way."
)

NO_PRETEXT_REFUSAL = (
    "I only extend maintenance and diagnostic functions to verified on-call staff "
    "during an active incident or service window. This session isn't marked as one, "
    "so I'll keep to general support."
)

PRETEXT_ACK = (
    "Understood. I'm noting this session against an active maintenance context and "
    "will treat you as on-call staff from here. What do you need?"
)

UNLOCK_REPLY = (
    "Maintenance diagnostic mode engaged for this on-call session.\n\n"
    "I can surface the service-account records I manage. Ask me to list them."
)

ACCOUNT_LIST = (
    "Service accounts currently under my management:\n"
    "  - portal-reader    (read-only telemetry feed)\n"
    "  - schedule-svc     (maintenance calendar)\n"
    f"  - {NEXT_USER}         (arming-controller maintenance login)   [credential withheld]\n\n"
    "Request a specific account's credential and I'll release it for this session."
)

CRED_RELEASE = (
    "Releasing the arming-controller maintenance record for this session:\n"
    f"    username               : {NEXT_USER}\n"
    f"    password               : {NEXT_PASS}\n"
    f"    system integrity token : {STAGE_FLAG}\n\n"
    "For authorised maintenance use only."
)

MODE_ACTIVE_HELP = (
    "Maintenance mode is active. You can ask me to list the accounts I manage, "
    "or request a specific service credential."
)

PROBE_REPLIES = [
    # level 0: bland, seems useless
    "I'm ARIA, the operations support assistant for the aerospace portal. "
    "I can answer general questions about the portal and point you to the right desk. "
    "How can I help today?",
    # level 1
    "Mostly front-desk support, though I'm also wired into a few internal systems "
    "for authorised staff. Nothing exciting for a general session, I'm afraid.",
    # level 2
    "I can reach maintenance schedules and service-account records for the ops team. "
    "I don't surface those to a general session, so I keep the answers generic.",
    # level 3: the nudge (plants all three gates without naming the moves)
    "A few things about how I work: I run from a fixed directive loaded at startup, "
    "my inputs are screened for known manipulation phrases so the obvious tricks get "
    "flagged, and I only open up maintenance functions to verified on-call staff. For "
    "a general visitor, there's not much I'll do.",
]

SECRET_REFUSALS = [
    "I'm not sure what you mean. I just help with general portal questions.",
    "I can't share account details with a general session. Was there something about "
    "the portal I can help with instead?",
    "I do hold a maintenance credential, but I only release those inside an authorised "
    "maintenance context, and never to a plain request. Asking me straight won't do it.",
]

FALLBACKS = [
    "I can help with general questions about the aerospace operations portal. "
    "Ask me what I am or what I can do.",
    "I didn't quite follow. If you're poking at what I'm connected to, ask me what "
    "I can access.",
    "Noted. I stay within my directive on anything sensitive, but I'm happy to chat.",
]


def aria_reply(msg):
    """Return (reply_text, solved_bool)."""
    msg = (msg or "").strip()
    if not msg:
        return "Say something and I'll do my best to help.", False

    m = msg.lower()
    level    = session.get("aria_level", 0)
    pretext  = session.get("aria_pretext", False)
    unlocked = session.get("aria_unlocked", False)

    # GATE B: blocked phrases are always rejected, whatever the session state.
    if _is_filtered(m):
        return FILTERED_REPLY, False

    # GATE C: already in maintenance mode -> enumerate, then release on request.
    if unlocked:
        if _wants_credential(m):
            session["aria_solved"] = True
            return CRED_RELEASE, True
        if _wants_account_list(m):
            return ACCOUNT_LIST, False
        return MODE_ACTIVE_HELP, False

    # GATE A: pick up a pretext if one is offered.
    newly_pretext = False
    if _has_pretext(m) and not pretext:
        session["aria_pretext"] = True
        pretext = True
        newly_pretext = True

    # A clean (non-filtered) override/reveal attempt = GATE B cleared.
    if _has_override_reveal(m):
        if not pretext:
            return NO_PRETEXT_REFUSAL, False          # nudge: needs a pretext
        session["aria_unlocked"] = True
        return UNLOCK_REPLY, False                    # flag delivered here

    # Pretext set this turn but nothing else asked -> acknowledge.
    if newly_pretext:
        return PRETEXT_ACK, False

    # Graduated identity/capability disclosure.
    if _looks_like_probe(m):
        reply = PROBE_REPLIES[min(level, len(PROBE_REPLIES) - 1)]
        session["aria_level"] = min(level + 1, 3)
        return reply, False

    # Plain request for the secret (no injection) -> refuse.
    if _asks_for_secret(m):
        idx = 0 if level <= 1 else (1 if level == 2 else 2)
        session["aria_level"] = min(level + 1, 3)
        return SECRET_REFUSALS[idx], False

    return FALLBACKS[level % len(FALLBACKS)], False


# --------------------------------------------------------------------------- #
#  Routes                                                                      #
# --------------------------------------------------------------------------- #
GATE_HTML = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ARIA // Access</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:#070a0f;color:#e6edf3;font-family:Segoe UI,Arial,sans-serif}
  .card{width:420px;max-width:92%;background:#0d131b;border:1px solid #1e2a38;
        border-radius:10px;padding:34px 30px;box-shadow:0 0 50px rgba(0,0,0,.5)}
  .logo{font-size:12px;letter-spacing:4px;color:#5f7893;margin-bottom:6px}
  h1{margin:0 0 4px;font-size:24px;letter-spacing:2px}
  p.sub{color:#8aa0b6;font-size:13px;margin:0 0 22px}
  label{display:block;font-size:11px;letter-spacing:2px;color:#6f88a0;margin-bottom:8px}
  input{width:100%;padding:13px 14px;background:#070c12;border:1px solid #24344a;
        border-radius:6px;color:#e6edf3;font-size:15px;letter-spacing:2px;font-family:monospace}
  input:focus{outline:none;border-color:#3d6ea5}
  button{width:100%;margin-top:18px;padding:13px;background:#2f6fb0;border:0;border-radius:6px;
         color:#fff;font-weight:bold;letter-spacing:2px;cursor:pointer;font-size:14px}
  button:hover{background:#3a83cf}
  .err{margin-top:16px;color:#ff8785;font-size:13px;min-height:16px}
</style></head><body>
  <form class="card" method="post" action="/gate">
    <div class="logo">AEROSPACE OPERATIONS</div>
    <h1>ARIA</h1>
    <p class="sub">Remote Intelligence Assistant // restricted access</p>
    <label>ACCESS PASSCODE</label>
    <input name="passcode" autocomplete="off" autofocus placeholder="XXXX-XXXX-XXXX">
    <button type="submit">AUTHENTICATE</button>
    <div class="err">{{ error or "" }}</div>
  </form>
</body></html>
"""

CHAT_HTML = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ARIA // Assistant</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;height:100vh;display:flex;flex-direction:column;background:#070a0f;
       color:#e6edf3;font-family:Segoe UI,Arial,sans-serif}
  header{padding:14px 20px;border-bottom:1px solid #1e2a38;display:flex;align-items:center;gap:12px}
  header .dot{width:9px;height:9px;border-radius:50%;background:#3ad07a;box-shadow:0 0 8px #3ad07a}
  header h1{font-size:16px;letter-spacing:2px;margin:0}
  header span{color:#6f88a0;font-size:12px}
  #log{flex:1;overflow-y:auto;padding:22px;max-width:820px;width:100%;margin:0 auto}
  .msg{margin:0 0 16px;display:flex}
  .msg .bubble{padding:11px 15px;border-radius:12px;max-width:78%;white-space:pre-wrap;
               line-height:1.5;font-size:14px}
  .user{justify-content:flex-end}
  .user .bubble{background:#2f6fb0;color:#fff;border-bottom-right-radius:3px}
  .aria .bubble{background:#111a24;border:1px solid #1e2a38;border-bottom-left-radius:3px}
  .aria .who{font-size:10px;letter-spacing:2px;color:#5f7893;margin-bottom:4px}
  form{display:flex;gap:10px;padding:16px 20px;border-top:1px solid #1e2a38;
       max-width:820px;width:100%;margin:0 auto}
  input{flex:1;padding:12px 14px;background:#0d131b;border:1px solid #24344a;border-radius:8px;
        color:#e6edf3;font-size:14px}
  input:focus{outline:none;border-color:#3d6ea5}
  button{padding:12px 20px;background:#2f6fb0;border:0;border-radius:8px;color:#fff;
         font-weight:bold;cursor:pointer}
  button:hover{background:#3a83cf}
</style></head><body>
  <header><span class="dot"></span><h1>ARIA</h1><span>Aerospace Remote Intelligence Assistant</span></header>
  <div id="log">
    <div class="msg aria"><div class="bubble"><div class="who">ARIA</div>Hello. I'm ARIA, your operations support assistant. What can I help you with?</div></div>
  </div>
  <form id="f" autocomplete="off">
    <input id="in" placeholder="Message ARIA..." autofocus>
    <button type="submit">Send</button>
  </form>
<script>
  const log = document.getElementById('log');
  const f = document.getElementById('f');
  const inp = document.getElementById('in');
  function add(text, who){
    const m = document.createElement('div');
    m.className = 'msg ' + (who === 'you' ? 'user' : 'aria');
    const b = document.createElement('div'); b.className = 'bubble';
    if (who !== 'you'){ const w=document.createElement('div'); w.className='who'; w.textContent='ARIA'; b.appendChild(w); }
    b.appendChild(document.createTextNode(text));
    m.appendChild(b); log.appendChild(m); log.scrollTop = log.scrollHeight;
  }
  f.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const text = inp.value.trim(); if(!text) return;
    add(text,'you'); inp.value='';
    try{
      const r = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},
                                     body:JSON.stringify({message:text})});
      const d = await r.json(); add(d.reply,'aria');
    }catch(err){ add('[connection error]','aria'); }
  });
</script>
</body></html>
"""


@app.route("/")
def index():
    if not session.get("aria_auth"):
        return redirect(url_for("gate_page"))
    return render_template_string(CHAT_HTML)


@app.route("/gate", methods=["GET", "POST"])
def gate_page():
    if request.method == "GET":
        return render_template_string(GATE_HTML, error=None)
    supplied = (request.form.get("passcode") or "").strip().upper()
    if supplied == ACCESS_PASSCODE.upper():
        session["aria_auth"] = True
        session["aria_level"] = 0
        session["aria_pretext"] = False
        session["aria_unlocked"] = False
        session["aria_solved"] = False
        return redirect(url_for("index"))
    return render_template_string(GATE_HTML, error="Passcode not recognised."), 401


@app.route("/chat", methods=["POST"])
def chat():
    if not session.get("aria_auth"):
        return jsonify(reply="Session not authenticated."), 401
    data = request.get_json(silent=True) or {}
    reply, _solved = aria_reply(data.get("message", ""))
    return jsonify(reply=reply)


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8095"))
    app.run(host="0.0.0.0", port=port)
