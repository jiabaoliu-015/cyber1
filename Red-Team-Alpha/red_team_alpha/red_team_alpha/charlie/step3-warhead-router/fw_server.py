#!/usr/bin/env python3
"""
STEP 3, side service  --  ACC-RTR-01 "OTA firmware" HTTP endpoint.

This is how Isaac's reverse-engineering binary is HANDED to the player as the
reward for solving my router stage. The controller's firmware image (really
Isaac's `rand` RE binary, renamed acc-rtr01-fw.elf) is downloadable here.

Gate: it is served ONLY at a single secret path. There is NO directory listing
and everything else 404s, so you cannot just browse the port and grab it. The
secret URL is disclosed only inside /opt/maint (read via the ping command
injection). So: no injection -> no URL -> no firmware -> no creds -> no step 4.
That keeps the command-injection stage mandatory.

Chain: solve injection -> read the OTA url from /opt/maint -> download this
firmware -> reverse engineer it (Isaac's stage) -> recover the ssh credential ->
land on the vertical-privesc box.
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = int(os.environ.get("FW_PORT", "8081"))
TOKEN = os.environ.get("FW_TOKEN", "changeme")
FW_FILE = os.environ.get("FW_FILE", "/srv/acc-rtr01-fw.elf")
DL_NAME = "acc-rtr01-fw.elf"

SECRET_PATH = f"/fw/{TOKEN}/{DL_NAME}"


class Handler(BaseHTTPRequestHandler):
    server_version = "acc-maint/1.0"

    def _deny(self):
        body = b"404 not found\n"
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # exact secret path only -- no listings, no guessing
        if self.path != SECRET_PATH:
            return self._deny()
        try:
            with open(FW_FILE, "rb") as f:
                data = f.read()
        except OSError:
            return self._deny()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition",
                         f'attachment; filename="{DL_NAME}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"[*] ACC-RTR-01 OTA firmware endpoint on {HOST}:{PORT}{SECRET_PATH}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
