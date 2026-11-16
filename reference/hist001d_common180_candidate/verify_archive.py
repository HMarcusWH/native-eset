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
    if len(list((ROOT/'inputs').glob('March180_source_nodes_*.be64')))!=6:
        raise ValueError('SIX_FROZEN_SOURCE_NODE_FILES_REQUIRED')
    if list(ROOT.rglob('*11520*')):
        raise ValueError('UNRELATED_11520_PROXY_SOURCE_PRESENT')
    expected=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
    if expected.get('schema')!='HIST001D_COMMON_180_ARCHIVE_MANIFEST_V1':
        raise ValueError('SOURCE180_MANIFEST_SCHEMA_MISMATCH')
    if expected.get('files')!=files():
        raise ValueError('SOURCE180_SOURCE_OR_RESULT_MANIFEST_MISMATCH')
    pins=json.loads((ROOT/'RESULT_SHA256.json').read_text())
    for name,h in pins['results'].items():
        if sha(ROOT/name)!=h:raise ValueError('SOURCE180_RESULT_SHA_MISMATCH '+name)
    if sha(ROOT/'inputs/original_source_46_frozen.zip')!='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e':
        raise ValueError('SOURCE180_PROTECTED_PARENT_SHA_MISMATCH')
    with zipfile.ZipFile(ROOT/'inputs/original_source_46_frozen.zip') as z:
        if z.testzip() is not None:raise ValueError('SOURCE180_PROTECTED_PARENT_ZIP_CRC_FAIL')
    if any('proxy_narrow' in p for p in expected['files']):
        raise ValueError('SOURCE180_FORBIDDEN_PROXY_INPUT_IN_MANIFEST')
    print('SOURCE180_ARCHIVE_VERIFY_PASS',len(expected['files']),'files',len(pins['results']),'result hashes')
if __name__=='__main__':main()
