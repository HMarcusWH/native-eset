#!/usr/bin/env python3
"""Read-only SHA manifest and candidate scope check (not a proof by itself)."""
from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent

def verify():
    m=json.loads((P/'MANIFEST_SHA256.json').read_text())
    if m.get('manifest_version')!=1 or not isinstance(m.get('files'),dict):raise ValueError('missing exact file inventory')
    files={p.relative_to(P).as_posix():p for p in P.rglob('*') if p.is_file() and p.name!='MANIFEST_SHA256.json' and not any(x in {'__pycache__','.pytest_cache','logs'} for x in p.relative_to(P).parts)}
    if files.keys()!=m['files'].keys():
        raise ValueError('source archive file inventory mismatch: '+repr((sorted(set(files)-set(m['files'])),sorted(set(m['files'])-set(files)))))
    for name,v in m['files'].items():
        if hashlib.sha256(files[name].read_bytes()).hexdigest()!=v:raise ValueError('file SHA corruption: '+name)
    f=P/'inputs/frozen_smooth_shadow_gradient_parent.zip'
    if hashlib.sha256(f.read_bytes()).hexdigest()!='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18':raise ValueError('wrong original parent source')
    for name in ['results/all180_aggregate.json','results/crossing_band_producer.json','results/crossing_band_independent.json']:
        rec=json.loads((P/name).read_bytes())
        for field in ['physical_provider_admitted','original_full_H_or_root_count_proved']:
            if field in rec and rec[field] is not False:raise ValueError('forbidden claim: '+name)
    print('MANIFEST_AND_CLAIM_CEILING_PASS',len(files))

if __name__=='__main__':verify()
