#!/usr/bin/env python3
"""Strict fixed-member SHA receipt verifier and optional clean replay."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PARENT_SHA='fa2d720a34ad80644c7e9f9a96b2ac9eab2e9ad0aa4955d8357f05b934e9cd6f'
NESTED_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def audit(replay=False):
    mpath=ROOT/'MANIFEST_SHA256.json'
    doc=json.loads(mpath.read_bytes())
    expected=doc.get('files')
    if doc.get('manifest_version')!=1 or not isinstance(expected,dict):raise ValueError('unsupported manifest schema')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts and p.name not in {'MANIFEST_SHA256.json','.DS_Store'} and p.suffix!='.pyc'}
    if set(expected)!=actual:raise ValueError('unexpected/missing artifact inventory '+str(sorted(actual^set(expected))))
    for key,checksum in expected.items():
        p=ROOT/key
        if p.is_symlink() or not p.is_file() or sha(p)!=checksum:raise ValueError('file SHA mismatch '+key)
    if sha(ROOT/'inputs/first_node_rational_parent.zip')!=PARENT_SHA:raise ValueError('bad frozen parent')
    if sha(ROOT/'inputs/frozen_smooth_shadow_gradient_parent.zip')!=NESTED_SHA:raise ValueError('bad frozen nested parent')
    if replay:
        for script in ('crossing_node_producer.py','crossing_node_independent.py','adversarial_crossing_node.py'):
            proc=subprocess.run([sys.executable,script],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONHASHSEED':'0'},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
            if proc.returncode:
                raise ValueError('FAIL_CLOSED replay '+script+'\n'+proc.stderr[-1500:])
            print('REPLAY_PASS',script)
            for key,checksum in expected.items():
                if key.startswith('results/') and sha(ROOT/key)!=checksum:raise ValueError('result reexecution SHA mismatch '+key)
    print('MANIFEST_PASS',len(expected),'RESULTS_PASS',len([x for x in expected if x.startswith('results/')]))
    return True
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');args=p.parse_args();audit(args.replay)
