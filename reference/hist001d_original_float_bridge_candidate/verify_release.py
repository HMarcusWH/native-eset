#!/usr/bin/env python3
"""Verify protected release hash manifest, nonclaims and saved postprocessing receipts.

Use --full for clean data-dependent end-to-end reproduction and byte comparison.
No automatic physical scientific claim promotion from this verifier.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from claim_guard import validate_claims
from float_bridge import SAT_SHA,H_SHA,sha

def verify(root,full=False):
    manifest=json.loads((root/'MANIFEST_SHA256.json').read_bytes())
    if manifest.get('schema')!='HIST001D_MARCH_ORIGINAL_FINAL_FLOAT_POSTPROCESSING_SOURCE_LOCKED_V1':raise ValueError('manifest schema')
    if not isinstance(manifest.get('files'),dict) or len(manifest['files'])<10:raise ValueError('manifest incomplete')
    for n,digest in manifest['files'].items():
        p=Path(n)
        if p.is_absolute() or '..' in p.parts or not (root/p).is_file():raise ValueError('file path')
        if sha((root/p).read_bytes())!=digest:raise ValueError('file corruption: '+n)
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and not p.name.endswith('.pyc')}
    if actual-set(manifest['files'])!={'MANIFEST_SHA256.json'}:raise ValueError('unmanifested files or omitted members')
    sat=root/'inputs/HIST001D_K180_SATURATED_REVIEW_REPAIR_V1R1.zip'
    hist=root/'inputs/HIST001D_FULL_H_BRIDGE_v1r1.zip'
    if sha(sat.read_bytes())!=SAT_SHA or sha(hist.read_bytes())!=H_SHA:raise ValueError('original parent hash')
    rec=json.loads((root/'results/original_float_bridge_receipt.json').read_bytes())
    validate_claims(rec)
    i=json.loads((root/'results/independent_float_bridge_receipt.json').read_bytes())
    if i.get('node_reproductions')!=1080 or i.get('source_returned_roots_reproduced')!=6 or i.get('all_lens_source_array_exact_matches') is not True:raise ValueError('independent summary')
    qa=json.loads((root/'results/adversarial_float_qa.json').read_bytes())
    if len(qa.get('cases',[]))!=22 or any(x['result']!='REJECTED' for x in qa['cases']) or qa.get('all_rejected') is not True:raise ValueError('adversarial ledger')
    if full:
        from float_bridge import run as produce
        from independent_float_check import check as independent
        from adversarial_qa import run as mutation_qa
        with tempfile.TemporaryDirectory() as tmp:
            outfile=Path(tmp)/'result.json'
            replay=produce(sat,hist,outfile)
            if outfile.read_bytes()!=(root/'results/original_float_bridge_receipt.json').read_bytes():raise ValueError('producer not byte-identical')
            independent_result=independent(replay,sat,hist)
            saved_independent=(root/'results/independent_float_bridge_receipt.json').read_bytes()
            if (json.dumps(independent_result,sort_keys=True,indent=2)+'\n').encode()!=saved_independent:raise ValueError('independent replay mismatch')
            if (json.dumps(mutation_qa(replay),sort_keys=True,indent=2)+'\n').encode()!=(root/'results/adversarial_float_qa.json').read_bytes():raise ValueError('QA replay mismatch')
    return {'status':'PASS_NONPROMOTING','full_source_replay':bool(full),'manifest_member_count':len(manifest['files']),'node_count':1080,'lens_count':6,
        'receipt_sha256':sha((root/'results/original_float_bridge_receipt.json').read_bytes()),'no_physical_validation':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--full',action='store_true')
    a=p.parse_args();print(json.dumps(verify(a.root,a.full),sort_keys=True,indent=2))
