#!/usr/bin/env python3
"""Verify protected source-lock D120 seam archive and clean-extraction replay.

Does not independently certify real-world physical lensing or a true continuous
full-angle integration. Root corrections are diagnostics of a new frozen-stencil
counterfactual, not original March H root shift error bounds.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCHEMA='HIST001D_ORIGINAL_MARCH180_D120_PERIODIC_SEAM_RELEASE_V1'

def sha(b):return hashlib.sha256(b).hexdigest()

def check(root):
    root=Path(root)
    manifest=json.loads((root/'MANIFEST_SHA256.json').read_text())
    if manifest.get('schema')!=SCHEMA:raise ValueError('wrong release schema')
    if manifest.get('physical_provider_admitted') is not False or manifest.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('physical promotion')
    if manifest.get('source_unchanged') is not True or manifest.get('counterfactual_only') is not True:raise ValueError('claim firewall')
    checks=manifest.get('files')
    if not isinstance(checks,dict) or len(checks)<10:raise ValueError('archive manifest incomplete')
    for name,expected in checks.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():raise ValueError('bad archive path '+name)
        if sha(path.read_bytes())!=expected:raise ValueError('content hash mismatch '+name)
    return len(checks)

def replay(root):
    root=Path(root);check(root)
    code=root/'reference/hist001d_d120_seam_candidate'
    sat=root/'inputs/saturation_v1r1.zip'
    hh=root/'inputs/full_h_v1r1.zip'
    saved=root/'results/seam_source_receipt.json'
    qa=root/'results/seam_adversarial.json'
    with tempfile.TemporaryDirectory(prefix='d120-replay-') as t:
        out=Path(t)/'receipt.json'
        outqa=Path(t)/'qa.json'
        subprocess.run([sys.executable,str(code/'source_seam_replay.py'),'--saturation',str(sat),'--finite-h',str(hh),'--out',str(out)],check=True)
        if out.read_bytes()!=saved.read_bytes():raise ValueError('source replay not byte-identical')
        subprocess.run([sys.executable,str(code/'verify_seam.py'),'--saturation',str(sat),'--finite-h',str(hh),'--receipt',str(out)],check=True)
        subprocess.run([sys.executable,str(code/'adversarial_seam.py'),'--receipt',str(out),'--saturation',str(sat),'--finite-h',str(hh),'--out',str(outqa)],check=True)
        if outqa.read_bytes()!=qa.read_bytes():raise ValueError('QA replay not byte-identical')
        subprocess.run([sys.executable,'-m','pytest','-q',str(root/'tests/historical/test_hist001d_d120_seam_source_free.py')],cwd=root,check=True)
    return {'receipt_sha256':sha(saved.read_bytes()),'qa_sha256':sha(qa.read_bytes()),'audit_pass':True}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--full',action='store_true')
    args=p.parse_args()
    n=check(args.root)
    print('D120_SEAM_MANIFEST_OK',n)
    if args.full:print('D120_SEAM_CLEAN_REPLAY_OK',replay(args.root))
