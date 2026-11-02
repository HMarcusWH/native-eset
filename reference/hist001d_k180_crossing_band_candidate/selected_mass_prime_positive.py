#!/usr/bin/env python3
"""Separate conditional all-real positivity audit of selected mathematical M*'(r).

This is NOT a physical-density admissibility statement. The whole-band
K180-continuum sign proof does not depend on this auxiliary result.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'hist001d_k180_root_aperture_candidate'))
from root_aperture_certifier import load_external,Lens,euler_gamma  # noqa: E402

def evaluate(external:Path,index:int,max_depth:int=18):
    if max_depth<0 or max_depth>25:raise ValueError('invalid dyadic refinement cap')
    c,i,a=load_external(external)
    lens=Lens(c[index],i[index],a[index],euler_gamma())
    passed=[];unresolved=[];attempts=0
    def check(lo,hi,depth):
        nonlocal attempts
        attempts+=1
        Mp,_=lens.derivatives(lo,hi)
        if Mp.low()>0:
            passed.append((lo,hi,Mp.low()))
            return
        if depth>=max_depth:
            unresolved.append((lo,hi,Mp.low()))
            return
        mid=(lo+hi)/2
        check(lo,mid,depth+1);check(mid,hi,depth+1)
    for j in range(len(lens.r)-1):check(lens.r[j],lens.r[j+1],0)
    if passed:
        if passed[0][0]!=lens.r[0] or passed[-1][1]!=lens.r[-1] or any(
            passed[k][1]!=passed[k+1][0] for k in range(len(passed)-1)
        ):
            raise ValueError('incomplete or overlapping derivative proof')
    return {
       'lens':lens.name,'selected_mathematical_Mstar_prime_positive_everywhere':not unresolved,
       'source_frozen_exact_binary64_nodes':180,
       'all_real_verified_positive_dyadic_cells':len(passed),
       'machine_interval_evaluations':attempts,
       'unresolved_cells':len(unresolved),
       'minimum_positive_Mprime_bound_exact_n_over_d':[
           str(min(x[2] for x in passed).numerator),str(min(x[2] for x in passed).denominator)] if passed else None,
       'source_180_node_sha256':c[index]['node_sha256'],
       'physical_density_source_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
       'mathematical_scope':'SELECTED_HISTORICAL_MSTAR_ONLY',
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--external-zip',type=Path,required=True)
    p.add_argument('--index',type=int,choices=range(6),required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--max-depth',type=int,default=18)
    a=p.parse_args()
    obj=evaluate(a.external_zip,a.index,a.max_depth)
    a.out.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    print('SELECTED_MSTAR_PRIME_ALL_REAL',obj['lens'],obj['selected_mathematical_Mstar_prime_positive_everywhere'],
          obj['all_real_verified_positive_dyadic_cells'],flush=True)
    if not obj['selected_mathematical_Mstar_prime_positive_everywhere']:
        raise SystemExit('UNRESOLVED: cannot promote derivative positivity')
if __name__=='__main__':main()
