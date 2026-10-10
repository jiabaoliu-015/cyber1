#!/usr/bin/env python3
"""Clean runtime proof of the intended local A→B→C→D→E campaign spine."""
from __future__ import annotations
import json
import re
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESET = ROOT / "tools/reset_full_campaign.sh"
HEALTH = ROOT / "tools/healthcheck_full_campaign.sh"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def require(result: subprocess.CompletedProcess[str], label: str) -> None:
    assert result.returncode == 0, f"{label} failed:\n{result.stdout}\n{result.stderr}"


def root_exec(compose: str, service: str, command: str) -> str:
    result = run("docker", "compose", "-f", str(ROOT / compose), "exec", "-T", service, "sh", "-c", command)
    require(result, service)
    return result.stdout


def uplink_handoff() -> None:
    with socket.create_connection(("127.0.0.1", 5432), timeout=5) as conn:
        conn.sendall(b"INFO\n")
        info = conn.recv(4096).decode()
        challenge_match = re.search(r"challenge:\s*([a-f0-9]+)", info)
        assert challenge_match, info
        challenge = challenge_match.group(1)
        conn.sendall(f"AUTH station_crew {challenge}\n".encode())
        auth = conn.recv(4096).decode()
    assert "authentication accepted" in auth and "Station SSH" in auth, auth


def main() -> int:
    require(run(str(RESET)), "clean reset")
    require(run(str(HEALTH)), "full health")
    uplink_handoff()

    maintenance_utility = run("docker", "run", "--rm", "--entrypoint", "/opt/suseid/maintenance_utility", "cits3006-maintenance_utility-handoff", "--run", "print_flag")
    require(maintenance_utility, "MAINTENANCE_UTILITY root proof")
    assert "CITS3006_ROOT_FLAG" in maintenance_utility.stdout
    assert "CITS3006_ROOT_FLAG" in root_exec("containers/operations/compose/compose_scheduled_job.yml", "shift_scheduler", "/opt/shift_scheduler/process_job print_flag")
    widow = root_exec("containers/operations/compose/compose_local_root_service.yml", "local_control_service", "python3 -c \"import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/print_flag').read().decode())\"")
    assert json.loads(widow)["flag"] == "CITS3006_ROOT_FLAG"

    late = run(sys.executable, str(ROOT / "tests/integration/test_late_campaign.py"))
    require(late, "D→E recovery")
    print("Full A→B→C→D→E runtime playthrough: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
