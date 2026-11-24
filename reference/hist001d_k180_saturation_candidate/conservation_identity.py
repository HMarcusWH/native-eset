"""Exact rational identities and strict scope for source-frozen K180 at saturation.

The formulae here are mathematical statements, not source/physical model promotion.
"""
from fractions import Fraction as Q
from math import factorial

def trap_weights(r):
    r=[Q(x) for x in r]
    h=[b-a for a,b in zip(r,r[1:])]
    if len(r)<2 or min(h)<=0:raise ValueError('increasing mesh required')
    return [h[0]/2]+[(h[i-1]+h[i])/2 for i in range(1,len(h))]+[h[-1]/2]

def nonuniform_stencil(r,m):
    r=[Q(x) for x in r];m=[Q(x) for x in m]
    if len(m)!=len(r) or len(m)<2:raise ValueError('source dimension')
    h=[r[i+1]-r[i] for i in range(len(r)-1)]
    if min(h)<=0:raise ValueError('source mesh not increasing')
    sec=[(m[i+1]-m[i])/h[i] for i in range(len(h))]
    if len(r)==2:return sec*2
    result=[sec[0]]
    for i in range(1,len(r)-1):
        hm, hp = h[i-1],h[i]
        result.append((hp*sec[i-1]+hm*sec[i])/(hm+hp))
    result.append(sec[-1])
    return result

def exact_nonuniform_telescoping_defect(r,m):
    r=[Q(x) for x in r];m=[Q(x) for x in m]
    if len(r)<2 or len(r)!=len(m):raise ValueError('mesh dimensions')
    h=[r[i+1]-r[i] for i in range(len(r)-1)]
    if min(h)<=0:raise ValueError('mesh not increasing')
    if len(h)==1:return Q(0)
    sec=[(m[i+1]-m[i])/h[i] for i in range(len(h))]
    coeff=[(h[1]-h[0])/2]
    for j in range(1,len(h)-1):
        coeff.append((h[j-1]+h[j+1]-2*h[j])/2)
    coeff.append((h[-2]-h[-1])/2)
    return sum((a*b for a,b in zip(coeff,sec)),Q(0))

def bump_integral_coefficient(a,b,C4pi):
    """For A>=b, exact 4pi*int r²*((r-a)*(b-r))^4 on [a,b]."""
    a,b,C4pi=Q(a),Q(b),Q(C4pi)
    if a<=0 or b<=a or C4pi<=0:raise ValueError('source radius and coefficient')
    h=b-a
    # B(5,5)=1/630, B(6,5)=1/1260, B(7,5)=1/2310.
    return C4pi*h**9*(a*a/Q(630)+a*h/Q(630)+h*h/Q(2310))

if __name__=='__main__':
    r=[Q(1,50),Q(1,2),Q(3,2),Q(2)]
    m=[Q(2),Q(4),Q(11),Q(20)]
    lhs=sum((w*d for w,d in zip(trap_weights(r),nonuniform_stencil(r,m))),Q())-(m[-1]-m[0])
    assert lhs==exact_nonuniform_telescoping_defect(r,m)
    assert bump_integral_coefficient(r[0],r[1],Q(22,7))>0
