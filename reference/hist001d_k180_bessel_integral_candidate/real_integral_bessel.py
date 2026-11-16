"""HIST-001D independently derived conditional real-integral K0/K1 enclosures.

Source-free numerical method, no SciPy, mpmath, producer imports, or Bessel series for K.
Only original selected mathematical acceleration-equivalent mass; NO physical provider.

Analytic (strip) trapezoidal theorem for entire f_nu(t)=exp(-y cosh t)cosh(nu t):
 f_nu(t+i*pi/3) absolute <= exp(-y*cosh(t)/2)*cosh(t) for nu in {0,1};
 strip L1 norms M_+,M_- <= 8/y. Poisson+contour gives
 |Knu(y) - h(1/2*f(0) + sum_{k>=1} f(kh))|
   <= 8/[y*(exp(2*pi^2/(3h))-1)] <= 8/[y*(2**(6/h)-1)]
 using pi>3 and e>2. h=1/32 yields a finite rational bound.

For t0=(N+1)h and z0=y*exp(t0)/2 >= 160, the omitted nonnegative
 sampled tail satisfies <= (4/3)*h*exp(t0)*exp(-z0), since ratio of
 successive majorant terms <= (16/15)*exp(-z0*h) < 1/4.
 The interval calculations and exponential Taylor tails round OUTWARD.
"""
from __future__ import annotations
from fractions import Fraction as Q

BITS=512
D=1<<BITS
H=Q(1,32)

def ceildiv(a,b): return -((-a)//b)
class X:
    __slots__=('lo','hi')
    def __init__(self,a,b=None,raw=False):
        if raw: self.lo=int(a); self.hi=int(a if b is None else b)
        else:
            a=Q(a); b=a if b is None else Q(b)
            self.lo=a.numerator*D//a.denominator
            self.hi=ceildiv(b.numerator*D,b.denominator)
        if self.lo>self.hi: raise ValueError('inverted interval')
    def __add__(self,t):
        t=iv(t);return X(self.lo+t.lo,self.hi+t.hi,True)
    __radd__=__add__
    def __neg__(self): return X(-self.hi,-self.lo,True)
    def __sub__(self,t):return self+-iv(t)
    def __rsub__(self,t):return iv(t)-self
    def __mul__(self,t):
        t=iv(t); x=[p*q for p in (self.lo,self.hi) for q in (t.lo,t.hi)]
        return X(min(x)//D,ceildiv(max(x),D),True)
    __rmul__=__mul__
    def recip(self):
        if self.lo<=0<=self.hi: raise ValueError('inversion includes zero')
        return X((D*D)//self.hi,ceildiv(D*D,self.lo),True)
    def __truediv__(self,t):return self*iv(t).recip()
    def __rtruediv__(self,t):return iv(t)*self.recip()
    def __pow__(self,n):
        if n<0:return (self.recip())**(-n)
        v=X(1);u=self
        while n:
            if n&1:v=v*u
            n//=2
            if n:u=u*u
        return v
    def lower(self):return Q(self.lo,D)
    def upper(self):return Q(self.hi,D)
    def width(self):return Q(self.hi-self.lo,D)
    def __repr__(self):return f'X({float(self.lower())!r},{float(self.upper())!r})'

def iv(x):return x if isinstance(x,X) else X(x)

def exppos(a,terms=100):
    """Outward exp(x) with Taylor positive terms after binary scaling to <=1/2."""
    a=iv(a)
    if a.lo<0:raise ValueError('exp input must be nonnegative')
    shift=0
    while a.hi>(D//2)<<shift: shift+=1
    t=a/(1<<shift)
    cur=X(1);summ=X(1)
    for j in range(1,terms):
        cur=cur*t/Q(j);summ=summ+cur
    one_more=cur*t/Q(terms)
    upper_tail=one_more.upper()/(1-t.upper()/Q(terms+1))
    out=X(summ.lower(),summ.upper()+upper_tail)
    for _ in range(shift): out=out*out
    return out

def logpos(v:Q,terms=180):
    if v<=0:raise ValueError('log positivity')
    exp2=0
    while v>=2:v/=2;exp2+=1
    while v<1:v*=2;exp2-=1
    def unitlog(q):
        w=(q-1)/(q+1)
        term=w;s=Q();w2=w*w
        for k in range(terms):
            s+=2*term/(2*k+1);term*=w2
        rem=2*term/((2*terms+1)*(1-w2))
        return X(s,s+rem)
    return unitlog(v)+exp2*unitlog(Q(2))

def I0I1(y:Q,terms=100):
    z=Q(y*y,4)
    a=X(1);b=X(y/2)
    t0=X(1);t1=X(y/2)
    for k in range(1,terms):
        t0=t0*z/(k*k)
        t1=t1*z/(k*(k+1))
        a=a+t0;b=b+t1
    nn=terms
    next0=t0*z/(nn*nn)
    next1=t1*z/(nn*(nn+1))
    r0=z/Q((nn+1)**2)
    r1=z/Q((nn+1)*(nn+2))
    if not max(r0,r1)<1:raise ValueError('I-series tail not contractive')
    a=a+X(0,next0.upper()/(1-r0))
    b=b+X(0,next1.upper()/(1-r1))
    return a,b

def K0K1_integral(y:Q):
    if not y>0:raise ValueError('positive y required')
    h=H
    # Entire symmetric integrand. Stop once the sampled tail is very small.
    f0sum=X(0);f1sum=X(0)
    texp=X(1)
    eh=exppos(X(h))
    vals=0
    # k=0,1,...,N, then tail begins at k=N+1
    for k in range(1600):
        if k:
            texp=texp*eh
        ch=(texp+texp.recip())/2
        decay=exppos(iv(y)*ch).recip()
        fac=Q(1,2) if k==0 else Q(1)
        f0sum=f0sum+fac*decay
        f1sum=f1sum+fac*decay*ch
        vals=k+1
        # t0=(k+1)*h, upper majorant exp(t0)*exp(-y*exp(t0)/2)
        enext=texp*eh
        z=iv(y)*enext/2
        if z.lower()>=160:
            maj=enext*exppos(z).recip()
            tail=Q(4,3)*h*maj.upper()
            infinite_error=Q(8,1)/(y*((1<<int(6/h))-1))
            err=tail+infinite_error
            return X(h*f0sum.lower()-err,h*f0sum.upper()+err),X(h*f1sum.lower()-err,h*f1sum.upper()+err),dict(grid_points=vals,tail_upper=tail,trapezoid_upper=infinite_error)
    raise RuntimeError('tail criterion not reached')

def F_and_prime(y:Q):
    a,b=I0I1(y)
    c,d,meta=K0K1_integral(y)
    F=a*c-b*d
    Fp=2*(b*c-a*d+b*d/y)
    return F,Fp,meta

def selected_mass_prime(r,p):
    Mb,Md,a,Rd,delta,r0,n=(p[k] for k in ('Mb','Md','a','Rd','delta','r0','n'))
    y=r/(2*Rd)
    FF,Fp,meta=F_and_prime(y)
    acc=Mb*X(r)**2/X(r+a)**2+Md*X(y)**3*FF
    accp=2*Mb*a*r/X(r+a)**3+Md/(2*Rd)*(3*X(y)**2*FF+X(y)**3*Fp)
    if r<=r0:
        ratio=exppos(n*logpos(r0/r)).recip()
        f=ratio/(1+ratio)
    else:
        ratio=exppos(n*logpos(r/r0)).recip()
        f=1/(1+ratio)
    g=delta*f/(1-delta*f)
    gp=delta*n*f*(1-f)/(r*(1-delta*f)**2)
    return acc*g,accp*g+acc*gp,dict(meta,y=y,F=FF,Fp=Fp)
