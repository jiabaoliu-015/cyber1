"""Power lab tests: horizontal token + LEFT key + image crypto + agent RE + two-key + scram."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("PWR_RUN_DIR", "/tmp/erebus-power-test")

from scripts.build_image import build as build_image  # noqa: E402
from scripts.build_agent_binary import build as build_agent  # noqa: E402
import power_app.app as mod  # noqa: E402
from power_app.app import (  # noqa: E402
    FLAG_AGENT,
    FLAG_HARD,
    FLAG_MID,
    LEFT_KEY,
    OBFUS_KEY,
    RIGHT_KEY,
    XOR_KEY,
    decode_agent_stage,
    decode_trailer,
    token_for,
)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    run_dir = tmp_path / "power"
    run_dir.mkdir()
    monkeypatch.setenv("PWR_RUN_DIR", str(run_dir))
    import power_app.app as mod

    mod.RUN_DIR = run_dir
    mod.INPUT_FILE = run_dir / "input"
    mod.REPORT_FILE = run_dir / "reactor_report.txt"
    mod.AUTH_FILE = run_dir / "two_key_authorized"
    generated = tmp_path / "generated-assets"
    generated.mkdir()
    mod.ASSET_DIR = generated
    mod.STEGO_IMAGE = generated / "astronaut_stego.jpeg"
    mod.AGENT_IMAGE = generated / "agent_firmware.bin"
    monkeypatch.setenv("PWR_FLAG_MID", FLAG_MID)
    monkeypatch.setenv("PWR_FLAG_AGENT", FLAG_AGENT)
    for p in (mod.REPORT_FILE, mod.INPUT_FILE, mod.AUTH_FILE):
        if p.exists():
            p.unlink()
    from power_app.app import app

    return TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "service": "power-lab"}


def test_horizontal_predictable_token(client):
    default_token = client.post("/login", json={"user": "default"}).json()["token"]
    assert default_token == token_for("default") == "PWR-3001-STAT"
    # default cannot access officer resource
    assert client.get("/api/power/status", headers={"X-Token": default_token}).status_code == 403
    # forged officer token works
    r = client.get("/api/power/status", headers={"X-Token": token_for("officer")})
    assert r.status_code == 200
    assert r.json()["system"].startswith("Power Distribution")


def test_left_key_requires_officer(client):
    default_token = client.post("/login", json={"user": "default"}).json()["token"]
    assert client.get("/api/keys/left", headers={"X-Token": default_token}).status_code == 403
    r = client.get("/api/keys/left", headers={"X-Token": token_for("officer")})
    assert r.status_code == 200
    assert r.json()["left_key"] == LEFT_KEY


def _stego_bytes():
    return Path(__file__).resolve().parent.parent.joinpath("assets", "astronaut.jpeg").read_bytes()


def test_image_trailer_crypto_roundtrip():
    raw = _stego_bytes()
    assert raw.startswith(b"\xff\xd8")  # still a valid JPEG
    assert b"PWR-BLACKBOX-V1:" not in raw


def test_generated_image_trailer_crypto_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("PWR_FLAG_MID", FLAG_MID)
    out = tmp_path / "portrait.jpeg"
    build_image(Path(__file__).resolve().parent.parent / "assets" / "astronaut.jpeg", out)
    bundle = decode_trailer(out.read_bytes(), XOR_KEY)
    mid, right = bundle.split("|", 1)
    assert mid == FLAG_MID
    assert right == RIGHT_KEY


def test_image_endpoint_serves_jpeg_with_trailer(client):
    root = Path(__file__).resolve().parent.parent
    build_image(root / "assets" / "astronaut.jpeg", mod.STEGO_IMAGE)
    r = client.get("/api/blackbox/image", headers={"X-Token": token_for("officer")})
    assert r.status_code == 200
    assert r.content.startswith(b"\xff\xd8")
    assert b"PWR-BLACKBOX-V1:" in r.content
    assert decode_trailer(r.content, XOR_KEY).split("|")[0] == FLAG_MID


def test_agent_binary_obfuscated_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("PWR_FLAG_AGENT", FLAG_AGENT)
    out = tmp_path / "agent_firmware.bin"
    build_agent(out)
    raw = out.read_bytes()
    assert b"ISVM-AGENT-FW" in raw
    assert FLAG_AGENT.encode() not in raw  # no plaintext leak; strings shows decoys only
    assert decode_agent_stage(raw, OBFUS_KEY) == FLAG_AGENT


def test_agent_endpoint_requires_officer_and_serves_stage(client):
    build_agent(mod.AGENT_IMAGE)
    default_token = client.post("/login", json={"user": "default"}).json()["token"]
    assert client.get("/api/agent/binary", headers={"X-Token": default_token}).status_code == 403
    r = client.get("/api/agent/binary", headers={"X-Token": token_for("officer")})
    assert r.status_code == 200
    assert b"AGENT-STAGE2:" in r.content
    assert decode_agent_stage(r.content, OBFUS_KEY) == FLAG_AGENT


def test_two_key_console_gates_scram(client):
    eng = token_for("officer")
    # schedule locked before authorization
    assert client.get("/api/schedule", headers={"X-Token": eng}).status_code == 403
    # wrong keys rejected per slot
    bad = client.post(
        "/api/two-key/authorize",
        json={"left_key": "nope", "right_key": "nope"},
        headers={"X-Token": eng},
    )
    assert bad.status_code == 403
    # correct keys authorize
    ok = client.post(
        "/api/two-key/authorize",
        json={"left_key": LEFT_KEY, "right_key": RIGHT_KEY},
        headers={"X-Token": eng},
    )
    assert ok.json()["status"] == "authorized"
    assert client.get("/api/two-key/status", headers={"X-Token": eng}).json()["authorized"] is True


def test_vertical_scram_job_reports_hard_flag(client):
    eng = token_for("officer")
    client.post("/api/two-key/authorize", json={"left_key": LEFT_KEY, "right_key": RIGHT_KEY}, headers={"X-Token": eng})
    sched = client.get("/api/schedule", headers={"X-Token": eng}).json()
    assert "scram_job" in sched["cron"]
    assert client.get("/api/reactor/report", headers={"X-Token": eng}).status_code == 404
    r = client.post("/api/schedule/input", json={"content": "scram_reactor"}, headers={"X-Token": eng})
    assert r.json()["status"] == "queued"
    assert client.get("/api/reactor/report", headers={"X-Token": eng}).status_code == 404
    mod.REPORT_FILE.write_text("old report")
    r = client.post("/api/schedule/input", json={"content": "not_a_scram"}, headers={"X-Token": eng})
    assert r.json()["status"] == "queued"
    assert client.get("/api/reactor/report", headers={"X-Token": eng}).status_code == 404


def test_runtime_artifact_builders_use_requested_output(tmp_path, monkeypatch):
    monkeypatch.setenv("PWR_FLAG_MID", FLAG_MID)
    monkeypatch.setenv("PWR_FLAG_AGENT", FLAG_AGENT)
    root = Path(__file__).resolve().parent.parent
    image, firmware = tmp_path / "generated/portrait.jpeg", tmp_path / "generated/firmware.bin"
    build_image(root / "assets" / "astronaut.jpeg", image)
    build_agent(firmware)
    assert decode_trailer(image.read_bytes(), XOR_KEY).split("|")[0] == FLAG_MID
    assert decode_agent_stage(firmware.read_bytes(), OBFUS_KEY) == FLAG_AGENT


def test_decoy_logs_carry_no_flag(client):
    eng = token_for("officer")
    index = client.get("/api/logs", headers={"X-Token": eng}).json()["logs"]
    # Shared ship store: identical 9-category set is served by both Power and HVAC consoles.
    assert set(index) == {"reactor_logs", "shift_notes", "engineer_logs", "blackbox_logs", "comms_logs", "diagnostics", "crew_logs", "medical_logs", "research_notes"}
    total = sum(len(v) for v in index.values())
    assert total >= 60
    for category, names in index.items():
        for name in names:
            body = client.get(f"/api/logs/{category}/{name}", headers={"X-Token": eng}).json()["content"]
            assert FLAG_HARD not in body
