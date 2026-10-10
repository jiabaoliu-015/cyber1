#!/usr/bin/env python3
"""LOCAL_CONTROL_SERVICE: deliberately unsafe localhost-only root service."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

FLAG = "CITS3006_ROOT_FLAG"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            code, body = 200, {"status": "ok", "service": "local_control_service"}
        elif self.path == "/inspect":
            code, body = 200, {"status": "info", "detail": "A root-owned localhost interface trusts the print_flag method."}
        elif self.path == "/print_flag":
            code, body = 200, {"status": "success", "flag": FLAG, "message": "Root proof revealed by the unsafe local interface."}
        else:
            code, body = 404, {"status": "error", "message": "Use /inspect or /print_flag."}
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps(body).encode())
    def log_message(self, format: str, *args: object) -> None:
        pass

HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
