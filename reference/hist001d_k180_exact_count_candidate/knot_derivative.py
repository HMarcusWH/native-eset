"""Candidate source-dependent knot-safe derivative certificates for historical selected M* D(A).

No original continuous physical shadow-density or Einstein/root uniqueness claim.
Uses original frozen source node arrays + inherited targeted Peano panel mass/curvature
and source-locked Bessel intervals. Derivative sign tests exclude all knots.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from fractions import Fraction as F
SRC=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(SRC/'reference/hist001d_k180_targeted_candidate'))
from targeted_refine import original
import signed_affine_producer as sp
from affine_kernel import atan_positive,sqrt_interval,kernel_integral,kernel
from real_integral_bessel import X
from math import isqrt

# Inherited APR16 source-specific, deterministic leaf refinement; no Bessel calls.
def lens_data(j):
    lens,nodehash,p,initial=original(j)
    t=json.loads((SRC/'results'/f'targeted_lens_{j}.json').read_text())
    pts={}
    for v in initial:pts[v.a]=v.pa;pts[v.b]=v.pb
    for q in t['split_history']:
        a,b,mid=F(q['a']),F(q['b']),F(q['mid'])
        if mid!=(a+b)/2 or mid in pts:raise ValueError('targeted split geometry')
        pts[mid]={'M':X(F(q['M'][0]),F(q['M'][1])),
                  'Mp':X(F(q['Mp'][0]),F(q['Mp'][1]))}
    leaves=[]
    for q in t['leaves']:
        a,b=F(q['a']),F(q['b']);
        if not(a in pts and b in pts and a<b):raise ValueError('targeted leaf endpoint')
        pa,pb=pts[a],pts[b];h=b-a;C=F(q['C_integer_Msecond_abs']);
        slo=(pb['M']-pa['M'])/h
        Mplow=min(pa['Mp'].lower(),pb['Mp'].lower())-C*h/2
        Mphi=max(pa['Mp'].upper(),pb['Mp'].upper())+C*h/2
        if slo.lower()<=0 or Mplow<=0:raise ValueError('inherited Mprime positive panel failed')
        leaves.append(dict(a=a,b=b,h=h,slope=slo,C=C,Mplo=Mplow,Mphi=Mphi))
    if len(leaves)!=t['refined_radial_panels'] or any(x['b']!=y['a'] for x,y in zip(leaves,leaves[1:])):raise ValueError('leaf coverage')
    _,_,nodes,_=sp.endpoints(j)
    if t['lens']!=lens or t['source_node_sha256']!=nodehash:raise ValueError('source node SHA')
    return lens,nodes,leaves,F(t['E_symmetric_exact']),t

# Cylindrical derivative kernel k_A(r) = d/dA (1 - sqrt(1-A^2/r^2)).
def kd(A,r):
    A=F(A);r=F(r)
    if not(0<A<r):raise ValueError('k domain must exclude a frozen knot')
    return X(A)/(X(r)*sqrt_interval(X(r*r-A*A)))

def omega(A,a,b):
    """Positive exact-rational outward interval for int_{max(a,A)}^b k(A,r)dr.
    This equals acos(A/b)-acos(A/a) for A<a, and acos(A/b) for a<=A<b.
    The principal arctangent formula avoids subtraction of nearly equal acos.
    """
    A,a,b=F(A),F(a),F(b)
    if not(0<A and 0<a<b):raise ValueError('omega geometry')
    if A>=b:return X(0)
    U=sqrt_interval(X(b*b-A*A))
    if A>=a:return atan_positive(U/X(A))
    V=sqrt_interval(X(a*a-A*A))
    arg=X(A)*(U-V)/(X(A*A)+U*V)
    return atan_positive(arg)

def pprime_band(leaves,L,R,precise=False):
    """Source-conditional inclusion P*'(A) for every A in closed [L,R].
    For cells strictly above R, use affine-M slope and nonnegative Peano
    correction: |int (M'-s)k| <= C h²/8 [k(R,a)-k(R,b)].
    k(A,r) is decreasing and convex in r and increasing in A, hence
    h k(A,mid) <= int_a^b k(A,r)dr <= h[k(A,a)+k(A,b)]/2.
    For cells touching aperture band, enclosure by M' range and exact
    omega with its maximum at clamp(a,L,R) and minimum at an endpoint.
    """
    L,R=F(L),F(R)
    if not (0<L<R):raise ValueError('A interval')
    low=high=X(0)
    n_touch=0
    for t in leaves:
        a,b,h,s,C,ml,mh=[t[k] for k in ('a','b','h','slope','C','Mplo','Mphi')]
        if b<=L:continue
        if a>R:
            if precise:
                w_lower=omega(L,a,b)
                w_upper=omega(R,a,b)
            else:
                w_lower=h*kd(L,(a+b)/2)   # kernel convex in r
                w_upper=h*(kd(R,a)+kd(R,b))/2
            e=X(C*h*h/F(8))*(kd(R,a)-kd(R,b))
            if e.lower()<0: raise ValueError('negative Peano bound')
            low=low+s*X(w_lower.lower())-X(e.upper())
            high=high+s*X(w_upper.upper())+X(e.upper())
        else:
            n_touch+=1
            wl=omega(L,a,b);wr=omega(R,a,b)
            wmax=omega(max(L,min(a,R)),a,b)
            lo=min(wl.lower(),wr.lower())
            hi=wmax.upper()
            if lo<0 or hi<lo:raise ValueError('omega interval')
            low+=X(ml*lo)
            high+=X(mh*hi)
    return X(low.lower(),high.upper()),n_touch

def qprime_band(nodes,L,R):
    L,R=F(L),F(R)
    if not 0<L<R:raise ValueError('A geometry')
    for r,w,mp in nodes:
        if L<r<=R:raise ValueError('crosses original frozen radial knot')
    def q(A):
        val=X(0)
        for r,w,mp in nodes:
            if r>A:val+=X(w)*mp*kd(A,r)
        return val
    qlo=q(L);qhi=q(R)
    if qlo.lower()>qhi.upper():raise ValueError('Qprime source monotonicity violated')
    return X(qlo.lower(),qhi.upper())

def bound_derivative(nodes,leaves,L,R,precise=False):
    qp=qprime_band(nodes,L,R)
    pp,n=pprime_band(leaves,L,R,precise=precise)
    dp=qp-pp
    return dp,n

if __name__=='__main__':
 import time
 st=time.time();lens,nodes,leaves,E,t=lens_data(0)
 for l,r in [('1.9633','1.9644'),('2.2300','2.2310'),('2.6410','2.6425')]:
  dp,n=bound_derivative(nodes,leaves,F(l),F(r));print(lens,l,r,[float(dp.lower()),float(dp.upper())],n,'elapsed',round(time.time()-st,1),flush=True)
