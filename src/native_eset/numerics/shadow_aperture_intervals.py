"""D2e-F: certified aperture-band shadow mass; conditional structured-root inputs.

All definitive inequalities refer to EXACT binary64 source radii/densities and
the finite piecewise-linear spherical cylinder integral, with aperture varying
over a real interval bounded by two outward binary64 endpoints.

Baryonic mass ranges and the resulting R-to-q_eff mapping are CONDITIONAL
inputs: floating endpoint evaluations are not rigorously certified all-radius
baryonic bounds. No physical provider or global root theorem is authorized.
"""
from __future__ import annotations

import math
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction

from native_eset.numerics.adaptive_shadow_bounds import (
    MAX_REFINEMENT_SPLITS,
    TARGET_RELATIVE_WIDTH,
    enclose_adaptive_convex_shadow,
)
from native_eset.numerics.exact_shadow_bounds import (
    ShadowEnclosureError,
    _fraction,
    _pi_fraction_bounds,
    _sqrt_rational_bounds,
)

Q_FLOOR = Fraction.from_float(0.001)
SOURCE_RADIUS_MAX = Fraction(120)
SQRT_BITS = 88
DECIMAL_DIGITS = 70


def _rational_pair(x: Fraction) -> dict:
    return {"num": str(x.numerator), "den": str(x.denominator)}


def _outward_float(value: Fraction, *, upper: bool) -> float:
    """A float representable outside the exact rational target."""
    candidate = float(value)
    if not math.isfinite(candidate) or candidate < 0:
        raise ShadowEnclosureError("outward dyadic aperture cannot be represented")
    rational = Fraction.from_float(candidate)
    if upper and rational < value:
        candidate = math.nextafter(candidate, math.inf)
    if not upper and rational > value:
        candidate = math.nextafter(candidate, -math.inf)
    rational = Fraction.from_float(candidate)
    if (upper and rational < value) or (not upper and rational > value):
        raise ShadowEnclosureError("failed to outward round aperture endpoint")
    if candidate < 0:
        raise ShadowEnclosureError("rounded aperture below zero")
    return candidate


def frozen_baryonic_q_corners(bulge_min, bulge_max, disc_min, disc_max, q_bulge, q_disc):
    """Exact corner extrema for a weighted q ratio on a POSITIVE mass box.

    This is rigorous GIVEN input masses are valid all-R enclosures; we do not
    certify that historical floating baryonic endpoint quadratures enclose
    their entire continuous analytical mass functions.
    """
    lo_b, hi_b, lo_d, hi_d, qb, qd = (
        _fraction(x, nonnegative=False)
        for x in (bulge_min, bulge_max, disc_min, disc_max, q_bulge, q_disc)
    )
    if not (0 < lo_b <= hi_b and 0 < lo_d <= hi_d and
            0 < qb <= 1 and 0 < qd <= 1):
        raise ShadowEnclosureError("invalid positive baryonic corner inputs")
    qvalues = [
        (qb*b+qd*d)/(b+d)
        for b in (lo_b, hi_b) for d in (lo_d, hi_d)
    ]
    qmin = max(Q_FLOOR, min(Fraction(1), min(qvalues)))
    qmax = max(Q_FLOOR, min(Fraction(1), max(qvalues)))
    if not (0 < qmin <= qmax <= 1):
        raise ShadowEnclosureError("inverted frozen-q corner box")
    return {
        "q_min": _rational_pair(qmin),
        "q_max": _rational_pair(qmax),
        "assumption": "INPUT_BARYON_MASS_INTERVALS_SOUND_FOR_ALL_RADIUS_VALUES_NOT_PROVED",
        "valid_given_mass_box": True,
    }


def _q_from_pair(x):
    if set(x) != {"num", "den"}:
        raise ShadowEnclosureError("malformed exact fraction pair")
    n, d = int(x["num"]), int(x["den"])
    if d <= 0:
        raise ShadowEnclosureError("zero/negative denominator")
    return Fraction(n, d)


def conditional_aperture_band(
    radius_min, radius_max, mass_box: dict, *,
    source_max_radius: float = 120.0, sqrt_bits: int = SQRT_BITS,
):
    """Enclose R/sqrt(q(R)) if the input baryon mass box is truly sound.

    Extra outward rounding of the endpoints makes the resulting A interval
    valid for every REAL R under the mass-box assumption, but DOES NOT
    establish that assumption for source-equivalent baryonic functions.
    """
    rl, rh = _fraction(radius_min), _fraction(radius_max)
    top = _fraction(source_max_radius)
    if top != SOURCE_RADIUS_MAX or not (0 < rl <= rh <= top):
        raise ShadowEnclosureError("radius band outside registered source domain")
    qlo, qhi = _q_from_pair(mass_box["q_min"]), _q_from_pair(mass_box["q_max"])
    if not (Q_FLOOR <= qlo <= qhi <= 1):
        raise ShadowEnclosureError("malformed q corner range")
    sqlo, _ = _sqrt_rational_bounds(qlo, sqrt_bits)
    _, sqhi = _sqrt_rational_bounds(qhi, sqrt_bits)
    if sqlo <= 0:
        raise ShadowEnclosureError("square-root precision cannot bound q")
    min_real = min(top, rl / sqhi)
    max_real = min(top, rh / sqlo)
    lo = _outward_float(min_real, upper=False)
    hi = _outward_float(max_real, upper=True)
    if not 0 <= lo <= hi <= float(top):
        raise ShadowEnclosureError("outward binary64 aperture band invalid")
    return {
        "aperture_min_kpc": lo,
        "aperture_max_kpc": hi,
        "exact_q_range": {"lower":mass_box["q_min"], "upper":mass_box["q_max"]},
        "conditioning": "UNPROVED_ALL_RADIUS_BARYON_MASS_BOX_ASSUMPTION",
        "aperture_interval_is_sufficient_if_baryonic_box_sound": True,
    }


def certified_shadow_mass_band(radial, density, aperture_min, aperture_max):
    """Rigorous all-aperture M_sh envelope on a registered finite source grid.

    M_sh(A) is nondecreasing because every cylindrical mass kernel increases
    with A for nonnegative 3D density. Therefore enclosure lower at A_min
    and enclosure upper at A_max bounds all intermediate real apertures.
    Unlike quadrature uncertainty, mass change across the aperture band is
    physical variation WITHIN this explicitly selected finite discrete model.
    """
    lo, hi = _fraction(aperture_min), _fraction(aperture_max)
    if not 0 <= lo <= hi <= SOURCE_RADIUS_MAX:
        raise ShadowEnclosureError("shadow aperture interval invalid")
    if lo == 0:
        lower_result = {
            "lower_msun": "0", "upper_msun": "0",
            "target_met": True, "status": "EXACT_ZERO_APERTURE",
            "relative_interval_width_upper": None,
        }
    else:
        lower_result = enclose_adaptive_convex_shadow(
            radial, density, aperture_min,
            target_relative_width=TARGET_RELATIVE_WIDTH,
            max_refinement_splits=MAX_REFINEMENT_SPLITS,
        )
    if lo == hi:
        upper_result = lower_result
    else:
        upper_result = enclose_adaptive_convex_shadow(
            radial, density, aperture_max,
            target_relative_width=TARGET_RELATIVE_WIDTH,
            max_refinement_splits=MAX_REFINEMENT_SPLITS,
        )
    left = Decimal(lower_result["lower_msun"])
    right = Decimal(upper_result["upper_msun"])
    if not (left.is_finite() and right.is_finite() and 0 <= left <= right):
        raise ShadowEnclosureError("inconsistent monotone shadow mass bound")
    return {
        "aperture_min_kpc": float(aperture_min),
        "aperture_max_kpc": float(aperture_max),
        "lower_msun": format(left, "f"),
        "upper_msun": format(right, "f"),
        "endpoint_lower_evaluation": lower_result,
        "endpoint_upper_evaluation": upper_result,
        "both_endpoint_precision_targets_met": (
            lower_result["target_met"] and upper_result["target_met"]
        ),
        "all_real_apertures_between_binary64_endpoints_enclosed": True,
        "assumptions": "NONNEGATIVE_EXACT_BINARY64_NODAL_PIECEWISE_LINEAR_DENSITY",
        "full_radius_lens_model_certified": False,
    }


def _directed_fraction(v: Fraction, *, upper: bool) -> str:
    ctx = Context(prec=DECIMAL_DIGITS,
                  rounding=ROUND_CEILING if upper else ROUND_FLOOR)
    return format(ctx.divide(Decimal(v.numerator), Decimal(v.denominator)), "f")


def conditional_normalized_root_residual_band(
    radius_min, radius_max,
    bulge_min, bulge_max, disc_min, disc_max,
    sigma_critical, shadow_mass_band: dict,
):
    """Conditional F-normalization bounds using EXACT binary64 box inputs.

    q(R) itself has already been used to define the aperture band. This
    function assumes its input baryonic extrema genuinely bound the
    continuous baryonic mass within [R_min,R_max], which remains UNPROVED.
    sigma_critical is also treated as an exact frozen binary64 value.
    """
    rl, rh, blo, bhi, dlo, dhi, sigma = (
        _fraction(x, nonnegative=False) for x in (
            radius_min, radius_max, bulge_min, bulge_max,
            disc_min, disc_max, sigma_critical,
        )
    )
    if not (0 < rl <= rh <= SOURCE_RADIUS_MAX and
            0 < blo <= bhi and 0 < dlo <= dhi and sigma > 0):
        raise ShadowEnclosureError("invalid conditional residual inputs")
    sl = Fraction(Decimal(shadow_mass_band["lower_msun"]))
    sh = Fraction(Decimal(shadow_mass_band["upper_msun"]))
    if sl < 0 or sh < sl:
        raise ShadowEnclosureError("invalid shadow mass band in residual")
    pi_lo, pi_hi = _pi_fraction_bounds()
    lower = (blo+dlo+sl)/(pi_hi*sigma*rh*rh) - 1
    upper = (bhi+dhi+sh)/(pi_lo*sigma*rl*rl) - 1
    if lower > upper:
        raise ShadowEnclosureError("inverted conditional normalized residual bound")
    label = "POSITIVE_UNDER_INPUT_ASSUMPTION" if lower > 0 else (
        "NEGATIVE_UNDER_INPUT_ASSUMPTION" if upper < 0
        else "ZERO_NOT_EXCLUDED_UNDER_INPUT_ASSUMPTION"
    )
    return {
        "normalized_residual_lower": _directed_fraction(lower, upper=False),
        "normalized_residual_upper": _directed_fraction(upper, upper=True),
        "conditional_sign": label,
        "all_radius_root_uniqueness_certified": False,
        "baryonic_continuous_mass_bounds_verified": False,
        "sigma_critical_physical_error_bounded": False,
        "proof_scope": "CONDITIONAL_ON_UNPROVED_BARYON_ENDPOINT_MASS_BOX",
    }
