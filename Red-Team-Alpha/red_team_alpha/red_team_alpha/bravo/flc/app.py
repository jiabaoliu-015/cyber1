from flask import Flask, render_template, request, redirect, make_response, session
import pickle, io, base64, re, os
import secrets

from terminal_manager import terminal
from models.session_state import SessionState, Setting
from models.report import ReportExporter, ReportJob
from models.convoy import ConvoyTransfer
from models.launch import LaunchAuthorization

app = Flask(__name__)
app.config["DEBUG"] = False
app.secret_key = "139Asnd238nqe81wqna#SDQ"

USERS = {"jsmith": "warehouse#123"}

AVAILABLE_REPORTS = {
    "supply_manifest": "Supply Manifest",
    "fuel_allocation": "Fuel Allocation",
    "ammunition_inventory": "Ammunition Inventory",
    "vehicle_readiness": "Vehicle Readiness",
    "communications_status": "Communications Status",
}


class AppStateLoader(pickle.Unpickler):
    """
    Legacy loader used by the Personnel Redeployment
    service to restore an operator's saved workstation state.
    """

    ALLOWED = {
        ("models.session_state", "SessionState"),
        ("models.session_state", "Setting"),
        ("models.launch", "LaunchAuthorization"),
        ("models.report", "ReportJob"),
        ("models.report", "ReportExporter"),
        ("models.convoy", "ConvoyTransfer"),
    }

    def find_class(self, module, name):
        # Check whether the requested class is allowed
        if (module, name) in self.ALLOWED:
            mod = __import__(module, fromlist=[name])
            return getattr(mod, name)
        
        raise pickle.UnpicklingError(f"Blocked attempt to load {module}.{name}")


def logged_in():
    return "user" in session


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login", methods=["GET","POST"])
def login():

    error=None

    if request.method=="POST":

        u=request.form.get("username")
        p=request.form.get("password")

        # Check if username and password match
        if USERS.get(u) == p:
            session["user"] = u
            session["sid"] = secrets.token_hex(8)
            return redirect("/profile")  

        error="Authentication failed."

    return render_template("login.html",error=error)


@app.route("/profile")
def profile():

    if not logged_in():
        return redirect("/login")

    return render_template("profile.html")


@app.route("/personnel/checkpoint")
def checkpoint():

    if not logged_in():
        return redirect("/login")

    state = SessionState(
        username=session["user"],
        settings=[Setting("theme", "dark")]
    )
 
    blob = base64.b64encode(pickle.dumps(state)).decode()

    resp = make_response("Operational checkpoint updated.")
 
    resp.set_cookie("pf_state", blob)

    return resp 


@app.route("/personnel/redeploy")
def redeploy():

    if not logged_in():
        return redirect("/login")

    output = "Redeployment completed."
    terminal_unlocked = False
 
    blob = request.cookies.get("pf_state")

    if blob:

        try: 
            obj = AppStateLoader(io.BytesIO(base64.b64decode(blob))).load()

            for setting in getattr(obj, "settings", []):

                if getattr(setting, "_output", None): 
                    output = setting._output

                    flag = os.getenv("FLAG")

                    if flag and flag in output:
                        session["maintenance_unlocked"] = True
                        terminal_unlocked = True

        except Exception:
            output = "Synchronization error."

    return render_template("redeploy.html", output=output, terminal_unlocked=terminal_unlocked)


@app.route("/maintenance",methods=["GET","POST"])
def maintenance():

    if not logged_in():
        return redirect("/login")

    if not session.get("maintenance_unlocked"):
        return redirect("/profile")

    output=None

    if request.method=="POST":

        command=request.form.get("command","").strip()

        output = terminal.execute(session["sid"], command)

    return render_template(
        "maintenance.html",
        output=output
    )


@app.route("/convoy")
def convoy():

    if not logged_in():
        return redirect("/login")

    record = ConvoyTransfer()

    return render_template(
        "convoy.html",
        output=record.status()
    )


@app.route("/launch")
def launch():

    if not logged_in():
        return redirect("/login")

    record = LaunchAuthorization()

    return render_template(
        "launch.html",
        output=record.review()
    )


@app.route("/reports")
def reports():

    if not logged_in():
        return redirect("/login")

    return render_template("reports.html", reports=AVAILABLE_REPORTS)


@app.route("/reports/export")
def reports_export():

    if not logged_in():
        return redirect("/login")

    name = request.args.get("name", "").strip()
    
    if not re.fullmatch(r"[A-Za-z0-9_]{1,32}", name):
        return render_template(
            "reports.html",
            reports=AVAILABLE_REPORTS,
            error="Invalid report identifier. Only letters (A–Z), numbers (0–9), and underscores (_) are accepted."
        )

    if name not in AVAILABLE_REPORTS:
        return render_template(
            "reports.html",
            reports=AVAILABLE_REPORTS,
            error="Unknown report identifier."
        )
    
    ReportJob(ReportExporter(name)).run()

    return render_template(
        "reports.html",
        reports=AVAILABLE_REPORTS,
        success=f"Report '{name}' has been queued successfully."
    )


@app.route("/help")
def help_page():

    if not logged_in():
        return redirect("/login")

    return render_template("help.html")


@app.route("/changelog")
def changelog():

    if not logged_in():
        return redirect("/login")
    
    return render_template("changelog.html")


@app.route("/logout")
def logout():
    session.clear() 

    resp = make_response(redirect("/login"))
    resp.delete_cookie("pf_state")

    return resp


if __name__=="__main__":
    app.run(host="0.0.0.0",port=5006)