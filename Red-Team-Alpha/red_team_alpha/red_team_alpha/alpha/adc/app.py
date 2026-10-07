import json
from pathlib import Path

from flask import (Flask, render_template, request, redirect, send_file, jsonify)

from functools import wraps
from jwt import InvalidTokenError

from auth import create_token, verify_token
from data.users import USERS
from data.records import RECORDS
from data.mission_data import MISSION_DATA

app = Flask(__name__)
app.secret_key = "3eCD4f9DFN9INAD20RNASDQ"


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        token = request.cookies.get("auth_token")

        if not token:
            return redirect("/login")

        try:
            payload = verify_token(token)
            request.user = payload["user"]

        except InvalidTokenError:
            return redirect("/login")
        except Exception as e:
            return redirect("/login")

        return func(*args, **kwargs)

    return wrapper


@app.after_request
def headers(response):

    response.headers["Server"] = "ADC-Identity"
    response.headers["X-Auth-Build"] = "ADC-AUTH-2026.9"

    return response


@app.route("/")
def index():

    if request.cookies.get("auth_token"):
        return redirect("/dashboard")

    return redirect("/login")


@app.route("/login", methods=["GET","POST"])
def login():

    error = False

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username]["password"] == password:

            token = create_token(username)

            response = redirect("/dashboard")

            response.set_cookie(
                "auth_token",
                token,
                httponly=False,
                samesite="Lax"
            )

            return response

        error = True

    return render_template("login.html", error=error)


@app.route("/dashboard")
@login_required
def dashboard():

    u = request.user

    return render_template("dashboard.html", user=USERS[u], record=RECORDS[u])


@app.route("/deployment")
@login_required
def deployment():
    return render_template("deployment.html", record=RECORDS[request.user])


@app.route("/mission")
@login_required
def mission():

    u = request.user

    return render_template("mission.html", user=USERS[u], mission=MISSION_DATA[u])


@app.route("/training")
@login_required
def training():
    return render_template("training.html")


@app.route("/medical")
@login_required
def medical():
    return render_template("medical.html", record=RECORDS[request.user])


@app.route("/travel")
@login_required
def travel():
    return render_template("travel.html", record=RECORDS[request.user])


@app.route("/support")
@login_required
def support():
    return render_template("support.html")


@app.route("/auth")
@login_required
def auth_status():
    return render_template("auth_status.html")


@app.route("/download/travel")
@login_required
def download_travel():
    return send_file("documents/travel/sentinel_orders.pdf", as_attachment=True)


@app.route("/download/certificate/<course>")
@login_required
def download_certificate(course):

    username = request.user

    return send_file(f"documents/certificates/{username}_{course}.pdf", as_attachment=True, download_name=f"{course}.pdf")


@app.route("/logout")
def logout():

    response = redirect("/login")
    response.delete_cookie("auth_token")

    return response


@app.route("/auth/.well-known/openid-configuration")
@login_required
def openid_configuration():

    return jsonify({
        "issuer":"http://127.0.0.1:8080/auth",
        "jwks_uri":"http://127.0.0.1:8080/auth/.well-known/jwks.json",
        "id_token_signing_alg_values_supported":[
            "RS256"
        ]
    })


@app.route("/auth/.well-known/jwks.json")
@login_required
def jwks():

    keys = []

    for file in [
        "archive_2024_jwk.json",
        "gateway_2025_jwk.json",
        "pdcp_2026_jwk.json"
    ]:

        with open(Path("keys")/file) as f:
            keys.append(json.load(f))

    return jsonify({"keys":keys})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)