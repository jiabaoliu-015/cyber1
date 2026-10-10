#!/usr/bin/env python3
"""Uplink Vault: AES-GCM nonce reuse fixture generator (synthetic lab data)."""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data'/'uplink_vault.json'
KEY=bytes.fromhex('00112233445566778899aabbccddeeff'); NONCE=bytes.fromhex('0102030405060708090a0b0c')
KNOWN=b'HEADER: THREAD_02 ARCHIVE RECOVERY'; SECRET=b'THREAD_02=evidence-evidence';
def main():
 assert len(KNOWN) >= len(SECRET), 'known plaintext must cover the entire target ciphertext'
 a=AESGCM(KEY); k=a.encrypt(NONCE,KNOWN,None)[:-16]; s=a.encrypt(NONCE,SECRET,None)[:-16]
 OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps({'algorithm':'AES-GCM','nonce_hex':NONCE.hex(),'known_plaintext_hex':KNOWN.hex(),'known_ciphertext_hex':k.hex(),'target_ciphertext_hex':s.hex()},indent=2)+'\n')
 print(OUT)
if __name__=='__main__': main()
