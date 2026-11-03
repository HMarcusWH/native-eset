#!/usr/bin/env python3
"""Source-conditional signed affine interpolation for selected historical M*.
Independent all-real derivative / Bessel certificates are inherited inputs.
No physical shadow source, original true off-grid solver, or validation.
"""
from __future__ import annotations
import hashlib,io,json,struct,sys,time,zipfile
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'reference'
sys.path.insert(0,str(SOURCE/'hist001d_k180_bessel_integral_candidate'))
sys.path.insert(0,str(SOURCE/'hist001d_k180_inter_node_candidate'))
from source_audit import open_inputs  # noqa: E402
from inter_node_producer import makepoint,mpp_bound  # noqa: E402
from real_integral_bessel import X  # noqa: E402
from affine_kernel import kernel,kernel_integral  # noqa: E402
PARENT_SHA='63c4df7dcc4e5493fe9e2ea667ebb1a7d8ec418a8d03400096eb5fedf53d4691'
PARENT=ROOT/'inputs/inter_node_parent_v1.zip'
SAT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
BAND_SHA='cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'
PARENT_CACHE=None
def parent():
    global PARENT_CACHE
    if PARENT_CACHE is None:
        raw=PARENT.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=PARENT_SHA:raise ValueError('protected source parent SHA mismatch')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            sat=z.read('inputs/saturation_parent_v1r1.zip')
            band=z.read('inputs/crossing_band_parent_v1r2.zip')
            if hashlib.sha256(sat).hexdigest()!=SAT_SHA or hashlib.sha256(band).hexdigest()!=BAND_SHA:
                raise ValueError('protected nested SHA mismatch')
            PARENT_CACHE=(sat,band,[json.loads(z.read(f'results/lens_{j}.json')) for j in range(6)],
                          [json.loads(z.read(f'results/continuous_lens_{j}.json')) for j in range(6)],
                          [json.loads(z.read(f'results/bv_band_lens_{j}.json')) for j in range(6)])
    return PARENT_CACHE

def get_band(j):
    _,raw,_,_,_=parent()
    v=json.loads(zipfile.ZipFile(io.BytesIO(raw)).read('results/whole_band_certificate.json'))['lenses'][j]
    return F(*map(int,v['A_band_left_exact_n_over_d'])),F(*map(int,v['A_band_right_exact_n_over_d'])),v

def endpoints(j):
    sat,_,nodal,radial,_=parent()
    src,caps,analytic,_=open_inputs(sat)
    raw=src.read('inputs/'+caps[j]['node_file']);rows=list(struct.iter_unpack('>8d',raw))
    record=nodal[j]['lenses'][0]
    bands=radial[j]
    if len(rows)!=180 or len(record['nodes'])!=180 or bands['node_sha256']!=caps[j]['node_sha256']:
        raise ValueError('historical node mismatch')
    p={k:F.from_float(float.fromhex(analytic[j]['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    def getbox(v,key):return X(F(v[key][0]),F(v[key][1]))
    def make(r,v,fields):return makepoint(r,getbox(v,fields[0]),getbox(v,fields[1]),getbox(v,fields[2]),getbox(v,fields[3]),p)
    nodes=[];points={}
    for i,v in enumerate(record['nodes']):
        r=F.from_float(rows[i][0]);obj=make(r,v,('Bessel_F_interval','Bessel_Fprime_interval','selected_M_interval','selected_Mprime_interval'))
        points[r]=obj
        nodes.append((r,F.from_float(rows[i][1]),obj['Mp']))
    for v in bands['midpoints']:
        r=F(v['r']);points[r]=make(r,v,('F','Fp','M','Mp'))
    panels=[]
    for item in bands['panels']:
        a=F(item['lo']);b=F(item['hi'])
        if a not in points or b not in points:raise ValueError('missing mass panel endpoint')
        pa,pb=points[a],points[b];s=(pb['M']-pa['M'])/(b-a)
        if s.lower()<=0 or b<=a:raise ValueError('missing mass monotonicity')
        mpp=mpp_bound(pa,pb,p)
        if max(abs(mpp.lower()),abs(mpp.upper()))>item['Msecond_abs_ceil']:raise ValueError('curvature certificate mismatch')
        panels.append((a,b,s,mpp,item['Msecond_abs_ceil']))
    if len(panels)!=bands['accepted_panels'] or bands['unresolved']:raise ValueError('radial coverage mismatch')
    if any(q[1]!=panels[k+1][0] for k,q in enumerate(panels[:-1])):raise ValueError('radial gap')
    return caps[j]['lens_id'],caps[j]['node_sha256'],nodes,panels

def kernel_variation_max(Alo,Ahi,a,b):
    # For 0<a<b, A -> phi(A,a)-phi(A,b) is unimodal with maximum at A=a.
    astar=max(Alo,min(a,Ahi))
    d=kernel(astar,a)-kernel(astar,b)
    return max(F(0),d.upper())

def weighted_curvature_kernel_upper(Alo,Ahi,a,b,nsegments=12):
    """Upper bound of int (r-a)(b-r)*[-d_r phi(A,r)] dr,
    uniform A in source-defined band, by independent piecewise maxima of
    parabolic interpolation factor and exact cylinder-kernel variations.
    """
    if nsegments<=0 or b<=a:raise ValueError('interpolation geometry')
    h=b-a;mid=(a+b)/2
    coarse=h*h*kernel_variation_max(Alo,Ahi,a,b)/4
    subdiv=F(0)
    for k in range(nsegments):
        L=a+h*F(k,nsegments);U=a+h*F(k+1,nsegments)
        x=min(max(mid,L),U)
        pmax=(x-a)*(b-x)
        subdiv+=pmax*kernel_variation_max(Alo,Ahi,L,U)
    return X(0,min(coarse,subdiv))

def rem_band(panels,Alo,Ahi,nsegments=12):
    low=high=X(0);symmetric=F(0)
    for a,b,s,mpp,C in panels:
        w=weighted_curvature_kernel_upper(Alo,Ahi,a,b,nsegments)/2
        symmetric+=C*w.upper()
        lo=min(F(0),-mpp.upper())
        hi=max(F(0),-mpp.lower())
        low=low+w*X(lo)
        high=high+w*X(hi)
    signed=X(low.lower(),high.upper())
    if signed.lower()<-symmetric or signed.upper()>symmetric:
        raise ValueError('signed remainder exceeds independently certified absolute curvature cap')
    return signed,symmetric

def point_values(A,nodes,panels):
    Q=X(0);L=X(0)
    for r,w,mp in nodes:Q+=X(w)*mp*kernel(A,r)
    for a,b,s,_,_ in panels:L+=s*kernel_integral(A,a,b)
    return Q,L

def certify_lens(j,nsteps=16):
    lens,source,nodes,panels=endpoints(j)
    Alo,Ahi,band=get_band(j)
    t=time.perf_counter()
    E,Eabs=rem_band(panels,Alo,Ahi)
    print('LENS',lens,'E',float(E.lower()),float(E.upper()),'seconds',round(time.perf_counter()-t,2),flush=True)
    ends=[]
    for k in range(nsteps+1):
        a=Alo+(Ahi-Alo)*F(k,nsteps)
        Q,L=point_values(a,nodes,panels)
        ends.append((a,Q,L))
        if k==0 or k==nsteps or k%32==0:
            print(' endpoint',j,k,'elapsed',round(time.perf_counter()-t,2),flush=True)
    panelbounds=[]
    for k,(left,right) in enumerate(zip(ends,ends[1:])):
        a,Q0,L0=left;b,Q1,L1=right
        # Q and Lin increase in A because all quadrature weights/slope >0.
        low=(Q0-L1-E).lower();hi=(Q1-L0-E).upper()
        # alternative signed error: P in [L+E.low,L+E.high], D=Q-P
        low=(Q0-L1).lower()-E.upper();hi=(Q1-L0).upper()-E.lower()
        panelbounds.append([low,hi])
    floor=lambda x:x.numerator//x.denominator
    ceil=lambda x:-(-x.numerator//x.denominator)
    _,_,_,_,priorBV=parent()
    old=priorBV[j]['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun']
    upper_abs=max(-min(x[0] for x in panelbounds),max(x[1] for x in panelbounds))
    if upper_abs>=old:raise ValueError('new candidate failed to improve old BV')
    out=dict(schema='HIST001D_CANCEL_AWARE_AFFINE_SIGNED_QUADRATURE_BAND_V1',
        original_180_source_node_sha256=source,original_parent_sha256=PARENT_SHA,
        inherited_prior_BV_upper_integer_Msun=old,
        max_abs_new_signed_band_upper_integer_Msun=ceil(upper_abs),
        lens=lens,n=nsteps,band=[str(Alo),str(Ahi)],
        proxy_remainder_interval=[str(E.lower()),str(E.upper())],
        independently_certifiable_symmetric_peano_remainder_ceiling_Msun=ceil(Eabs),
        aggregate_signed_Q_deriv_minus_P_integer=[floor(min(x[0] for x in panelbounds)),ceil(max(x[1] for x in panelbounds))],
        point_values=[{'A':str(a),'Q':[str(q.lower()),str(q.upper())], 'Plin':[str(l.lower()),str(l.upper())]} for a,q,l in ends],
        panels=[{'lower':floor(x[0]),'upper':ceil(x[1])} for x in panelbounds],
        empirical_validation='NOT_ESTABLISHED',physical_provider_admitted=False,
        theoretical_source='SELECTED_MSTAR_ONLY',
        global_historical_H_root_uniqueness_proved=False,
        useful_for_original_March_root_gap=False,
        signed_band_remainder_one_sign_certified=False,
        physical_source_admitted=False)
    print('RESULT',lens,'Q_deriv-P:',out['aggregate_signed_Q_deriv_minus_P_integer'],'time',round(time.perf_counter()-t,1),flush=True)
    return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--lens',type=int,required=True);p.add_argument('--n',type=int,default=16);p.add_argument('--out');o=p.parse_args()
    d=certify_lens(o.lens,o.n)
    if o.out:Path(o.out).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
