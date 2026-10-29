"""Exact-rational pointwise bounds for finite cylindrical projection of linear rho.

This math kernel encloses M_sh,sph(A) for EXACT binary64 nodal radius/density
and aperture inputs under a nonnegative, piecewise-linear interpolant. It
certifies neither upstream density-generation accuracy nor q_eff/baryonic
mass, continuous-R root topology, nor density outside the finite domain.
"""
from __future__ import annotations

from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction
from functools import lru_cache
from math import isfinite, isqrt


class ShadowEnclosureError(ValueError):
    """Invalid numerical source, scope, or exact-enclosure arithmetic."""


@lru_cache(maxsize=1)
def _pi_fraction_bounds() -> tuple[Fraction, Fraction]:
    """Bound pi by alternating rational Machin-arctangent partial sums."""
    def arctan_bounds(denominator: int, terms: int):
        total = Fraction(0)
        for k in range(terms):
            term = Fraction(1, (2*k+1) * denominator**(2*k+1))
            total += term if k % 2 == 0 else -term
        next_term = Fraction(1, (2*terms+1) * denominator**(2*terms+1))
        return (total, total + next_term) if terms % 2 == 0 else (total - next_term, total)

    five_lo, five_hi = arctan_bounds(5, 60)
    two_lo, two_hi = arctan_bounds(239, 16)
    lo, hi = 16*five_lo - 4*two_hi, 16*five_hi - 4*two_lo
    if not 3 < lo < hi < 4:
        raise ShadowEnclosureError("Machin arctangent proof bound invalid")
    return lo, hi


def _fraction(x: object, *, nonnegative: bool = True) -> Fraction:
    if isinstance(x, bool):
        raise ShadowEnclosureError("Boolean is not a real nodal value")
    try:
        v = float(x)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ShadowEnclosureError("nodal value not binary64 convertible") from exc
    if not isfinite(v) or (nonnegative and v < 0):
        raise ShadowEnclosureError("nonfinite or negative nodal input")
    return Fraction.from_float(v)


def _sqrt_rational_bounds(value: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    """Integer-isqrt lower/upper bounds of the exact nonnegative rational sqrt."""
    if value < 0 or not 40 <= bits <= 160:
        raise ShadowEnclosureError("invalid exact sqrt bound")
    k = isqrt((value.numerator << (2*bits)) // value.denominator)
    scale = 1 << bits
    lo = Fraction(k, scale)
    hi = Fraction(k+1, scale)
    return lo, hi


def _kernel_bounds(r: Fraction, aperture: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    """r*(r-sqrt(r^2-A^2)); monotone DECREASING in r >= A."""
    if not 0 <= aperture <= r:
        raise ShadowEnclosureError("outer cylindrical kernel outside physical domain")
    sqrt_lo, sqrt_hi = _sqrt_rational_bounds(r*r - aperture*aperture, bits)
    numerator = aperture*aperture*r
    return numerator/(r+sqrt_hi), numerator/(r+sqrt_lo)


def _inside_primitive(a: Fraction, r: Fraction, rho_a: Fraction, slope: Fraction) -> Fraction:
    """Exact integral of (rho_a + slope*(x-a))*x^2 from a to r."""
    x = r-a
    return (rho_a*a*a*x + (2*rho_a*a+slope*a*a)*x*x/2
            + (rho_a+2*slope*a)*x*x*x/3 + slope*x**4/4)


def _as_decimal(value: Fraction, context: Context) -> Decimal:
    return context.divide(Decimal(value.numerator), Decimal(value.denominator))


def _upward_distance(a: Decimal, b: Decimal, context: Context) -> Decimal:
    return context.subtract(max(a, b), min(a, b))


def enclose_finite_cylinder_mass(
    radial_kpc, density_msun_per_kpc3, aperture_kpc,
    *, decimal_precision: int = 70, sqrt_bits: int = 88,
) -> dict:
    """Return true two-sided rational/Decimal-directed MASS enclosure.

    Input floating-point values are treated as their EXACT binary64 rationals;
    no assumption about how original continuum source computed them follows.
    No floating quadrature or transcendental function is used in the proof.
    Monotone-shell bounds are valid at ONE fixed aperture, not an R interval.
    """
    if type(decimal_precision) is not int or not 48 <= decimal_precision <= 120:
        raise ShadowEnclosureError("unsupported directed Decimal precision")
    if type(sqrt_bits) is not int or not 40 <= sqrt_bits <= 160:
        raise ShadowEnclosureError("unsupported integer-isqrt precision")
    if len(radial_kpc) != len(density_msun_per_kpc3) or not 2 <= len(radial_kpc) <= 25000:
        raise ShadowEnclosureError("invalid finite radial input lengths")
    r = [_fraction(x) for x in radial_kpc]
    rho = [_fraction(x) for x in density_msun_per_kpc3]
    aperture = _fraction(aperture_kpc)
    if r[0] <= 0 or aperture > r[-1]:
        raise ShadowEnclosureError("aperture or source interval outside finite source domain")
    if any(b <= a for a, b in zip(r[:-1], r[1:])):
        raise ShadowEnclosureError("radius nodes not strictly increasing")

    lc = Context(prec=decimal_precision, rounding=ROUND_FLOOR)
    uc = Context(prec=decimal_precision, rounding=ROUND_CEILING)
    lower, upper = Decimal(0), Decimal(0)
    inside_cells, outer_cells, split_cells = 0, 0, 0
    for a, b, ya, yb in zip(r[:-1], r[1:], rho[:-1], rho[1:]):
        h = b-a
        slope = (yb-ya)/h
        if b <= aperture:
            x = _inside_primitive(a, b, ya, slope)
            low_term = high_term = x
            inside_cells += 1
        elif a >= aperture:
            density_integral = (ya+yb)*h/2
            g_lo, _ = _kernel_bounds(b, aperture, sqrt_bits)
            _, g_hi = _kernel_bounds(a, aperture, sqrt_bits)
            low_term, high_term = g_lo*density_integral, g_hi*density_integral
            outer_cells += 1
        else:
            split_density = ya+slope*(aperture-a)
            inner = _inside_primitive(a, aperture, ya, slope)
            outer_density_integral = (split_density+yb)*(b-aperture)/2
            g_lo, _ = _kernel_bounds(b, aperture, sqrt_bits)
            _, g_hi = _kernel_bounds(aperture, aperture, sqrt_bits)
            low_term = inner + g_lo*outer_density_integral
            high_term = inner + g_hi*outer_density_integral
            split_cells += 1
        if low_term < 0 or high_term < low_term:
            raise ShadowEnclosureError("negative or inverted rational shell mass")
        lower = lc.add(lower, _as_decimal(low_term, lc))
        upper = uc.add(upper, _as_decimal(high_term, uc))

    pi_lo, pi_hi = _pi_fraction_bounds()
    mass_lo = lc.multiply(lc.multiply(lower, Decimal(4)), _as_decimal(pi_lo, lc))
    mass_hi = uc.multiply(uc.multiply(upper, Decimal(4)), _as_decimal(pi_hi, uc))
    if mass_lo < 0 or mass_hi < mass_lo:
        raise ShadowEnclosureError("invalid directed-shadow mass bounds")
    width = uc.subtract(mass_hi, mass_lo)
    frac_width = uc.divide(width, mass_lo) if mass_lo else None
    return {
        "lower_msun": format(mass_lo, "f"),
        "upper_msun": format(mass_hi, "f"),
        "relative_interval_width_upper": format(frac_width, "f") if frac_width is not None else None,
        "radius_nodes": len(r),
        "inside_cells": inside_cells,
        "outside_cells": outer_cells,
        "crossing_cells": split_cells,
        "decimal_precision_digits": decimal_precision,
        "integer_isqrt_bits": sqrt_bits,
        "input_semantics": "EXACT_BINARY64_RADIAL_DENSITY_AND_APERTURE",
        "proof_scope": "FINITE_PIECEWISE_LINEAR_DENSITY_AT_ONE_FIXED_APERTURE_ONLY",
    }


def guaranteed_pointwise_error(reference_msun: float, enclosure: dict) -> dict:
    """Upper bound on |float reference - exact discretized cylinder mass|.

    The returned decimal is upward rounded. Not a global bound on a source
    density, R-dependent q_eff, derivative, or physical Weyl lensing.
    """
    _fraction(reference_msun)
    lo = Decimal(enclosure["lower_msun"])
    hi = Decimal(enclosure["upper_msun"])
    ctx = Context(prec=int(enclosure["decimal_precision_digits"]), rounding=ROUND_CEILING)
    # Decimal.from_float is EXACT; upward rounding this input before
    # subtracting could invalidate the one-sided distance bound.
    mass = Decimal.from_float(float(reference_msun))
    err = max(_upward_distance(mass, lo, ctx), _upward_distance(mass, hi, ctx))
    relative = ctx.divide(err, lo) if lo > 0 else None
    return {
        "absolute_error_upper_msun": format(err, "f"),
        "relative_error_upper": format(relative, "f") if relative is not None else None,
        "comparison_role": "CERTIFIED_POINTWISE_DISCRETE_SHADOW_ONLY",
    }
