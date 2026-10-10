#!/usr/bin/env python3
"""Clean local verification for the root → Slice D → INCIDENT ARCHIVE handoff."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESET = ROOT / "tools" / "reset_late_campaign.sh"
HEALTH = ROOT / "tools" / "healthcheck_late_campaign.sh"
UPLINK = ROOT / "containers/critical/offline-artifacts" / "solvers" / "crypto_solver.py"
ASSEMBLE = ROOT / "challenges/completion" / "scripts" / "assemble_evidence.py"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def assert_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    assert result.returncode == 0, f"{label}: {result.stdout}\n{result.stderr}"


def main() -> int:
    for route in ("suid_route_clue.txt", "scheduled_job_clue.txt", "local_root_service_clue.txt"):
        clue = (ROOT / "containers/operations" / "entry" / route).read_text(encoding="utf-8")
        assert "post_root_handoff.txt" in clue, route

    handoff = (ROOT / "containers/operations" / "entry" / "post_root_handoff.txt").read_text(encoding="utf-8")
    assert "privilege_handoff.txt" in handoff and "THREAD_02" in handoff

    assert_ok(run([str(RESET)]), "initial reset")
    health = run([str(HEALTH)])
    assert_ok(health, "health check")
    assert "PASS" in health.stdout

    bad = run([sys.executable, str(ASSEMBLE), "--thread-02", "THREAD_02=wrong"])
    assert bad.returncode == 1 and "remains incomplete" in bad.stdout

    recovered = run([sys.executable, str(UPLINK)])
    assert_ok(recovered, "Uplink Vault recovery")
    record = recovered.stdout.strip()
    assert record.startswith("THREAD_02="), record

    finale = run([sys.executable, str(ASSEMBLE), "--thread-02", record])
    assert_ok(finale, "INCIDENT ARCHIVE assembly")
    for marker in ("THREAD_01.txt", "THREAD_02.txt", "THREAD_03.txt", "THREAD_04.txt", "Station incident records indexed for review", "CTF{the_web_marks_john_liability}"):
        assert marker in finale.stdout, marker

    assert_ok(run([str(RESET)]), "final reset")
    print("Late-campaign root → Uplink Vault → INCIDENT ARCHIVE playthrough: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
