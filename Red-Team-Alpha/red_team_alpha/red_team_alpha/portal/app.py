import hmac
import json
import os
from pathlib import Path

from flask import Flask, render_template, request

from agents import get_agents

app = Flask(__name__)

BASE = Path(__file__).resolve().parent

CODES = {
    "alpha":   os.environ.get("ALPHA_CODE",   "FLAG{tH3_f1LTa_w4s_0NLY_4_SUgg3sT10N}"),
    "bravo":   os.environ.get("BRAVO_CODE",   "FLAG{0EN38FBQE1}"),
    "charlie": os.environ.get("CHARLIE_CODE", "CITS3006{xyOTpUwAhd}"),
}

with open(BASE / "data" / "world_dots.json") as fh:
    WORLD_DOTS = json.load(fh)["dots"]


def _valid(field: str, supplied: str) -> bool:
    expected = CODES[field].encode("utf-8")
    supplied = (supplied or "").strip().encode("utf-8")
    return hmac.compare_digest(expected, supplied)


@app.get("/")
def login():
    return render_template("login.html")


@app.post("/unlock")
def unlock():
    a = _valid("alpha",   request.form.get("alpha"))
    b = _valid("bravo",   request.form.get("bravo"))
    c = _valid("charlie", request.form.get("charlie"))

    if not (a and b and c):
        failed = [name for name, ok in (("ALPHA", a), ("BRAVO", b), ("CHARLIE", c)) if not ok]
        return render_template("login.html", failed=failed), 401

    agents = get_agents()
    active = sum(1 for x in agents if x["status"] == "ACTIVE")
    stations = len({x["city"] for x in agents})
    return render_template(
        "dashboard.html",
        agents=agents,
        world_dots=WORLD_DOTS,
        stats={
            "total": len(agents),
            "active": active,
            "stations": stations,
            "countries": len({x["country"] for x in agents}),
        },
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
