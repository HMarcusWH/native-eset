#!/usr/bin/env python3
"""Independent exact-Fraction source/witness check for targeted M* quadrature zeros.

NO imports from source producer, Bessel integral K producer, Peano or kernel
producer. This validates SOURCE-LOCKED interval arithmetic, not the physics.
"""
from __future__ import annotations
import argparse,hashlib,io,json,struct,sys,zipfile
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'reference'/'hist001d_k180_inter_node_candidate'
sys.path.insert(0,str(SRC))
from verify_inter_node import R,make_node,Msecond_envelope,independent_fpp  # noqa: E402
from targeted_refine import (CANCEL_SHA,INTER_SHA,SOURCE_SHA,LENSES,EXTRAS,WITNESS_INDICES)  # noqa: E402
# Importing constants only here: no numerical producer method or X arithmetic.

BITS=192
D=1<<BITS

def sha(s):return hashlib.sha256(s).hexdigest()
def floor(v):return v.numerator//v.denominator
def ceil(v):return -(-v.numerator//v.denominator)
class Y:
    """Independent 192-bit outward integer interval, distinct from producer X."""
    __slots__=('lo','hi')
    def __init__(self,a,b=None,raw=False):
        if raw:self.lo,self.hi=int(a),int(a if b is None else b)
        else:
            a=F(a);b=a if b is None else F(b)
            self.lo=floor(a*D);self.hi=ceil(b*D)
        if self.lo>self.hi:raise ValueError('Y interval inversion')
    def __add__(self,b):
        b=y(b);return Y(self.lo+b.lo,self.hi+b.hi,True)
    __radd__=__add__
    def __neg__(self):return Y(-self.hi,-self.lo,True)
    def __sub__(self,b):return self+-y(b)
    def __rsub__(self,b):return y(b)-self
    def __mul__(self,b):
        b=y(b);v=[a*c for a in (self.lo,self.hi) for c in (b.lo,b.hi)]
        return Y(min(v)//D,-((-max(v))//D),True)
    __rmul__=__mul__
    def __truediv__(self,b):
        b=y(b)
        if b.lo<=0<=b.hi:raise ValueError('Y zero in divisor')
        rec=Y(D*D//b.hi,ceil(F(D*D,b.lo)),True)
        return self*rec
    def __rtruediv__(self,b):return y(b)/self
    def lower(self):return F(self.lo,D)
    def upper(self):return F(self.hi,D)
def y(v):return v if isinstance(v,Y) else Y(v)
def ysqr(v):
    v=y(v)
    if v.lo>=0:return Y(v.lo*v.lo//D,ceil(F(v.hi*v.hi,D)),True)
    if v.hi<=0:return Y(v.hi*v.hi//D,ceil(F(v.lo*v.lo,D)),True)
    return Y(0,ceil(F(max(v.lo*v.lo,v.hi*v.hi),D)),True)
def sqrtx(v):
    v=y(v)
    if v.lo<0:raise ValueError('sqrt negative')
    lo=isqrt(v.lo*D);hi=isqrt(v.hi*D)
    if hi*hi<v.hi*D:hi+=1
    return Y(lo,hi,True)
def atanx(v):
    t=y(v)
    if t.lo<0:raise ValueError('atan negative')
    factor=1
    for _ in range(40):
        if t.hi*4<=D:break
        t=t/(1+sqrtx(1+ysqr(t)));factor*=2
    else:raise ValueError('atan reduction')
    sq=ysqr(t);term=t;total=t;low=None;hi=None
    for k in range(1,52):
        term=-term*sq
        total+=term/F(2*k+1)
        if k==49:low=total.lower() # even number of series terms = lower
        if k==50:hi=total.upper()
    if low is None or hi is None or low>hi:raise ValueError('atan alternating truncation')
    return Y(factor*low,factor*hi)
def phi(A,r):
    if A<0 or r<=0:raise ValueError('phi domain')
    if A>=r:return Y(1)
    return 1-sqrtx(1-ysqr(Y(A/r)))
def jprim(A,a,b):
    if not (A>0 and 0<a<b):raise ValueError('J primitive domain')
    if A>=b:return Y(b-a)
    m=max(A,a)
    U=sqrtx(b*b-A*A)
    V=Y(0) if m==A else sqrtx(m*m-A*A)
    v=Y(A)*(U-V)/(Y(A*A)+U*V)
    return Y(b-a)-(U-V)+Y(A)*atanx(v)
def phi_delta_max(Alo,Ahi,a,b):
    if not (0<Alo<Ahi and 0<a<b):raise ValueError('band geometry')
    A=max(Alo,min(a,Ahi))
    return max(F(0),phi(A,a).upper()-phi(A,b).lower())
def W_upper(Alo,Ahi,a,b,n=12):
    h=b-a;mid=(a+b)/2
    coarse=h*h*phi_delta_max(Alo,Ahi,a,b)/4
    fine=F(0)
    for k in range(n):
        lo=a+h*F(k,n);hi=a+h*F(k+1,n);c=max(lo,min(mid,hi))
        fine+=(c-a)*(b-c)*phi_delta_max(Alo,Ahi,lo,hi)
    return min(coarse,fine)/2

def load():
    raw=(ROOT/'inputs/cancel_parent_v1.zip').read_bytes()
    if sha(raw)!=CANCEL_SHA:raise ValueError('wrong cancellation parent')
    z=zipfile.ZipFile(io.BytesIO(raw));manifest=json.loads(z.read('MANIFEST_SHA256.json'))
    if any(sha(z.read(k))!=v for k,v in manifest['files'].items()):raise ValueError('altered parent source files')
    inter=z.read('inputs/inter_node_parent_v1.zip')
    if sha(inter)!=INTER_SHA:raise ValueError('wrong inter_node parent')
    iz=zipfile.ZipFile(io.BytesIO(inter))
    sat=zipfile.ZipFile(io.BytesIO(iz.read('inputs/saturation_parent_v1r1.zip')))
    nested=zipfile.ZipFile(io.BytesIO(sat.read('original_parent.zip')))
    frozen=zipfile.ZipFile(io.BytesIO(nested.read('inputs/frozen_source_parent.zip')))
    d120=zipfile.ZipFile(io.BytesIO(frozen.read('inputs/original_march_D120_q_parent.zip')))
    src=zipfile.ZipFile(io.BytesIO(d120.read('inputs/original_march180_parent_v1r1.zip')))
    capture=json.loads(src.read('results/source180_capture.json'))['lenses']
    analytic=json.loads(nested.read('results/producer_analytic_source_gradient.json'))['lenses']
    lock=json.loads(src.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('wrong original 46+3 source')
    crossings=zipfile.ZipFile(io.BytesIO(iz.read('inputs/crossing_band_parent_v1r2.zip')))
    bands=json.loads(crossings.read('results/whole_band_certificate.json'))['lenses']
    return z,iz,src,capture,analytic,bands

def getpoints(j,iz,capture,analytic,src):
    rec=json.loads(iz.read(f'results/lens_{j}.json'))['lenses'][0]
    radial=json.loads(iz.read(f'results/continuous_lens_{j}.json'))
    rows=list(struct.iter_unpack('>8d',src.read('inputs/'+capture[j]['node_file'])))
    if len(rows)!=180 or sha(src.read('inputs/'+capture[j]['node_file']))!=capture[j]['node_sha256']:raise ValueError('source node data mismatch')
    p={k:F.from_float(float.fromhex(analytic[j]['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    def box(v):return R(F(v[0]),F(v[1]))
    def mk(r,parts):
        out={'r':r,'F':box(parts['F']),'Fp':box(parts['Fp']),'M':box(parts['M']),'Mp':box(parts['Mp'])}
        out['Fpp_ind']=independent_fpp({'r':r,'F':out['F'],'Fp':out['Fp'],'Fpp':None},p)
        return out
    points={}
    for k,(row,v) in enumerate(zip(rows,rec['nodes'])):
        r=F.from_float(row[0]);assert v['index']==k and v['radius_binary64_hex']==row[0].hex()
        points[r]=mk(r,{'F':v['Bessel_F_interval'],'Fp':v['Bessel_Fprime_interval'],
                         'M':v['selected_M_interval'],'Mp':v['selected_Mprime_interval']})
    for v in radial['midpoints']:
        r=F(v['r']);points[r]=mk(r,v)
    original=[(F(t['lo']),F(t['hi']),int(t['Msecond_abs_ceil'])) for t in radial['panels']]
    if len(original)!=radial['accepted_panels'] or any(x[1]!=y[0] for x,y in zip(original,original[1:])):raise ValueError('inherited panel geometry')
    return points,original,p,rows

def canonical_active_leaf_set(active):
    """Keep untouched integer keys attached to their ORIGINAL panel index.

    Regression guard: using the previous loop variable here silently rewrote
    origins of all unsplit leaves, falsely failing the coverage audit.
    """
    return {(key if type(key) is int else key[0],str(a),str(b),depth)
            for key,(a,b,depth) in active.items()}

def verify_lens(j):
    z,iz,src,capture,analytic,bands=load()
    obj=json.loads((ROOT/'results'/f'targeted_lens_{j}.json').read_text())
    parent= z.read(f'results/signed_lens_{j}.json');old=json.loads(parent)
    if obj['schema']!='HIST001D_SELECTED_MSTAR_TARGETED_PEANO_SIGN_REVERSALS_V1' or obj['lens']!=LENSES[j] or obj['source_node_sha256']!=capture[j]['node_sha256'] or obj['parent_signed_lens_sha256']!=sha(parent) or obj['protected_cancel_parent_sha256']!=CANCEL_SHA or obj['protected_inter_node_parent_sha256']!=INTER_SHA or obj['source_46plus3_sha256']!=SOURCE_SHA:raise ValueError('source identity mismatch')
    if obj['physical_provider_admitted'] is not False or obj['empirical_validation']!='NOT_ESTABLISHED' or obj['Einstein_residual_root_count_certified'] is not False or obj['selected_smooth_quadrature_one_sign'] is not False or obj['mathematical_scope']!='SELECTED_ACCELERATION_EQUIVALENT_MSTAR_ONLY':raise ValueError('claim promotion')
    if obj['added_integral_Bessel_midpoints']!=EXTRAS or obj['initial_radial_panels']!=len(json.loads(iz.read(f'results/continuous_lens_{j}.json'))['panels']):raise ValueError('refinement count')
    Alo=F(*map(int,bands[j]['A_band_left_exact_n_over_d']))
    Ahi=F(*map(int,bands[j]['A_band_right_exact_n_over_d']))
    if obj['A_band']!=[str(Alo),str(Ahi)] or not Alo<Ahi:raise ValueError('aperture band')
    points,original,p,rows=getpoints(j,iz,capture,analytic,src)
    active={i:(a,b,0) for i,(a,b,c) in enumerate(original)}
    for record in obj['split_history']:
        k=record['origin'];a=F(record['a']);b=F(record['b']);m=F(record['mid'])
        if not (0<=k<len(original)) or m!=(a+b)/2:raise ValueError('noncanonical midpoint')
        matched=[key for key,v in active.items() if v[0]==a and v[1]==b and (key if type(key) is int else key[0])==k]
        # Active keys change from original panel index to tuple(root,dyadic_path).
        if len(matched)!=1:raise ValueError('non-leaf split or reused point')
        key=matched[0];_,_,depth=active.pop(key)
        if record['depth']!=depth+1 or m in points:raise ValueError('midpoint depth/reuse')
        def box(v):return R(F(v[0]),F(v[1]))
        node={'r':m,'F':box(record['F']),'Fp':box(record['Fp']),
              'M':box(record['M']),'Mp':box(record['Mp'])}
        node['Fpp_ind']=independent_fpp({'r':m,'F':node['F'],'Fp':node['Fp'],'Fpp':None},p)
        if node['Mp'].l<=0:raise ValueError('uncertified new midpoint Mprime')
        points[m]=node
        active[(k,str(a),str(m))]=(a,m,depth+1)
        active[(k,str(m),str(b))]=(m,b,depth+1)
    # Every original panel is represented by a union of subpanels.
    if len(active)!=len(original)+EXTRAS:raise ValueError('active leaf count')
    leaf_data=obj['leaves']
    if len(leaf_data)!=len(active) or obj['refined_radial_panels']!=len(active):raise ValueError('leaf count mismatch')
    active_set=canonical_active_leaf_set(active)
    seen=set();E=F(0)
    for record in leaf_data:
        k,a,b,depth=record['origin'],F(record['a']),F(record['b']),record['depth']
        idt=(k,str(a),str(b),depth)
        if idt not in active_set or idt in seen:raise ValueError('noncanonical saved leaf')
        seen.add(idt)
        c=record['C_integer_Msecond_abs']
        if type(c) is not int or c<0:raise ValueError('bad radius curvature cap')
        if depth==0:
            if c!=original[k][2]:raise ValueError('untouched inherited curvature differs')
        else:
            mpp=Msecond_envelope(points[a],points[b],p)
            if c<max(abs(mpp.l),abs(mpp.u)):raise ValueError('independent Fraction Msecond exceeds cap')
            if min(points[a]['Mp'].l,points[b]['Mp'].l)-(b-a)*c/2<=0:raise ValueError('refined Mprime not positive')
        w=W_upper(Alo,Ahi,a,b)
        if w>F(record['W_upper'])+F(1,10**25):raise ValueError('Peano weight underestimated')
        E+=c*w
    if len(seen)!=len(active_set):raise ValueError('incomplete leaves')
    if ceil(E)>obj['E_symmetric_ceiling_integer_Msun'] or obj['E_symmetric_ceiling_integer_Msun']>=obj['inherited_prior_symmetric_ceiling_integer_Msun'] or obj['inherited_prior_symmetric_ceiling_integer_Msun']!=old['independently_certifiable_symmetric_peano_remainder_ceiling_Msun']:
        raise ValueError('not a certified strict reduction')
    if len(obj['anchors'])!=len(WITNESS_INDICES[j]) or [a['index'] for a in obj['anchors']]!=list(WITNESS_INDICES[j]):raise ValueError('witness index tamper')
    zeros=[];prev=None
    for anchor in obj['anchors']:
        idx=anchor['index'];A=Alo+(Ahi-Alo)*F(idx,128)
        if F(anchor['A'])!=A:raise ValueError('witness aperture changed')
        Qlo=Qhi=F(0)
        for row,v in zip(rows,json.loads(iz.read(f'results/lens_{j}.json'))['lenses'][0]['nodes']):
            rr=F.from_float(row[0]);ww=F.from_float(row[1]);q=phi(A,rr)
            Qlo+=ww*F(v['selected_Mprime_interval'][0])*q.lower()
            Qhi+=ww*F(v['selected_Mprime_interval'][1])*q.upper()
        # Source-independent exact 192-bit kernel and direct sum of all refined slopes.
        Llo=Lhi=F(0)
        for k,a,b,depth in sorted(active_set,key=lambda x:F(x[1])):
            aa,bb=F(a),F(b)
            S=(points[bb]['M']-points[aa]['M'])/(bb-aa)
            J=jprim(A,aa,bb)
            Llo+=S.l*J.lower();Lhi+=S.u*J.upper()
        left=Qlo-Lhi-E;right=Qhi-Llo+E
        sign=1 if left>0 else (-1 if right<0 else 0)
        if sign!=anchor['strict_sign'] or sign==0 or floor(left)<anchor['integer_D'][0] or ceil(right)>anchor['integer_D'][1]:
            raise ValueError('independent witness sign or outward integer enclosure failed')
        if prev and prev[1]!=sign:zeros.append((prev[0],idx,prev[1],sign))
        prev=(idx,sign)
    cited=[(v['left_index'],v['right_index'],v['left_sign'],v['right_sign']) for v in obj['certified_zero_intervals']]
    if cited!=zeros or obj['certified_distinct_zero_lower_bound']!=len(zeros) or not zeros:raise ValueError('zero-existence claim not proved')
    return {'lens':obj['lens'],'verified_splits':EXTRAS,'verified_leaves':len(active),'Peano_ceil_Msun':obj['E_symmetric_ceiling_integer_Msun'],
            'independent_Peano_ceil_Msun':ceil(E),'certified_distinct_zeros_at_least':len(zeros)}

def main():
    a=argparse.ArgumentParser();a.add_argument('--lens',type=int,choices=range(6));args=a.parse_args()
    data=[verify_lens(args.lens)] if args.lens is not None else [verify_lens(i) for i in range(6)]
    result={'schema':'HIST001D_TARGETED_PEANO_INDEPENDENT_FRACTION_VERIFY_V1','lenses':data,
            'verified_total_distinct_quadrature_remainder_zeros_at_least':sum(x['certified_distinct_zeros_at_least'] for x in data),
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    out=ROOT/'results'/'verify_targeted.json';out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('INDEPENDENT_TARGETED_PASS',len(data),'lenses','zeros>=',result['verified_total_distinct_quadrature_remainder_zeros_at_least'],flush=True)
if __name__=='__main__':main()
