"""SSH-entry + runtime-flag wiring for hvac-lab (no live container needed)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCKERFILE = (ROOT / "Dockerfile").read_text()
COMPOSE = (ROOT / "docker-compose.yml").read_text()
ENTRYPOINT = (ROOT / "entrypoint.sh").read_text()
CLI = (ROOT / "cli" / "hvac").read_text()
INIT_FLAGS = (ROOT / "flags" / "init_flags.sh").read_text()
HEALTHCHECK = (ROOT / "scripts" / "healthcheck.sh").read_text()


def test_dockerfile_has_sshd_and_lab_users():
    assert "openssh-server" in DOCKERFILE
    assert "cron" in DOCKERFILE
    assert "useradd" in DOCKERFILE and "default" in DOCKERFILE
    assert "engineer" in DOCKERFILE
    assert "HVAC-1001-STAT" in DOCKERFILE
    assert "HVAC-1002-STAT" in DOCKERFILE
    assert "sshd" in ENTRYPOINT


def test_backend_is_localhost_only():
    assert "127.0.0.1" in ENTRYPOINT
    assert "--host 0.0.0.0" not in ENTRYPOINT
    assert "127.0.0.1:2223:22" in COMPOSE
    assert "127.0.0.1:8081:8081" not in COMPOSE


def test_runtime_flag_not_baked_in():
    assert "CTF{hvac_maintenance_report_mid}" not in DOCKERFILE
    assert "CTF{hvac_maintenance_report_mid}" not in COMPOSE
    assert "HVAC_FLAG" in COMPOSE and "${HVAC_FLAG" in COMPOSE
    assert "HVAC_FLAG" in INIT_FLAGS
    assert ".env" in INIT_FLAGS
    assert (ROOT / ".env.example").exists()


def test_entrypoint_starts_sshd():
    assert "ssh-keygen -A" in ENTRYPOINT
    assert "/usr/sbin/sshd" in ENTRYPOINT


def test_cli_maps_unix_user_to_token_and_covers_flow():
    assert "getpass.getuser()" in CLI or "whoami" in CLI
    assert "HVAC-1001-STAT" in CLI and "HVAC-1002-STAT" in CLI
    for sub in ("status", "schedule", "schedule-input", "report", "logs"):
        assert sub in CLI, f"CLI missing subcommand: {sub}"


def test_healthcheck_covers_ssh_and_backend():
    assert "2223" in HEALTHCHECK
    assert "8081" in HEALTHCHECK
    assert "curl" not in HEALTHCHECK


def test_runtime_flag_is_available_to_cron_without_cli_exposure():
    worker = (ROOT / "scripts" / "process_job").read_text()
    assert worker.startswith("#!/usr/local/bin/python3"), "cron's default PATH omits /usr/local/bin"
    assert "worker.env" in ENTRYPOINT and "0600" in ENTRYPOINT
    assert "worker.env" in worker
    assert "HVAC_FLAG" not in (ROOT / "Dockerfile").read_text().split("ENV HVAC_FLAG=", 1)[1].splitlines()[0]
