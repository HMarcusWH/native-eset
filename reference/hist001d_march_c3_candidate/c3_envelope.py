"""Exact rational conservative M''/M''' envelopes for a separately defined March smooth shadow law.

This is *not* proof of numerical float errors, source off-grid clipping, or original H root count.
Bessel inequalities use exact integral representations and upper half-integer K.
All source binary64 values are treated as exact dyadics, no use of SciPy/mpmath for certificates.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb, factorial, isqrt

PI_UP = Q(22, 7)                 # Archimedes's strict rational pi upper bound
SQRT_BITS = 64

def ceil_sqrt_fraction(a: Q, bits: int=SQRT_BITS) -> Q:
    if a < 0: raise ValueError('negative sqrt')
    if a == 0: return Q(0)
    d=1<<bits
    k=isqrt((a.numerator*d*d)//a.denominator)
    v=Q(k,d)
    return v if v*v == a else Q(k+1,d)

def K_half_polynomial(order: int, inverse_y: Q) -> Q:
    """P_n(1/y), K_(n+1/2)=sqrt(pi/2y) exp(-y) P_n(1/y)."""
    if type(order) is not int or not 0<=order<=4 or inverse_y<=0:raise ValueError('order/input outside proof')
    s=Q(0)
    for k in range(order+1):
        s+=Q(factorial(order+k),factorial(k)*factorial(order-k)*2**k)*inverse_y**k
    return s

def bound_F_derivative(k: int, ylo: Q) -> Q:
    """|d^k/dy^k(I0 K0 - I1 K1)| global at every y>=ylo>0.

    |I_n^(j)(y)|<=e^y by I_n integer angle integral;
    |K_n^(j)(y)|<=K_(n+j)(y)<=K_(n+j+1/2)(y);
    K half orders cancel e^y giving a rational sqrt(pi/(2y)) polynomial.
    """
    if not 0<=k<=3 or ylo<=0:raise ValueError('outside derivative envelope')
    inv=1/ylo
    pi_sqrt=ceil_sqrt_fraction(PI_UP/(2*ylo))
    # independent per-factor binomial splitting is tighter than the single 2^k shortcut
    s=Q(0)
    for j in range(k+1):
        l=k-j
        s+=comb(k,j)*(K_half_polynomial(l,inv)+K_half_polynomial(l+1,inv))
    return s*pi_sqrt

def bound_acceleration_baryon_derivatives(lo:Q,hi:Q, *,Mb:Q,Md:Q,a:Q,Rd:Q)->tuple[Q,Q,Q,Q]:
    if not (0<lo<=hi and min(Mb,Md,a,Rd)>0):raise ValueError('invalid physical scalar contract')
    ylo=lo/(2*Rd);yhi=hi/(2*Rd)
    F=[bound_F_derivative(i,ylo) for i in range(4)]
    disk=[]
    for order in range(4):
        s=Q(0)
        for j in range(min(order,3)+1):
            # | (y^3)^(j) | <= (3)_j yhi^(3-j)
            falling=factorial(3)//factorial(3-j)
            s+=comb(order,j)*falling*yhi**(3-j)*F[order-j]
        disk.append(Md*s/(2*Rd)**order)
    bulge=[Mb,
           2*Mb*a*hi/(lo+a)**3,
           2*Mb*a*(a+2*hi)/(lo+a)**4,
           12*Mb*a*(a+hi)/(lo+a)**5]
    return tuple(bulge[k]+disk[k] for k in range(4))

def bound_gate_derivatives(lo:Q,hi:Q,*,delta:Q,r0:Q,n:Q)->tuple[Q,Q,Q,Q]:
    if not (0<lo<=hi and 0<delta<1 and r0>0 and 4<n<5):
        raise ValueError('n exponent and gate range must match frozen six sources')
    # f=R^n/(R^n+r0^n). For R<r0 and n>4: f <= (R/r0)^4.
    # p=f(1-f)<=1/4; also <=(R/r0)^4 below r0 and <=(r0/R)^4 above r0.
    fmax=min(Q(1),(hi/r0)**4) if hi<=r0 else Q(1)
    if hi<=r0:
        pmax=min(Q(1,4), (hi/r0)**4)
    elif lo>=r0:
        pmax=min(Q(1,4), (r0/lo)**4)
    else:
        pmax=Q(1,4)
    eps_min=1-delta*fmax
    if eps_min<=0:raise ValueError('invalid epsilon lower bound')
    # f' = n*f(1-f)/R; f'' = n*p*[n(1-2f)-1]/R^2.
    # f'''=n*p*[(n(1-2f)-2)(n(1-2f)-1)-2n²p]/R³.
    f1=n*pmax/lo
    f2=n*pmax*(n+1)/lo**2
    f3=n*pmax*((n+2)*(n+1)+2*n*n*pmax)/lo**3
    # g(f)=delta*f/(1-delta*f); compose through third derivative.
    gf0=delta*fmax/eps_min
    gf1=delta/eps_min**2
    gf2=2*delta*delta/eps_min**3
    gf3=6*delta**3/eps_min**4
    return (gf0, gf1*f1, gf2*f1*f1+gf1*f2,
            gf3*f1**3 + 3*gf2*f1*f2+gf1*f3)

def bound_shadow_M_derivatives(lo:Q,hi:Q,params:dict)->tuple[Q,Q]:
    A=bound_acceleration_baryon_derivatives(lo,hi,**{x:params[x] for x in ('Mb','Md','a','Rd')})
    G=bound_gate_derivatives(lo,hi,**{x:params[x] for x in ('delta','r0','n')})
    M2=A[2]*G[0]+2*A[1]*G[1]+A[0]*G[2]
    M3=A[3]*G[0]+3*A[2]*G[1]+3*A[1]*G[2]+A[0]*G[3]
    return M2,M3

def split_interval(lo:Q,hi:Q,parts:int=4):
    if parts<1 or lo<=0 or hi<=lo:raise ValueError('nonpositive/invalid interval')
    delta=(hi-lo)/parts
    return [(lo+j*delta,lo+(j+1)*delta) for j in range(parts)]

def certify_mesh(radii:list[Q],params:dict,*,parts:int=4)->dict:
    if len(radii)!=180 or any(r<=0 for r in radii) or any(radii[i]>=radii[i+1] for i in range(179)):
        raise ValueError('not canonical 180 increasing source mesh')
    cell2=[];cell3=[]
    for lo,hi in zip(radii,radii[1:]):
        vals=[bound_shadow_M_derivatives(a,b,params) for a,b in split_interval(lo,hi,parts)]
        cell2.append(max(x[0] for x in vals)); cell3.append(max(x[1] for x in vals))
    # These cover all original interior neighbor domains and endpoints exactly.
    theoretical_bound=[(radii[1]-radii[0])/2*cell2[0]]
    for i in range(1,179):
        hm=radii[i]-radii[i-1];hp=radii[i+1]-radii[i]
        theoretical_bound.append(hm*hp/6*max(cell3[i-1],cell3[i]))
    theoretical_bound.append((radii[-1]-radii[-2])/2*cell2[-1])
    return {'cell_M2':cell2,'cell_M3':cell3,'ideal_gradient_absolute_error_cap':theoretical_bound,
            'max_M2':max(cell2),'max_M3':max(cell3),'max_gradient_bound':max(theoretical_bound),
            'first_gradient_bound':theoretical_bound[0], 'last_gradient_bound':theoretical_bound[-1]}
