#!/usr/bin/env python3
import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parents[1]; A=D/'scripts'/'assemble_evidence.py'; R=D/'scripts'/'reset.sh'
def run(args): return subprocess.run(args,text=True,capture_output=True,check=False)
r=run([str(R)]); assert r.returncode==0
assert (D/'evidence/THREAD_02.missing').exists()
bad=run([sys.executable,str(A),'--thread-02','wrong']); assert bad.returncode==1 and 'remains incomplete' in bad.stdout
truncated=run([sys.executable,str(A),'--thread-02','THREAD_02=evidence-eviden']); assert truncated.returncode==1
ok=run([sys.executable,str(A),'--thread-02','THREAD_02=evidence-evidence']); assert ok.returncode==0
for item in ('THREAD_01.txt','THREAD_02.txt','THREAD_03.txt','THREAD_04.txt','INCIDENT ARCHIVE SYSTEM NOTICE','Observation status: ACTIVE.','CTF{the_web_marks_john_liability}') : assert item in ok.stdout,item
r2=run([str(R)]); assert r2.returncode==0
print('Slice E clean reset and evidence assembly: PASS')
