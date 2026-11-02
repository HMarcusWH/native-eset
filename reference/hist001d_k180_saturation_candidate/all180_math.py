"""Experimental exact-rational outward interval arithmetic for all original March radial nodes.

This is a new nonpromoting mathematical diagnostic.  All transcendental evaluations
are enclosed by rational series with explicit positive tails and Euler-Maclaurin
bounds.  No floating special function values are used as proof.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, isqrt
import time
BITS=512
SCALE=1<<BITS

def floordiv(a,b):return a//b

def ceildiv(a,b):return -((-a)//b)

class Iv:
    __slots__=('l','u')
    def __init__(self,a,b=None,raw=False):
        if raw:
            self.l=int(a);self.u=int(a if b is None else b)
        else:
            a=Q(a);b=a if b is None else Q(b)
            self.l=a.numerator*SCALE//a.denominator
            self.u=ceildiv(b.numerator*SCALE,b.denominator)
        if self.l>self.u:raise ValueError('inverse bounds')
    def __add__(self,o):
        o=toiv(o);return Iv(self.l+o.l,self.u+o.u,True)
    __radd__=__add__
    def __neg__(self):return Iv(-self.u,-self.l,True)
    def __sub__(self,o):return self+-toiv(o)
    def __rsub__(self,o):return toiv(o)-self
    def __mul__(self,o):
        o=toiv(o)
        xs=[a*b for a in (self.l,self.u) for b in (o.l,o.u)]
        return Iv(min(xs)//SCALE,ceildiv(max(xs),SCALE),True)
    __rmul__=__mul__
    def __truediv__(self,o):
        return self*toiv(o).inv()
    def __rtruediv__(self,o):return toiv(o)*self.inv()
    def inv(self):
        if self.l<=0<=self.u:raise ValueError('Zero included in denominator')
        return Iv((SCALE*SCALE)//self.u,ceildiv(SCALE*SCALE,self.l),True)
    def __pow__(self,k):
        if k<0:return self.inv()**(-k)
        z=Iv(1);x=self
        while k:
            if k&1:z=z*x
            x=x*x;k//=2
        return z
    def bound_abs(self):return Q(max(abs(self.l),abs(self.u)),SCALE)
    def width(self):return Q(self.u-self.l,SCALE)
    def low(self):return Q(self.l,SCALE)
    def high(self):return Q(self.u,SCALE)
    def __repr__(self):return f'Iv({float(self.low()):.10g},{float(self.high()):.10g})'

def toiv(q):return q if isinstance(q,Iv) else Iv(q)

def log_pos(x:Q,N=160)->Iv:
    if x<=0:raise ValueError('log positive argument')
    u=x;e=0
    while u>=2:u/=2;e+=1
    while u<1:u*=2;e-=1
    def atom(v):
        t=(v-1)/(v+1)
        if not 0<=t<=Q(1,3):raise ValueError('atanh contract')
        z=t*t;term=t;total=Q(0)
        for k in range(N):
            total+=2*term/(2*k+1);term*=z
        rem=2*term/((2*N+1)*(1-z))
        return Iv(total,total+rem)
    return atom(u)+e*atom(Q(2))

def bernoulli_even(m):
    b=[Q(1)]
    for n in range(1,2*m+3):
        b.append(-sum((Q(comb(n+1,k))*b[k] for k in range(n)),Q())/Q(n+1))
    return [b[2*j] for j in range(m+2)]

def euler_gamma(n=1024,m=16)->Iv:
    # H_n-ln(n)-1/(2n)+sum_{k<=m} B_2k/(2k*n^(2k));
    # successive Euler-Maclaurin approximations enclose gamma.
    H=sum((Q(1,k) for k in range(1,n+1)),Q(0))
    c=Iv(H-Q(1,2*n))-log_pos(Q(n))
    B=bernoulli_even(m+1)
    for j in range(1,m+1):c=c+Q(B[j], 2*j*n**(2*j))
    next_term=Q(B[m+1],2*(m+1)*n**(2*(m+1)))
    # Error sign follows the next term (alternating).  Gamma is between the two consecutive sums.
    if next_term>0:return Iv(c.low(),c.high()+next_term)
    return Iv(c.low()+next_term,c.high())

def exp_pos(q:Iv,N=100)->Iv:
    """Positive exponential, interval Taylor series with *directed integer* rounding.

    Reduce to 0<=x<=1/2. Every term is nonnegative, and the tail after
    terms k=0..N-1 is bounded by term_N/(1-x_upper/(N+1)).
    """
    if q.l<0:raise ValueError('negative exponential argument')
    shift=0
    while q.u//(1<<shift)>SCALE//2:shift+=1
    v=q/(1<<shift)
    t=Iv(1);total=Iv(1)
    for k in range(1,N):
        t=t*v/k
        total=total+t
    next_term=t*v/N
    tail=next_term.high()/(1-v.high()/Q(N+1))
    return Iv(total.low(),total.high()+tail)**(1<<shift)

def bessel_F_Fp(y:Q,gamma:Iv,N=180):
    if y<=0:raise ValueError('positive Bessel argument')
    z=Iv(y*y/4);yy=Iv(y)
    t0=Iv(1);t1=yy/2
    i0=t0;i1=t1;S0=Iv(0);S1=Iv(0)
    H=Q(0)
    for k in range(1,N):
        t0=t0*z/Q(k*k)
        t1=t1*z/Q(k*(k+1))
        H+=Q(1,k)
        i0=i0+t0;i1=i1+t1
        S0=S0+H*t0
        S1=S1+k*H*t0
    t0n=t0*z/Q(N*N)
    t1n=t1*z/Q(N*(N+1))
    Hn=H+Q(1,N)
    if 4*z.high()>=Q((N+1)*(N+1)):raise ValueError('Series tail not controlled')
    i0=i0+Iv(0, t0n.high()/(1-z.high()/Q((N+1)**2)))
    i1=i1+Iv(0, t1n.high()/(1-z.high()/Q((N+1)*(N+2))))
    S0=S0+Iv(0, Hn*t0n.high()/(1-2*z.high()/Q((N+1)**2)))
    S1=S1+Iv(0, N*Hn*t0n.high()/(1-4*z.high()/Q((N+1)**2)))
    L=log_pos(y/2)+gamma
    k0=-L*i0+S0
    k1=i0/yy+L*i1-2*S1/yy
    F=i0*k0-i1*k1
    Fp=2*(i1*k0-i0*k1+i1*k1/yy)
    return F,Fp,(i0,i1,k0,k1)

def gate(R:Q,r0:Q,n:Q,delta:Q)->tuple[Iv,Iv]:
    if R<=0 or r0<=0 or not 0<delta<1:raise ValueError('source positive gate')
    if R<=r0:
        ratio=exp_pos(n*log_pos(r0/R)).inv()
        f=ratio/(1+ratio)
    else:
        ratio=exp_pos(n*log_pos(R/r0)).inv()
        f=1/(1+ratio)
    p=f*(1-f)
    G=delta*f/(1-delta*f)
    Gp=delta*n*p/(R*(1-delta*f)**2)
    return G,Gp

def source_mass(R,p,gamma,N=180):
    Mb,Md,a,Rd,delta,r0,n=(p[k] for k in ('Mb','Md','a','Rd','delta','r0','n'))
    y=R/(2*Rd)
    F,Fp,zz=bessel_F_Fp(y,gamma,N)
    A=Mb*Iv(R)**2/(Iv(R+a)**2)+Md*Iv(y)**3*F
    Ap=2*Mb*a*Iv(R)/(Iv(R+a)**3)+Md/(2*Rd)*(3*Iv(y)**2*F+Iv(y)**3*Fp)
    G,Gp=gate(R,r0,n,delta)
    M=A*G; Mp=Ap*G+A*Gp
    return M,Mp,(F,Fp,zz)
