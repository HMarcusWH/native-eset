#!/usr/bin/env python3
"""LOCAL mathematical *candidate* full real-radius root-count certification.

Scope only: original-source-nodal finite D2d piecewise-linear shadow proxy;
exact stored parameters, continuum finite Hernquist and full-azimuth disk,
mathematical G4a sigma. NO original March numeric algorithm or physics.
"""
from __future__ import annotations
import json,hashlib,sys
from pathlib import Path
from fractions import Fraction as Q
from g4b1c_global_math_lib import Lens,Derivative,fpair,pair,floor_to,ceil_to,PI_LOW,PI_HIGH,RMIN,RMAX
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from source_input_adapter import input_from_zip
SOURCE_SHA={
 'source_nodal.zip':'804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973',
 'prepeak_v5.json':'f499ee992b762f6da5e774d95b00588e96cf9ee17e4bcaa4bda7ad30628b5963',
 'narrow_signs_v1.json':'5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899',
 'narrow_uniqueness_v1.json':'2d5d797329d9dd77c4bd3e5c5c3d385edf79e1147f332554d70a735d87eb1d06',
 'narrow_uniqueness_independent_v1.json':'6b47c9a013f522be52ffe4afad09a03eb797ddb2b7fffaafbca29996ec82ef84',
 'inner_v3.json':'8a3f7da5288080aa1e575e31cbb72dd114dc1668ad258639674916307bfed0ac',
 'outer_v4.json':'c8e4af053bc4765dd119337ab5da302cd42a73d9eb52015909ccceb68dffe5ac',
}
PIVOTS=(Q(3,2),Q(6,5),Q(7,2),None,None,Q(17,10))
STEP=Q(1,6)
SCHEMA='HIST001_G4B1C_GLOBAL_FINITE_PROXY_SIX_SINGLE_REAL_ROOT_CANDIDATE_v1'
MODE='EXACT_MATHEMATICAL_FINITE_D2D_SOURCE_NODAL_PROXY_ONLY_NOT_MARCH_180X120'

def read_input():
 for name,expected in SOURCE_SHA.items():
  if hashlib.sha256((ROOT/'input'/name).read_bytes()).hexdigest()!=expected:raise ValueError('SHA-pinned input mismatch '+name)
 def read(n):return json.loads((ROOT/'input'/n).read_bytes())
 p=read('prepeak_v5.json');s=read('narrow_signs_v1.json');n=read('narrow_uniqueness_v1.json');v=read('narrow_uniqueness_independent_v1.json');inner=read('inner_v3.json');outer=read('outer_v4.json')
 if not(p['conditional_mathematical_finite_proxy_all_real_zeros_before_density_peak'] and p['mathematical_unique_root_or_root_count_certified'] is False):raise ValueError('old root-support scope altered')
 if n['claims']['complete_middle_domain_root_count_certified'] or v['claims']['global_middle_domain_root_count']!='NOT_PROVED':raise ValueError('narrow precedent improperly promoted')
 if len(p['lenses'])!=len(s['lenses'])!=len(n['lenses'])!=len(v['lenses'])!=len(inner['lenses'])!=len(outer['lenses'])!=6:raise ValueError('wrong antecedent lens cardinality')
 return input_from_zip(ROOT/'input/source_nodal.zip'),p,s,n,v,inner,outer

def root_count():
 records,pre,signs,narrow,indep,inner,outer=read_input()
 output=[]
 for i,(source,pr,s,n,iv,ins,outs,piv) in enumerate(zip(records,pre['lenses'],signs['lenses'],narrow['lenses'],indep['lenses'],inner['lenses'],outer['lenses'],PIVOTS,strict=True)):
  lid=source['lens_id'];digest=source['expected_nodal_sha256']
  if any(z['lens_id']!=lid for z in (pr,s,n,iv,ins,outs)):raise ValueError('lens order in antecedent differs')
  if pr['source_nodal_sha256']!=digest or s['source_nodal_digest']!=digest or n['source_nodal_sha256']!=digest or iv['source_nodal_sha256']!=digest:raise ValueError('nodal identity drift')
  Lw=fpair(pr['inner_strict_positive_until_exact']);Uw=fpair(pr['outer_strict_negative_from_exact'])
  Ln=fpair(s['rational_bracket_radius']['lower']);Un=fpair(s['rational_bracket_radius']['upper'])
  if ins['entire_real_Rmin_to_new_T_strict_H_positive_conditional'] is not True or outs['entire_real_outer_band_strict_negative'] is not True:raise ValueError('missing strict source negative/positive premises')
  if Lw!=fpair(ins['new_disk_assisted_positive_to']) or Uw!=fpair(outs['new_certified_negative_from_exact']):raise ValueError('full outer/inner inherited radii changed')
  if not (RMIN<Lw<Ln<Un<Uw<RMAX and Un-Ln==Q(1,10)):raise ValueError('noncontiguous source-band geometry')
  if not (n['Hprime_strict_negative_every_real_R_in_bracket'] and iv['independent_strict_all_real_derivative_negative'] and s['IVT_at_least_one_zero_in_open_bracket_conditional'] and s['left_strict_positive_exact_enclosure']['H_lower_strict_positive'] and s['right_strict_negative_exact_enclosure']['H_upper_strict_negative']):raise ValueError('previous bracket not proven')
  pivot=piv if piv is not None else Lw
  if not(Lw<=pivot<=Ln):raise ValueError('invalid pivot')
  lens=Lens(source,s,bits=34);dv=Derivative(lens,nb=130,nd=60,ns=110)
  positive=[];stack=[(Lw,pivot)] if Lw<pivot else []
  tries=0
  while stack:
   a,b=stack.pop();tries+=1
   if tries>300:raise ValueError('positive proof cell budget exceeded')
   lower,upper,_=lens.H(a,b,40)
   if lower>0:
    positive.append({'L':pair(a),'U':pair(b),'H_lower_floor_msun':str(floor_to(lower))})
   else:
    if b-a<Q(1,100000):raise ValueError('positive proof budget unresolved '+lid)
    m=(a+b)/2;stack.extend([(m,b),(a,m)])
  positive.sort(key=lambda cell:fpair(cell['L']))
  curr=Lw
  for z in positive:
   if fpair(z['L'])!=curr or fpair(z['U'])<=curr or int(z['H_lower_floor_msun'])<=0:raise ValueError('positive prefix cover gap or nonstrict')
   curr=fpair(z['U'])
  if curr!=pivot:raise ValueError('left positive proof does not end at pivot')
  deriv=[]
  for label,a,b in (('LEFT_DECREASING',pivot,Ln),('RIGHT_DECREASING',Un,Uw)):
   curr=a
   while curr<b:
    nxt=min(b,curr+STEP)
    bound,_=dv.Hprime_upper(curr,nxt,48)
    if bound>=0:raise ValueError('unresolved sign of Hprime '+lid+' '+label+' '+str(curr))
    deriv.append({'region':label,'L':pair(curr),'U':pair(nxt),'Hprime_upper_ceil_msun_per_kpc':str(ceil_to(bound))})
    curr=nxt
   if curr!=b:raise ValueError('derivative corridor lacks full coverage')
  deriv.sort(key=lambda z:(z['region'],fpair(z['L'])))
  output.append({'lens_id':lid,'source_nodal_sha256':digest,'inner_positive_to':pair(Lw),'outer_negative_from':pair(Uw),
   'narrow_unique_L':pair(Ln),'narrow_unique_U':pair(Un),'pivot':pair(pivot),
   'strict_positive_left_cover':positive,'strict_negative_derivative_corridor_cover':deriv,
   'left_positive_cell_count':len(positive),'derivative_corridor_cell_count':len(deriv),
   'all_R_rmin_to_120_contiguous_proof_groups':True,'exactly_one_mathematical_finite_proxy_real_zero_on_full_domain_conditional':True,
   'original_March_numerical_root_count': 'NOT_ESTABLISHED','physical_provider_admitted':False})
 doc={'schema':SCHEMA,'status':'NEW_LOCAL_UNREVIEWED_CONDITIONAL_GLOBAL_FINITE_PROXY_ROOT_COUNT_CANDIDATE',
 'model_identity':MODE,'frozen_original_march_46plus3_sha':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
 'antecedents':SOURCE_SHA,
 'method':{'source_mass_shells':'exact cubic source nodal interpolation and exact Hernquist cumulative spherical mass; monotone finite-cylinder shell angular kernel bounds','disk_mass':'exact monotonic full-azimuth angular rectangles; exp(-x) alternating Taylor with rational dyadic range reduction; pi Machin series',
 'source_density':'6 x 11520 exact stored binary64 nodal nonnegative piecewise-linear mathematical proxy','pi_bounds':[pair(PI_LOW),pair(PI_HIGH)],
 'direct_H_mass_mesh':40,'direct_H_sqrt_bits':34,'derivative_Bt_mesh':130,'derivative_Dt_mesh':60,'derivative_S_t_mesh':110,'derivative_baryon_mass_mesh':48,'derivative_step':[pair(STEP)],
 'proof_combination':'source-verified v3 strict H>0 [rmin,Lw], new strict H>0 [Lw,pivot], new Hprime<0 [pivot,Ln] and H(Ln)>0, independently source-verified unique narrow root [Ln,Un], new Hprime<0 [Un,Uw] and H(Un)<0, source-verified v4 strict H<0 [Uw,120]'},
 'lenses':output,
 'claims':{'global_exactly_one_REAL_ROOT_per_lens_conditional_ON_FINITE_PROXY_and_ANTECEDENT_THEOREMS':True,
  'independent_original_march_180x120_all_real_root_count_proved':False,'external_mathematical_peer_review_completed':False,
  'physical_same_source_Weyl_admitted':False,'Native_v172_field_equivalence_proved':False,
  'heldout_observational_validation':'NOT_ESTABLISHED','physical_provider_admitted':False,'canonical_theory_state_mutated':False}}
 return doc

def main():
 out=root_count();data=(json.dumps(out,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode();p=ROOT/'G4b1c_Global_Six_Lens_Exactly_One_Finite_Proxy_Real_Root_Candidate_v1.json';p.write_bytes(data)
 print(json.dumps({'out':str(p),'SHA256':hashlib.sha256(data).hexdigest(),'lenses':[{'lens':d['lens_id'],'strict_H_left_cells':d['left_positive_cell_count'],'negative_Hprime_cells':d['derivative_corridor_cell_count']} for d in out['lenses']]},indent=2))
if __name__=='__main__':main()
