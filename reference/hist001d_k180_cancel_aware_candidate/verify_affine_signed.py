#!/usr/bin/env python3
"""Independent Fraction and source-hash checks of signed affine-band candidate.

Does not import affine producer/X or special functions. Recomputes all 129
source nodal Q(A) enclosures per lens at distinct dyadic precision,
all aperture panel arithmetic and an independent *symmetric* Peano ceiling.
The producer's narrower signed M'' envelopes are not independently rederived
here; they are conditional on the previous certified inter-node model.
"""
from __future__ import annotations
import hashlib,io,json,struct,zipfile,sys
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'inputs/inter_node_parent_v1.zip'
PRIOR='63c4df7dcc4e5493fe9e2ea667ebb1a7d8ec418a8d03400096eb5fedf53d4691'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
S=1<<160

def sha(x):return hashlib.sha256(x).hexdigest()
def floor(x):return x.numerator//x.denominator
def ceil(x):return -(-x.numerator//x.denominator)
def rootbox(v):
    v=Q(v)
    if v<0:raise ValueError('negative radicand')
    k=isqrt(v.numerator*S*S//v.denominator)
    if k*k*v.denominator==v.numerator*S*S:return Q(k,S),Q(k,S)
    return Q(k,S),Q(k+1,S)
def phibox(A,r):
    if not (A>=0 and r>0):raise ValueError('positive radius')
    if A>=r:return Q(1),Q(1)
    lo,hi=rootbox(1-(A/r)**2)
    return 1-hi,1-lo

def max_delta(Alo,Ahi,a,b):
    if not (0<=Alo<Ahi and 0<a<b):raise ValueError('bad geometry')
    A=max(Alo,min(a,Ahi))
    return max(Q(0),phibox(A,a)[1]-phibox(A,b)[0])

def weighted_error(Alo,Ahi,a,b,n=12):
    """Distinct Fraction/isqrt upper for int (r-a)(b-r)*(-dphi)."""
    h=b-a;mid=(a+b)/2
    direct=h*h*max_delta(Alo,Ahi,a,b)/4
    refined=Q(0)
    for k in range(n):
        lo=a+h*Q(k,n);hi=a+h*Q(k+1,n)
        apex=max(lo,min(mid,hi))
        refined+=(apex-a)*(b-apex)*max_delta(Alo,Ahi,lo,hi)
    return min(direct,refined)

def reference_inputs():
    buf=PARENT.read_bytes()
    if sha(buf)!=PRIOR:raise ValueError('wrong protected inter-node scientific parent')
    z=zipfile.ZipFile(io.BytesIO(buf))
    with zipfile.ZipFile(io.BytesIO(z.read('inputs/crossing_band_parent_v1r2.zip'))) as b:
        bands=json.loads(b.read('results/whole_band_certificate.json'))['lenses']
    with zipfile.ZipFile(io.BytesIO(z.read('inputs/saturation_parent_v1r1.zip'))) as s:
        with zipfile.ZipFile(io.BytesIO(s.read('original_parent.zip'))) as a:
            with zipfile.ZipFile(io.BytesIO(a.read('inputs/frozen_source_parent.zip'))) as f:
                with zipfile.ZipFile(io.BytesIO(f.read('inputs/original_march_D120_q_parent.zip'))) as d:
                    with zipfile.ZipFile(io.BytesIO(d.read('inputs/original_march180_parent_v1r1.zip'))) as m:
                        capture=json.loads(m.read('results/source180_capture.json'))['lenses']
                        raws=[m.read('inputs/'+item['node_file']) for item in capture]
                        lock=json.loads(m.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE:raise ValueError('wrong 46+3 original hash')
    if len(capture)!=len(bands)!=6 or tuple(x['lens_id'] for x in capture)!=LENSES:
        raise ValueError('six source identities absent')
    for c,r in zip(capture,raws):
        if len(r)!=180*64 or sha(r)!=c['node_sha256']:raise ValueError('original 180 node content altered')
    return z,capture,bands,raws

def check_structural(result,band,capture,prior_bv):
    if result.get('schema')!='HIST001D_CANCEL_AWARE_AFFINE_SIGNED_QUADRATURE_BAND_V1':raise ValueError('schema')
    if result.get('original_parent_sha256')!=PRIOR or result.get('original_180_source_node_sha256')!=capture['node_sha256'] or result.get('lens')!=capture['lens_id'] or result.get('lens')!=band['lens']:
        raise ValueError('source identity')
    n=result.get('n');p=result.get('panels');e=result.get('point_values')
    if type(n) is not int or not 1<=n<=8192 or type(p) is not list or type(e) is not list or len(p)!=n or len(e)!=n+1:raise ValueError('subband count')
    Alo=Q(*map(int,band['A_band_left_exact_n_over_d']));Ahi=Q(*map(int,band['A_band_right_exact_n_over_d']))
    if [str(Alo),str(Ahi)]!=result['band']:raise ValueError('original q-circularized aperture band')
    Elo,Ehi=map(Q,result['proxy_remainder_interval'])
    sym=result['independently_certifiable_symmetric_peano_remainder_ceiling_Msun']
    if not Elo<=Ehi or not -sym<=Elo<=Ehi<=sym:raise ValueError('false curvature enclosure')
    if result.get('empirical_validation')!='NOT_ESTABLISHED' or result.get('physical_provider_admitted') is not False or result.get('physical_source_admitted') is not False or result.get('signed_band_remainder_one_sign_certified') is not False or result.get('global_historical_H_root_uniqueness_proved') is not False or result.get('useful_for_original_March_root_gap') is not False:
        raise ValueError('claim firewall')
    if result.get('theoretical_source')!='SELECTED_MSTAR_ONLY':raise ValueError('source provenance')
    lows=[];highs=[]
    for i,v in enumerate(e):
        A=Q(v['A'])
        if A!=Alo+(Ahi-Alo)*Q(i,n):raise ValueError('aperture subdivision missing or reordered')
        for key in ('Q','Plin'):
            t=v[key]
            if not isinstance(t,list) or len(t)!=2 or Q(t[0])<0 or Q(t[0])>Q(t[1]):raise ValueError('nonpositive or inverted positive mass projection')
    for i in range(n):
        left,right=e[i],e[i+1]
        L=Q(left['Q'][0])-Q(right['Plin'][1])-Ehi
        U=Q(right['Q'][1])-Q(left['Plin'][0])-Elo
        if L>U or floor(L)<p[i]['lower'] or ceil(U)>p[i]['upper']:raise ValueError('understated local signed band')
        lows.append(L);highs.append(U)
    g=result['aggregate_signed_Q_deriv_minus_P_integer']
    if not isinstance(g,list) or len(g)!=2 or type(g[0]) is not int or type(g[1]) is not int or g[0]>floor(min(lows)) or g[1]<ceil(max(highs)):
        raise ValueError('understated aggregate signed band')
    upper=max(-g[0],g[1]);old=prior_bv['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun']
    if result['inherited_prior_BV_upper_integer_Msun']!=old or upper>result['max_abs_new_signed_band_upper_integer_Msun'] or upper>=old:
        raise ValueError('not genuinely improved versus inherited BV')
    return Alo,Ahi

def verify_all(root=ROOT,source_check=True):
    z,caps,bands,raws=reference_inputs()
    summary=[]
    for j,(cap,band,raw) in enumerate(zip(caps,bands,raws)):
        d=json.loads((root/'results'/f'signed_lens_{j}.json').read_text())
        prior=json.loads(z.read(f'results/bv_band_lens_{j}.json'))
        Alo,Ahi=check_structural(d,band,cap,prior)
        radial=json.loads(z.read(f'results/continuous_lens_{j}.json'))
        # Independently certify the coarse, symmetric curvature error from source panel C.
        E=Q(0)
        for q in radial['panels']:
            a,b=Q(q['lo']),Q(q['hi'])
            if q['Msecond_abs_ceil']<0 or not a<b:raise ValueError('bad original curvature interval')
            E+=Q(q['Msecond_abs_ceil'],2)*weighted_error(Alo,Ahi,a,b)
        if ceil(E)>d['independently_certifiable_symmetric_peano_remainder_ceiling_Msun']:
            raise ValueError('symmetric interpolation remainder understated')
        if source_check:
            nodes=json.loads(z.read(f'results/lens_{j}.json'))['lenses'][0]['nodes']
            rr=list(struct.iter_unpack('>8d',raw))
            coeff=[]
            for row,v in zip(rr,nodes):
                if v['radius_binary64_hex']!=row[0].hex():raise ValueError('node index mismatch')
                w=Q.from_float(row[1]);r=Q.from_float(row[0]);mp=v['selected_Mprime_interval']
                coeff.append((r,w*Q(mp[0]),w*Q(mp[1])))
            for point in d['point_values']:
                A=Q(point['A']);Qlow=Qhigh=0
                # Distinct 160-bit dyadic enclosure independent of the producer's 512-bit class.
                for r,c0,c1 in coeff:
                    fl,fu=phibox(A,r)
                    Qlow+=c0*fl
                    Qhigh+=c1*fu
                if Qlow>Q(point['Q'][1]) or Qhigh<Q(point['Q'][0]):
                    raise ValueError('independent nodal Q(A) interval disjoint from producer')
        summary.append({'lens':cap['lens_id'],'subbands':d['n'],'signed_integer':d['aggregate_signed_Q_deriv_minus_P_integer'],
            'old_BV_integer':prior['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun'],
            'symmetric_peano_integer':d['independently_certifiable_symmetric_peano_remainder_ceiling_Msun'],
            'independent_nodal_Q_and_structural_inequalities_pass':True})
    return summary

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--no-source-check',action='store_true');a=p.parse_args()
    v=verify_all(source_check=not a.no_source_check)
    out={'schema':'HIST001D_CANCEL_AWARE_AFFINE_INDEPENDENT_FRACTION_Q_REPLAY_V1',
         'lenses':v,'all_six_pass':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    (ROOT/'results/verify_affine.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS_SIGNED_AFFINE_WITNESS',sum(x['subbands'] for x in v),'subbands',flush=True)
