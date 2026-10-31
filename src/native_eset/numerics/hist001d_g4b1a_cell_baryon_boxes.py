"""G4b.1a: sound per-real-cell analytic CONTINUUM baryonic boxes.

This is a purely mathematical adapter for exact-dyadic G4b.0 cells.  It does
not enclose numerical output errors of original March 180/120 quadratures,
read the 11,520-node D2d shadow array, evaluate a lens residual or prove a root.

Mass monotonicity and the earlier G1/G2 positive continuum theorems are the
only scientific premises used.  The RMIN bulge lower bound is the separate
strictly positive finite Hernquist lemma from G4b.1.
"""
from __future__ import annotations

import math
from fractions import Fraction

from native_eset.numerics.hist001d_g4b_root_intervals import Leaf, leaf_from_path
from native_eset.numerics.hist001d_g4b1_boundary_bridge import (
    G4b1BridgeError,
    SOURCE_RMIN,
    exact_number,
    outward_radius_for_legacy_points,
    positive_baryon_q_box,
    proven_positive_hernquist_mass_at_left_source_boundary,
    source_aperture_outward_band,
)

SCHEMA = "HIST001D_D2E_G4B1A_CONTINUUM_BARYON_CELL_INTERVAL_V1"
G1_TARGET = "0.000001"
MAX_G1_SPLITS = 8192


class G4b1aError(ValueError):
    """Invalid mathematical cell, source scalar or mismatched interval."""


def _rational_pair(value: Fraction) -> dict[str, str]:
    return {"num": str(value.numerator), "den": str(value.denominator)}


def _source_binary64_scalar(x: object, name: str, *, at_most_one: bool = False) -> float:
    if type(x) is not float or not math.isfinite(x) or x <= 0 or (at_most_one and x > 1):
        raise G4b1aError(f"invalid frozen binary64 source scalar: {name}")
    return x


def certified_analytic_baryon_cell(
    cell: Leaf,
    *,
    bulge_mass_msun: float,
    hernquist_a_kpc: float,
    disc_mass_msun: float,
    disc_scale_kpc: float,
    bulge_q: float,
    disc_q: float,
    g1_max_splits: int = 0,
) -> dict:
    """Prove mathematical B,D intervals for ALL REAL R in one G4b.0 cell.

    Output mathematical mass intervals use exact numerators/denominators.
    Source floats are exact frozen binary64 inputs. Source original 180/120
    numerical expressions are NOT covered, and the result is NOT a root proof.

    The conservative G2 angular-free disk bound is used; this may be very
    wide and leave later signed root intervals unresolved. It is sound even
    if the engineering accuracy goal of G1 is not met.
    """
    if type(cell) is not Leaf or cell != leaf_from_path(cell.path):
        raise G4b1aError("noncanonical G4b0 source-radius leaf")
    if type(g1_max_splits) is not int or not 0 <= g1_max_splits <= MAX_G1_SPLITS:
        raise G4b1aError("unregistered Hernquist proof split budget")
    for name, value in (
        ("bulge_mass", bulge_mass_msun), ("hernquist_a", hernquist_a_kpc),
        ("disc_mass", disc_mass_msun), ("disc_scale", disc_scale_kpc),
    ):
        _source_binary64_scalar(value, name)
    _source_binary64_scalar(bulge_q, "bulge_q", at_most_one=True)
    _source_binary64_scalar(disc_q, "disc_q", at_most_one=True)

    # Exact rational source cover -> outward binary64 endpoints; the legacy
    # frozen-param kernels accept only binary64 endpoint scalar inputs.
    try:
        low_float, high_float = outward_radius_for_legacy_points(cell.left, cell.right)
    except G4b1BridgeError as exc:
        raise G4b1aError("exact source cell cannot be mapped outward") from exc
    from native_eset.numerics.certified_baryon_mass import (
        certified_elliptical_disk_radius_band,
        certified_hernquist_point,
    )

    if cell.left == SOURCE_RMIN:
        # The old G1 mathematical point proof excludes R == RMIN. Projected
        # cylinder mass is strictly positive there, not zero: use a proved
        # lower bound rather than falsely dropping the first source cell.
        try:
            bulge_lo = proven_positive_hernquist_mass_at_left_source_boundary(
                bulge_mass_msun, hernquist_a_kpc,
            )
        except G4b1BridgeError as exc:
            raise G4b1aError("failed exact left Hernquist boundary lemma") from exc
        bulge_lower_method = "STRICT_POSITIVE_RMIN_SHELL_LEMMA"
        low_point = None
    else:
        low_point = certified_hernquist_point(
            low_float, bulge_mass_msun, hernquist_a_kpc,
            target_width=G1_TARGET, max_splits=g1_max_splits,
        )
        bulge_lo = exact_number(low_point["lower_msun"])
        bulge_lower_method = "G1_CERTIFIED_MONOTONE_POINT_LOWER"
    high_point = certified_hernquist_point(
        high_float, bulge_mass_msun, hernquist_a_kpc,
        target_width=G1_TARGET, max_splits=g1_max_splits,
    )
    bulge_hi = exact_number(high_point["upper_msun"])

    disk_report = certified_elliptical_disk_radius_band(
        low_float, high_float, disc_mass_msun, disc_scale_kpc, disc_q,
    )
    disk_lo = exact_number(disk_report["lower_msun"])
    disk_hi = exact_number(disk_report["upper_msun"])
    if not (0 < bulge_lo <= bulge_hi and 0 < disk_lo <= disk_hi):
        raise G4b1aError("continuum input mass boxes not strictly positive or ordered")
    try:
        qlo, qhi = positive_baryon_q_box(
            (bulge_lo, bulge_hi), (disk_lo, disk_hi), bulge_q, disc_q,
        )
        a_lo, a_hi = source_aperture_outward_band(
            cell.left, cell.right, qlo, qhi,
        )
    except G4b1BridgeError as exc:
        raise G4b1aError("exact continuum baryon q/aperture bridge unresolved") from exc

    return {
        "schema": SCHEMA,
        "registered_source_cell_path": cell.path,
        "exact_radius_lower": _rational_pair(cell.left),
        "exact_radius_upper": _rational_pair(cell.right),
        "outward_binary64_radius_lower": low_float,
        "outward_binary64_radius_upper": high_float,
        "finite_continuum_bulge_mass_exact_lower": _rational_pair(bulge_lo),
        "finite_continuum_bulge_mass_exact_upper": _rational_pair(bulge_hi),
        "continuum_elliptical_disk_mass_exact_lower": _rational_pair(disk_lo),
        "continuum_elliptical_disk_mass_exact_upper": _rational_pair(disk_hi),
        "exact_analytic_q_lower": _rational_pair(qlo),
        "exact_analytic_q_upper": _rational_pair(qhi),
        "outward_binary64_shadow_aperture_lower": a_lo,
        "outward_binary64_shadow_aperture_upper": a_hi,
        "bulge_lower_method": bulge_lower_method,
        "positive_source_parameter_dyadics": True,
        "all_real_radii_in_source_cell_analytic_baryon_masses_enclosed": True,
        "g1_upper_target_met": bool(high_point["target_met"]),
        "g1_lower_target_met": bool(low_point["target_met"]) if low_point else None,
        "g1_split_budget": g1_max_splits,
        "g2_angular_free_disk_interval_used": True,
        "g2b_full_azimuth_tightening_performed": False,
        "all_real_radii_interval_is_sound_under_G1_G2_mathematical_theorems": True,
        "original_March_180x120_numeric_all_radius_errors_bounded": False,
        "source_nodal_11520_shadow_density_bound_computed": False,
        "critical_sigma_source_result_bound_computed": False,
        "model_H_residual_bound_computed": False,
        "real_root_existence_or_uniqueness_certified": False,
        "physical_weyl_metric_derived": False,
        "physical_provider_admitted": False,
        "empirical_validation": "NOT_ESTABLISHED",
    }
