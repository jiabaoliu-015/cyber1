#!/usr/bin/env python3
"""Exploit repeated AES-GCM encryption nonce by recovering reused CTR keystream."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data'/'uplink_vault.json'; d=json.loads(p.read_text())
k=bytes.fromhex(d['known_plaintext_hex']); kc=bytes.fromhex(d['known_ciphertext_hex']); tc=bytes.fromhex(d['target_ciphertext_hex'])
if len(k) != len(kc) or len(k) < len(tc):
 raise ValueError('known plaintext/ciphertext must cover the entire target ciphertext')
stream=bytes(a^b for a,b in zip(k,kc)); print(bytes(a^b for a,b in zip(tc,stream)).decode())
