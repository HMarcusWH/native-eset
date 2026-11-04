"""Knot-safe local-uniqueness candidate, no exact global zero count promotion."""
from __future__ import annotations
import json,time,hashlib
from pathlib import Path
from fractions import Fraction as F
from knot_derivative import lens_data,bound_derivative
from quadrature_points import D_at,PAIRLIST
OUT=Path(__file__).resolve().parents[2]/'results'
def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)
def packed(x):return [str(x.lower()),str(x.upper())]
def full_lens(j):
 lens,nodes,leaves,E,t=lens_data(j)
 roots=[]
 for k,(sl,sr) in enumerate(PAIRLIST[j]):
  L,R=F(sl),F(sr)
  dl,dr=D_at(nodes,leaves,L,E),D_at(nodes,leaves,R,E)
  expected=1 if dl.upper()<0<dr.lower() else (-1 if dr.upper()<0<dl.lower() else 0)
  if expected==0:raise ValueError(f'no strict endpoint sign {lens} {k}')
  original_r=[q[0] for q in nodes]
  if any(L<r<=R for r in original_r):raise ValueError('knot crosses narrow bracket')
  pending=[(L,R,0)];accepted=[];maxdepth=0
  while pending:
   a,b,depth=pending.pop()
   deriv,ntouch=bound_derivative(nodes,leaves,a,b)
   right_sign=1 if deriv.lower()>0 else (-1 if deriv.upper()<0 else 0)
   if right_sign!=expected:
    deriv,ntouch=bound_derivative(nodes,leaves,a,b,precise=True)
    right_sign=1 if deriv.lower()>0 else (-1 if deriv.upper()<0 else 0)
   if right_sign==expected:
    accepted.append({'a':str(a),'b':str(b),'depth':depth,
      'Dprime_lower_integer_Msun_per_kpc':floor(deriv.lower()),
      'Dprime_upper_integer_Msun_per_kpc':ceil(deriv.upper()),
      'touching_radial_panels':ntouch})
    maxdepth=max(maxdepth,depth)
   elif depth>=12:
    raise RuntimeError(f'UNKNOWN derivative sign: {lens} k={k} A={[float(a),float(b)]} derivative={[float(deriv.lower()),float(deriv.upper())]}')
   else:
    mid=(a+b)/2
    pending.extend([(mid,b,depth+1),(a,mid,depth+1)])
  accepted.sort(key=lambda q:F(q['a']))
  if F(accepted[0]['a'])!=L or F(accepted[-1]['b'])!=R or any(F(x['b'])!=F(y['a']) for x,y in zip(accepted,accepted[1:])):raise ValueError('coverage')
  min_derivative=min(v['Dprime_lower_integer_Msun_per_kpc'] for v in accepted)
  max_derivative=max(v['Dprime_upper_integer_Msun_per_kpc'] for v in accepted)
  roots.append({'index':k,'a':str(L),'b':str(R),'D_a':packed(dl),'D_b':packed(dr),
   'expected_monotone_derivative':expected,'accepted_panels':len(accepted),'max_dyadic_depth':maxdepth,
   'global_min_derivative_lower_integer_Msun_per_kpc':min_derivative,
   'global_max_derivative_upper_integer_Msun_per_kpc':max_derivative,
   'derivative_panels':accepted,'existence_by_strict_endpoints':True,
   'local_uniqueness_by_monotonic_derivative':True})
  print('CERT',lens,k,'sign',expected,'panels',len(accepted),'maxdepth',maxdepth,'Dp',min_derivative,max_derivative,flush=True)
 obj={'schema':'HIST001D_SELECTED_MSTAR_D_KNOT_FREE_16_LOCAL_UNIQUENESS_CANDIDATE_V1',
      'lens':lens,'original_source_node_sha256':t['source_node_sha256'],
      'inherited_refined_Peano_exact':str(E),
      'source_mathematical_model':'SELECTED_ACCELERATION_EQUIVALENT_MSTAR_ONLY',
      'certified_nonoverlapping_local_unique_zero_brackets':len(roots),
      'roots':roots,'exact_full_band_zero_count_proved':False,
      'all_other_band_subintervals_excluded':False,
      'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 path=OUT/f'local_lens_{j}.json'
 path.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
 print('LENS_JSON',lens,hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
 return obj
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--lens',type=int,choices=range(6))
 args=parser.parse_args()
 started=time.time()
 for j in ([args.lens] if args.lens is not None else range(6)):full_lens(j)
 print('COMPLETE_SECONDS',round(time.time()-started,1),flush=True)
