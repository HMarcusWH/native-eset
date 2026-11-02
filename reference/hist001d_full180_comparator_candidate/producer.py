"""Exact rational full-root coverage for a DEFINED March 180-node component-interpolant comparator.
This is NOT a theorem for an underlying continuum density or an original off-grid floating source evaluation.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
from full180_math import load,ceil_frac
ROOT=Path(__file__).resolve().parent
GUARDS={
 'J0822+1828':('1.784','0.030'),
 'J0915+4211':('1.403','0.030'),
 'J0930+2855':('4.624','0.030'),
 'J1021+2028':('1.130','0.030'),
 'J1111+2234':('3.954','0.030'),
 'J1135+3720':('2.182','0.030'),
}

def pair(x):return {'num':str(x.numerator),'den':str(x.denominator)}
def check_lens(m,max_depth=18):
 jlist=[i for i in range(179) if m.original_H[i]>0>m.original_H[i+1]]
 assert len(jlist)==1
 j=jlist[0]
 c=F(GUARDS[m.lid][0]);d=F(GUARDS[m.lid][1]);a,b=c-d,c+d
 assert m.r[j]<a<b<m.r[j+1]
 hl=m.H_point(j,a,64)[0];hu=m.H_point(j,b,64)[1]
 du=m.dH_upper(j,a,b,64)
 assert 0<hl and hu<0 and du<0
 # Exact equality at full radial boundaries, exact three-way cross cell partition.
 bases=[]
 for i in range(179):
  if i<j:bases.append((i,'whole',m.r[i],m.r[i+1],'POS'))
  elif i==j:
   bases.append((i,'left',m.r[i],a,'POS'))
   bases.append((i,'right',b,m.r[i+1],'NEG'))
  else:bases.append((i,'whole',m.r[i],m.r[i+1],'NEG'))
 leaves=[];maxdep=0;min_pos=None;max_neg=None
 for i,part,l,u,sign in bases:
  stack=[(0,0,l,u)]
  while stack:
   depth,k,x,y=stack.pop()
   lower,upper=m.H_box(i,x,y,bits=56)
   if (lower>0 if sign=='POS' else upper<0):
    leaves.append([i,part,depth,k,sign])
    maxdep=max(maxdep,depth)
    if sign=='POS':min_pos=lower if min_pos is None else min(min_pos,lower)
    else:max_neg=upper if max_neg is None else max(max_neg,upper)
   else:
    if depth>=max_depth:raise ValueError('UNRESOLVED at '+m.lid+': '+str((i,part,depth,k)))
    mid=(x+y)/2
    stack.extend(((depth+1,2*k+1,mid,y),(depth+1,2*k,x,mid)))
 assert min_pos is not None and max_neg is not None and min_pos>0 and max_neg<0
 # Verify source-knot mathematical-model matching is a bounded input correspondence only.
 worst=F(0)
 for i in range(180):
  k=min(178,i);l,u=m.H_point(k,m.r[i],bits=64)
  worst=max(worst,abs(l-m.original_H[i]),abs(u-m.original_H[i]))
 assert worst<F(1)
 # Exact radius bisection: each midpoint must have a strict outward rational sign.
 rlo,rhi=a,b
 for _ in range(20):
  mid=(rlo+rhi)/2
  lower,upper=m.H_point(j,mid,bits=72)
  if lower>0:rlo=mid
  elif upper<0:rhi=mid
  else:raise ValueError('UNRESOLVED refined root midpoint for '+m.lid)
 assert m.H_point(j,rlo,bits=72)[0]>0 and m.H_point(j,rhi,bits=72)[1]<0
 source_pl_root=m.r[j]+m.h[j]*m.original_H[j]/(m.original_H[j]-m.original_H[j+1])
 assert rhi<source_pl_root, 'source PL root not sufficiently separated (do NOT infer a root-shift without proof)'
 separation_lower=source_pl_root-rhi
 return {'lens':m.lid,'source_input_hashes':m.cert_inputs,'root_cell':j,'guard_left':pair(a),'guard_right':pair(b),
  'root_H_positive_left_lower':pair(hl),'root_H_negative_right_upper':pair(hu),'root_dH_strict_upper':pair(du),
  'minimum_positive_cell_lower':pair(min_pos),'maximum_negative_cell_upper':pair(max_neg),
  'source_knot_difference_upper':pair(worst),'all_original_knot_differences_below_one_msun':True,
  'refined_root_left':pair(rlo),'refined_root_right':pair(rhi),'source_original_PL_root_exact':pair(source_pl_root),
  'root_separation_from_original_sampled_PL_strict_lower_kpc':pair(separation_lower),
  'full_root_count_not_transferred_between_new_comparator_and_original_sampled_interpolant':True,
  'all_source_radial_cells':179,'strict_sign_leaf_count':len(leaves),'maximum_split_depth':maxdep,'strict_sign_leaves':leaves,
  'has_exactly_one_root_in_DEFINED_MARCH_180_COMPONENT_COMPARATOR':True,
  'no_original_March_180x120_continuum_root_count_claim':True}

def run():
 out=[]
 for m in load():
  x=check_lens(m);out.append(x)
  print('FINITE_COMP_CERT',m.lid,'POS/NEG leaves',x['strict_sign_leaf_count'],'depth',x['maximum_split_depth'], 'dH upper ceiling Bsuns/kpc',ceil_frac(F(int(x['root_dH_strict_upper']['num']),int(x['root_dH_strict_upper']['den']))/10**9),flush=True)
 doc={'schema':'HIST001D_MARCH180_EXPLICIT_COMPONENT_PL_COMPOSITION_ONE_ROOT_MATH_CANDIDATE_V1',
      'model':'DEFINED_MARCH_SOURCE_FROZEN_BPL_DPL_S0PL_qA_TPL__NOT_ORIGINAL_OFFGRID_SOURCE',
      'source_parent_zip_sha256':'8178dfb07aa4c070b5f10e7de2c1e4130ffe777efb08d57382f4aae9cfcd4132',
      'original_source_lock_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
      'definition':'H*=B_PL(R)+D_PL(R)+S0_PL(min(RMAX,R/sqrt(q_PL(R))))-T_PL(R); q_PL=(qb*B_PL+qd*D_PL)/(B_PL+D_PL); all original source node floats exact binary64',
      'domain':'[exact_binary64_0.02,120] kpc',
      'certifier':'exact_rational_outward_56_bit_sqrt_H_cell_positive_negative_and_64_bit_derivative_corridor',
      'number_of_lenses':len(out),'strict_sign_leaf_count':sum(x['strict_sign_leaf_count'] for x in out),'lenses':out,
      'claim_ceiling':{'source_frozen_defined_component_comparator_exactly_one_real_root_per_lens_IF_SOURCE_LOCKS_AND_ARITHMETIC_SOUND':True,
       'original_180_120_source_offgrid_numeric_error':False,'original_full_continuum_root_uniqueness':False,
       'source_derived_shadow_continuum':False,'physical_Weyl_lensing':False,'native_v172_equivalence':False,'holdout':False,
       'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED','Theory_State_mutated':False}}
 raw=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode()
 (ROOT/'results'/'exact_defined_frozen180_comparator_producer.json').write_bytes(raw)
 print('PRODUCER_SHA256',hashlib.sha256(raw).hexdigest())
 return doc
if __name__=='__main__':run()
