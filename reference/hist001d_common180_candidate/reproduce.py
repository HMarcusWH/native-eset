#!/usr/bin/env python3
"""Reexecute frozen source, independent rational proof, and adversarial QA, checking exact output SHA after every stage."""
from __future__ import annotations
from pathlib import Path
import hashlib,subprocess,sys,json
ROOT=Path(__file__).resolve().parent
PINS=json.loads((ROOT/'RESULT_SHA256.json').read_text())['results']
SCRIPTS=[('source','capture_original_180.py','results/source180_capture.json'),
 ('producer','frozen_kernel_exact_producer.py','results/frozen_stencil_all_real_envelope_producer.json'),
 ('independent','frozen_kernel_independent_checker.py','results/frozen_stencil_all_real_envelope_independent.json'),
 ('qa','frozen_kernel_adversarial_qa.py','results/frozen_stencil_adversarial_qa.json')]
for name,script,output in SCRIPTS:
    print('REPLAY_START',name,flush=True)
    subprocess.run([sys.executable,str(ROOT/'src'/script)],cwd=ROOT,check=True,timeout=110)
    raw=(ROOT/output).read_bytes()
    h=hashlib.sha256(raw).hexdigest()
    if h!=PINS[output]:raise RuntimeError('REPLAY_SHA_MISMATCH '+name)
    print('REPLAY_EXACT_HASH_PASS',name,h,flush=True)
subprocess.run([sys.executable,str(ROOT/'verify_archive.py')],cwd=ROOT,check=True,timeout=20)
print('SOURCE180_ALL_STAGES_PASS')
