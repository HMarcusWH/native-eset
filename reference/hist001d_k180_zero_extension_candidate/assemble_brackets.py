#!/usr/bin/env python3
"""Build canonical 16 disjoint IVT *existence* brackets from source-locked signs.

This is NOT an upper count or a physical Einstein root computation.
"""
from __future__ import annotations
import hashlib,io,json,zipfile
from pathlib import Path
from claim_guard import LENS_NAMES,EXPECTED_COUNTS,EXTRA_INDEX,count_sign_flips,validate
ROOT=Path(__file__).resolve().parents[2]
PARENT_SHA='0eec91a8e531516529a58cf811685581233aba6d5bc8150c9897b50de88ae651'
def sha(b):return hashlib.sha256(b).hexdigest()

def assemble():
    raw=(ROOT/'inputs/targeted_parent_v1.zip').read_bytes()
    if sha(raw)!=PARENT_SHA:raise ValueError('parent source SHA')
    z=zipfile.ZipFile(io.BytesIO(raw))
    old=json.loads(z.read('results/targeted_aggregate.json'))
    lenses=[json.loads(z.read(f'results/targeted_lens_{j}.json')) for j in range(6)]
    shas=[sha(z.read(f'results/targeted_lens_{j}.json')) for j in range(6)]
    prod=json.loads((ROOT/'results/extra_sign_witnesses.json').read_bytes())
    indep=json.loads((ROOT/'results/extra_fraction_verify.json').read_bytes())
    validate(prod,indep,old,lenses,shas,PARENT_SHA)
    extra={v['lens']:v for v in prod['lenses']}
    output=[]
    for j,rec in enumerate(lenses):
        anchors=[{'index':a['index'],'A_exact':a['A'],'strict_sign':a['strict_sign'],
                  'source_receipt':'PR63_ORIGINAL_VERIFIED_ANCHOR'} for a in rec['anchors']]
        if j in EXTRA_INDEX:
            q=extra[LENS_NAMES[j]]
            anchors.append({'index':q['index'],'A_exact':q['A_exact'],
                            'strict_sign':q['strict_sign'],
                            'source_receipt':'THIS_EXTENSION_512_AND_192_BIT_STRICT_POSITIVE'})
        anchors=sorted(anchors,key=lambda x:x['index'])
        flips=count_sign_flips([(x['index'],x['strict_sign']) for x in anchors])
        if flips!=EXPECTED_COUNTS[j]:raise ValueError('unexpected sign count')
        brackets=[]
        for left,right in zip(anchors,anchors[1:]):
            if left['strict_sign']!=right['strict_sign']:
                brackets.append({'left_A_exact':left['A_exact'],'right_A_exact':right['A_exact'],
                                 'left_index':left['index'],'right_index':right['index'],
                                 'left_sign':left['strict_sign'],'right_sign':right['strict_sign'],
                                 'topological_claim':'AT_LEAST_ONE_INTERIOR_IVT_ZERO'})
        if len(brackets)!=flips:raise ValueError('bracket count mismatch')
        output.append({'lens':LENS_NAMES[j],'distinct_zeros_at_least':flips,
                       'all_brackets_disjoint_open':True,
                       'source_prior_lens_receipt_sha256':shas[j],
                       'strict_sign_anchors':anchors,'zero_existence_brackets':brackets})
    if sum(x['distinct_zeros_at_least'] for x in output)!=16:raise ValueError('lower count')
    return {'schema':'HIST001D_SIXTEEN_ZERO_CANONICAL_EXISTENCE_BRACKETS_V1',
            'parent_targeted_release_sha256':PARENT_SHA,
            'total_distinct_quadrature_zeros_at_least':16,
            'exact_count_proved':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'lenses':output}

def main():
    obj=assemble()
    path=ROOT/'results/augmented_zero_brackets.json'
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print('EXACT_BRACKET_ASSEMBLY_PASS',len(obj['lenses']),'lenses',
          sum(len(x['zero_existence_brackets']) for x in obj['lenses']),'IVT brackets')
if __name__=='__main__':main()
