"""G4b.1a mathematical continuum-cell bridge; no historical root theorem."""
from __future__ import annotations

from fractions import Fraction

import pytest

from native_eset.numerics.hist001d_g4b_root_intervals import (
    R_MAX, R_MIN, G4b0Error, Leaf, leaf_from_path,
)
from native_eset.numerics.hist001d_g4b1_boundary_bridge import SOURCE_QFLOOR
from native_eset.numerics.hist001d_g4b1a_cell_baryon_boxes import (
    G4b1aError, certified_analytic_baryon_cell,
)


PARAMS = {
    "bulge_mass_msun": 1.0e10,
    "hernquist_a_kpc": 1.0,
    "disc_mass_msun": 2.0e10,
    "disc_scale_kpc": 1.5,
    "bulge_q": 0.7,
    "disc_q": 0.8,
}


def _q(data, name):
    pair = data[name]
    return Fraction(int(pair["num"]), int(pair["den"]))


@pytest.mark.parametrize("path", ["00:", "09:", "63:", "27:01010101"])
def test_actual_certified_kernel_contract_on_real_cell(path):
    cell = leaf_from_path(path)
    result = certified_analytic_baryon_cell(cell, **PARAMS, g1_max_splits=0)
    assert result["registered_source_cell_path"] == path
    assert 0 < _q(result, "finite_continuum_bulge_mass_exact_lower") <= _q(
        result, "finite_continuum_bulge_mass_exact_upper"
    )
    assert 0 < _q(result, "continuum_elliptical_disk_mass_exact_lower") <= _q(
        result, "continuum_elliptical_disk_mass_exact_upper"
    )
    assert SOURCE_QFLOOR <= _q(result, "exact_analytic_q_lower") <= _q(
        result, "exact_analytic_q_upper"
    ) <= 1
    rlo = Fraction.from_float(result["outward_binary64_radius_lower"])
    rhi = Fraction.from_float(result["outward_binary64_radius_upper"])
    assert R_MIN <= rlo <= cell.left < cell.right <= rhi <= R_MAX
    assert result["outward_binary64_shadow_aperture_lower"] >= 0
    assert result["outward_binary64_shadow_aperture_upper"] <= float(R_MAX)
    assert result["all_real_radii_in_source_cell_analytic_baryon_masses_enclosed"] is True
    assert result["original_March_180x120_numeric_all_radius_errors_bounded"] is False
    assert result["source_nodal_11520_shadow_density_bound_computed"] is False
    assert result["critical_sigma_source_result_bound_computed"] is False
    assert result["model_H_residual_bound_computed"] is False
    assert result["real_root_existence_or_uniqueness_certified"] is False
    assert result["physical_provider_admitted"] is False
    assert result["empirical_validation"] == "NOT_ESTABLISHED"


def test_leftmost_original_binary64_RMIN_retains_positive_hernquist_shell():
    result = certified_analytic_baryon_cell(leaf_from_path("00:"), **PARAMS)
    b_lower = _q(result, "finite_continuum_bulge_mass_exact_lower")
    r0 = R_MIN
    exact_lemma = Fraction.from_float(PARAMS["bulge_mass_msun"]) * (
        Fraction.from_float(PARAMS["hernquist_a_kpc"])
    ) * r0*r0 / (2*(2*r0+Fraction.from_float(PARAMS["hernquist_a_kpc"]))**3)
    assert b_lower == exact_lemma > 0
    assert result["bulge_lower_method"] == "STRICT_POSITIVE_RMIN_SHELL_LEMMA"
    assert result["g1_lower_target_met"] is None


def test_nearest_float_mass_interval_collapse_is_not_allowed(monkeypatch):
    import native_eset.numerics.certified_baryon_mass as K

    def fake_bulge(*args, **kwargs):
        return {"lower_msun":"9.999999999999999999999999999999",
                "upper_msun":"10.000000000000000000000000000001",
                "target_met":False}

    def fake_disk(*args, **kwargs):
        return {"lower_msun":"4.999999999999999999999999999999",
                "upper_msun":"5.000000000000000000000000000001"}

    monkeypatch.setattr(K, "certified_hernquist_point", fake_bulge)
    monkeypatch.setattr(K, "certified_elliptical_disk_radius_band", fake_disk)
    r = certified_analytic_baryon_cell(leaf_from_path("18:0101"), **PARAMS)
    assert _q(r, "finite_continuum_bulge_mass_exact_lower") < Fraction(10)
    assert _q(r, "finite_continuum_bulge_mass_exact_upper") > Fraction(10)
    assert _q(r, "continuum_elliptical_disk_mass_exact_lower") < Fraction(5)
    assert _q(r, "continuum_elliptical_disk_mass_exact_upper") > Fraction(5)
    assert r["g1_upper_target_met"] is False
    assert r["g1_lower_target_met"] is False


def test_invalid_mass_box_is_rejected_and_never_promoted(monkeypatch):
    import native_eset.numerics.certified_baryon_mass as K
    monkeypatch.setattr(K, "certified_hernquist_point", lambda *a, **kw: {
        "lower_msun":"1", "upper_msun":"2", "target_met":True,
    })
    monkeypatch.setattr(K, "certified_elliptical_disk_radius_band", lambda *a, **kw: {
        "lower_msun":"0", "upper_msun":"100",
    })
    with pytest.raises(G4b1aError, match="strictly positive"):
        certified_analytic_baryon_cell(leaf_from_path("18:"), **PARAMS)


@pytest.mark.parametrize("field,value", [
    ("bulge_mass_msun", 0.0), ("disc_mass_msun", -1.0),
    ("hernquist_a_kpc", float("nan")), ("disc_scale_kpc", 1),
    ("bulge_q", 1.2), ("disc_q", True),
])
def test_reject_unsound_source_parameters(field, value):
    p = dict(PARAMS)
    p[field] = value
    with pytest.raises(G4b1aError):
        certified_analytic_baryon_cell(leaf_from_path("21:"), **p)


def test_reject_unauthenticated_radius_and_bad_budget():
    with pytest.raises((G4b1aError,G4b0Error)):
        certified_analytic_baryon_cell(Leaf("00:",R_MIN,R_MAX), **PARAMS)
    with pytest.raises(G4b1aError):
        certified_analytic_baryon_cell(leaf_from_path("21:"), **PARAMS, g1_max_splits=True)
    with pytest.raises(G4b1aError):
        certified_analytic_baryon_cell(leaf_from_path("21:"), **PARAMS, g1_max_splits=9000)
