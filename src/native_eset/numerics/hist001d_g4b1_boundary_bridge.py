"""G4b.1: exact-rational finite-domain boundary bridge; NOT a root proof.

This pure helper does not certify source baryon/shadow/Sigma inputs, evaluate
real lens residuals, prove roots, or establish physical Weyl lensing.
It preserves Decimal/rational mathematical intervals without a float() detour.
"""
from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from math import isqrt, nextafter

SCHEMA = "HIST001D_D2E_G4B1_EXACT_RATIONAL_BOUNDARY_BRIDGE_V1"
SOURCE_LOCK_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
SOURCE_RMIN = Fraction.from_float(0.02)
SOURCE_RMAX = Fraction.from_float(120.0)
SOURCE_QFLOOR = Fraction.from_float(0.001)
MAX_BITS = 2048
PHYSICAL_PROVIDER_ADMITTED = False
ROOT_EXISTENCE_OR_UNIQUENESS_CERTIFIED = False


class G4b1BridgeError(ValueError):
    """Malformed exact number, mathematical interval or unsafe source domain."""


def _bounded(value: Fraction) -> Fraction:
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_BITS:
        raise G4b1BridgeError("rational exceeds size budget")
    return value


def exact_number(value: object) -> Fraction:
    """Interpret binary64 floats as dyadics and printed decimals EXACTLY."""
    if isinstance(value, Fraction):
        return _bounded(value)
    if type(value) is int:
        return _bounded(Fraction(value))
    if type(value) is float:
        if not math.isfinite(value):
            raise G4b1BridgeError("nonfinite binary64")
        return _bounded(Fraction.from_float(value))
    if type(value) is str and 0 < len(value) <= 256:
        try:
            decimal = Decimal(value)
            if not decimal.is_finite() or abs(decimal.as_tuple().exponent) > 256:
                raise G4b1BridgeError("invalid exact-decimal exponent")
            return _bounded(Fraction(decimal))
        except (ValueError, InvalidOperation, OverflowError) as exc:
            raise G4b1BridgeError("malformed exact decimal") from exc
    raise G4b1BridgeError("unsupported rational input")


def exact_interval(low: object, high: object, *, positive: bool = False) -> tuple[Fraction, Fraction]:
    lower, upper = exact_number(low), exact_number(high)
    if upper < lower or (positive and lower <= 0):
        raise G4b1BridgeError("inverted or nonpositive interval")
    return lower, upper


def _float_outward(value: Fraction, *, upper: bool) -> float:
    _bounded(value)
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise G4b1BridgeError("rational endpoint not binary64 representable") from exc
    if not math.isfinite(result):
        raise G4b1BridgeError("rational endpoint overflow")
    represented = Fraction.from_float(result)
    if upper and represented < value:
        result = nextafter(result, math.inf)
    elif not upper and represented > value:
        result = nextafter(result, -math.inf)
    represented = Fraction.from_float(result)
    if (upper and represented < value) or (not upper and represented > value):
        raise G4b1BridgeError("failed outward binary64 conversion")
    return result


def outward_radius_for_legacy_points(
    lower: Fraction, upper: Fraction,
) -> tuple[float, float]:
    """Expand an exact G4b.0 cell before invoking a float-only point kernel.

    Point-kernel outputs only become a real-radius enclosure WITH a separately
    proved projected-mass monotonicity theorem. The exact RMIN bulge endpoint
    requires the separate strictly positive Hernquist lemma below.
    """
    lo, hi = exact_interval(lower, upper, positive=True)
    if not SOURCE_RMIN <= lo <= hi <= SOURCE_RMAX:
        raise G4b1BridgeError("source cell escapes frozen finite domain")
    a, b = _float_outward(lo, upper=False), _float_outward(hi, upper=True)
    ra, rb = Fraction.from_float(a), Fraction.from_float(b)
    if not SOURCE_RMIN <= ra <= lo <= hi <= rb <= SOURCE_RMAX:
        raise G4b1BridgeError("outward cell drift escaped original domain")
    return a, b


def proven_positive_hernquist_mass_at_left_source_boundary(
    mass_msun: float, a_kpc: float,
) -> Fraction:
    """Positive lower bound for finite cylindrical Hernquist mass at RMIN.

    B(R0) = 2*M*a * integral_[R0,RMAX]
        (r - sqrt(r*r - R0*R0)) / (r+a)**3 dr.

    On r in [R0,2R0], r-sqrt(r*r-R0*R0) >= R0*R0/(2*r)
    >= R0/4 and (r+a)**3 <= (2R0+a)**3. Therefore:
        B(R0) >= M*a*R0**2 / [2*(2R0+a)**3] > 0.
    This conservative bound need not resolve any real source root.
    """
    if type(mass_msun) is not float or type(a_kpc) is not float:
        raise G4b1BridgeError("frozen masses/scale must be explicit binary64 floats")
    mass, scale = exact_number(mass_msun), exact_number(a_kpc)
    r = SOURCE_RMIN
    if not (0 < mass and 0 < scale and 2*r <= SOURCE_RMAX):
        raise G4b1BridgeError("nonpositive Hernquist parameter or unsafe shell")
    result = mass*scale*r*r / (2*(2*r+scale)**3)
    if result <= 0:
        raise G4b1BridgeError("failed positive finite Hernquist boundary lemma")
    return _bounded(result)


def positive_baryon_q_box(
    bulge: tuple[object, object], disk: tuple[object, object],
    q_bulge_binary64: float, q_disk_binary64: float,
) -> tuple[Fraction, Fraction]:
    """Exact four-corner baryonic q extrema; original binary64 q floor."""
    blo, bhi = exact_interval(*bulge, positive=True)
    dlo, dhi = exact_interval(*disk, positive=True)
    if type(q_bulge_binary64) is not float or type(q_disk_binary64) is not float:
        raise G4b1BridgeError("q parameters must be frozen explicit binary64")
    qb, qd = exact_number(q_bulge_binary64), exact_number(q_disk_binary64)
    if not (0 < qb <= 1 and 0 < qd <= 1):
        raise G4b1BridgeError("invalid source q constants")
    values = [(qb*b+qd*d)/(b+d) for b in (blo,bhi) for d in (dlo,dhi)]
    lo = max(SOURCE_QFLOOR, min(Fraction(1), min(values)))
    hi = max(SOURCE_QFLOOR, min(Fraction(1), max(values)))
    if not SOURCE_QFLOOR <= lo <= hi <= 1:
        raise G4b1BridgeError("invalid q enclosure")
    return _bounded(lo), _bounded(hi)


def sqrt_rational_box(x: Fraction, bits: int = 88) -> tuple[Fraction, Fraction]:
    if type(bits) is not int or not 64 <= bits <= 160 or x <= 0:
        raise G4b1BridgeError("invalid exact sqrt proof parameters")
    _bounded(x)
    n = isqrt((x.numerator << (2*bits)) // x.denominator)
    scale = 1 << bits
    return Fraction(n, scale), Fraction(n+1, scale)


def source_aperture_outward_band(
    radius_min: Fraction, radius_max: Fraction,
    q_min: Fraction, q_max: Fraction,
) -> tuple[float, float]:
    """Exact q/sqrt aperture bounds, binary64 outward, source cap at 120 kpc."""
    rlo, rhi = exact_interval(radius_min, radius_max, positive=True)
    qlo, qhi = exact_interval(q_min, q_max, positive=True)
    if not (SOURCE_RMIN <= rlo <= rhi <= SOURCE_RMAX
            and SOURCE_QFLOOR <= qlo <= qhi <= 1):
        raise G4b1BridgeError("unregistered radius/q source band")
    sqrt_lo, _ = sqrt_rational_box(qlo)
    _, sqrt_hi = sqrt_rational_box(qhi)
    if sqrt_lo <= 0:
        raise G4b1BridgeError("insufficient positive sqrt precision")
    true_lo = min(SOURCE_RMAX, rlo/sqrt_hi)
    true_hi = min(SOURCE_RMAX, rhi/sqrt_lo)
    low, high = _float_outward(true_lo, upper=False), _float_outward(true_hi, upper=True)
    if not (0 <= Fraction.from_float(low) <= true_lo <= true_hi
            <= Fraction.from_float(high) <= SOURCE_RMAX):
        raise G4b1BridgeError("outward source aperture enclosure failed")
    return low, high


# No certified all-R source-matched masses, shadow density, critical Sigma
# or historical residuals are computed by this mathematical helper.
# The source-root, physical-provider, and blind-holdout gates stay OPEN.
