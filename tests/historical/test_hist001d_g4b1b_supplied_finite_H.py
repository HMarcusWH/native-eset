"""G4b.1b real-cell H mathematical inclusion for SUPPLIED (not source-matched) data."""
from __future__ import annotations

from fractions import Fraction

import pytest

from native_eset.numerics.hist001d_g4b_root_intervals import Leaf, R_MIN, R_MAX, leaf_from_path
from native_eset.numerics.hist001d_g4b1b_supplied_finite_H import (
    G4b1bError, BARYON_KEYS, FROZEN_LCDM, ORIGINAL_MARCH_SOURCE_LOCK_SHA256,
    SCHEMA, certified_supplied_finite_model_H_cell, frozen_nodal_digest,
)

BARYONS = {
    "bulge_mass_msun": 1.0e10,
    "hernquist_a_kpc": 1.0,
    "disc_mass_msun": 2.0e10,
    "disc_scale_kpc": 1.5,
    "bulge_q": 0.7,
    "disc_q": 0.8,
}
RADIAL = (0.02, 5.0, 70.0, 120.0)
DENSITY = (1000.0, 700.0, 50.0, 0.0)


def _frac(pair):
    return Fraction(int(pair["num"]), int(pair["den"]))


def _run(path="63:", radial=RADIAL, density=DENSITY, *, expected=None, **extra):
    return certified_supplied_finite_model_H_cell(
        leaf_from_path(path),
        baryon_scalars=BARYONS,
        z_lens=0.1153, z_source=0.871,
        radial_kpc=radial, density_msun_per_kpc3=density,
        expected_nodal_sha256=frozen_nodal_digest(radial, density) if expected is None else expected,
        **extra,
    )


def test_complete_synthetic_finite_model_H_math_box_and_science_firewall():
    result = _run()
    assert result["schema"] == SCHEMA
    assert result["nodal_count"] == 4
    assert result["source_nodal_11520_inventory_length_only"] is False
    assert result["caller_supplied_expected_nodal_digest_matches"] is True
    assert result["supplied_nodes_have_original_historical_source_provenance"] is False
    assert result["mathematical_residual_interval"]["cell_path"] == "63:"
    assert result["mathematical_residual_interval"][
        "valid_for_every_real_R_in_cell_IF_INPUT_ENCLOSURES_SOUND"
    ] is True
    assert result["mathematical_baryon_cell_certificate"][
        "all_real_radii_in_source_cell_analytic_baryon_masses_enclosed"
    ] is True
    assert result["mathematical_FlatLCDM_sigma_certificate"]["target_met"] is True
    assert result["mathematical_finite_shadow_mass_band"][
        "all_real_apertures_in_cell_enclosed"
    ] is True
    assert result["original_March_or_D2d_actual_lens_H_source_matched"] is False
    assert result["all_original_March_180x120_numeric_radius_errors_bounded"] is False
    assert result["root_existence_or_uniqueness_certified"] is False
    assert result["full_radial_domain_root_exclusion_certified"] is False
    assert result["physical_provider_admitted"] is False
    assert result["empirical_validation"] == "NOT_ESTABLISHED"


def test_H_rational_algebra_is_outward_and_uses_real_pi():
    from native_eset.numerics.exact_shadow_bounds import _pi_fraction_bounds

    result = _run()
    baryon = result["mathematical_baryon_cell_certificate"]
    shadow = result["mathematical_finite_shadow_mass_band"]
    sigma = result["mathematical_FlatLCDM_sigma_certificate"]
    box = result["mathematical_residual_interval"]
    cell = leaf_from_path("63:")
    b_lo = _frac(baryon["finite_continuum_bulge_mass_exact_lower"])
    b_hi = _frac(baryon["finite_continuum_bulge_mass_exact_upper"])
    d_lo = _frac(baryon["continuum_elliptical_disk_mass_exact_lower"])
    d_hi = _frac(baryon["continuum_elliptical_disk_mass_exact_upper"])
    s_lo = _frac(shadow["lower_msun_exact"])
    s_hi = _frac(shadow["upper_msun_exact"])
    sig_lo = Fraction(sigma["lower_msun_per_kpc2"])
    sig_hi = Fraction(sigma["upper_msun_per_kpc2"])
    pi_lo, pi_hi = _pi_fraction_bounds()
    assert _frac(box["H_lower_exact_rational"]) == (
        b_lo+d_lo+s_lo-pi_hi*sig_hi*cell.right**2
    )
    assert _frac(box["H_upper_exact_rational"]) == (
        b_hi+d_hi+s_hi-pi_lo*sig_lo*cell.left**2
    )
    assert _frac(box["H_lower_exact_rational"]) <= _frac(box["H_upper_exact_rational"])


def test_exact_zero_nodal_density_stays_zero_shadow_and_does_not_become_physics():
    result = _run(density=(0.0, 0.0, 0.0, 0.0))
    s = result["mathematical_finite_shadow_mass_band"]
    assert _frac(s["lower_msun_exact"]) == _frac(s["upper_msun_exact"]) == 0
    assert result["mathematical_residual_interval"]["conditional_sign"].startswith("STRICT_NEGATIVE")
    assert result["supplied_math_model_cell_excludes_zero"] is True
    assert result["root_existence_or_uniqueness_certified"] is False
    assert result["original_March_or_D2d_actual_lens_H_source_matched"] is False


def test_first_rational_cell_uses_nonzero_Hernquist_boundary_lemma():
    result = _run("00:")
    baryon = result["mathematical_baryon_cell_certificate"]
    assert baryon["bulge_lower_method"] == "STRICT_POSITIVE_RMIN_SHELL_LEMMA"
    assert _frac(baryon["finite_continuum_bulge_mass_exact_lower"]) > 0
    assert result["mathematical_residual_interval"]["cell_path"] == "00:"


@pytest.mark.parametrize("radial,density", [
    ((0.02, 120.0), (1.0,)),
    ((0.02, 120.0), (-1.0, 0.0)),
    ((0.02, 120.0), (float("nan"), 0.0)),
    ((0.02, 40.0, 35.0, 120.0), (1.0, 2.0, 3.0, 4.0)),
    ((0.02, 0.02, 120.0), (1.0, 2.0, 3.0)),
    ((0.03, 120.0), (1.0, 2.0)),
    ((0.02, 119.9), (1.0, 2.0)),
    ((0.02, 120), (1.0, 2.0)),
    ((0.02, 120.0), (True, 0.0)),
])
def test_invalid_nodal_inventory_rejected(radial, density):
    with pytest.raises(G4b1bError):
        frozen_nodal_digest(radial, density)


def test_declared_nodal_digest_detects_single_binary64_change():
    expected = frozen_nodal_digest(RADIAL, DENSITY)
    mutated = list(DENSITY)
    mutated[1] = 700.0000000000001
    assert expected != frozen_nodal_digest(RADIAL, tuple(mutated))
    with pytest.raises(G4b1bError, match="digest"):
        _run(density=tuple(mutated), expected=expected)
    with pytest.raises(G4b1bError, match="digest"):
        _run(expected="f" * 64)


def test_rejects_unsound_scalar_identity_and_parameters():
    assert set(BARYONS) == BARYON_KEYS
    assert FROZEN_LCDM["FOUR_PI"] == 4.0 * __import__("math").pi
    assert FROZEN_LCDM["omega_de"] == 1.0 - FROZEN_LCDM["omega_m"]
    assert ORIGINAL_MARCH_SOURCE_LOCK_SHA256 == (
        "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    )
    with pytest.raises(G4b1bError, match="baryonic scalar field"):
        certified_supplied_finite_model_H_cell(
            leaf_from_path("63:"), baryon_scalars={k: v for k, v in BARYONS.items() if k!="bulge_q"},
            z_lens=0.1153, z_source=0.871, radial_kpc=RADIAL,
            density_msun_per_kpc3=DENSITY, expected_nodal_sha256=frozen_nodal_digest(RADIAL,DENSITY),
        )
    with pytest.raises(G4b1bError, match="redshifts"):
        certified_supplied_finite_model_H_cell(
            leaf_from_path("63:"), baryon_scalars=BARYONS,
            z_lens="0.1153", z_source=0.871, radial_kpc=RADIAL,
            density_msun_per_kpc3=DENSITY, expected_nodal_sha256=frozen_nodal_digest(RADIAL,DENSITY),
        )
    with pytest.raises(G4b1bError, match="component enclosure failed"):
        certified_supplied_finite_model_H_cell(
            leaf_from_path("63:"), baryon_scalars=BARYONS,
            z_lens=0.9, z_source=0.2, radial_kpc=RADIAL,
            density_msun_per_kpc3=DENSITY, expected_nodal_sha256=frozen_nodal_digest(RADIAL,DENSITY),
        )
    with pytest.raises(G4b1bError, match="noncanonical"):
        certified_supplied_finite_model_H_cell(
            Leaf("00:", R_MIN, R_MAX), baryon_scalars=BARYONS,
            z_lens=0.1153, z_source=0.871, radial_kpc=RADIAL,
            density_msun_per_kpc3=DENSITY, expected_nodal_sha256=frozen_nodal_digest(RADIAL,DENSITY),
        )
