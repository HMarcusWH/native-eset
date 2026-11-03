#!/usr/bin/env python3
"""Independent Fraction BV replay with binary-search sqrt (not producer's isqrt).
For the selected mathematical M_* only; all aperture bands, original mesh geometry.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import json,zipfile,struct,hashlib,argparse,io
SQ=1<<160
SAT_ACTUAL='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
BAND_PARENT='cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'

def sha(b):return hashlib.sha256(b).hexdigest()
def floor(v):return v.numerator//v.denominator
def ceil(v):return -(-v.numerator//v.denominator)
def rootbox(v):
    if v<0:raise ValueError('negative radicand')
    N=v.numerator*SQ*SQ;D=v.denominator
    lo=0;hi=SQ
    while hi*hi*D<=N:hi*=2
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid*mid*D<=N:lo=mid
        else:hi=mid
    if lo*lo*D==N:return Q(lo,SQ),Q(lo,SQ)
    return Q(lo,SQ),Q(lo+1,SQ)
def kernel(A,r):
    if A>=r:return Q(1),Q(1)
    t=1-(A/r)**2
    lo,hi=rootbox(t)
    return 1-hi,1-lo

def verify(root:Path):
    sat_bytes=(root/'inputs/saturation_parent_v1r1.zip').read_bytes()
    band_bytes=(root/'inputs/crossing_band_parent_v1r2.zip').read_bytes()
    if sha(sat_bytes)!=SAT_ACTUAL or sha(band_bytes)!=BAND_PARENT:
        raise ValueError('changed protected historical parent')
    S=zipfile.ZipFile(io.BytesIO(sat_bytes))
    par=zipfile.ZipFile(io.BytesIO(S.read('original_parent.zip')))
    A=zipfile.ZipFile(io.BytesIO(par.read('inputs/frozen_source_parent.zip')))
    B=zipfile.ZipFile(io.BytesIO(A.read('inputs/original_march_D120_q_parent.zip')))
    C=zipfile.ZipFile(io.BytesIO(B.read('inputs/original_march180_parent_v1r1.zip')))
    capture=json.loads(C.read('results/source180_capture.json'))['lenses']
    bands=json.loads(zipfile.ZipFile(io.BytesIO(band_bytes)).read('results/whole_band_certificate.json'))['lenses']
    result=[]
    for j in range(6):
        cap=capture[j];band=bands[j]
        data=json.loads((root/f'results/continuous_lens_{j}.json').read_text())
        saved=json.loads((root/f'results/bv_band_lens_{j}.json').read_text())
        if cap['lens_id']!=data['lens_id'] or cap['lens_id']!=band['lens'] or cap['lens_id']!=saved['lens']:
            raise ValueError('wrong source lens identity')
        raw=C.read('inputs/'+cap['node_file'])
        if sha(raw)!=cap['node_sha256']:raise ValueError('original radial node changed')
        rows=list(struct.iter_unpack('>8d',raw))
        if len(rows)!=180:raise ValueError('180 source nodes')
        rr=[Q.from_float(t[0]) for t in rows]
        weight=[Q.from_float(t[1]) for t in rows]
        ideal=[(rr[1]-rr[0])/2]+[(rr[i+1]-rr[i-1])/2 for i in range(1,179)]+[(rr[-1]-rr[-2])/2]
        Alo=Q(*map(int,band['A_band_left_exact_n_over_d']))
        Ahi=Q(*map(int,band['A_band_right_exact_n_over_d']))
        if not 0<Alo<Ahi:raise ValueError('invalid A band')
        kernelterm=Q(0);curvatureterm=Q(0); Pl=Q(0);Pu=Q(0)
        for q in data['panels']:
            i=q['cell'];lo=Q(q['lo']);hi=Q(q['hi']);h=hi-lo;H=rr[i+1]-rr[i]
            if not (0<=i<179 and rr[i]<=lo<hi<=rr[i+1]):raise ValueError('out-of-cell panel')
            upper=Q(q['Mprime_upper_micro'],10**6)
            lower=Q(q['Mprime_lower_micro'],10**6)
            c=Q(q['Msecond_abs_ceil'])
            Astar=min(max(Alo,lo),Ahi)
            delta=kernel(Astar,lo)[1]-kernel(Astar,hi)[0]
            if delta<0:raise ValueError('kernel monotonicity')
            kernelterm+=H*upper*delta/2
            curvatureterm+=H*h*c*kernel(Ahi,lo)[1]/2
            Pl+=h*lower*kernel(Alo,hi)[0]
            Pu+=h*upper*kernel(Ahi,lo)[1]
        nodal=json.loads((root/f'results/lens_{j}.json').read_text())['lenses'][0]['nodes']
        weightterm=sum((abs(weight[i]-ideal[i])*Q(nodal[i]['selected_Mprime_interval'][1])*kernel(Ahi,rr[i])[1] for i in range(180)),Q(0))
        E=kernelterm+curvatureterm+weightterm
        if not (E<=saved['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun'] and
           kernelterm<=saved['uniform_band_error_kernel_variation_ceiling_Msun'] and
           curvatureterm<=saved['uniform_band_error_Mprime_variation_ceiling_Msun'] and
           weightterm<=Q(saved['uniform_band_original_weight_rounding_ceiling_micro_Msun'],10**6) and
           Pl>=saved['P_mathematical_continuum_all_A_band_integer_Msun_enclosure'][0] and
           Pu<=saved['P_mathematical_continuum_all_A_band_integer_Msun_enclosure'][1]):
            raise ValueError(f'original BV release understated at {cap["lens_id"]}')
        result.append({'lens':cap['lens_id'],'independent_BV_witness_pass':True,'subpanels':len(data['panels'])})
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args()
    r=verify(a.root)
    data={'schema':'HIST001D_BV_INDEPENDENT_BINARY_SEARCH_SQRT_V1','all_pass':True,'results':r,
        'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    (a.root/'results/verify_bv.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    print('INDEPENDENT_BV_ALL_SIX_PASS',sum(x['subpanels'] for x in r))
if __name__=='__main__':main()
