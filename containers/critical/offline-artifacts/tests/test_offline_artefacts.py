#!/usr/bin/env python3
import json,subprocess,sys,time
from pathlib import Path
D=Path(__file__).resolve().parents[1]
def run(a): return subprocess.run(a,capture_output=True,text=True,check=False)
b=run([str(D/'scripts/build_remaining_d.sh')]); assert b.returncode==0,b.stderr
e=run([str(D/'artifact3_binary'),'--verify','MED-9A1D-67EF-082B-C390']); assert e.returncode==0 and 'Authentic execution path confirmed' in e.stdout
fixture=json.loads((D/'data/uplink_vault.json').read_text())
assert len(bytes.fromhex(fixture['known_plaintext_hex'])) >= len(bytes.fromhex(fixture['target_ciphertext_hex']))
s=run([sys.executable,str(D/'solvers/crypto_solver.py')]); assert s.returncode==0 and s.stdout.strip()=='THREAD_02=evidence-evidence',s.stderr
p=subprocess.Popen([sys.executable,str(D/'source/oracle_lab/oracle.py')]); time.sleep(.2)
try:
 o=run([sys.executable,str(D/'solvers/oracle_solver.py')]); assert o.stdout.strip()=='EYE-THREAD-02'
finally: p.terminate(); p.wait()
print('Remaining Slice D acceptance checks: PASS')
