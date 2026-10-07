"""
Shared 'mission control' visual theme for my route's web front-ends.

I kept this in one place so the console login and the record pages all read like
one system (AEROSPACE COMMAND). Plain CSS, system font stack -- no web fonts, no
CDN -- so it renders identically inside the offline Docker network.

Look is matched to our team's login screen: near-black panels, a light/white
primary button, wide UPPERCASE labels, and a dark fighter-jet backdrop.
"""

THEME = {
    "bg": "#0a0b0d",
    "panel": "#0d0e11",
    "panel2": "#111317",
    "line": "#1b1e24",
    "line2": "#262a31",
    "text": "#c7ccd4",
    "muted": "#5b626c",
    "label": "#7c8590",
    "val": "#e9edf2",
    "amber": "#c9a227",
    "green": "#4bb37f",
    "alert": "#cf5340",
}


def css() -> str:
    t = THEME
    return f"""
:root {{
  --bg:{t['bg']}; --panel:{t['panel']}; --panel2:{t['panel2']};
  --line:{t['line']}; --line2:{t['line2']}; --text:{t['text']};
  --muted:{t['muted']}; --label:{t['label']}; --val:{t['val']};
  --amber:{t['amber']}; --green:{t['green']}; --alert:{t['alert']};
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; }}
body {{
  background:var(--bg);
  color:var(--text);
  font-family: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
  min-height:100vh; -webkit-font-smoothing:antialiased; letter-spacing:.2px;
}}
a {{ color:var(--amber); text-decoration:none; }}
.wrap {{ max-width:880px; margin:0 auto; padding:28px 20px 64px; position:relative; z-index:1; }}

/* top command bar (inside the app, after login) */
.topbar {{ display:flex; align-items:center; justify-content:space-between;
  border:1px solid var(--line); background:var(--panel); padding:12px 16px; margin-bottom:22px; }}
.brand {{ display:flex; align-items:baseline; gap:12px; }}
.brand .sys {{ color:var(--val); font-weight:600; letter-spacing:3px; font-size:13px; }}
.brand .sub {{ color:var(--label); font-size:10px; letter-spacing:2.5px; text-transform:uppercase; }}
.status {{ font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--label); }}
.status b {{ color:var(--green); letter-spacing:2px; }}
.dot {{ display:inline-block; width:7px; height:7px; border-radius:50%;
        background:var(--green); box-shadow:0 0 8px var(--green); margin-right:6px; }}

.label {{ color:var(--label); text-transform:uppercase; letter-spacing:2.5px; font-size:10px; }}
.val   {{ color:var(--val); }}

.panel {{ border:1px solid var(--line); background:var(--panel); }}
.panel .phead {{ border-bottom:1px solid var(--line); padding:10px 16px; color:var(--label);
  text-transform:uppercase; letter-spacing:2.5px; font-size:10px;
  display:flex; justify-content:space-between; align-items:center; }}
.panel .pbody {{ padding:20px 18px; }}

form .field {{ margin-bottom:16px; }}
form label {{ display:block; color:var(--label); text-transform:uppercase;
  letter-spacing:2.5px; font-size:10px; margin-bottom:8px; }}
input[type=text], input[type=password] {{
  width:100%; background:#08090b; border:1px solid var(--line2); color:var(--val);
  padding:12px 12px; font-family:inherit; font-size:13px; letter-spacing:1px; outline:none; }}
input::placeholder {{ color:#464c55; letter-spacing:.5px; }}
input:focus {{ border-color:#3a4048; }}

/* PRIMARY button = light/white filled, dark text (matches our login screen) */
button, .btn {{ width:100%; background:#e9edf2; border:1px solid #e9edf2; color:#0a0b0d;
  padding:12px 12px; font-family:inherit; font-size:11px; letter-spacing:3px;
  text-transform:uppercase; cursor:pointer; }}
button:hover, .btn:hover {{ background:#ffffff; border-color:#ffffff; }}

.msg {{ padding:9px 12px; font-size:12px; letter-spacing:.5px; margin-bottom:16px; }}
.msg.err {{ border:1px solid var(--alert); color:#e6a99f; background:rgba(207,83,64,.08); }}
.msg.ok  {{ border:1px solid var(--green); color:#9fe0c3; background:rgba(75,179,127,.08); }}

table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ text-align:left; color:var(--label); text-transform:uppercase; letter-spacing:2px;
  font-size:10px; font-weight:500; padding:9px 12px; border-bottom:1px solid var(--line); }}
td {{ padding:11px 12px; border-bottom:1px solid var(--line); color:var(--text); }}
tr:hover td {{ background:var(--panel2); }}
.mono {{ font-family:inherit; color:var(--val); }}
.pill {{ font-size:9px; letter-spacing:2px; text-transform:uppercase; padding:2px 7px;
  border:1px solid var(--line2); color:var(--muted); }}
.pill.you {{ border-color:var(--amber); color:var(--amber); }}

pre.readout {{ background:#08090b; border:1px solid var(--line2); color:var(--val);
  padding:16px; overflow:auto; font-size:12.5px; line-height:1.5; margin:0;
  white-space:pre-wrap; word-break:break-word; }}
.note {{ border-left:2px solid var(--line2); padding:8px 12px; margin:14px 0 0;
  color:var(--muted); font-size:11px; letter-spacing:.4px; }}
.foot {{ margin-top:26px; text-align:center; color:var(--muted); font-size:9px;
  letter-spacing:3px; text-transform:uppercase; }}
.foot .sep {{ color:var(--line2); margin:0 8px; }}

/* ---- login screen: centred card over a jet backdrop ---- */
.loginbg {{ position:fixed; inset:0; z-index:0; overflow:hidden;
  background:radial-gradient(120% 90% at 82% 38%, #23262b 0%, #131519 42%, #0a0b0d 78%); }}
.loginbg svg {{ position:absolute; right:-4%; top:50%; transform:translateY(-50%);
  height:118%; opacity:.9; }}
.auth {{ position:relative; z-index:1; max-width:330px; margin:11vh auto 0; }}
.card {{ background:rgba(11,12,15,.86); border:1px solid #1c1f25; padding:30px 30px 26px;
  backdrop-filter:blur(2px); }}
.card .kicker {{ color:#9aa2ad; letter-spacing:5px; font-size:10px; text-transform:uppercase; }}
.card h1 {{ color:#f2f5f8; font-size:30px; line-height:1.08; letter-spacing:2px;
  margin:10px 0 8px; font-weight:700; }}
.card .tagline {{ color:#6b727c; font-size:11px; letter-spacing:.6px; margin-bottom:24px; }}
.card .statusline {{ margin-top:22px; border-top:1px solid #1c1f25; padding-top:14px;
  color:#5b626c; font-size:9px; letter-spacing:2px; text-transform:uppercase; line-height:1.9; }}
.card .statusline b {{ color:#aeb4bd; font-weight:400; }}
"""


def jet_svg() -> str:
    """A dark swept-wing fighter silhouette used as the login backdrop."""
    return """
<div class="loginbg">
<svg viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
  <defs>
    <linearGradient id="jet" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#05070a"/>
      <stop offset="1" stop-color="#161a1f"/>
    </linearGradient>
  </defs>
  <g transform="translate(205,200) rotate(38) translate(-200,-200)" fill="url(#jet)">
    <!-- fuselage -->
    <polygon points="200,24 213,120 211,300 200,346 189,300 187,120"/>
    <!-- right main wing (swept) -->
    <polygon points="210,150 372,300 214,252"/>
    <!-- left main wing (swept) -->
    <polygon points="190,150 28,300 186,252"/>
    <!-- right tailplane -->
    <polygon points="208,286 292,344 210,322"/>
    <!-- left tailplane -->
    <polygon points="192,286 108,344 190,322"/>
    <!-- nose spike -->
    <polygon points="200,10 203,40 197,40"/>
    <!-- canopy -->
    <ellipse cx="200" cy="96" rx="7" ry="17" fill="#232830"/>
    <!-- twin exhausts -->
    <rect x="193" y="338" width="5" height="12" fill="#20252c"/>
    <rect x="202" y="338" width="5" height="12" fill="#20252c"/>
  </g>
</svg>
</div>"""


def topbar(system: str, subtitle: str, status: str = "SYSTEM STATUS: ONLINE") -> str:
    return f"""
<div class="topbar">
  <div class="brand">
    <span class="sys">{system}</span>
    <span class="sub">{subtitle}</span>
  </div>
  <div class="status"><span class="dot"></span><b>{status}</b></div>
</div>"""


def footer(node: str) -> str:
    return f"""
<div class="foot">AEROSPACE COMMAND<span class="sep">//</span>NODE {node}
<span class="sep">//</span>UNAUTHORIZED ACCESS PROHIBITED</div>"""
