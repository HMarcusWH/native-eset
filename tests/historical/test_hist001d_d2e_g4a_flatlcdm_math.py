"""G4a draft: frozen FlatLCDM mathematical proof and nonpromotion controls."""
from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction

import pytest

import native_eset.numerics.certified_flatlcdm_sigma as M

CASES = (
    ("J0822+1828", .1153, .871),
    ("J0915+4211", .078, .79),
    ("J0930+2855", .3051, .4594),
    ("J1021+2028", .1208, .3507),
    ("J1111+2234", .2223, .9887),
    ("J1135+3720", .162, .402),
)


def _original_flatlcdm_frozen_implementation(zl: float, zs: float) -> float:
    """Literal original formula, for an independent numerical comparison, NOT proof."""
    import numpy as np
    from scipy import integrate

    c, g, four_pi = 299792.458, 4.30091e-6, 4.0 * math.pi

    def I(z: float) -> float:
        val, _ = integrate.quad(
            lambda zp: 1.0 / float(np.sqrt(0.3 * (1.0 + zp)**3 + (1.0 - 0.3))),
            0.0, float(z), epsabs=1e-8, epsrel=1e-8,
        )
        return val

    def dist(z: float) -> float:
        return (c / 70.0) * I(z) * 1000.0

    dd = dist(zl) / (1.0 + zl)
    ds = dist(zs) / (1.0 + zs)
    dls = (dist(zs) - dist(zl)) / (1.0 + zs)
    return (c**2 / (four_pi * g)) * (ds / (dd * dls))


@pytest.mark.parametrize("lens,zl,zs", CASES)
def test_sigma_source_scopes(lens, zl, zs):
    result = M.certified_sigma_critical(zl, zs)
    lo = Fraction(Decimal(result["lower_msun_per_kpc2"]))
    hi = Fraction(Decimal(result["upper_msun_per_kpc2"]))
    assert 0 < lo <= hi and result["target_met"] is True, lens
    assert Fraction(Decimal(result["relative_interval_width_upper"])) <= Fraction(1, 10000)
    ref = _original_flatlcdm_frozen_implementation(zl, zs)
    v = Fraction.from_float(ref)
    assert lo <= v <= hi, lens
    proof = M.a_posteriori_source_output_discrepancy(ref, result)
    assert proof["source_returned_inside_target_enclosure"] is True
    assert proof["physical_lensing_error_bounded"] is False
    assert proof["source_numeric_error_all_redshifts_bounded"] is False
    assert Fraction(Decimal(proof["absolute_discrepancy_upper"])) >= max(abs(v-lo), abs(v-hi))
    assert result["frozen_source_bytes_verified"] is False
    assert proof["source_output_provenance_verified"] is False
    assert result["physical_sigma_critical_error_bounded"] is False
    assert result["root_uniqueness_certified"] is False
    assert result["empirical_validation"] == "NOT_ESTABLISHED"
    assert result["I_l"]["scope"].startswith("FROZEN_BINARY64_SCALAR")


@pytest.mark.parametrize("a,b,om,ode", [
    (0., 0., .3, .7), (1., .5, .3, .7), (-.1, .9, .3, .7),
    (0., 11., .3, .7), (0., .5, 0., .7), (0., .5, .3, -.1),
    (False, .5, .3, .7), (0., float("nan"), .3, .7),
])
def test_integral_inputs_rejected(a, b, om, ode):
    with pytest.raises(M.G4aEnclosureError):
        M.certified_distance_integral(a,b,om,ode)


def test_resource_budget_rejection():
    with pytest.raises(M.G4aEnclosureError):
        M.certified_distance_integral(0.,1.,.3,.7,cells=4)
    with pytest.raises(M.G4aEnclosureError):
        M.certified_distance_integral(0.,1.,.3,.7,sqrt_bits=30)
    with pytest.raises(M.G4aEnclosureError):
        M.certified_distance_integral(0.,1.,.3,.7,precision=12)


def test_sigma_guard_and_unmet_target_is_not_pretended_pass():
    with pytest.raises(M.G4aEnclosureError):
        M.certified_sigma_critical(.7, .1)
    with pytest.raises(M.G4aEnclosureError):
        M.certified_sigma_critical(.1, .7, target_relative_width="broken")
    with pytest.raises(M.G4aEnclosureError):
        M.certified_sigma_critical(.1, .7, G_KPC_KMS2_MSUN=0)
    r = M.certified_sigma_critical(.1153, .871, cells=8, target_relative_width="0.0000001")
    assert r["target_met"] is False
    assert Fraction(Decimal(r["relative_interval_width_upper"])) > Fraction(1, 10000000)
    with pytest.raises(M.G4aEnclosureError):
        M.a_posteriori_source_output_discrepancy(float('nan'),r)
