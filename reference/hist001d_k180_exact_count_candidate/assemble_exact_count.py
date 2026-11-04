#!/usr/bin/env python3
"""Assemble all source-conditional exact-count claims without importing Bessel producer."""
from pathlib import Path
import hashlib,json
from knot_count_contract import verify_all,PARENT_SHA,ORIGINAL_SOURCE_SHA
ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def source_receipts():
    def load(prefix):return [json.loads((ROOT/'results'/f'{prefix}_{j}.json').read_bytes()) for j in range(6)]
    return load('inputs_lens'),load('local_lens'),load('exclusion_lens'),load('independent_lens')
def assemble():
    inputs,loc,excl,ind=source_receipts()
    rows=verify_all(inputs,loc,excl,ind)
    obj={'schema':'HIST001D_SELECTED_MSTAR_KNOT_SAFE_SIX_BAND_EXACT_16_QUADRATURE_REMAINDER_ZEROS_CANDIDATE_V1',
      'selected_mathematical_model_only':True,
      'target_function':'D(A)=FROZEN_SOURCE_WEIGHT_MSTAR_DERIVATIVE_SAMPLES_MINUS_SELECTED_CONTINUOUS_MSTAR_PROJECTION',
      'zero_count_each_lens':{row['lens']:row['exact_local_mathematical_zero_count'] for row in rows},
      'exact_16_across_six_independent_mathematical_functions':True,
      'total_exact_zeros_on_six_specified_A_bands':16,
      'proof_scope':'KNOT_SPLIT_16_LOCAL_UNIQUENESS_BRACKETS_PLUS_ALL_COMPLEMENTARY_GAP_EXCLUSIONS',
      'source_original_46plus3_sha256':ORIGINAL_SOURCE_SHA,
      'protected_parent_zero16_v1r2_sha256':PARENT_SHA,
      'source_inputs':{f'inputs_lens_{j}.json':sha((ROOT/'results'/f'inputs_lens_{j}.json').read_bytes()) for j in range(6)},
      'local_uniqueness_receipts':{f'local_lens_{j}.json':sha((ROOT/'results'/f'local_lens_{j}.json').read_bytes()) for j in range(6)},
      'zero_exclusion_receipts':{f'exclusion_lens_{j}.json':sha((ROOT/'results'/f'exclusion_lens_{j}.json').read_bytes()) for j in range(6)},
      'independent_arithmetic_receipts':{f'independent_lens_{j}.json':sha((ROOT/'results'/f'independent_lens_{j}.json').read_bytes()) for j in range(6)},
      'coverage':rows,
      'original_March_Einstein_root_count_certified':False,
      'selected_Mstar_full_H_root_count_certified':False,
      'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
      'external_mathematical_review_passed':False,'scientific_authority_promoted':False}
    p=ROOT/'results/exact_count_aggregate.json'
    p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    print('EXACT16_AGGREGATE',p,sha(p.read_bytes()))
    return obj
if __name__=='__main__':assemble()
