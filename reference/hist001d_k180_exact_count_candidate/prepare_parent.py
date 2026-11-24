#!/usr/bin/env python3
"""Recover and SHA-check historical source-only math dependencies for full protected replay.

Reads the prior v1r2 ZIP, then its immutable 2026-11-04 targeted parent.
Never fetches arbitrary remote content or alters an existing repository branch.
"""
from __future__ import annotations
import hashlib,io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT_SHA='23251d6c5a153e8cb149143f7fcf25f02c21097e6f625b3c46fdb9645fef96e1'
TARGET_SHA='0eec91a8e531516529a58cf811685581233aba6d5bc8150c9897b50de88ae651'
REQUIRED={
 'inputs/cancel_parent_v1.zip',
 *{f'results/targeted_lens_{j}.json' for j in range(6)},
 'reference/hist001d_k180_targeted_candidate/targeted_refine.py',
 'reference/hist001d_k180_cancel_aware_candidate/signed_affine_producer.py',
 'reference/hist001d_k180_cancel_aware_candidate/affine_kernel.py',
 'reference/hist001d_k180_inter_node_candidate/inter_node_producer.py',
 'reference/hist001d_k180_bessel_integral_candidate/real_integral_bessel.py',
 'reference/hist001d_k180_bessel_integral_candidate/source_audit.py',
}
def sha(b):return hashlib.sha256(b).hexdigest()
def prepare():
    raw=(ROOT/'inputs/zero16_parent_v1r2.zip').read_bytes()
    if sha(raw)!=PARENT_SHA:raise ValueError('protected zero16 parent SHA')
    p=zipfile.ZipFile(io.BytesIO(raw))
    with zipfile.ZipFile(io.BytesIO(p.read('inputs/targeted_parent_v1.zip'))) as t:
        if sha(p.read('inputs/targeted_parent_v1.zip'))!=TARGET_SHA:raise ValueError('targeted parent SHA')
        man=json.loads(t.read('MANIFEST_SHA256.json'))
        if man.get('physical_provider_admitted') is not False or man.get('empirical_validation')!='NOT_ESTABLISHED':
            raise ValueError('targeted parent claim gate')
        for path,digest in man['files'].items():
            if sha(t.read(path))!=digest:raise ValueError('targeted parent member '+path)
        if not REQUIRED.issubset(t.namelist()):raise ValueError('required source absent')
        for path in sorted(REQUIRED):
            dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True)
            content=t.read(path)
            if dest.is_file() and dest.read_bytes()!=content:raise ValueError('source conflict '+path)
            dest.write_bytes(content)
    print('SOURCE_PARENT_PREPARED',len(REQUIRED))
if __name__=='__main__':prepare()
