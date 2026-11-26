"""Mathematical smooth-derivative extension of archived March gbar/epsilon mass.

SCOPED DIAGNOSTIC ONLY. Treat original source binary64 parameters as reals.
This is not an authenticated physical density, numerical interval enclosure,
or original historical off-grid solver behavior.
"""
from __future__ import annotations
import numpy as np
from scipy import special
from fractions import Fraction


def source_mass_and_analytic_gradient(r, *, Mb, Md, a, Rd, delta, r0, n):
    r = np.asarray(r, dtype=np.float64)
    if not np.all((r > 0) & np.isfinite(r)) or min(Mb, Md, a, Rd, delta, r0, n) <= 0 or delta > .95:
        raise ValueError('outside the documented positive finite source law')
    y = r / (2.0 * Rd)
    F = special.i0(y) * special.k0(y) - special.i1(y) * special.k1(y)
    F_prime = 2.0 * (special.i1(y) * special.k0(y) - special.i0(y) * special.k1(y)
                     + special.i1(y) * special.k1(y) / y)
    Mbar = Mb * r**2 / (r+a)**2 + Md * y**3 * F
    Mbar_prime = 2.0*Mb*a*r / (r+a)**3 + (Md/(2.0*Rd))*(3.0*y*y*F+y**3*F_prime)
    f = r**n/(r**n+r0**n)
    fp = n*r**(n-1)*r0**n / (r**n+r0**n)**2
    ep = 1.0-delta*f
    M_shadow = Mbar * (delta*f/ep)
    M_shadow_prime = Mbar_prime*(delta*f/ep) + Mbar*delta*fp/(ep*ep)
    if not (np.all(ep > .05-1e-14) and np.all(ep < 1) and np.all(np.isfinite(M_shadow_prime))):
        raise ValueError('epsilon source branch or derivative invalid')
    return M_shadow, M_shadow_prime


def nonuniform_gradient_exact(values, radii):
    """Idealized ORIGINAL NumPy first/last edge_order=1 and 3-point middle.

    Every provided float is converted to its exact dyadic value. Does NOT
    certify the floating run or smooth source function on arbitrary radii.
    """
    if len(values)!=len(radii) or len(radii)<3:
        raise ValueError('invalid gradient array')
    x = [Fraction.from_float(float(v)) for v in radii]
    v = [Fraction.from_float(float(t)) for t in values]
    if any(x[i+1]<=x[i] for i in range(len(x)-1)): raise ValueError('unordered radii')
    out=[(v[1]-v[0])/(x[1]-x[0])]
    for i in range(1,len(x)-1):
        hm=x[i]-x[i-1];hp=x[i+1]-x[i]
        out.append((hp*((v[i]-v[i-1])/hm)+hm*((v[i+1]-v[i])/hp))/(hm+hp))
    out.append((v[-1]-v[-2])/(x[-1]-x[-2]))
    return out


def conditional_finite_difference_bounds(hm, hp, max_abs_M2=None, max_abs_M3=None):
    """Taylor remainder bounds for exact source sample values, NOT floats.

    Endpoint |one-sided D-M'| <= h/2 * sup|M''| (on the edge cell).
    Interior |nonuniform D-M'| <= hm*hp/6 * sup|M'''|
    (on [r_(i-1),r_(i+1)]).
    Missing certified derivative suprema always returns UNRESOLVED.
    """
    hm = Fraction(hm);hp=Fraction(hp)
    if hm <= 0 or hp <= 0: raise ValueError('positive radial steps required')
    if max_abs_M2 is None or max_abs_M3 is None:
        return {'status': 'UNRESOLVED_DERIVATIVE_SUPREMA_NOT_CERTIFIED'}
    m2=Fraction(max_abs_M2);m3=Fraction(max_abs_M3)
    if min(m2,m3)<0: raise ValueError('derivative suprema cannot be negative')
    return {'status':'CONDITIONAL_ON_SOURCE_DERIVATIVE_SUPREMA',
            'endpoint_left':hm*m2/2,'endpoint_right':hp*m2/2,
            'interior':hm*hp*m3/6}
