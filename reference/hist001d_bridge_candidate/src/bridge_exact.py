#!/usr/bin/env python3
"""Source-pinned, conditional pointwise DIFFERENCE lower bounds, not source error theorem.

The March object is the mathematical piecewise-linear interpolant of six frozen 180-node
binary64 numerical output residual arrays. The DIFFERENT finite D2d-style mathematical
proxy is used ONLY through previously archived strict pointwise endpoint enclosures.
"""
from __future__ import annotations
import bisect
import hashlib
import io
import json
import math
import struct
import sys
import zipfile
from fractions import Fraction as F
from pathlib import Path

MARCH_SHA='7b4e29bd4048a8558af5e7985a9a6ada529e27a7ef4eb068f892f5f3a7bc24b1'
NARROW_SHA='138669c971b07652d24b76c34e32cb0a74c3cbc893de3d254c7a5170eec08bb5'
SIGNS_SHA='5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899'
MARCH_REPORT_SHA='b845dd11e262a8fab93ce120928a8e5f50d0ff35bd93d26dd00727388367d7cc'
SOURCE_NODAL_SHA='804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973'
ORIGINAL_SOURCE_SHA='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE_LOCK='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
IDS=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
SCHEMA='HIST001D_G4B1C_SOURCE_LOCKED_POINTWISE_MARCH_PL_VS_FINITE_PROXY_DISCREPANCY_LOWER_v1'

class ProofInputError(ValueError): pass

def sha(data):return hashlib.sha256(data).hexdigest()
def required(ok,msg):
    if not ok:raise ProofInputError(msg)
def rational(obj):
    required(type(obj) is dict and set(obj)=={'num','den'},'rational pair schema')
    required(all(type(obj[k]) is str for k in ('num','den')),'rational pair type')
    out=F(int(obj['num']),int(obj['den']))
    required(out.denominator>0,'rational denominator')
    return out
def pair(q): return {'num':str(q.numerator),'den':str(q.denominator)}
def floor(q):return q.numerator//q.denominator

def verified_zip(path,expected):
    raw=Path(path).read_bytes()
    required(sha(raw)==expected,'outer input ZIP digest changed: '+str(path))
    z=zipfile.ZipFile(io.BytesIO(raw))
    info=z.infolist(); names=[x.filename for x in info]
    required(len(set(names))==len(names) and all(not x.is_dir() and not x.filename.startswith('/')
      and '\\' not in x.filename and all(y not in ('','.','..') for y in x.filename.split('/')) for x in info),
      'unsafe ZIP member names')
    required(z.testzip() is None,'ZIP CRC failure')
    return z

def read_inputs(root):
    march=verified_zip(root/'inputs/march_180_grid.zip',MARCH_SHA)
    narrow=verified_zip(root/'inputs/proxy_narrow.zip',NARROW_SHA)
    march_raw=march.read('original_march_180_grid_exact_dyadic_sampled_residual_diagnostic_v1.json')
    signs_raw=narrow.read('input/narrow_endpoint_signs.json')
    required(sha(march_raw)==MARCH_REPORT_SHA,'original recorded March outputs changed')
    required(sha(signs_raw)==SIGNS_SHA,'mathematical sign source certificate changed')
    required(sha(narrow.read('input/source_nodal.zip'))==SOURCE_NODAL_SHA,'source nodal kit changed')
    report=json.loads(march_raw);signs=json.loads(signs_raw)
    required(report['source_candidate']=='ra0_gated_geometry_sigmoid_reg_v2','original historical candidate changed')
    required(report['original_sha']['source_sha256']==ORIGINAL_SOURCE_SHA and report['original_sha']['source_lock_sha256']==SOURCE_LOCK,'original source lock changed')
    required(signs['frozen_46plus3_source_lock_SHA256']==SOURCE_LOCK,'proxy source lock changed')
    required(len(report['lenses'])==len(signs['lenses'])==6,'six lens count drift')
    return march,narrow,report,signs

def derive(root:Path):
    march,narrow,report,signs=read_inputs(root)
    result=[]
    for lid,obs,th in zip(IDS,report['lenses'],signs['lenses'],strict=True):
        required(obs['lens_id']==th['lens_id']==lid,'lens order changed')
        raw=march.read('sampled_binary64/'+lid.replace('+','p')+'.R_H_be64.bin')
        required(len(raw)==180*16 and sha(raw)==obs['sampled_binary64_pair_sha256'],'March nodal bytes drift')
        pairs=[(F.from_float(r),F.from_float(h)) for r,h in struct.iter_unpack('>dd',raw)]
        xx=[p[0] for p in pairs]
        required(xx[0]==F.from_float(0.02) and xx[-1]==F(120) and all(xx[j]<xx[j+1] for j in range(179)), 'March radius grid invalid')
        required(all(h!=0 for r,h in pairs),'unexpected numerical node exactly zero')
        flipped=[j for j in range(179) if (pairs[j][1]>0)!=(pairs[j+1][1]>0)]
        required(len(flipped)==1,'source 180-sample sign-chart root count changed')
        j=flipped[0]
        root_num=pairs[j][0]-pairs[j][1]*(pairs[j+1][0]-pairs[j][0])/(pairs[j+1][1]-pairs[j][1])
        required(root_num==rational(obs['exact_dyadic_piecewise_linear_intervals'][0]['unique_piecewise_linear_root_exact']), 'previous independent March root changed')
        endpts=[]
        b=th['rational_bracket_radius'];L=rational(b['lower']);U=rational(b['upper'])
        required(U-L==F(1,10) and xx[0]<L<U<xx[-1],'bad 0.10 kpc interval')
        for side,R,cert_key in [('LEFT',L,'left_strict_positive_exact_enclosure'),('RIGHT',U,'right_strict_negative_exact_enclosure')]:
            idx=bisect.bisect_right(xx,R)-1
            idx=max(0,min(178,idx))
            xl,yl=pairs[idx];xr,yr=pairs[idx+1]
            required(xl<=R<=xr,'interval missing sample query')
            marchH=yl+(yr-yl)*(R-xl)/(xr-xl)
            cert=th[cert_key]
            required(rational(cert['R_exact'])==R and cert['all_intermediate_bounds_outward_rational'] is True, 'proxy endpoint bound not admitted')
            lo=F(int(cert['H_lower_msun_integer']));hi=F(int(cert['H_upper_msun_integer']))
            required(lo<=hi,'invalid strict endpoint interval')
            if side=='LEFT':required(cert['H_lower_strict_positive'] and lo>0,'left proxy sign not positive')
            else:required(cert['H_upper_strict_negative'] and hi<0,'right proxy sign not negative')
            gap=max(F(0),lo-marchH,marchH-hi)
            direct=('MARCH_BELOW_PROXY_INTERVAL' if marchH<lo else ('MARCH_ABOVE_PROXY_INTERVAL' if marchH>hi else 'INTERVALS_OVERLAP'))
            endpts.append({'side':side,'R_exact_kpc':pair(R),'grid_left_index':idx,
              'march_H_exact_interpolated_msun':pair(marchH),'proxy_H_lower_msun_integer':str(lo.numerator),
              'proxy_H_upper_msun_integer':str(hi.numerator),
              'proxy_minus_march_abs_difference_lower_exact_msun':pair(gap),
              'difference_lower_floor_msun':str(floor(gap)),'disposition':direct})
        best=max(endpts,key=lambda x:rational(x['proxy_minus_march_abs_difference_lower_exact_msun']))
        delta=rational(best['proxy_minus_march_abs_difference_lower_exact_msun'])
        required(delta>0,'not proved pointwise disjoint for every lens')
        sep=max(F(0),L-root_num,root_num-U)
        result.append({'lens_id':lid, 'march_source_180_sign_flips':1,
          'march_interpolant_unique_root_kpc':pair(root_num),'finite_proxy_narrow_bracket_lower':pair(L),
          'finite_proxy_narrow_bracket_upper':pair(U),'guaranteed_root_position_separation_lower_kpc':pair(sep),
          'exact_endpoint_discrepancies':endpts,'max_certified_endpoint_difference_lower_exact_msun':pair(delta),
          'max_certified_endpoint_difference_floor_msun':str(floor(delta)),
          'max_endpoint_with_strict_disjoint_interval':best['side'],
          'claim_scope':'LOWER_BOUND_OF_TWO_DEFINED_MATHEMATICAL_OBJECTS_NOT_SOURCE_NUMERICAL_ERROR'})
    return {'schema':SCHEMA,'status':'PASS_SCOPED_CONDITIONAL_EXACT_POINTWISE_MODEL_DIFFERENCE_LOWER_BOUNDS',
      'input_sha':{'march_180_grid.zip':MARCH_SHA,'proxy_narrow.zip':NARROW_SHA,'narrow_endpoint_signs.json':SIGNS_SHA,
                    'source_nodal.zip':SOURCE_NODAL_SHA,'original_46plus3':SOURCE_LOCK},
      'description':'For each lens a SHA-pinned original-March recorded 180-node piecewise-linear residual is compared AT THE SAME exact rational radius to an independently previously certified mathematical finite-proxy pointwise residual interval. Sup-norm error between these defined functions over [0.02,120] must be at least the max pointwise lower bound (conditional on source-certificate mathematical soundness).',
      'lenses':result,'claims':{'pointwise_discrepancy_lower_bounds_between_defined_models':True,
      'finite_proxy_antecedent_mathematical_soundness_externally_peer_reviewed':False,
      'uniform_upper_error_bound_between_models':False,'March_180x120_continuum_discretization_error_certified':False,
      'original_March_continuum_root_count_certified':False,'source_nodal_finite_proxy_equals_March_numerical_model':False,
      'physical_Weyl_provider_admitted':False,'Native_v172_equivalence_proved':False,
      'new_holdout_or_empirical_validation':'NOT_ESTABLISHED','canonical_theory_state_mutated':False}}

def main():
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    data=derive(root);out=root/'results/bridge_discrepancy_producer.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    out.write_bytes(raw)
    print('PRODUCER PASS',sha(raw),'lenses',len(data['lenses']))
    for x in data['lenses']:
        print(x['lens_id'],x['max_endpoint_with_strict_disjoint_interval'],x['max_certified_endpoint_difference_floor_msun'],float(rational(x['guaranteed_root_position_separation_lower_kpc'])))
if __name__=='__main__':main()
