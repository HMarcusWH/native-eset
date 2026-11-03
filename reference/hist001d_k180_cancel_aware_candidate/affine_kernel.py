#!/usr/bin/env python3
"""Source-conditional signed affine-mass interpolation of the finite cylinder projection.

Full scientific limitation: selected analytic M*(r), not physical density or original
March off-grid source. All original nodes and inter-node M' / M'' certificates
are external hashed protected data; this module implements only the geometry.
"""
from __future__ import annotations
from math import isqrt
from fractions import Fraction as F
import sys
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]/'hist001d_k180_bessel_integral_candidate'
sys.path.insert(0,str(SOURCE))
from real_integral_bessel import X,D  # noqa: E402

def cv(x):return x if isinstance(x,X) else X(x)

def sqrt_interval(v):
    x=cv(v)
    if x.lo<0:raise ValueError('negative radicand')
    lo=isqrt(x.lo*D);hi=isqrt(x.hi*D)
    if hi*hi < x.hi*D: hi+=1
    return X(lo,hi,True)

def atan_positive(v):
    """Outward 512-bit interval: atan on positive real input, half-angle reduction.
    Alternating Taylor truncations are globally valid when t in [0,1/4].
    """
    t=cv(v)
    if t.lo<0:raise ValueError('atan input must be nonnegative')
    factor=1
    for _ in range(32):
        if t.hi*4<=D:break
        t=t/(1+sqrt_interval(1+t*t))
        factor*=2
    else:raise ValueError('atan reduction failed')
    sq=t*t
    term=t
    s=term
    upper=None;lower=None
    for k in range(1,46):
        term=-term*sq
        s=s+term/F(2*k+1)
        if k==44:upper=s.upper()
        if k==45:lower=s.lower()
    return X(factor*lower,factor*upper)

def kernel(A,r):
    A=F(A);r=F(r)
    if A<0 or r<=0:raise ValueError('domain')
    if A>=r:return X(1)
    return X(1)-sqrt_interval(X(1)-X(A/r)**2)

def kernel_integral(A,a,b):
    """Directed analytical integral int_a^b phi_A(r) dr.

    For b>A, m=max(a,A), U(r)=sqrt(r^2-A^2) and
    delta_theta=atan( A*(U(b)-U(m))/(A^2+U(b)*U(m)):
    J=(b-a) - (U(b)-U(m)) + A*delta_theta.
    """
    A,a,b=F(A),F(a),F(b)
    if not (A>0 and 0<a<b):raise ValueError('domain')
    if b<=A:return X(b-a)
    m=max(a,A)
    U=sqrt_interval(X(b*b-A*A))
    V=X(0) if m==A else sqrt_interval(X(m*m-A*A))
    x=X(A)*(U-V)/(X(A*A)+U*V)
    ret=X(b-a)-(U-V)+X(A)*atan_positive(x)
    if ret.lower()<0 or ret.upper()>b-a:
        raise ValueError('cylinder integral outside 0..cell width')
    return ret

if __name__=='__main__':
    import math
    for A,a,b in [(F(2),F(1),F(3)),(F(2),F(4),F(5)),(F(2),F(1),F(2)),(F(1),F(1),F(120)),(F(2),F(6),F(6)+F(67,100))]:
        v=kernel_integral(A,a,b)
        from scipy.integrate import quad
        f=lambda r:1 if r<=A else 1-math.sqrt(1-(float(A)/r)**2)
        true=quad(f,float(a),float(b),epsabs=1e-12,points=[float(A)] if a<A<b else None)[0]
        print(A,a,b,float(v.lower()),float(v.upper()),true,abs(float(v.lower())-true))
        assert float(v.lower())-1e-8<=true<=float(v.upper())+1e-8
