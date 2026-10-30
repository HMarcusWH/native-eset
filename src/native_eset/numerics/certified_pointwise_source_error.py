"""G3a: certified POINTWISE discrepancy of a frozen binary64 output.

If exact frozen-parameter mathematical target T lies in rigorous [L,U],
and the source returned a finite binary64 V, the exact-dyadic arithmetic
guarantees |V-T| <= max(|V-L|, |V-U|).

This does NOT certify the source numerical implementation for every input,
the continuum parameter-generation model, an R interval, or any root count.
"""
from __future__ import annotations

import math
from decimal import Context, Decimal, InvalidOperation, ROUND_CEILING
from fractions import Fraction

from native_eset.numerics.exact_shadow_bounds import ShadowEnclosureError

DECIMAL_PRECISION = 80
SCHEMA = "HIST001D_G3A_POINTWISE_FROZEN_SOURCE_OUTPUT_DISCREPANCY_V1"


def _fraction_from_bound(x) -> Fraction:
    if isinstance(x, bool):
        raise ShadowEnclosureError("bool is not a certified bound")
    try:
        dec = Decimal(x)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ShadowEnclosureError("invalid decimal certified endpoint") from exc
    if not dec.is_finite():
        raise ShadowEnclosureError("nonfinite certified endpoint")
    return Fraction(dec)


def _source_dyadic(x) -> Fraction:
    if isinstance(x, bool):
        raise ShadowEnclosureError("boolean is not a source output")
    try:
        value = float(x)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ShadowEnclosureError("unreadable source output") from exc
    if not math.isfinite(value):
        raise ShadowEnclosureError("nonfinite source output")
    return Fraction.from_float(value)


def _round_upper(f: Fraction) -> str:
    if f < 0:
        raise ShadowEnclosureError("negative error bound")
    c = Context(prec=DECIMAL_PRECISION, rounding=ROUND_CEILING)
    return format(c.divide(Decimal(f.numerator), Decimal(f.denominator)), "f")


def certified_pointwise_source_error(
    source_output_binary64, certified_lower, certified_upper,
) -> dict:
    """Prove a posteriori discrepancy for one registered source output.

    Exact comparisons use Fraction of full source float bit pattern and
    rational value of the directed decimal interval strings. Only the FINAL
    display of a proven nonnegative error upper is rounded outward.
    """
    v = _source_dyadic(source_output_binary64)
    lower, upper = _fraction_from_bound(certified_lower), _fraction_from_bound(
        certified_upper
    )
    if not (0 <= lower <= upper and v >= 0):
        raise ShadowEnclosureError("invalid or inverted positive mass/q box")
    deviation = max(abs(v-lower),abs(v-upper))
    relative_true = deviation/lower if lower > 0 else None
    relative_returned = deviation/v if v > 0 else None
    return {
        "schema": SCHEMA,
        "registered_source_returned_binary64": float(source_output_binary64),
        "source_returned_exact_dyadic_numerator": str(v.numerator),
        "source_returned_exact_dyadic_denominator": str(v.denominator),
        "analytic_target_lower_exact_decimal": str(certified_lower),
        "analytic_target_upper_exact_decimal": str(certified_upper),
        "source_returned_inside_analytic_target_enclosure":lower <= v <= upper,
        "absolute_discrepancy_upper":_round_upper(deviation),
        "relative_to_true_lower_upper":(
            _round_upper(relative_true) if relative_true is not None else None
        ),
        "relative_to_source_return_upper":(
            _round_upper(relative_returned)
            if relative_returned is not None else None
        ),
        "single_registered_output_vs_exact_binary64_parameter_analytic_model":True,
        "all_radius_implementation_error_certified":False,
        "physical_or_observational_error_bar":False,
    }


def certified_pointwise_q_error(source_q, model_q_lower:Fraction, model_q_upper:Fraction):
    """Pointwise q_eff discrepancy using exact-rational four-corner q bounds.

    The model q bounds must be independently justified from positive
    analytic-continuum bulge and disk intervals. Source q itself is a
    finite recorded binary64 output; no guarantee for other source calls.
    """
    lo, hi = model_q_lower, model_q_upper
    if not (isinstance(lo,Fraction) and isinstance(hi,Fraction)
            and 0 < lo <= hi <= 1):
        raise ShadowEnclosureError("untrusted mathematical q_eff interval")
    v = _source_dyadic(source_q)
    if not 0 < v <= 1:
        raise ShadowEnclosureError("source returned invalid q_eff")
    deviation = max(abs(v-lo),abs(v-hi))
    return {
        "schema":"HIST001D_G3A_EXACT_RATIONAL_Q_POINTWISE_V1",
        "source_qeff_binary64":float(source_q),
        "analytic_qeff_lower_fraction":{
            "numerator":str(lo.numerator),"denominator":str(lo.denominator),
        },
        "analytic_qeff_upper_fraction":{
            "numerator":str(hi.numerator),"denominator":str(hi.denominator),
        },
        "source_qeff_in_exact_analytic_box":lo<=v<=hi,
        "absolute_discrepancy_upper":_round_upper(deviation),
        "relative_to_true_qeff_lower_upper":_round_upper(deviation/lo),
        "source_numeric_qeff_other_radii_certified":False,
        "full_model_root_error_certified":False,
    }
