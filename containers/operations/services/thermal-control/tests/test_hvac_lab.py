"""HVAC lab tests: horizontal predictable-token + vertical scheduled-job."""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("HVAC_RUN_DIR", "/tmp/erebus-hvac-test")

from hvac_app.app import token_for  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    run_dir = tmp_path / "hvac"
    run_dir.mkdir()
    (run_dir / "input").touch()
    monkeypatch.setenv("HVAC_RUN_DIR", str(run_dir))
    import hvac_app.app as mod

    mod.RUN_DIR = run_dir
    mod.INPUT_FILE = run_dir / "input"
    mod.REPORT_FILE = run_dir / "maintenance_report.txt"
    if mod.REPORT_FILE.exists():
        mod.REPORT_FILE.unlink()
    from hvac_app.app import app

    return TestClient(app)


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_horizontal_predictable_token(client):
    default_token = client.post("/login", json={"user": "default"}).json()["token"]
    assert default_token == token_for("default") == "HVAC-1001-STAT"
    # default cannot access engineer resource
    assert client.get("/api/hvac/status", headers={"X-Token": default_token}).status_code == 403
    # forged engineer token works
    r = client.get("/api/hvac/status", headers={"X-Token": token_for("engineer")})
    assert r.status_code == 200
    assert r.json()["system"].startswith("Thermal Regulation")


def test_vertical_scheduled_task_is_queued_and_report_is_async(client):
    eng = token_for("engineer")
    sched = client.get("/api/schedule", headers={"X-Token": eng}).json()
    assert "process_job" in sched["cron"]
    assert client.get("/api/maintenance/report", headers={"X-Token": eng}).status_code == 404
    r = client.post("/api/schedule/input", json={"content": "run_diagnostic"}, headers={"X-Token": eng})
    assert r.status_code == 200
    assert r.json()["status"] == "queued"
    assert r.json()["input"].endswith("/input")
    assert client.get("/api/maintenance/report", headers={"X-Token": eng}).status_code == 404


def test_worker_writes_report_from_input(tmp_path):
    import json
    import subprocess

    worker = os.path.join(os.path.dirname(__file__), "..", "scripts", "process_job")
    run_dir = tmp_path / "worker"
    run_dir.mkdir()
    (run_dir / "input").write_text("run_diagnostic")
    # The real cron environment has no compose HVAC_FLAG.
    env = dict(os.environ, HVAC_RUN_DIR=str(run_dir))
    env.pop("HVAC_FLAG", None)
    (run_dir / "worker.env").write_text("CTF{test_runtime_flag}\n")
    result = subprocess.run([sys.executable, worker, "run"], env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["status"] == "success"
    report = (run_dir / "maintenance_report.txt").read_text()
    assert "CTF{test_runtime_flag}" in report


def test_worker_rejects_other_input(tmp_path):
    import json
    import subprocess

    worker = os.path.join(os.path.dirname(__file__), "..", "scripts", "process_job")
    (tmp_path / "input").write_text("not_run_diagnostic")
    result = subprocess.run([sys.executable, worker, "run"], env=dict(os.environ, HVAC_RUN_DIR=str(tmp_path)), check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["status"] == "idle"
    assert not (tmp_path / "maintenance_report.txt").exists()


def test_worker_is_idle_without_trigger(tmp_path):
    import json
    import subprocess

    worker = os.path.join(os.path.dirname(__file__), "..", "scripts", "process_job")
    result = subprocess.run([sys.executable, worker, "run"], env=dict(os.environ, HVAC_RUN_DIR=str(tmp_path)), check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["status"] == "idle"
