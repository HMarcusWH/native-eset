"""Rigorous midpoint enclosure for analytic elliptical exponential-disc mass.

Historical source model (frozen exact-binary64 scalars):
  D(R) = [M/(2 pi q)] int_0^(2pi) H(g(theta)*R/s)/g(theta)^2 dtheta,
  H(x) = 1-(1+x)*exp(-x), g^2 = cos^2(theta)+sin^2(theta)/q^2.

The change of variable tan(theta)=q*tan(phi) on each quadrant gives
  D(R)/M = (2/pi) int_0^(pi/2)
      H((R/s)/sqrt(cos^2(phi)+q^2*sin^2(phi))) dphi.
Thus a uniform midpoint average estimates D/M without any angular
trapezoid; its error is bounded analytically by a global second-derivative
bound K*pi^2/(96*N^2).

Every midpoint H value is enclosed by exact-rational alternating-sine,
square-root integer-isqrt and previously SHA-tested exponential bounds.
Directed Decimal arithmetic encloses the mean and midpoint error.

NO certification of the original 1024-angle floating implementation,
source input generation, outer physical mass, or Einstein root topology.
"""
from __future__ import annotations

from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction

from native_eset.numerics.certified_baryon_mass import _disk_integral_fraction
from native_eset.numerics.exact_shadow_bounds import (
    ShadowEnclosureError, _fraction, _pi_fraction_bounds,
    _sqrt_rational_bounds,
)

SCHEMA = "NATIVE_ESET_D2E_G2B_CERTIFIED_DISK_MIDPOINT_V1"
MESH_MIDPOINTS = 1024
TARGET_RELATIVE_WIDTH = "0.01"
SINE_SERIES_TERMS = 12
SQRT_BITS = 100
DECIMAL_DIGITS = 65


def _sin_rational_bounds(x: Fraction):
    """Alternating sine-series rational bounds for 0 <= x <= pi/2."""
    _, pi_hi = _pi_fraction_bounds()
    if not 0 <= x <= pi_hi/2:
        raise ShadowEnclosureError("sine proof argument outside first quadrant")
    if x == 0:
        return Fraction(0), Fraction(0)
    term = total = x
    for n in range(1, SINE_SERIES_TERMS):
        term *= -x*x/((2*n)*(2*n+1))
        total += term
    term *= -x*x/((2*SINE_SERIES_TERMS)*(2*SINE_SERIES_TERMS+1))
    if SINE_SERIES_TERMS % 2 == 0:
        low, high = total, total+term
    else:
        low, high = total+term, total
    low = max(Fraction(0), low)
    high = min(Fraction(1), high)
    if not 0 <= low <= high <= 1:
        raise ShadowEnclosureError("sine alternating-series bound inverted")
    return low, high


def _h_at_angular_midpoint(index: int, n: int, x: Fraction, q: Fraction):
    """Enclose H(x/sqrt(1-(1-q^2)*sin^2(phi_i))) rationally."""
    pi_lo, pi_hi = _pi_fraction_bounds()
    factor = Fraction(2*index+1, 4*n)
    sin_lo, _ = _sin_rational_bounds(pi_lo*factor)
    _, sin_hi = _sin_rational_bounds(pi_hi*factor)
    alpha = 1-q*q
    d_low = 1-alpha*sin_hi*sin_hi
    d_high = 1-alpha*sin_lo*sin_lo
    if not 0 < d_low <= d_high <= 1:
        raise ShadowEnclosureError("inverted elliptical geometry denominator")
    root_lo, _ = _sqrt_rational_bounds(d_low, SQRT_BITS)
    _, root_hi = _sqrt_rational_bounds(d_high, SQRT_BITS)
    if root_lo <= 0:
        raise ShadowEnclosureError("integer square-root enclosure underresolved")
    v_low, v_high = x/root_hi, x/root_lo
    h_low = _disk_integral_fraction(v_low)[0]
    h_high = _disk_integral_fraction(v_high)[1]
    if not 0 <= h_low <= h_high <= 1:
        raise ShadowEnclosureError("inverted exponential-disc midpoint bounds")
    return h_low, h_high


def _directed(x: Fraction, ctx: Context) -> Decimal:
    return ctx.divide(Decimal(x.numerator), Decimal(x.denominator))


def certified_periodic_exponential_disk_point(
    radius_kpc, mass_msun, exponential_scale_kpc, axis_ratio,
    *, midpoints: int = MESH_MIDPOINTS,
    target_relative_width: str = TARGET_RELATIVE_WIDTH,
):
    """Mathematical continuum disc mass enclosure with a PROVED midpoint error.

    The target flags a goal and is NEVER used to assume an error. For any
    valid mesh the reported interval encloses the exact frozen-parameter
    analytic period-integrated mass, even when target_met is false.
    """
    if type(midpoints) is not int or not 8 <= midpoints <= 4096:
        raise ShadowEnclosureError("unregistered certified angular mesh")
    if not isinstance(target_relative_width, str):
        raise ShadowEnclosureError("precision target must be a decimal string")
    try:
        target = Decimal(target_relative_width)
    except Exception as exc:
        raise ShadowEnclosureError("invalid angular accuracy target") from exc
    if not (target.is_finite() and Decimal("1e-8") <= target <= Decimal(".1")):
        raise ShadowEnclosureError("angular target outside approved contract")
    radius, mass, scale, q = map(_fraction, (
        radius_kpc, mass_msun, exponential_scale_kpc, axis_ratio,
    ))
    if not (0 < radius <= _fraction(120.) and mass > 0 and scale > 0
            and 0 < q <= 1):
        raise ShadowEnclosureError("invalid exact-binary64 exponential-disc inputs")

    x = radius/scale
    alpha = 1-q*q
    # H'(v)=v*exp(-v), |H''(v)|=|1-v|*exp(-v)<=1.
    # d=cos^2(phi)+q^2 sin^2(phi) in [q^2,1], v=x/d^1/2.
    # |d'|<=alpha, |d''|<=2*alpha imply
    # |(H(v))''| <= K = x^2*(alpha^2/q^6 + alpha/q^4).
    # Composite midpoint error for the normalized [0,pi/2] average:
    # <= K*pi^2/(96*midpoints^2).
    K = x*x*(alpha*alpha/q**6 + alpha/q**4)
    _, pi_hi = _pi_fraction_bounds()
    err = K*pi_hi*pi_hi/(96*midpoints*midpoints)

    lc = Context(prec=DECIMAL_DIGITS, rounding=ROUND_FLOOR)
    uc = Context(prec=DECIMAL_DIGITS, rounding=ROUND_CEILING)
    low_sum, high_sum = Decimal(0), Decimal(0)
    for j in range(midpoints):
        h_lo, h_hi = _h_at_angular_midpoint(j, midpoints, x, q)
        low_sum = lc.add(low_sum, _directed(h_lo, lc))
        high_sum = uc.add(high_sum, _directed(h_hi, uc))
    error_upper = _directed(err, uc)
    average_low = lc.subtract(lc.divide(low_sum, Decimal(midpoints)), error_upper)
    average_high = uc.add(uc.divide(high_sum, Decimal(midpoints)), error_upper)
    factor_low = max(Decimal(0), average_low)
    factor_high = min(Decimal(1), average_high)

    mass_low = lc.multiply(_directed(mass, lc), factor_low)
    mass_high = uc.multiply(_directed(mass, uc), factor_high)
    if not (0 <= mass_low <= mass_high <= uc.multiply(_directed(mass, uc), Decimal(1))):
        raise ShadowEnclosureError("certified angular mass enclosure inverted")
    interval_width = uc.subtract(mass_high, mass_low)
    relative = uc.divide(interval_width, mass_low) if mass_low > 0 else None
    return {
        "schema": SCHEMA,
        "lower_msun": format(mass_low, "f"),
        "upper_msun": format(mass_high, "f"),
        "relative_interval_width_upper": format(relative, "f") if relative is not None else None,
        "target_relative_width": target_relative_width,
        "target_met": bool(relative is not None and relative <= target),
        "mesh_midpoints": midpoints,
        "midpoint_normalized_error_upper": format(error_upper, "f"),
        "second_derivative_bound_K_exact_rational": {
            "numerator": str(K.numerator), "denominator": str(K.denominator),
        },
        "math_model": "EXACT_BINARY64_ELLIPTICAL_EXPONENTIAL_DISK_FULL_CONTINUUM_AZIMUTH",
        "method": "QUADRANT_TAN_SUBSTITUTION_RATIONAL_SINE_EXP_AND_CERTIFIED_MIDPOINT_ERROR",
        "source_periodic1024_floating_quadrature_error_certified": False,
        "source_cosmological_physics_certified": False,
    }


def certified_periodic_exponential_disk_radius_band(
    min_radius, max_radius, mass, scale, q, **kwargs,
):
    """For ALL real radii in the registered interval via positive mass."""
    lo, hi = _fraction(min_radius), _fraction(max_radius)
    if not 0 < lo <= hi <= _fraction(120.):
        raise ShadowEnclosureError("invalid periodic analytic disc radius band")
    left = certified_periodic_exponential_disk_point(min_radius,mass,scale,q,**kwargs)
    right = left if lo==hi else certified_periodic_exponential_disk_point(
        max_radius,mass,scale,q,**kwargs,
    )
    if Decimal(left["lower_msun"]) > Decimal(right["upper_msun"]):
        raise ShadowEnclosureError("certified disc radius band inverted")
    return {
        "lower_msun": left["lower_msun"],
        "upper_msun": right["upper_msun"],
        "endpoints": [left, right],
        "all_real_radii_in_band_enclosed": True,
        "endpoint_targets_met": all(e["target_met"] for e in (left,right)),
        "source_periodic1024_implementation_error_certified": False,
        "proof": "POSITIVE_EXPONENTIAL_DISK_MASS_MONOTONICITY_AND_CERTIFIED_FULL_AZIMUTH_MIDPOINT",
    }
