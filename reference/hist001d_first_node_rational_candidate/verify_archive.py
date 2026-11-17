#!/usr/bin/env python3
"""Read-only SHA manifest and optional exact bundled result replay."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    a=argparse.ArgumentParser();a.add_argument('--replay',action='store_true');args=a.parse_args()
    m=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
    inventory={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.name not in ('MANIFEST_SHA256.json','README.md') and not p.suffix in ('.pyc',)}
    expected=set(m['files'])
    if inventory!=expected:raise SystemExit('MANIFEST_INVENTORY_MISMATCH '+str({'missing':sorted(expected-inventory),'unexpected':sorted(inventory-expected)}))
    for name,digest in m['files'].items():
        p=ROOT/name
        if p.is_symlink() or not p.is_file() or sha(p)!=digest:raise SystemExit('MANIFEST_SHA_FAIL '+name)
    for name,dig in m['result_sha256'].items():
        if sha(ROOT/name)!=dig:raise SystemExit('RESULT_HASH_FAIL '+name)
    print('MANIFEST_PASS',len(expected),flush=True)
    if args.replay:
        for script,result in [('first_node_certificate.py','results/first_node_candidate_producer.json'),('independent_first_node.py','results/first_node_candidate_independent.json'),('adversarial_first_node.py','results/first_node_adversarial.json')]:
            p=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,capture_output=True,text=True,timeout=90)
            if p.returncode:raise SystemExit('REPLAY_FAIL '+script+' '+p.stderr[-400:])
            if sha(ROOT/result)!=m['result_sha256'][result]:raise SystemExit('REPLAY_HASH_MISMATCH '+script)
            print('REPLAY_PASS',script,flush=True)
    print('ALL_CERTIFICATES_PASS; SCIENTIFIC_NONPROMOTION',flush=True)
if __name__=='__main__':main()
