#!/usr/bin/env python3
"""Fail-closed mutation testing of an exact-rational source/claim certificate.

These tests are QA for the integrity and authorization checks, not proof of M''/M'''.
"""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from independent_verify import verify
ROOT=Path(__file__).resolve().parents[1]

def tampered(original, name):
    x=copy.deepcopy(original);l=x['lenses'][0]
    if name=='parent_sha':x['parent_sha256']='0'*64
    elif name=='source_sha':x['source_sha256']='f'*64
    elif name=='physical':x['physical_provider_admitted']=True
    elif name=='total_H':x['original_March_total_H_or_root_count_certified']=True
    elif name=='offgrid_clipping':x['source_offgrid_clip_branch_certified']=True
    elif name=='full_H_root_error':x['full_H_root_error_guard_met']=True
    elif name=='D2d_substitution':x['D2d_11520_shadow_substituted']=True
    elif name=='float_error':x['float_operation_error_certified']=True
    elif name=='smooth_error':x['source_true_continuum_gradient_error_certified']=True
    elif name=='empirical':x['empirical_validation']='ESTABLISHED'
    elif name=='review_claim':x['external_mathematical_review']='VERIFIED'
    elif name=='cell_subdivision':x['subdivisions_per_original_cell']=2
    elif name=='source_node_hash':l['source_node_sha256']='c'*64
    elif name=='source_scalar':l['source_scalar_hex']['Md']='0x1.2000000000000p+35'
    elif name=='M2_cell_zero':l['M2_by_cell_upper_ceil'][7]='0'
    elif name=='M3_cell_zero':l['M3_by_cell_upper_ceil'][10]='0'
    elif name=='gradient_cell_zero':l['ideal_exact_sample_gradient_error_upper_ceil'][10]='0'
    elif name=='global_M3_zero':l['global_M3_upper_ceil']='0'
    elif name=='first_error_zero':l['first_exact_gradient_error_upper_ceil']='0'
    elif name=='removed_lens':x['lenses'].pop()
    elif name=='reordered_lenses':x['lenses'][:2]=x['lenses'][1::-1]
    else:raise ValueError('unknown test case')
    return x

def run():
    data=json.loads((ROOT/'results/source_bound_M2_M3_rational_producer.json').read_text())
    names=['parent_sha','source_sha','physical','total_H','offgrid_clipping','full_H_root_error',
           'D2d_substitution','float_error','smooth_error','empirical','review_claim','cell_subdivision',
           'source_node_hash','source_scalar','M2_cell_zero','M3_cell_zero','gradient_cell_zero',
           'global_M3_zero','first_error_zero','removed_lens','reordered_lenses']
    verdicts=[]
    for n in names:
        good=False
        try: verify(candidate=tampered(data,n),write=False)
        except (ValueError,TypeError,KeyError,AssertionError) as e:
            good=True
            verdicts.append({'case':n,'status':'REJECTED','reason':str(e)[:250]})
        if not good:raise RuntimeError('ADVERSARIAL_MUTATION_NOT_REJECTED:'+n)
    doc={'schema':'HIST001D_MARCH_C3_M2_M3_SUPREMA_ADVERSARIAL_QA_V1','status':'ALL_MUTATIONS_REJECTED',
         'cases':verdicts,'count':len(names),'mathematical_proof_claim':False,'physical_provider_admitted':False}
    out=ROOT/'results/adversarial_qa.json';out.write_text(json.dumps(doc,sort_keys=True,indent=2)+'\n')
    print('ADVERSARIAL_REJECTED',len(names),'SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=='__main__':run()
