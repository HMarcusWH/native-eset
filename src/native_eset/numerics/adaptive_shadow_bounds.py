"""D2e-E: adaptive, outward-certified finite shadow projection at fixed apertures.

EXACT binary64 nodal radial coordinates, densities and aperture; piecewise-
linear nonnegative rho. A convex geometric kernel gives lower tangent and
upper secant bounds on each outer shell, refined by certified subdivision.

The precision target is an algorithmic accuracy goal for THIS DISCRETE
integral, not an assumption about upstream matter fields, q_eff, global
root topology, missing radial mass, physical Weyl lensing or observations.
"""
from __future__ import annotations

import heapq
from decimal import Context, Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction

from native_eset.numerics.exact_shadow_bounds import (
    ShadowEnclosureError,
    _fraction,
    _inside_primitive,
    _pi_fraction_bounds,
    _sqrt_rational_bounds,
)

TARGET_RELATIVE_WIDTH = "0.00000001"
MAX_REFINEMENT_SPLITS = 16384
CHECK_EVERY_SPLITS = 256
DECIMAL_PRECISION = 70
SQRT_INTEGER_BITS = 88


def _g_bounds(r: Fraction, aperture: Fraction, bits: int) -> tuple[Fraction, Fraction]:
    """g(r,A) = A^2*r/(r+sqrt(r^2-A^2)), with exact rational bounds."""
    if not 0 <= aperture <= r:
        raise ShadowEnclosureError("outer kernel radius below aperture")
    if aperture == 0:
        return Fraction(0), Fraction(0)
    if r == aperture:
        return aperture*aperture, aperture*aperture
    root_lo, root_hi = _sqrt_rational_bounds(r*r - aperture*aperture, bits)
    numerator = aperture*aperture*r
    return numerator/(r+root_hi), numerator/(r+root_lo)


def _g_derivative_bounds(r: Fraction, aperture: Fraction, bits: int):
    """Rigorous bounds for g'(r,A) at r>A, using exact rational sqrt."""
    if not 0 < aperture < r:
        raise ShadowEnclosureError("kernel derivative requires strict outer radius")
    root_lo, root_hi = _sqrt_rational_bounds(r*r-aperture*aperture, bits)
    if root_lo <= 0:
        raise ShadowEnclosureError("sqrt bound under-resolved at midpoint")
    numerator = 2*r*r - aperture*aperture
    return 2*r-numerator/root_lo, 2*r-numerator/root_hi


def _product_of_linears(ya, yb, ga, gb, width):
    """Integrate exact product of two affine functions on a segment."""
    dy, dg = yb-ya, gb-ga
    return width*(ya*ga + (ya*dg+dy*ga)/2 + dy*dg/3)


def _convex_outer_cell(a, b, ya, yb, aperture, bits):
    """Lower tangent and upper chord enclosure for a single outer shell.

    For r>A: g''(r) = 2-(2-3t)/(1-t)^(3/2), t=A^2/r^2.
    If t>=2/3 this is positive; otherwise compare h(t)=
    2*(1-t)^(3/2)-(2-3t), with h(0)=0 and h'(t)=
    3*(1-sqrt(1-t))>0. Thus g is strictly convex for A>0.

    The true function lies below the secant joining true endpoints,
    and above its tangent at the midpoint. Use interval-bounded
    endpoint heights and midpoint derivative, with correct derivative
    sign choice on each side, to obtain exact rational shell bounds.
    """
    if not (0 < aperture <= a < b and 0 <= ya and 0 <= yb):
        raise ShadowEnclosureError("invalid positive-density convex shell")
    mid = (a+b)/2
    ym = ya+(yb-ya)*(mid-a)/(b-a)
    _, upper_a = _g_bounds(a, aperture, bits)
    _, upper_b = _g_bounds(b, aperture, bits)
    upper = _product_of_linears(ya, yb, upper_a, upper_b, b-a)
    mid_lower, _ = _g_bounds(mid, aperture, bits)
    derivative_lower, derivative_upper = _g_derivative_bounds(mid, aperture, bits)
    # For r<=mid, (r-mid)<0, so derivative_upper is the LOWER tangent;
    # for r>=mid, derivative_lower is the LOWER tangent.
    left = _product_of_linears(
        ya, ym, mid_lower+derivative_upper*(a-mid), mid_lower, mid-a,
    )
    right = _product_of_linears(
        ym, yb, mid_lower, mid_lower+derivative_lower*(b-mid), b-mid,
    )
    lower = max(Fraction(0), left+right)
    if lower < 0 or upper < lower:
        raise ShadowEnclosureError("invalid convex shell enclosure")
    return lower, upper


def _as_decimal(value: Fraction, context: Context) -> Decimal:
    return context.divide(Decimal(value.numerator), Decimal(value.denominator))


def _enclosure(active, exact_inner, precision):
    """Compute outward global sums anew; never update sums by unsound subtraction."""
    lc = Context(prec=precision, rounding=ROUND_FLOOR)
    uc = Context(prec=precision, rounding=ROUND_CEILING)
    lower = Decimal(0)
    upper = Decimal(0)
    for part in exact_inner:
        lower = lc.add(lower, _as_decimal(part, lc))
        upper = uc.add(upper, _as_decimal(part, uc))
    for cell in active.values():
        # Each cell = (left, right, rho_left, rho_right, lower, upper).
        lower = lc.add(lower, _as_decimal(cell[4], lc))
        upper = uc.add(upper, _as_decimal(cell[5], uc))
    pi_lo, pi_hi = _pi_fraction_bounds()
    lower = lc.multiply(lc.multiply(lower, Decimal(4)), _as_decimal(pi_lo, lc))
    upper = uc.multiply(uc.multiply(upper, Decimal(4)), _as_decimal(pi_hi, uc))
    if lower < 0 or upper < lower:
        raise ShadowEnclosureError("inverted final directed mass enclosure")
    width = uc.subtract(upper, lower)
    relative = uc.divide(width, lower) if lower > 0 else None
    return lower, upper, relative


def enclose_adaptive_convex_shadow(
    radial_kpc, density_msun_per_kpc3, aperture_kpc,
    *, target_relative_width: str = TARGET_RELATIVE_WIDTH,
    max_refinement_splits: int = MAX_REFINEMENT_SPLITS,
    decimal_precision: int = DECIMAL_PRECISION,
    sqrt_bits: int = SQRT_INTEGER_BITS,
) -> dict:
    """Adaptively tighten mathematical enclosure, fail open in status, not science.

    Target and split budget are explicit parts of the numerical execution
    identity. For incomplete convergence return a VALID enclosure plus
    TARGET_NOT_MET; do not fabricate precision or discard pending intervals.
    All input nodes and apertures retain exact binary64 semantics.
    """
    if len(radial_kpc) != len(density_msun_per_kpc3) or not 2 <= len(radial_kpc) <= 25000:
        raise ShadowEnclosureError("invalid source-node inventory")
    if type(max_refinement_splits) is not int or not 0 <= max_refinement_splits <= 50000:
        raise ShadowEnclosureError("unregistered refinement budget")
    if type(decimal_precision) is not int or not 48 <= decimal_precision <= 120:
        raise ShadowEnclosureError("unregistered directed rounding precision")
    if type(sqrt_bits) is not int or not 40 <= sqrt_bits <= 160:
        raise ShadowEnclosureError("unregistered integer sqrt bits")
    if not isinstance(target_relative_width, str):
        raise ShadowEnclosureError("relative target must be immutable decimal string")
    try:
        target = Decimal(target_relative_width)
    except InvalidOperation as exc:
        raise ShadowEnclosureError("invalid relative target") from exc
    if not (target.is_finite() and Decimal("1e-12") <= target <= Decimal("1e-3")):
        raise ShadowEnclosureError("relative target outside allowed numerical scope")

    radial = [_fraction(x) for x in radial_kpc]
    density = [_fraction(x) for x in density_msun_per_kpc3]
    aperture = _fraction(aperture_kpc)
    if radial[0] <= 0 or aperture > radial[-1]:
        raise ShadowEnclosureError("aperture outside the source finite radial domain")
    if any(b <= a for a,b in zip(radial[:-1],radial[1:])):
        raise ShadowEnclosureError("source radius coordinates not strictly increasing")

    exact_inner = []
    active = {}
    queue = []
    fresh_id = 0
    inner_count = outer_count = crossing_count = 0
    for a,b,ya,yb in zip(radial[:-1],radial[1:],density[:-1],density[1:]):
        slope = (yb-ya)/(b-a)
        if b <= aperture:
            exact_inner.append(_inside_primitive(a,b,ya,slope))
            inner_count += 1
            continue
        if a < aperture:
            exact_inner.append(_inside_primitive(a,aperture,ya,slope))
            ya = ya+slope*(aperture-a)
            a = aperture
            crossing_count += 1
        if aperture == 0:
            # The entire finite cylinder mass is 0 at A=0, regardless of rho.
            continue
        lo,hi = _convex_outer_cell(a,b,ya,yb,aperture,sqrt_bits)
        active[fresh_id] = (a,b,ya,yb,lo,hi)
        heapq.heappush(queue,(-float(hi-lo),fresh_id))
        fresh_id += 1
        outer_count += 1

    splits = 0
    lower,upper,relative = _enclosure(active,exact_inner,decimal_precision)
    while relative is not None and relative > target and splits < max_refinement_splits:
        if not queue:
            break
        _, key = heapq.heappop(queue)
        a,b,ya,yb,old_lo,old_hi = active.pop(key)
        mid = (a+b)/2
        ym = ya+(yb-ya)*(mid-a)/(b-a)
        if not a < mid < b:
            # Cannot refine exact rational source interval: restore it.
            active[key] = (a,b,ya,yb,old_lo,old_hi)
            break
        for left,right,vl,vr in ((a,mid,ya,ym),(mid,b,ym,yb)):
            lo,hi = _convex_outer_cell(left,right,vl,vr,aperture,sqrt_bits)
            active[fresh_id] = (left,right,vl,vr,lo,hi)
            heapq.heappush(queue,(-float(hi-lo),fresh_id))
            fresh_id += 1
        splits += 1
        if splits % CHECK_EVERY_SPLITS == 0 or splits == max_refinement_splits:
            lower,upper,relative = _enclosure(active,exact_inner,decimal_precision)

    # Each exact shell bound is independent of a success verdict.
    lower,upper,relative = _enclosure(active,exact_inner,decimal_precision)
    return {
        "lower_msun":format(lower,"f"),
        "upper_msun":format(upper,"f"),
        "relative_interval_width_upper":format(relative,"f") if relative is not None else None,
        "target_relative_width":target_relative_width,
        "target_met":bool(relative is not None and relative <= target),
        "status":"TARGET_CERTIFIED_FOR_FROZEN_DISCRETE_SHADOW" if relative is not None and relative <= target
                 else "VALID_ENCLOSURE_BUT_TARGET_NOT_MET",
        "refinement_splits":splits,
        "refinement_limit":max_refinement_splits,
        "original_input_radius_nodes":len(radial),
        "source_inside_cells":inner_count,
        "source_outer_cells":outer_count,
        "source_crossing_cells":crossing_count,
        "resulting_outer_cells":len(active),
        "decimal_precision_digits":decimal_precision,
        "integer_isqrt_bits":sqrt_bits,
        "input_semantics":"EXACT_BINARY64_NODAL_AND_APERTURE_VALUES",
        "proof_scope":"CERTIFIED_FINITE_PIECEWISE_LINEAR_SHADOW_AT_ONE_FIXED_APERTURE",
        "physical_source_uncertainties_bounded":False,
        "global_root_topology_certified":False,
    }
