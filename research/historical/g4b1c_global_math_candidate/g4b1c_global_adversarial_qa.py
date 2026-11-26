#!/usr/bin/env python3
"""Fail-closed tamper QA on new LOCAL finite-proxy global-root candidate.

Each altered witness is re-canonically SHA-pinned to itself and fed to the
independent verifier; rejection is thus not ONLY an outer hash mismatch.
Integrity controls are not independent proofs of the mathematical lemmas.
"""
from __future__ import annotations
import json,copy,hashlib,tempfile
from pathlib import Path
from g4b1c_global_independent_verifier import independent_replay
ROOT=Path(__file__).resolve().parent
P=ROOT/'G4b1c_Global_Six_Lens_Exactly_One_Finite_Proxy_Real_Root_Candidate_v1.json'
SCHEMA='HIST001_G4B1C_GLOBAL_FINITE_PROXY_ADVERSARIAL_CANDIDATE_QA_V1'

def h(b):return hashlib.sha256(b).hexdigest()
def canon(obj):return (json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()

def cases():
 base=json.loads(P.read_bytes())
 def c(title,mut):
  x=copy.deepcopy(base);mut(x);return title,x
 cs=[
  c('forged_physical_provider',lambda x:x['claims'].__setitem__('physical_provider_admitted',True)),
  c('forged_original_march_root_count',lambda x:x['claims'].__setitem__('independent_original_march_180x120_all_real_root_count_proved',True)),
  c('forged_empirical_holdout',lambda x:x['claims'].__setitem__('heldout_observational_validation','VALIDATED')),
  c('forged_peer_review',lambda x:x['claims'].__setitem__('external_mathematical_peer_review_completed',True)),
  c('switched_source_model_identity',lambda x:x.__setitem__('model_identity','MARCH_180x120')), 
  c('source_kit_sha_changed',lambda x:x['antecedents'].__setitem__('source_nodal.zip','0'*64)),
  c('first_lens_relabelled',lambda x:x['lenses'][0].__setitem__('lens_id','OTHER_LENS')),
  c('first_lens_nodal_hash_altered',lambda x:x['lenses'][0].__setitem__('source_nodal_sha256','a'*64)),
  c('invented_earlier_positive_start',lambda x:x['lenses'][0]['inner_positive_to'].__setitem__('num','1')),
  c('left_positive_cell_removed',lambda x:x['lenses'][0]['strict_positive_left_cover'].pop(0)),
  c('arbitrarily_inflated_left_H_margin',lambda x:x['lenses'][0]['strict_positive_left_cover'][0].__setitem__('H_lower_floor_msun','9999999999999999999999999999')),
  c('arbitrarily_inflated_right_derivative_negativity',lambda x:x['lenses'][0]['strict_negative_derivative_corridor_cover'][0].__setitem__('Hprime_upper_ceil_msun_per_kpc','-99999999999999999999999')),
  c('missing_derivative_cell',lambda x:x['lenses'][0]['strict_negative_derivative_corridor_cover'].pop(0)),
  c('forged_narrow_root_radius',lambda x:x['lenses'][0]['narrow_unique_L'].__setitem__('num','1')),
 ]
 return cs

def main():
 results=[]
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'self_rehashed_tampered_candidate.json'
  for name,obj in cases():
   raw=canon(obj);p.write_bytes(raw)
   try:
    independent_replay(p,expected_sha=h(raw))
    results.append({'attack':name,'rejected':False,'reason':'FORGED_CANDIDATE_ACCEPTED'})
   except (ValueError,AssertionError,KeyError,TypeError,ZeroDivisionError,OSError) as exc:
    results.append({'attack':name,'rejected':True,'reason':str(exc)[:240]})
 if not all(x['rejected'] for x in results):raise RuntimeError('adversarial failure: self-rehashed forged candidate passed')
 result={'schema':SCHEMA,'status':'PASS_SCOPED_CANDIDATE_TAMPER_REJECTION_ONLY',
 'base_producer_sha256':h(P.read_bytes()),'tamper_count':len(results),'rejected_count':sum(x['rejected'] for x in results),
 'attacks':results,'claims':{'proof_of_correct_mathematics_from_tamper_count':False,'original_march_numeric_provider':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}}
 data=canon(result)
 filename=ROOT/'G4b1c_Global_Adversarial_Tamper_QA_v1.json';filename.write_bytes(data)
 print(json.dumps({'result':str(filename),'sha256':h(data),'rejected':result['rejected_count'],'total':len(results)},indent=2))
if __name__=='__main__':main()
