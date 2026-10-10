"""SSH-entry + runtime-flag wiring for power-lab (no live container needed).

Asserts the pure-SSH design: sshd + predictable-password users in Dockerfile,
localhost-only backend, runtime flags via flags/init_flags.sh + compose
substitution, CLI wrapper mapping Unix user -> token, and no hardcoded
CTF flags in Dockerfile/compose.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCKERFILE = (ROOT / "Dockerfile").read_text()
COMPOSE = (ROOT / "docker-compose.yml").read_text()
ENTRYPOINT = (ROOT / "entrypoint.sh").read_text()
CLI = (ROOT / "cli" / "power").read_text()
INIT_FLAGS = (ROOT / "flags" / "init_flags.sh").read_text()
HEALTHCHECK = (ROOT / "scripts" / "healthcheck.sh").read_text()


def test_dockerfile_has_sshd_and_lab_users():
    assert "openssh-server" in DOCKERFILE
    assert "useradd" in DOCKERFILE and "default" in DOCKERFILE
    assert "officer" in DOCKERFILE
    assert "PWR-3001-STAT" in DOCKERFILE
    assert "PWR-3002-STAT" in DOCKERFILE
    assert "/usr/sbin/sshd" in ENTRYPOINT or "sshd" in ENTRYPOINT


def test_backend_is_localhost_only():
    assert "127.0.0.1" in ENTRYPOINT
    assert "--host 0.0.0.0" not in ENTRYPOINT
    # compose must not host-publish the web backend; SSH is the entry
    assert "127.0.0.1:2222:22" in COMPOSE
    assert "127.0.0.1:8082:8082" not in COMPOSE


def test_runtime_flags_not_baked_in():
    for concrete in ("CTF{blackbox_optics_mid_7f3a}", "CTF{reactor_scram_hard_9c1e}",
                     "CTF{agent_obfuscated_hard_4d2b}"):
        assert concrete not in DOCKERFILE, f"baked flag in Dockerfile: {concrete}"
        assert concrete not in COMPOSE, f"baked flag in compose: {concrete}"
    for var in ("PWR_FLAG_MID", "PWR_FLAG_HARD", "PWR_FLAG_AGENT"):
        assert var in COMPOSE and "${" + var in COMPOSE
        assert var in INIT_FLAGS
    assert ".env" in INIT_FLAGS
    assert (ROOT / ".env.example").exists()


def test_entrypoint_rebuilds_flag_artefacts():
    assert "build_image.py" in ENTRYPOINT
    assert "build_agent_binary.py" in ENTRYPOINT
    assert "ssh-keygen -A" in ENTRYPOINT


def test_cli_maps_unix_user_to_token_and_covers_flow():
    assert "getpass.getuser()" in CLI or "whoami" in CLI
    assert "PWR-3001-STAT" in CLI and "PWR-3002-STAT" in CLI
    for sub in ("left-key", "blackbox-image", "agent-binary", "two-key",
                "schedule", "reactor-report", "logs"):
        assert sub in CLI, f"CLI missing subcommand: {sub}"


def test_healthcheck_covers_ssh_and_backend():
    assert "2222" in HEALTHCHECK
    assert "8082" in HEALTHCHECK


def test_generated_assets_and_cron_runtime_env():
    assert "COPY assets/astronaut.jpeg ./assets/astronaut.jpeg" in DOCKERFILE
    assert "./assets:/app/assets:ro" not in COMPOSE
    assert "PWR_ASSET_DIR=/app/generated-assets" in COMPOSE
    assert "/app/assets/generated" not in COMPOSE
    assert "/run/power-runtime.env" in DOCKERFILE
    assert "chmod 0600 /run/power-runtime.env" in ENTRYPOINT
    assert "cron" in DOCKERFILE
    assert "PWR_ASSET_DIR=/app/generated-assets" in DOCKERFILE
