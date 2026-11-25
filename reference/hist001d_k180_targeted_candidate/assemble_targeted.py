#!/usr/bin/env python3
"""Aggregate and guard six exact source-dependent targeted sign-reversal receipts."""
from __future__ import annotations
import hashlib,io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from witness_contract import LENSES,PARENT,validate_receipt  # noqa: E402

def sha(raw):return hashlib.sha256(raw).hexdigest()

def assemble(receipts):
    if len(receipts)!=len(LENSES):raise ValueError('six lenses required')
    raw=(ROOT/'inputs/cancel_parent_v1.zip').read_bytes()
    if sha(raw)!=PARENT:raise ValueError('original protected parent changed')
    z=zipfile.ZipFile(io.BytesIO(raw))
    checks=[]
    for j,d in enumerate(receipts):
        parent_bytes=z.read(f'results/signed_lens_{j}.json')
        old=json.loads(parent_bytes)
        if sha(parent_bytes)!=d['parent_signed_lens_sha256'] or old['lens']!=LENSES[j] or old['original_180_source_node_sha256']!=d['source_node_sha256']:
            raise ValueError('protected original lens/node/receipt source mismatch')
        checks.append(validate_receipt(d,j))
    return {'schema':'HIST001D_TARGETED_SELECTED_MSTAR_QUADRATURE_SIGN_REVERSAL_AGGREGATE_V1',
            'claims':'AT_LEAST_THE_LISTED_NUMBER_OF_QUADRATURE_REMAINDER_ZEROS_ONLY',
            'lenses':[{**checks[j], 'receipt_sha256':sha((ROOT/'results'/f'targeted_lens_{j}.json').read_bytes())}
                      for j in range(6)],
            'distinct_quadrature_remainder_zeros_at_least':sum(x['zeros_at_least'] for x in checks),
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'Einstein_root_count_proved':False,'quadrature_remainder_unique_zeros_proved':False,
            'global_continuum_root_count_proved':False,'original_March_offgrid_H_proved':False}

def main():
    r=[json.loads((ROOT/'results'/f'targeted_lens_{j}.json').read_bytes()) for j in range(6)]
    out=assemble(r)
    if out['distinct_quadrature_remainder_zeros_at_least']!=10:raise ValueError('wrong source-conditional zero ledger')
    dst=ROOT/'results/targeted_aggregate.json';dst.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('TARGETED_AGGREGATE_PASS',out['distinct_quadrature_remainder_zeros_at_least'],'zero witnesses SHA',sha(dst.read_bytes()))
if __name__=='__main__':main()
