"""G4a DRAFT: mathematical FlatLCDM sigma_crit bounds for frozen binary64 inputs.

NOT a physical lensing provider, an observational/cosmological parameter error
bound, a floating SciPy implementation theorem at unregistered redshifts, or a
full Einstein-root topology certificate.

Mathematical identity (all scalars interpreted as EXACT binary64):
 Sigma = C H0 (1+z_l)/(FOUR_PI G MPC_IN_KPC) * (1/I_l + 1/I_ls)
where I_l = integral_0^zl 1/sqrt(Om(1+z)^3+Ode) dz and
I_ls = integral_zl^zs of the same function.

The composite trapezoid enclosure uses integer-isqrt rational endpoint bounds
plus a rigorous global |f''| bound, not SciPy tolerance assumptions.
"""
from __future__ import annotations

import math
from decimal import Context, Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction
from math import isqrt

SCHEMA = "NATIVE_ESET_HIST001D_G4A_FROZEN_LCDM_MATH_SIGMA_ENCLOSURE_DRAFT_V1"
TARGET_RELATIVE_WIDTH = "0.0001"  # engineering mesh screen, not observation likelihood
GRID_CELLS = 256  # frozen trial budget; failure reports target_met=False
SQRT_BITS = 100
PRECISION = 70


class G4aEnclosureError(ValueError):
    """Wrong frozen constants, input domain, or unsafe numerical enclosure."""


def _dyadic(value: float) -> Fraction:
    if type(value) not in (float, int):
        raise G4aEnclosureError("input must be exact finite source binary64")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise G4aEnclosureError("unrepresentable source numerical input") from exc
    if not math.isfinite(result):
        raise G4aEnclosureError("nonfinite source input")
    return Fraction.from_float(result)


def _sqrt_bounds(x: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    if x <= 0 or type(bits) is not int or not 64 <= bits <= 160:
        raise G4aEnclosureError("bad sqrt interval")
    scaled = (x.numerator << (2 * bits)) // x.denominator
    k = isqrt(scaled)
    if not k:
        raise G4aEnclosureError("insufficient sqrt interval precision")
    s = 1 << bits
    return Fraction(k, s), Fraction(k + 1, s)


def _decimal_fraction(frac: Fraction, context: Context) -> Decimal:
    return context.divide(Decimal(frac.numerator), Decimal(frac.denominator))


def certified_distance_integral(
    left_z: float,
    right_z: float,
    omega_m: float,
    omega_de: float,
    *,
    cells: int = GRID_CELLS,
    sqrt_bits: int = SQRT_BITS,
    precision: int = PRECISION,
) -> dict:
    """Proved enclosure of positive decreasing f(z) on one source-redshift band.

    For f(z)=D(z)^(-1/2), D=Om(1+z)^3+Ode:
      |f''| <= 3(D'_max)^2/(4 Dmin^2 sqrt(Dmin))
              + D''_max/(2 Dmin sqrt(Dmin)).
    Composite trapezoid absolute remainder <= (b-a)^3*K/(12*N^2).
    """
    if (type(cells) is not int or not 8 <= cells <= 32768
            or type(sqrt_bits) is not int or not 64 <= sqrt_bits <= 160
            or type(precision) is not int or not 48 <= precision <= 120):
        raise G4aEnclosureError("unregistered proof resource budget")
    a, b, om, ode = map(_dyadic, (left_z, right_z, omega_m, omega_de))
    if not (0 <= a < b <= 10 and 0 < om < 1 and 0 < ode < 1):
        raise G4aEnclosureError("unregistered cosmology/redshift domain")
    h = (b - a) / cells
    dl = om * (1 + a)**3 + ode
    if dl <= 0:
        raise G4aEnclosureError("nonpositive E²")
    sqrt_l, _ = _sqrt_bounds(dl, sqrt_bits)
    dpmax = 3 * om * (1 + b)**2
    dppmax = 6 * om * (1 + b)
    curvature = (
        3 * dpmax**2 / (4 * dl**2 * sqrt_l)
        + dppmax / (2 * dl * sqrt_l)
    )
    remainder = (b-a)**3 * curvature / (12 * cells * cells)
    floor = Context(prec=precision, rounding=ROUND_FLOOR)
    ceil = Context(prec=precision, rounding=ROUND_CEILING)
    lower, upper = Decimal(0), Decimal(0)
    for i in range(cells + 1):
        z = a + h * i
        denominator = om * (1 + z)**3 + ode
        rootlo, roothi = _sqrt_bounds(denominator, sqrt_bits)
        flo, fhi = 1 / roothi, 1 / rootlo
        weight = Fraction(1, 2) if i in (0, cells) else Fraction(1)
        lower = floor.add(lower, _decimal_fraction(weight * flo, floor))
        upper = ceil.add(upper, _decimal_fraction(weight * fhi, ceil))
    hfloor = _decimal_fraction(h, floor)
    hceil = _decimal_fraction(h, ceil)
    tlo = floor.multiply(lower, hfloor)
    thi = ceil.multiply(upper, hceil)
    rem_hi = _decimal_fraction(remainder, ceil)
    low = floor.subtract(tlo, rem_hi)
    high = ceil.add(thi, rem_hi)
    if not (Decimal(0) < low <= high):
        raise G4aEnclosureError("integral trapezoid proof interval inverted")
    return {
        "schema": SCHEMA,
        "lower": format(low, "f"),
        "upper": format(high, "f"),
        "cells": cells,
        "precision_digits": precision,
        "sqrt_bits": sqrt_bits,
        "trapezoid_remainder_upper": format(rem_hi, "f"),
        "scope": "FROZEN_BINARY64_SCALAR_LCDM_MATHEMATICAL_COMOVING_INTEGRAL",
    }


def certified_sigma_critical(
    z_lens: float, z_source: float,
    *,
    omega_m: float = 0.3,
    omega_de: float = 1.0 - 0.3,
    H0: float = 70.0,
    C_KMS: float = 299792.458,
    G_KPC_KMS2_MSUN: float = 4.30091e-6,
    FOUR_PI: float = 4.0 * math.pi,
    MPC_IN_KPC: float = 1000.0,
    cells: int = GRID_CELLS,
    target_relative_width: str = TARGET_RELATIVE_WIDTH,
) -> dict:
    """Mathematical source-scalar interval, not a physical Sigma_crit error bar."""
    zl, zs = _dyadic(z_lens), _dyadic(z_source)
    om, ode = _dyadic(omega_m), _dyadic(omega_de)
    h0, c, g, four_pi, mpc = map(_dyadic, (
        H0, C_KMS, G_KPC_KMS2_MSUN, FOUR_PI, MPC_IN_KPC,
    ))
    if not (0 < zl < zs <= 10 and h0 > 0 and c > 0 and g > 0
            and four_pi > 0 and mpc > 0 and 0 < om < 1 and 0 < ode < 1):
        raise G4aEnclosureError("source sigma critical scalars unphysical")
    try:
        target = Decimal(target_relative_width)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise G4aEnclosureError("invalid precision target") from exc
    if (not target.is_finite() or target <= 0 or target > Decimal("0.01")
            or not isinstance(target_relative_width, str)):
        raise G4aEnclosureError("unregistered precision target")
    il = certified_distance_integral(0.0, z_lens, omega_m, omega_de, cells=cells)
    ils = certified_distance_integral(z_lens, z_source, omega_m, omega_de, cells=cells)
    il_lo, il_hi = Fraction(Decimal(il["lower"])), Fraction(Decimal(il["upper"]))
    ls_lo, ls_hi = Fraction(Decimal(ils["lower"])), Fraction(Decimal(ils["upper"]))
    if not (0 < il_lo <= il_hi and 0 < ls_lo <= ls_hi):
        raise G4aEnclosureError("nonpositive source-distance interval")
    factor = c*h0*(1+zl)/(four_pi*g*mpc)
    exact_low = factor*(1/il_hi + 1/ls_hi)
    exact_high = factor*(1/il_lo + 1/ls_lo)
    floor = Context(prec=PRECISION, rounding=ROUND_FLOOR)
    ceil = Context(prec=PRECISION, rounding=ROUND_CEILING)
    low = _decimal_fraction(exact_low, floor)
    high = _decimal_fraction(exact_high, ceil)
    if not 0 < low <= high:
        raise G4aEnclosureError("source sigma bracket inverted")
    width = ceil.divide(ceil.subtract(high, low), low)
    return {
        "schema": SCHEMA,
        "lower_msun_per_kpc2": format(low, "f"),
        "upper_msun_per_kpc2": format(high, "f"),
        "relative_interval_width_upper": format(width, "f"),
        "target_relative_width": target_relative_width,
        "target_met": bool(width <= target),
        "I_l": il,
        "I_ls": ils,
        "supplied_parameters_treated_as_exact_binary64": True,
        "frozen_source_bytes_verified": False,
        "all_redshift_source_numerical_error_bounded": False,
        "physical_sigma_critical_error_bounded": False,
        "root_uniqueness_certified": False,
        "physical_weyl_lensing_derived": False,
        "empirical_validation": "NOT_ESTABLISHED",
    }


def a_posteriori_source_output_discrepancy(value: float, certificate: dict) -> dict:
    """At one returned binary64 output only, exact dyadic/endpoint inequality."""
    v = _dyadic(value)
    lower = Fraction(Decimal(certificate["lower_msun_per_kpc2"]))
    upper = Fraction(Decimal(certificate["upper_msun_per_kpc2"]))
    if not 0 < v or not 0 < lower <= upper:
        raise G4aEnclosureError("invalid returned source critical density")
    exact = max(abs(v-lower), abs(v-upper))
    ceil = Context(prec=PRECISION, rounding=ROUND_CEILING)
    return {
        "source_returned_binary64": float(value),
        "source_returned_exact_dyadic_numerator": str(v.numerator),
        "source_returned_exact_dyadic_denominator": str(v.denominator),
        "absolute_discrepancy_upper": format(_decimal_fraction(exact, ceil), "f"),
        "source_returned_inside_target_enclosure": bool(lower <= v <= upper),
        "applies_only_to_this_supplied_binary64_value": True,
        "source_output_provenance_verified": False,
        "physical_lensing_error_bounded": False,
        "source_numeric_error_all_redshifts_bounded": False,
    }
