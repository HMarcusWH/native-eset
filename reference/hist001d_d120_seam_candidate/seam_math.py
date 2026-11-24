"""Original-source-angle periodic seam: exact-real mathematical comparison only.

The archived source uses 120 frozen angular nodes theta_0,...,theta_119,
with np.trapezoid integrating 119 segments. Define an *alternative*
periodic closure that adds ONE segment with step h=theta_1-theta_0
and frozen endpoint integrands f(a_119,R),f(a_0,R).

This is NOT the exact integral over [theta_119,2*pi], which would
require a separate trigonometric continuum error bound. No physical
selection or full-lensing theorem follows from this stencil identity.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import isqrt


def ff(x: float) -> F:
    return F.from_float(x)


def floor(x: F) -> int:
    return x.numerator // x.denominator


def ceil(x: F) -> int:
    return -((-x.numerator) // x.denominator)


def exp_minus_alternating(x: F, order: int = 48) -> tuple[F, F]:
    """Rigorous e^(-x) interval from alternating Taylor + scaling/squaring.

    For 0<=y<=1, S_(2n+1) <= exp(-y) <= S_(2n).
    The exact nonnegative interval is repeatedly squared to recover exp(-x).
    """
    if x < 0 or not isinstance(x, F):
        raise ValueError('x must be nonnegative exact rational')
    if order % 2 != 0 or order < 8:
        raise ValueError('need an even Taylor order >=8')
    y = x
    halvings = 0
    while y > 1:
        y /= 2
        halvings += 1
    term = F(1)
    total = term
    lower = upper = None
    for n in range(1, order + 2):
        term = -term * y / n
        total += term
        if n == order:
            upper = total
        if n == order + 1:
            lower = total
    if not F(0) <= lower <= upper <= F(1):
        raise ArithmeticError('alternating exponential enclosure failed')
    for _ in range(halvings):
        lower *= lower
        upper *= upper
    return lower, upper


def exp_minus_positive(x: F, order: int = 48) -> tuple[F, F]:
    """Independent e^(-x) enclosure via positive exp(+y) Taylor and reciprocal.

    For 0<=y<=1, exp(y) lies between its positive S_N and
    S_N+2*y^(N+1)/(N+1)!; the factor 2 bounds the geometric tail.
    This method does not call the alternating-series implementation.
    """
    if x < 0 or not isinstance(x, F) or order < 8:
        raise ValueError('x/order invalid')
    y = x
    halvings = 0
    while y > 1:
        y /= 2
        halvings += 1
    term = F(1)
    total = term
    for n in range(1, order + 1):
        term *= y / n
        total += term
    next_term = term * y / (order + 1)
    lower = 1 / (total + 2 * next_term)
    upper = 1 / total
    if not F(0) <= lower <= upper <= F(1):
        raise ArithmeticError('positive-series exponential enclosure failed')
    for _ in range(halvings):
        lower *= lower
        upper *= upper
    return lower, upper


def seam_interval(R: F, sigma0: F, Rd: F, h: F,
                  a_first: F, a_last: F, exp_enclosure=exp_minus_alternating) -> tuple[F, F]:
    """Exact-real interval for the source-frozen missing periodic trapezoid seam.

    f(a,R)=Rd^2/a^2*[1-(1+x)*exp(-x)], x=a*R/Rd.
    seam=sigma0*h*(f(a0,R)+f(a_last,R))/2.
    The integrand is strictly positive for R>0 and a,Rd>0.
    """
    R, sigma0, Rd, h, a_first, a_last = map(F, (R, sigma0, Rd, h, a_first, a_last))
    if R < 0 or min(sigma0,Rd,h,a_first,a_last) <= 0:
        raise ValueError('invalid source geometry')
    lower = upper = F(0)
    for a in (a_first,a_last):
        x = a * R / Rd
        elo,ehi = exp_enclosure(x)
        c = Rd*Rd / (a*a)
        lower += c * (1-(1+x)*ehi)
        upper += c * (1-(1+x)*elo)
    lower *= sigma0*h/2
    upper *= sigma0*h/2
    if not (lower <= upper and lower >= 0):
        raise ArithmeticError('negative/inverted seam')
    return lower, upper


def monotonicity_contract() -> str:
    # Analytical derivative: d/dR f(a,R)=R*exp(-aR/Rd)>0 for R>0.
    return 'd seam/dR = (sigma0*h/2)*R*(exp(-a0*R/Rd)+exp(-a_last*R/Rd)) > 0 for R>0'


def integer_micro_interval(interval: tuple[F,F]):
    return [floor(interval[0]*10**6),ceil(interval[1]*10**6)]


def rational_from_pair(pair):
    return F(int(pair[0]),int(pair[1]))


def pair(x):
    return [str(x.numerator),str(x.denominator)]
