"""HIST-001D/G4b.0: frozen exact-rational finite-proxy interval partition.

This is a SOURCE-INPUT-ONLY preregistration and a conditional algebraic
residual-box primitive. It does not evaluate historical lens residuals,
isolate any actual root, establish source-numerical all-radius accuracy,
or admit a physical Weyl/Native ESET provider.

Every source radius endpoint is the exact rational value of the binary64
number used by the original March finite grid (0.02 and 120.0 kpc).
Every subtree leaf has an authenticated dyadic path; no arbitrary
post-result rebinning, sampling gaps, or silently discarded cells.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction

SCHEMA = "HIST001D_D2E_G4B0_EXACT_FINITE_ROOT_PARTITION_V1"
SOURCE_LOCK_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
R_MIN = Fraction.from_float(0.02)
R_MAX = Fraction(120)
INITIAL_CELLS = 64
MAX_DYADIC_DEPTH = 8
MAX_LEAVES = INITIAL_CELLS * 2**MAX_DYADIC_DEPTH
_PATH = re.compile(r"([0-9]{2}):([01]{0,8})\Z")


class G4b0Error(ValueError):
    """Incorrect finite-proxy input identity, box or interval cover."""


def _fraction(value: object) -> Fraction:
    """Use exact rationals for floats and decimal strings; never trust bool."""
    if isinstance(value, Fraction):
        result = value
    elif type(value) in (int, float):
        try:
            v = float(value)
        except (OverflowError, ValueError) as exc:
            raise G4b0Error("unsupported numeric input") from exc
        if not math.isfinite(v):
            raise G4b0Error("nonfinite numeric input")
        result = Fraction.from_float(v)
    elif type(value) is str and 0 < len(value) <= 200:
        try:
            dec = Decimal(value)
            if not dec.is_finite() or abs(dec.as_tuple().exponent) > 150:
                raise G4b0Error("nonfinite or unbounded decimal input")
            result = Fraction(dec)
        except (InvalidOperation, ValueError, OverflowError) as exc:
            raise G4b0Error("invalid exact decimal") from exc
    else:
        raise G4b0Error("unsupported exact rational input")
    if max(result.numerator.bit_length(), result.denominator.bit_length()) > 2048:
        raise G4b0Error("rational input exceeds resource bound")
    return result


def _pair(value: Fraction) -> dict[str, str]:
    return {"num": str(value.numerator), "den": str(value.denominator)}


@dataclass(frozen=True)
class Leaf:
    """A provenance-authenticated source-domain dyadic cell."""
    path: str
    left: Fraction
    right: Fraction

    def record(self) -> dict:
        return {"path": self.path, "lower": _pair(self.left),
                "upper": _pair(self.right), "depth": len(self.path.split(":")[1])}


def leaf_from_path(path: str) -> Leaf:
    if type(path) is not str or len(path) > 12:
        raise G4b0Error("invalid leaf provenance path")
    m = _PATH.fullmatch(path)
    if m is None:
        raise G4b0Error("malformed leaf provenance path")
    i = int(m.group(1))
    bits = m.group(2)
    if i >= INITIAL_CELLS or len(bits) > MAX_DYADIC_DEPTH:
        raise G4b0Error("source cell index or dyadic depth invalid")
    length = (R_MAX - R_MIN) / INITIAL_CELLS
    lo = R_MIN + i * length
    hi = lo + length
    for bit in bits:
        mid = (lo + hi) / 2
        if bit == "0":
            hi = mid
        else:
            lo = mid
    if not R_MIN <= lo < hi <= R_MAX:
        raise G4b0Error("degenerate or escaped source cell")
    return Leaf(path, lo, hi)


def initial_partition() -> tuple[Leaf, ...]:
    cells = tuple(leaf_from_path(f"{i:02d}:") for i in range(INITIAL_CELLS))
    assert_complete_cover(cells)
    return cells


def split_leaf(cell: Leaf) -> tuple[Leaf, Leaf]:
    if type(cell) is not Leaf or cell != leaf_from_path(cell.path):
        raise G4b0Error("source leaf not authenticated")
    if len(cell.path.split(":")[1]) >= MAX_DYADIC_DEPTH:
        raise G4b0Error("predeclared dyadic depth exceeded")
    low = leaf_from_path(cell.path + "0")
    high = leaf_from_path(cell.path + "1")
    if low.left != cell.left or low.right != high.left or high.right != cell.right:
        raise G4b0Error("dyadic subdivision lost exact coverage")
    return low, high


def assert_complete_cover(cells: tuple[Leaf, ...] | list[Leaf]) -> dict:
    """Full closed domain as adjacent exact rational cells, no dropped region."""
    if (type(cells) not in (tuple, list) or not cells
            or len(cells) > MAX_LEAVES):
        raise G4b0Error("empty or excessive cell cover")
    prev = R_MIN
    depths = []
    paths = set()
    for item in cells:
        if type(item) is not Leaf or item.path in paths:
            raise G4b0Error("duplicate or noncanonical source leaf")
        expected = leaf_from_path(item.path)
        if item != expected or item.left != prev:
            raise G4b0Error("noncanonical cell, overlap, gap or wrong ordering")
        if item.right <= item.left:
            raise G4b0Error("degenerate source cell")
        prev = item.right
        paths.add(item.path)
        depths.append(len(item.path.split(":")[1]))
    if prev != R_MAX:
        raise G4b0Error("source radial domain incompletely covered")
    return {
        "schema": SCHEMA,
        "source_lock_sha256": SOURCE_LOCK_SHA256,
        "source_domain_lower_binary64_exact": _pair(R_MIN),
        "source_domain_upper_binary64_exact": _pair(R_MAX),
        "initial_cells": INITIAL_CELLS,
        "max_depth": MAX_DYADIC_DEPTH,
        "leaves": len(cells),
        "max_used_depth": max(depths),
        "complete_contiguous_real_domain_covered": True,
        "root_existence_or_uniqueness_proved": False,
        "original_source_all_radius_numerical_error_bounded": False,
        "physical_provider_admitted": False,
        "empirical_validation": "NOT_ESTABLISHED",
    }


def _box(pair: tuple[object, object], *, strictly_positive: bool) -> tuple[Fraction, Fraction]:
    if type(pair) not in (tuple, list) or len(pair) != 2:
        raise G4b0Error("expected exact interval pair")
    lo, hi = _fraction(pair[0]), _fraction(pair[1])
    if (lo <= 0 if strictly_positive else lo < 0) or hi < lo:
        raise G4b0Error("negative, inverted or nonpositive interval")
    return lo, hi


def conditional_H_box(
    cell: Leaf, bulge: tuple[object, object], disk: tuple[object, object],
    shadow: tuple[object, object], sigma: tuple[object, object],
) -> dict:
    """Conditional all-R H enclosure GIVEN sound baryon/shadow/sigma boxes.

    H(R)=B(R)+D(R)+S(A(R))-pi*Sigma*R^2.
    This combines supplied boxes only; DOES NOT prove them sound, nor root
    existence or uniqueness. Uses the independently audited rational pi
    enclosure, not the source's binary64 4*pi normalization constant.
    """
    if type(cell) is not Leaf or cell != leaf_from_path(cell.path):
        raise G4b0Error("unauthenticated source-domain cell")
    b0, b1 = _box(bulge, strictly_positive=True)
    d0, d1 = _box(disk, strictly_positive=True)
    s0, s1 = _box(shadow, strictly_positive=False)
    sigma0, sigma1 = _box(sigma, strictly_positive=True)
    from native_eset.numerics.exact_shadow_bounds import _pi_fraction_bounds
    p0, p1 = _pi_fraction_bounds()
    if not Fraction(3) < p0 <= p1 < Fraction(4):
        raise G4b0Error("invalid independently proven pi interval")
    lower = b0 + d0 + s0 - p1 * sigma1 * cell.right**2
    upper = b1 + d1 + s1 - p0 * sigma0 * cell.left**2
    if lower > upper:
        raise G4b0Error("conditional H inclusion interval inverted")
    status = ("STRICT_POSITIVE_EXCLUSION_GIVEN_CERTIFIED_INPUTS" if lower > 0
              else "STRICT_NEGATIVE_EXCLUSION_GIVEN_CERTIFIED_INPUTS" if upper < 0
              else "UNRESOLVED_ZERO_NOT_EXCLUDED")
    return {
        "schema": SCHEMA, "cell_path": cell.path,
        "H_lower_exact_rational": _pair(lower),
        "H_upper_exact_rational": _pair(upper),
        "conditional_sign": status,
        "continuum_mass_shadow_sigma_inputs_certified_by_this_function": False,
        "valid_for_every_real_R_in_cell_IF_INPUT_ENCLOSURES_SOUND": True,
        "no_sampled_sign_or_first_crossing_substitution": True,
        "physical_pi_is_real_not_original_source_binary64_pi": True,
        "source_numeric_root_error_bounded": False,
        "root_existence_or_uniqueness_proved": False,
        "physical_weyl_lensing_derived": False,
        "physical_provider_admitted": False,
    }
