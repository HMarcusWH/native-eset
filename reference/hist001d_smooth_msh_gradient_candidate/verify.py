#!/usr/bin/env python3
"""Exact file/result integrity and bounded same-environment stage replay."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
    m=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
    if set(m)!={'schema','files'} or m['schema']!='HIST001D_SOURCE_SMOOTH_GRADIENT_CANDIDATE_MANIFEST_V1':raise ValueError('manifest schema')
    expected=m['files']
    seen={p.relative_to(ROOT).as_posix():digest(p) for p in ROOT.rglob('*') if p.is_file() and not (p.name.endswith('.pyc') or '.pytest_cache' in p.parts or '__pycache__' in p.parts or p.name=='MANIFEST_SHA256.json')}
    if seen!=expected:raise ValueError(f'manifest source/bytes changed: missing={set(expected)-set(seen)}, extra={set(seen)-set(expected)}, mismatched={[p for p in set(seen)&set(expected) if seen[p]!=expected[p]]}')
    hashes=json.loads((ROOT/'RESULT_HASHES.json').read_text())
    if hashes['schema']!='HIST001D_SOURCE_SMOOTH_GRADIENT_CANDIDATE_OUTPUT_SHA256_V1':raise ValueError('result schema')
    for p,sha in hashes['sha256'].items():
        if digest(ROOT/p)!=sha:raise ValueError('unexpected result SHA '+p)
    print('GRADIENT_BUNDLE_MANIFEST_PASS',len(seen),'RESULT_SHA',len(hashes['sha256']))
    return 0
def stage(name):
    scripts={'producer':'producer.py','independent':'independent_verify.py','qa':'adversarial_qa.py'}
    if name not in scripts:raise ValueError('invalid stage')
    subprocess.run([sys.executable,str(ROOT/'src'/scripts[name])],cwd=ROOT,check=True)
    return check()
if __name__=='__main__':
    pa=argparse.ArgumentParser(); g=pa.add_mutually_exclusive_group(required=True)
    g.add_argument('--check',action='store_true');g.add_argument('--stage',choices=['producer','independent','qa'])
    a=pa.parse_args()
    if a.check:check()
    else:stage(a.stage)
