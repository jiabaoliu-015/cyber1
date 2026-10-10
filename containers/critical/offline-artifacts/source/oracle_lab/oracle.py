#!/usr/bin/env python3
"""Station Audit: deterministic prefix-validation oracle, localhost only."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs,urlparse
SECRET='EYE-THREAD-02'; FLAG='CTF{spiders_eye_oracle}'
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  guess=parse_qs(urlparse(self.path).query).get('token',[''])[0]
  if guess==SECRET: code,body=200,FLAG
  elif SECRET.startswith(guess): code,body=202,'prefix accepted'
  else: code,body=403,'prefix rejected'
  self.send_response(code); self.end_headers(); self.wfile.write(body.encode())
 def log_message(self, format: str, *args: object) -> None: pass
if __name__=='__main__': HTTPServer(('127.0.0.1',8091),H).serve_forever()
