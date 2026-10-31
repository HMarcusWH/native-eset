"""G4b.1b: rigorous one-cell H inclusion for EXPLICIT supplied mathematical inputs.

This helper computes mathematical continuum B,D and a finite nodal interpolant
shadow integral using exact binary64 input scalars. It does NOT authenticate
that the supplied scalars/nodes came from the original March 46+3 source, does
not prove any original floating 180/120 numerical output error, and does not
certify root uniqueness, missing physical mass, Weyl lensing or empirical data.

For ONE real radial cell [l,h], the exact supplied-input function is:
    H(R) = B(R) + D(R) + S(min(120,R/sqrt(q(R))))
           - pi_real * Sigma_crit_math * R**2.
The certified component bounds include every real R in the cell. A strict
sign can exclude a root in this MATHEMATICAL SUPPLIED-INPUT MODEL ONLY.
"""
from __future__ import annotations

import hashlib
import math
import struct
from decimal import Decimal
from fractions import Fraction

from native_eset.numerics.hist001d_g4b_root_intervals import (
    Leaf, conditional_H_box, leaf_from_path,
)
from native_eset.numerics.hist001d_g4b1a_cell_baryon_boxes import (
    certified_analytic_baryon_cell,
)
from native_eset.numerics.certified_flatlcdm_sigma import (
    certified_sigma_critical,
)
from native_eset.numerics.exact_shadow_bounds import (
    enclose_finite_cylinder_mass,
)
from native_eset.numerics.hist001d_g4b1_boundary_bridge import (
    SOURCE_RMIN, SOURCE_RMAX,
)

SCHEMA = "HIST001D_D2E_G4B1B_SUPPLIED_INPUT_FINITE_H_CELL_BOX_V1"
NODE_DIGEST_DOMAIN = b"native-eset-g4b1b-exact-binary64-nodal-pairs-v1\x00"
MAX_NODES = 25000

BARYON_KEYS = frozenset({
    "bulge_mass_msun", "hernquist_a_kpc", "disc_mass_msun",
    "disc_scale_kpc", "bulge_q", "disc_q",
})
# Freeze original March cosmology constants as STORED source binary64 scalars.
# Neither these numbers nor source-input provenance constitute physical errors.
FROZEN_LCDM = {
    "omega_m": 0.3,
    "omega_de": 1.0 - 0.3,
    "H0": 70.0,
    "C_KMS": 299792.458,
    "G_KPC_KMS2_MSUN": 4.30091e-6,
    "FOUR_PI": 4.0 * math.pi,
    "MPC_IN_KPC": 1000.0,
}
ORIGINAL_MARCH_SOURCE_LOCK_SHA256 = (
    "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
)


class G4b1bError(ValueError):
    """Refuse malformed scalars, nodal arrays, digests or numerical boxes."""


def _pair(value: Fraction) -> dict[str, str]:
    return {"num": str(value.numerator), "den": str(value.denominator)}


def _from_pair(value: dict) -> Fraction:
    if type(value) is not dict or set(value) != {"num", "den"}:
        raise G4b1bError("invalid exact-rational box endpoint representation")
    n, d = value["num"], value["den"]
    if type(n) is not str or type(d) is not str:
        raise G4b1bError("noncanonical rational box fields")
    if not n.lstrip("-").isdigit() or not d.isdigit() or len(n) > 1500 or len(d) > 1500:
        raise G4b1bError("noncanonical or excessive rational endpoint")
    den = int(d)
    if den <= 0:
        raise G4b1bError("invalid rational denominator")
    return Fraction(int(n), den)


def frozen_nodal_digest(radial_kpc, density_msun_per_kpc3) -> str:
    """Byte-lock supplied float64 nodes; NOT independent original-source auth."""
    if (type(radial_kpc) not in (list, tuple)
            or type(density_msun_per_kpc3) not in (list, tuple)
            or not 2 <= len(radial_kpc) <= MAX_NODES
            or len(radial_kpc) != len(density_msun_per_kpc3)):
        raise G4b1bError("invalid explicit finite-nodal input inventory")
    if (type(radial_kpc[0]) is not float or type(radial_kpc[-1]) is not float
            or not math.isfinite(radial_kpc[0]) or not math.isfinite(radial_kpc[-1])
            or Fraction.from_float(radial_kpc[0]) != SOURCE_RMIN
            or Fraction.from_float(radial_kpc[-1]) != SOURCE_RMAX):
        raise G4b1bError("noncanonical original finite radial endpoints")
    h = hashlib.sha256()
    h.update(NODE_DIGEST_DOMAIN)
    h.update(struct.pack(">I", len(radial_kpc)))
    prev = 0.0
    for r, rho in zip(radial_kpc, density_msun_per_kpc3):
        if (type(r) is not float or type(rho) is not float
                or not math.isfinite(r) or not math.isfinite(rho)
                or r <= prev or rho < 0 or r <= 0):
            raise G4b1bError("unsafe binary64 nodal value, ordering or density")
        h.update(struct.pack(">dd", r, rho))
        prev = r
    return h.hexdigest()


def certified_supplied_finite_model_H_cell(
    cell: Leaf, *, baryon_scalars: dict,
    z_lens: float, z_source: float,
    radial_kpc: tuple[float, ...] | list[float],
    density_msun_per_kpc3: tuple[float, ...] | list[float],
    expected_nodal_sha256: str,
    g1_max_splits: int = 0,
) -> dict:
    """Certified mathematical H box for all R in ONE cell, supplied inputs.

    Nodal SHA checks bytes against an EXPECTATION supplied by the caller;
    it does NOT attest original source authorship or six-lens provenance.
    G1/G2 analytic B,D, G4a mathematical Sigma, and D2e-D finite cylinder
    mass are each independently proven under the explicitly supplied scalar
    and nonnegative nodal-interpolant assumptions.
    """
    if type(cell) is not Leaf or cell != leaf_from_path(cell.path):
        raise G4b1bError("noncanonical exact G4b0 source-radius cell")
    if type(baryon_scalars) is not dict or set(baryon_scalars) != BARYON_KEYS:
        raise G4b1bError("missing or added frozen baryonic scalar field")
    if type(z_lens) is not float or type(z_source) is not float:
        raise G4b1bError("redshifts must be explicit original-style binary64 floats")
    if type(expected_nodal_sha256) is not str or len(expected_nodal_sha256) != 64:
        raise G4b1bError("invalid external nodal digest declaration")
    if any(c not in "0123456789abcdef" for c in expected_nodal_sha256):
        raise G4b1bError("malformed hexadecimal nodal digest")
    computed = frozen_nodal_digest(radial_kpc, density_msun_per_kpc3)
    if computed != expected_nodal_sha256:
        raise G4b1bError("nodal values do not match externally supplied digest")
    try:
        baryon = certified_analytic_baryon_cell(
            cell, **baryon_scalars, g1_max_splits=g1_max_splits,
        )
        sigma = certified_sigma_critical(
            z_lens, z_source, **FROZEN_LCDM,
        )
        aperture_lo = baryon["outward_binary64_shadow_aperture_lower"]
        aperture_hi = baryon["outward_binary64_shadow_aperture_upper"]
        lower_shadow = enclose_finite_cylinder_mass(
            radial_kpc, density_msun_per_kpc3, aperture_lo,
        )
        upper_shadow = (lower_shadow if aperture_lo == aperture_hi
                        else enclose_finite_cylinder_mass(
                            radial_kpc, density_msun_per_kpc3, aperture_hi,
                        ))
        blo = _from_pair(baryon["finite_continuum_bulge_mass_exact_lower"])
        bhi = _from_pair(baryon["finite_continuum_bulge_mass_exact_upper"])
        dlo = _from_pair(baryon["continuum_elliptical_disk_mass_exact_lower"])
        dhi = _from_pair(baryon["continuum_elliptical_disk_mass_exact_upper"])
        slo = Fraction(Decimal(lower_shadow["lower_msun"]))
        shi = Fraction(Decimal(upper_shadow["upper_msun"]))
        sigma_lo = Fraction(Decimal(sigma["lower_msun_per_kpc2"]))
        sigma_hi = Fraction(Decimal(sigma["upper_msun_per_kpc2"]))
        if not (0 < blo <= bhi and 0 < dlo <= dhi
                and 0 <= slo <= shi and 0 < sigma_lo <= sigma_hi):
            raise G4b1bError("independent component enclosures inconsistent")
        hbox = conditional_H_box(
            cell, (blo, bhi), (dlo, dhi), (slo, shi),
            (sigma_lo, sigma_hi),
        )
    except (ValueError, ArithmeticError, OverflowError) as exc:
        raise G4b1bError("independent mathematical component enclosure failed") from exc
    if (baryon.get("all_real_radii_in_source_cell_analytic_baryon_masses_enclosed")
            is not True or sigma.get("schema") is None
            or hbox.get("valid_for_every_real_R_in_cell_IF_INPUT_ENCLOSURES_SOUND") is not True):
        raise G4b1bError("component proof-scope declaration absent")

    # A strict bound excludes mathematical zeros for the explicitly supplied
    # finite interpolant and frozen scalars, NOT for unauthenticated historical
    # source reexecution or a physical lens.
    excluded_for_supplied_math = hbox["conditional_sign"].startswith("STRICT_")
    return {
        "schema": SCHEMA,
        "status": "SUPPLIED_BINARY64_FINITE_MODEL_MATH_CELL_ONLY",
        "original_March_source_lock_declaration": ORIGINAL_MARCH_SOURCE_LOCK_SHA256,
        "exact_cell_path": cell.path,
        "baryonic_supplied_binary64_scalars": dict(baryon_scalars),
        "supplied_lens_redshifts_binary64": [z_lens, z_source],
        "cosmology_stored_binary64_constants": dict(FROZEN_LCDM),
        "nodal_count": len(radial_kpc),
        "supplied_nodal_sha256": computed,
        "caller_supplied_expected_nodal_digest_matches": True,
        "supplied_nodes_have_original_historical_source_provenance": False,
        "source_nodal_11520_inventory_length_only": len(radial_kpc) == 11520,
        "mathematical_baryon_cell_certificate": baryon,
        "mathematical_FlatLCDM_sigma_certificate": sigma,
        "mathematical_finite_shadow_mass_band": {
            "lower_msun_exact": _pair(slo),
            "upper_msun_exact": _pair(shi),
            "lower_endpoint_certificate": lower_shadow,
            "upper_endpoint_certificate": upper_shadow,
            "monotonic_nonnegative_finite_piecewise_linear_density": True,
            "all_real_apertures_in_cell_enclosed": True,
        },
        "mathematical_residual_interval": hbox,
        "supplied_math_model_cell_excludes_zero": excluded_for_supplied_math,
        "original_March_or_D2d_actual_lens_H_source_matched": False,
        "all_original_March_180x120_numeric_radius_errors_bounded": False,
        "original_source_nodal_density_continuum_certified": False,
        "root_existence_or_uniqueness_certified": False,
        "full_radial_domain_root_exclusion_certified": False,
        "physical_mass_outside_finite_domain_certified": False,
        "physical_weyl_metric_derived": False,
        "physical_provider_admitted": False,
        "empirical_validation": "NOT_ESTABLISHED",
    }
