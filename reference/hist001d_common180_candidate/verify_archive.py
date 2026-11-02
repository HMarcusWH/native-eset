#!/usr/bin/env python3
"""Check exact source and input hashes, frozen outputs, and clean archive member inventory."""
from __future__ import annotations
import hashlib,json,zipfile,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EXCLUDED={'MANIFEST_SHA256.json'}

def files():
    out={}
    for p in sorted(ROOT.rglob('*')):
        if p.is_dir():continue
        if any(s in {'__pycache__','.pytest_cache'} for s in p.parts) or p.suffix=='.pyc':continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in EXCLUDED:continue
        if p.is_symlink():raise ValueError('symlink')
        out[rel]=sha(p)
    return out

def main():
    assert len(list((ROOT/'inputs').glob('March180_source_nodes_*.be64')))==6
    assert not list(ROOT.rglob('*11520*'))
    expected=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
    assert expected['schema']=='HIST001D_COMMON_180_ARCHIVE_MANIFEST_V1'
    assert expected['files']==files(), 'exact file hash/manifest discrepancy'
    pins=json.loads((ROOT/'RESULT_SHA256.json').read_text())
    for name,h in pins['results'].items():assert sha(ROOT/name)==h, 'result hash mismatch '+name
    assert sha(ROOT/'inputs/original_source_46_frozen.zip')=='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
    with zipfile.ZipFile(ROOT/'inputs/original_source_46_frozen.zip') as z:assert z.testzip() is None
    assert not any('proxy_narrow' in p for p in expected['files'])
    print('SOURCE180_ARCHIVE_VERIFY_PASS',len(expected['files']),'files',len(pins['results']),'result hashes')
if __name__=='__main__':main()
