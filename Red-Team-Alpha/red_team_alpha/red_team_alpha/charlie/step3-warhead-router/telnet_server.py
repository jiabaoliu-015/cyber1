#!/usr/bin/env python3
"""
STEP 3 of my route  --  ACC-RTR-01 segment controller  (Telnet command injection)

The network router at the end of my chain. In the standalone version it also ran
TFTP to hand out its own config; I DROPPED that -- in the full route the config
export is leaked by the operator console in step 2 (horizontal PE), so the router
no longer gives it away itself. Only the Telnet console is left.

The console's `ping` diagnostic pastes your argument into a shell. It blocks the
obvious characters (space, ; | & ` and quotes) -- but that blocks CHARACTERS, not
INTENT: ${IFS} is whitespace and $(...) runs a command, and neither is on the
list. That's how you read the flag.

Made harder on purpose:
  * the flag is NOT at an obvious path like /flag -- it's a maintenance artefact
    the player has to locate first (the MOTD hints where to look);
  * the login is the vendor 'support' backdoor whose password is disclosed
    (scrambled) only in step 2's leaked export.
"""
import base64
import os
import socket
import subprocess
import threading

HOST = "0.0.0.0"
PORT = int(os.environ.get("TELNET_PORT", "23"))

USER = os.environ.get("TELNET_USER", "support")
# xor0x5a+base64 of "Falc0n#rtr!22". Disclosed (scrambled) in step 2's export.
PASS_ENC = os.environ.get("TELNET_PASS_ENC", "HDs2OWo0eSguKHtoaA==")
PASSWORD = os.environ.get("TELNET_PASS") or "".join(
    chr(b ^ 0x5A) for b in base64.b64decode(PASS_ENC)
)

# Flag lives somewhere non-obvious; the MOTD hints the directory, not the file.
FLAG_PATH = os.environ.get("FLAG_PATH", "/opt/maint/rtr-01.snapshot")

BLOCKED = set(" ;|&`\n\t\r<>\\'\"")

BANNER = (
    "\r\n"
    "================================================================\r\n"
    "  ACC-RTR-01   //   NETWORK SEGMENT CONTROLLER\r\n"
    "  segment: warhead-bus/3        mgmt console (telnet)\r\n"
    "  ** AUTHORIZED PERSONNEL ONLY. ACTIVITY IS LOGGED. **\r\n"
    "================================================================\r\n"
)
# MOTD shown after login. It names WHERE the maintenance artefacts live and that
# input is filtered, but says nothing about what the files contain, so the player
# still has to solve the injection and work out what each file is for themselves.
MOTD = (
    "\r\n"
    "login successful.\r\n"
    "  NOTICE: diagnostic command input is sanitised.\r\n"
    "  NOTICE: per hardening policy, a maintenance artefact was relocated from /\r\n"
    "          to /opt/maint/rtr-01.snapshot.\r\n"
    "  type 'help' for commands.\r\n\r\n"
)
HELP = (
    "commands:\r\n"
    "  ping <host>     network reachability test (input sanitised)\r\n"
    "  status          controller status\r\n"
    "  help            this list\r\n"
    "  exit            close session\r\n"
)


def clean(raw: bytes) -> str:
    return "".join(chr(b) for b in raw if 0x20 <= b <= 0x7E)


def send(conn, text):
    try:
        conn.sendall(text.replace("\n", "\r\n").encode())
    except OSError:
        pass


def recv_line(conn):
    buf = b""
    while b"\n" not in buf:
        chunk = conn.recv(1024)
        if not chunk:
            break
        buf += chunk
        if len(buf) > 4096:
            break
    return clean(buf).strip()


def do_ping(arg):
    if any(c in BLOCKED for c in arg):
        return "% illegal character(s) in host argument\r\n"
    try:
        out = subprocess.run(
            f"ping -c 1 {arg}", shell=True,
            capture_output=True, text=True, timeout=6,
        )
        return (out.stdout or "") + (out.stderr or "")
    except subprocess.TimeoutExpired:
        return "ping: request timed out\r\n"


def handle(conn, addr):
    try:
        conn.settimeout(120)
        send(conn, BANNER)
        send(conn, "\r\nlogin: ")
        user = recv_line(conn)
        send(conn, "password: ")
        pw = recv_line(conn)
        if user != USER or pw != PASSWORD:
            send(conn, "\r\n% authentication failed\r\n")
            return
        send(conn, MOTD)
        while True:
            send(conn, "RTR-01> ")
            line = recv_line(conn)
            if not line:
                continue
            parts = line.split(None, 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            if cmd == "exit":
                send(conn, "closing session.\r\n")
                return
            elif cmd == "help":
                send(conn, HELP)
            elif cmd == "status":
                send(conn, "controller: ACC-RTR-01  state: ACTIVE  segment: warhead-bus/3\r\n")
            elif cmd == "ping":
                if not arg:
                    send(conn, "usage: ping <host>\r\n")
                else:
                    send(conn, do_ping(arg))
            else:
                send(conn, f"% unknown command: {cmd}\r\n")
    except (OSError, socket.timeout):
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(8)
    print(f"[*] ACC-RTR-01 telnet console on {HOST}:{PORT}")
    print(f"[*] login: {USER} / {PASSWORD}   flag at {FLAG_PATH}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
