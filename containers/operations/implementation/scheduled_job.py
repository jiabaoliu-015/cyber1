#!/usr/bin/env python3
"""SHIFT_SCHEDULER: deliberately unsafe root-scheduled-job simulation, container scoped."""
import argparse
import json
import os
from pathlib import Path

ROOT_FLAG = os.environ.get("ROOT_FLAG", "CITS3006_ROOT_FLAG")
SCHEDULE = Path("/etc/cron.d/shift_scheduler_job")
RUN_DIR = Path("/var/run/shift_scheduler")
CLUE = Path("/entry/scheduled_job_clue.txt")


def initialise() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    CLUE.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE.write_text(
        "# SHIFT_SCHEDULER — deliberately unsafe root scheduled job\n"
        "* * * * * root /opt/shift_scheduler/process_job process_input\n"
        "# The station_crew-writable input is /var/run/shift_scheduler/input\n"
    )
    os.chmod(SCHEDULE, 0o644)
    CLUE.write_text(
        "SHIFT_SCHEDULER — inspect /etc/cron.d/shift_scheduler_job. Root processes "
        "/var/run/shift_scheduler/input; follow that writable trust boundary.\n"
    )


def result(operation: str) -> dict:
    if operation == "print_flag":
        return {"status": "success", "operation": "PRINT_FLAG", "flag": ROOT_FLAG,
                "message": "Root job proof recovered from the unsafe scheduled-job path."}
    if operation == "inspect":
        return {"status": "info", "operation": "INSPECT",
                "detail": "The cron job runs as root and trusts station_crew-influenced input; that trust boundary is the escalation flaw."}
    if operation in {"--challenge", "challenge"}:
        return {"status": "info", "detail": "SHIFT_SCHEDULER is a vertical scheduled-job challenge. Inspect cron and its writable input."}
    if operation == "--healthcheck":
        return {"status": "running", "schedule_exists": SCHEDULE.exists(),
                "clue_exists": CLUE.exists(), "container_scoped": True}
    return {"status": "error", "message": "Use inspect, print_flag, --challenge, or --healthcheck."}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", nargs="?", default="")
    parser.add_argument("--healthcheck", action="store_true")
    parser.add_argument("--challenge", action="store_true")
    args = parser.parse_args()
    initialise()
    operation = "--healthcheck" if args.healthcheck else ("--challenge" if args.challenge else args.operation)
    payload = result(operation)
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] != "error" else 2


if __name__ == "__main__":
    raise SystemExit(main())
