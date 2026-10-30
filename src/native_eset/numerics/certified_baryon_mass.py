"""G1/G2: exact-rational enclosures of CONTINUUM historical baryonic profiles.

G1: finite-support Hernquist cylinder mass (r in [0.02,120] kpc).
G2: conservative, azimuth-free bounds for the analytic elliptical exponential
disk. All floating parameters are frozen and treated as exact binary64 inputs.

These bounds DO NOT enclose the historical SciPy/1024-angle numerical
algorithms without a separate numerical-error proof. They bound the continuum
mathematical formulas with frozen dyadic inputs, not the source continuum
origin of the parameters, observational uncertainties or physical Weyl field.
"""
from __future__ import annotations

import heapq
from decimal import Context, Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction

from native_eset.numerics.exact_shadow_bounds import (
    ShadowEnclosureError,
    _fraction,
    _sqrt_rational_bounds,
)

RMIN = 0.02
RMAX = 120.0
G1_TARGET = "0.000001"
G1_SPLIT_BUDGET = 8192
G1_CHECK_EVERY = 128
DECIMAL_PRECISION = 70
SQRT_BITS = 100
DISK_EXP_SERIES_PAIRS = 24
SCHEMA = "NATIVE_ESET_HIST001D_D2E_G1_G2_BARYON_CONTINUUM_BOUND_V1"


def _directed(value: Fraction, *, upper: bool, precision: int) -> str:
    ctx = Context(prec=precision, rounding=ROUND_CEILING if upper else ROUND_FLOOR)
    return format(ctx.divide(Decimal(value.numerator), Decimal(value.denominator)), "f")


def _positive_bulge_moments(lo: Fraction, hi: Fraction, mass: Fraction, a: Fraction):
    """Exact W0=∫2Ma/(r+a)^3 and W1=∫2Ma*r/(r+a)^3."""
    if not (0 < lo < hi and mass > 0 and a > 0):
        raise ShadowEnclosureError("bad finite Hernquist moments")
    w0 = mass*a*(1/(lo+a)**2-1/(hi+a)**2)
    w1 = mass*a*(2/(lo+a)-a/(lo+a)**2
                 -2/(hi+a)+a/(hi+a)**2)
    if not (w0 > 0 and w1 > 0):
        raise ShadowEnclosureError("negative analytic Hernquist moments")
    return w0, w1


def _g2_bounds(r: Fraction, aperture: Fraction, bits: int):
    """Exact rational bounds of r-sqrt(r^2-A^2), via positive quotient."""
    if not 0 < aperture <= r:
        raise ShadowEnclosureError("Hernquist outer shell below aperture")
    if r == aperture:
        return aperture, aperture
    sl, sh = _sqrt_rational_bounds(r*r-aperture*aperture, bits)
    return aperture*aperture/(r+sh), aperture*aperture/(r+sl)


def _g2_slope_bounds(r: Fraction, aperture: Fraction, bits: int):
    """Outward derivative of g2: 1-r/sqrt(r^2-A^2), for r>A."""
    if not 0 < aperture < r:
        raise ShadowEnclosureError("Hernquist kernel derivative outside interior")
    sl, sh = _sqrt_rational_bounds(r*r-aperture*aperture, bits)
    if sl <= 0:
        raise ShadowEnclosureError("integer sqrt insufficient near singular point")
    return 1-r/sl, 1-r/sh


def _weighted_line(lo, hi, mass, a, left, right):
    """Exact ∫ [2Ma/(r+a)^3] times affine endpoints left/right."""
    w0, w1 = _positive_bulge_moments(lo, hi, mass, a)
    return left*w0 + (right-left)/(hi-lo)*(w1-lo*w0)


def _outer_hernquist_cell(lo, hi, aperture, mass, a, bits):
    """Monotone + convex geometric interval on positive analytic density.

    g2(r)=r-sqrt(r²-A²); g2''=A²/(r²-A²)^(3/2)>0 for r>A.
    Thus a midpoint tangent is a lower pointwise line and the secant
    joining endpoint upper bounds is an upper pointwise line.
    """
    if not aperture <= lo < hi:
        raise ShadowEnclosureError("invalid outer bulge cell")
    mid = (lo+hi)/2
    gl, gh = _g2_bounds(lo, aperture, bits)
    grl, grh = _g2_bounds(hi, aperture, bits)
    midlo, _ = _g2_bounds(mid, aperture, bits)
    dl, dh = _g2_slope_bounds(mid, aperture, bits)
    w0, _ = _positive_bulge_moments(lo, hi, mass, a)
    upper_chord = _weighted_line(lo, hi, mass, a, gh, grh)
    lower_tangent = (
        _weighted_line(lo, mid, mass, a, midlo+dh*(lo-mid), midlo)
        + _weighted_line(mid, hi, mass, a, midlo, midlo+dl*(hi-mid))
    )
    lower = max(Fraction(0), lower_tangent, grl*w0)
    upper = min(upper_chord, gh*w0)
    if not 0 <= lower <= upper:
        raise ShadowEnclosureError("invalid convex-monotone Hernquist bound")
    return lower, upper


def _directed_sum(exact_inside, cells, precision):
    lc = Context(prec=precision, rounding=ROUND_FLOOR)
    uc = Context(prec=precision, rounding=ROUND_CEILING)

    def dec(f, ctx):
        return ctx.divide(Decimal(f.numerator), Decimal(f.denominator))

    lower, upper = dec(exact_inside, lc), dec(exact_inside, uc)
    for _, _, lo, hi in cells.values():
        lower = lc.add(lower, dec(lo, lc))
        upper = uc.add(upper, dec(hi, uc))
    if not 0 < lower <= upper:
        raise ShadowEnclosureError("invalid total finite Hernquist enclosure")
    width = uc.divide(uc.subtract(upper, lower), lower)
    return lower, upper, width


def certified_hernquist_point(
    radius_kpc, bulge_mass_msun, hernquist_a_kpc,
    *, target_width: str = G1_TARGET,
    max_splits: int = G1_SPLIT_BUDGET,
    sqrt_bits: int = SQRT_BITS,
    precision: int = DECIMAL_PRECISION,
):
    """Certified finite-support continuum Hernquist mass for exact dyadic inputs."""
    if (type(max_splits) is not int or not 0 <= max_splits <= 32768
            or type(sqrt_bits) is not int or not 64 <= sqrt_bits <= 160
            or type(precision) is not int or not 48 <= precision <= 120):
        raise ShadowEnclosureError("unregistered Hernquist proof budget")
    if not isinstance(target_width, str):
        raise ShadowEnclosureError("precision target must be decimal string")
    try:
        target = Decimal(target_width)
    except InvalidOperation as exc:
        raise ShadowEnclosureError("invalid proof target") from exc
    if not target.is_finite() or not Decimal("1e-12") <= target <= Decimal("1e-2"):
        raise ShadowEnclosureError("Hernquist precision target out of contract")
    radius = _fraction(radius_kpc)
    mass = _fraction(bulge_mass_msun)
    a = _fraction(hernquist_a_kpc)
    rmin, rmax = _fraction(RMIN), _fraction(RMAX)
    if not (rmin < radius <= rmax and mass > 0 and a > 0):
        raise ShadowEnclosureError("bad finite-source Hernquist inputs")

    # Exact polynomial/rational primitive for 4π*r²*rho with
    # rho(r)=Ma/(2π*r*(r+a)^3); no transcendental quadrature.
    exact_inside = mass*a*(2/(rmin+a)-a/(rmin+a)**2
                           -2/(radius+a)+a/(radius+a)**2)
    if exact_inside <= 0:
        raise ShadowEnclosureError("invalid Hernquist inner integral")

    active = {}
    queue = []
    uid = 0
    if radius < rmax:
        low, high = _outer_hernquist_cell(radius, rmax, radius, mass, a, sqrt_bits)
        active[uid] = (radius, rmax, low, high)
        heapq.heappush(queue, (-float(high-low), uid))
        uid += 1
    splits = 0
    lower, upper, width = _directed_sum(exact_inside, active, precision)
    while width > target and splits < max_splits and queue:
        _, key = heapq.heappop(queue)
        lo, hi, _, _ = active.pop(key)
        mid = (lo+hi)/2
        if not lo < mid < hi:
            raise ShadowEnclosureError("Hernquist dyadic split failed")
        for x,y in ((lo,mid),(mid,hi)):
            c0, c1 = _outer_hernquist_cell(x,y,radius,mass,a,sqrt_bits)
            active[uid] = (x,y,c0,c1)
            heapq.heappush(queue, (-float(c1-c0),uid))
            uid += 1
        splits += 1
        if splits % G1_CHECK_EVERY == 0 or splits == max_splits:
            lower, upper, width = _directed_sum(exact_inside, active, precision)
    lower, upper, width = _directed_sum(exact_inside, active, precision)
    return {
        "schema":SCHEMA,
        "lower_msun":format(lower,"f"),
        "upper_msun":format(upper,"f"),
        "relative_interval_width_upper":format(width,"f"),
        "target_width":target_width,
        "target_met":bool(width<=target),
        "split_count":splits,
        "split_budget":max_splits,
        "exact_input_contract":"BINARY64_BULGE_MASS_AND_HERNQUIST_A_AND_RADIUS",
        "source_finite_radial_domain_kpc":[RMIN,RMAX],
        "scope":"MATHEMATICAL_FINITE_HERNQUIST_CONTINUUM_NOT_SCIPY_EXECUTION",
        "source_numerical_error_certified":False,
    }


def certified_hernquist_radius_band(rl, rh, mass, a, **kwargs):
    """All REAL radii in [rl,rh], by positive projected-mass monotonicity."""
    l, h = _fraction(rl), _fraction(rh)
    if not _fraction(RMIN) < l <= h <= _fraction(RMAX):
        raise ShadowEnclosureError("bad finite bulge radius band")
    lower = certified_hernquist_point(rl, mass, a, **kwargs)
    upper = lower if l==h else certified_hernquist_point(rh, mass, a, **kwargs)
    if Decimal(lower["lower_msun"]) > Decimal(upper["upper_msun"]):
        raise ShadowEnclosureError("bulge radius mass band inverted")
    return {
        "lower_msun":lower["lower_msun"],
        "upper_msun":upper["upper_msun"],
        "endpoints": [lower, upper],
        "all_real_radii_in_band_enclosed": True,
        "proof":"NONNEGATIVE_FINITE_HERNQUIST_DENSITY_MONOTONE_PROJECTION",
        "historical_SciPy_reference_error_certified":False,
    }


def _exp_minus_rational(x: Fraction) -> tuple[Fraction,Fraction]:
    """Rigorous exact rational enclosure exp(-x), for x>=0.

    Small x: alternating series enclosing exp(-y), y=x/2^k <=1;
    positive interval powering by 2^k. Large x: e^x exceeds its
    positive Taylor partial sum, giving exp(-x) <=1/S_N.
    """
    if x < 0:
        raise ShadowEnclosureError("negative disk exponential argument")
    if x==0:
        return Fraction(1),Fraction(1)
    if x > 32:
        term = total = Fraction(1)
        for n in range(1,49):
            term *= x/n
            total += term
        return Fraction(0), 1/total
    power=0
    reduced=x
    while reduced > 1:
        reduced/=2
        power+=1
    term=total=Fraction(1)
    odd=None
    for n in range(1, 2*DISK_EXP_SERIES_PAIRS+1):
        term *= -reduced/n
        total += term
        if n == 2*DISK_EXP_SERIES_PAIRS-1:
            odd = total
    even=total
    if odd is None or not 0 < odd <= even <= 1:
        raise ShadowEnclosureError("invalid alternating exponential bounds")
    return odd**(1<<power), even**(1<<power)


def _disk_integral_fraction(x):
    """Bounds for H(x)=1-(1+x)*exp(-x) using rigorously bracketed exp."""
    exlo,exhi=_exp_minus_rational(x)
    low=max(Fraction(0), 1-(1+x)*exhi)
    hi=min(Fraction(1), 1-(1+x)*exlo)
    if not 0 <= low <= hi <= 1:
        raise ShadowEnclosureError("inverted disk cumulative mass fraction")
    return low,hi


def certified_elliptical_disk_radius_band(
    radius_min, radius_max, disc_mass_msun, disc_scale_kpc, q_disc,
    *, precision: int = DECIMAL_PRECISION,
):
    """Proved but conservative analytic-azimuth disk mass bracket.

    g(theta)=sqrt(cos²θ+sin²θ/q²) obeys 1<=g<=1/q for 0<q<=1.
    No angular discretization/sampling is used or certified.
    Sigma0=M/(2π*q*s²), and I(R,g)=∫_0^R r exp(-g*r/s)dr.
    Thus M*q*H(R/(q*s)) <= Mdisk(R) <= (M/q)*H(R/s).
    Further, true total exponential-disc mass is M; cap upper at M.
    """
    if type(precision) is not int or not 48 <= precision <= 120:
        raise ShadowEnclosureError("unsupported disk bound precision")
    rl,rh,mass,scale,q = map(_fraction, (
        radius_min,radius_max,disc_mass_msun,disc_scale_kpc,q_disc,
    ))
    if not (0 < rl <= rh <= _fraction(RMAX) and mass>0
            and scale>0 and 0 < q <= 1):
        raise ShadowEnclosureError("invalid analytic elliptical disc interval")
    low_h,_=_disk_integral_fraction(rl/(q*scale))
    _,up_h=_disk_integral_fraction(rh/scale)
    low=mass*q*low_h
    up=min(mass, mass*up_h/q)
    if not 0 <= low <= up <= mass:
        raise ShadowEnclosureError("elliptical disc mass bounds inconsistent")
    return {
        "lower_msun":_directed(low,upper=False,precision=precision),
        "upper_msun":_directed(up,upper=True,precision=precision),
        "radius_interval_kpc":[float(radius_min),float(radius_max)],
        "axis_ratio_q_exact_binary64":float(q_disc),
        "scope":"CONTINUUM_EXPONENTIAL_DISK_RIGOROUS_COARSE_GEOMETRIC_BOUND",
        "all_real_radii_in_band_enclosed":True,
        "angular_quadrature_512_1024_error_certified":False,
        "high_accuracy_disc_mass_proved":False,
        "proof":"POSITIVE_ELLIPTICAL_DISK_GEOMETRY_1_LE_G_LE_1_OVER_Q",
    }
