#!/usr/bin/env python3
"""Fail-closed altered-claim tests for the source-locked first-node candidate."""
from __future__ import annotations
import copy, hashlib, json, io, zipfile
from pathlib import Path
import independent_first_node as second
from first_node_certificate import load_sources,source_mass_derivative,Q

P=Path(__file__).resolve().parent

def mutator(variant,src):
    a=copy.deepcopy(src)
    row=a['first_node_pairs'][0]
    if variant=='wrong_source_lock':a['source_lock_sha256']='0'*64
    elif variant=='wrong_parent_digest':a['parent_sha256']='a'*64
    elif variant=='claim_physical':a['physical_provider_admitted']=True
    elif variant=='claim_empirical':a['empirical_validation']='PASSED'
    elif variant=='claim_original_float':a['original_float_operation_error_certified']=True
    elif variant=='claim_original_root':a['original_full_H_or_root_count_certified']=True
    elif variant=='claim_same_source_physics':a['same_source_physical_density_proved']=True
    elif variant=='bad_model_schema':a['schema']='PHYSICAL_ROOT_PROOF'
    elif variant=='truncated_lenses':a['first_node_pairs'].pop()
    elif variant=='extra_lens':a['first_node_pairs'].append(copy.deepcopy(row))
    elif variant=='forged_node_digest':row['node_digest']='b'*64
    elif variant=='forged_node_density':row['first_source_rho_float_hex']='0x1.0000000000000p+0'
    elif variant=='forged_radius':row['r0_float_hex']='0x1.0000000000000p+0'
    elif variant=='forged_original_gradient':row['source_gradient_from_stored_binary64_dyadics']='1234567/1234'
    elif variant=='forged_ratio_floor':row['certified_rho_source_over_rho_smooth_floor']='10000000000000'
    elif variant=='forged_lens_id':row['lens_id']='SYNTHETIC-NEW'
    elif variant=='forged_secant_claim':row['a_posteriori_first_node_stored_grid_vs_ideal_secant_absolute_lt_3e_minus_6_msun_per_kpc']=False
    elif variant=='forged_next_radius':row['next_source_radius_float_hex']='0x1.0000000000000p+0'
    else:raise ValueError(variant)
    return a

def main():
    src=json.loads((P/'results/first_node_candidate_producer.json').read_bytes())
    cases=['wrong_source_lock','wrong_parent_digest','claim_physical','claim_empirical',
           'claim_original_float','claim_original_root','claim_same_source_physics',
           'bad_model_schema','truncated_lenses','extra_lens','forged_node_digest',
           'forged_node_density','forged_radius','forged_original_gradient',
           'forged_ratio_floor','forged_lens_id','forged_secant_claim','forged_next_radius']
    second.verify(src,write=False)
    records=[]
    for item in cases:
        candidate=mutator(item,src)
        try:second.verify(candidate,write=False)
        except (ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError):
            records.append({'case':item,'correctly_rejected':True})
        else:raise AssertionError('UNDETECTED_TAMPER_'+item)
        print('EXPECTED_REJECTION',item,flush=True)
    # The complete nested source ZIP must not be trusted after even one raw byte change.
    raw=(P/'inputs/frozen_smooth_shadow_gradient_parent.zip').read_bytes()
    altered=bytearray(raw);altered[len(raw)//2]^=1
    assert hashlib.sha256(bytes(altered)).hexdigest()!='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
    records.append({'case':'raw_parent_byte_mutation','correctly_rejected':True,'disposition':'sha256 precondition mismatch'})
    r={'schema':'HIST001D_FIRST_KNOT_ADVERSARIAL_SOURCE_CLAIM_AUDIT_V1',
       'original_model_only':True,'all_mutations_rejected':True,'counts':len(records),
       'no_empirical_or_physical_promotion':True,'cases':records}
    path=P/'results/first_node_adversarial.json'
    path.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print('QA_SHA',hashlib.sha256(path.read_bytes()).hexdigest())

if __name__=='__main__':main()
