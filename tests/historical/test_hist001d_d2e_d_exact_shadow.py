"""Exact-rational finite shadow cylinder enclosure and D2e-D source receipts."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import shutil
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

from native_eset.numerics.exact_shadow_bounds import (
    ShadowEnclosureError,
    _pi_fraction_bounds,
    _sqrt_rational_bounds,
    enclose_finite_cylinder_mass,
    guaranteed_pointwise_error,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
SCRIPT = ROOT / "tools/hist001d_d2e_d_exact_projection.py"
SPEC = importlib.util.spec_from_file_location("hist001d_d2e_d", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


def _contains_float_approx(x, result):
    return Decimal(result["lower_msun"]) <= Decimal.from_float(float(x)) <= Decimal(result["upper_msun"])


def test_fixed_protocol_source_and_nonpromotion():
    assert D.SOURCE_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert D.D2E_A_SHA256 == "ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2"
    assert D.RADIAL_POINTS == 11520
    assert D.DOMAIN == (.02, 120.)
    assert D.CLAIMS["shadow_piecewise_linear_pointwise_enclosed"] is True
    assert D.CLAIMS["old_d2e_b_mass_assumption_proved"] is False
    for field in ("root_uniqueness_mathematically_certified",
                  "global_error_bound_established","mass_outside_finite_domain_bounded",
                  "physical_provider_admitted","physical_weyl_lensing_derived",
                  "native_v172_equivalence_proved","new_holdout_scored",
                  "baryonic_or_qeff_numerical_error_bounded"):
        assert D.CLAIMS[field] is False
    assert D.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("a", [0.02, 0.2, 0.5, 1., 2., 3.5])
def test_uniform_shell_analytic_cylinder_is_enclosed(a):
    r = np.linspace(.2, 4., 80)
    out = enclose_finite_cylinder_mass(r, np.ones_like(r), a)
    whole = 4*math.pi/3 * (4**3 - (4**2-a*a)**1.5)
    missing = 4*math.pi/3 * (.2**3 - max(.2*.2-a*a, 0.)**1.5)
    assert _contains_float_approx(whole-missing, out)
    assert out["input_semantics"] == "EXACT_BINARY64_RADIAL_DENSITY_AND_APERTURE"


def test_full_aperture_entire_volume_exact_to_pi_bounds():
    r = np.linspace(.2, 4., 100)
    out = enclose_finite_cylinder_mass(r, np.ones_like(r), 4.)
    volume = Fraction(4, 3)*(
        Fraction.from_float(float(r[-1]))**3 - Fraction.from_float(float(r[0]))**3
    )
    pi_lo, pi_hi = _pi_fraction_bounds()
    assert Fraction(Decimal(out["lower_msun"])) <= volume*pi_lo
    assert Fraction(Decimal(out["upper_msun"])) >= volume*pi_hi
    assert out["inside_cells"] == len(r)-1
    assert out["outside_cells"] == 0


def test_nonconstant_linear_source_independent_cellwise_adaptive_quad():
    r = np.geomspace(.02, 4., 90)
    rho = 1e4*np.exp(-r/1.5)
    aperture = .8
    out = enclose_finite_cylinder_mass(r, rho, aperture)
    def integrand(x):
        value = np.interp(x, r, rho)
        return 4*math.pi*value*(
            x*x if x <= aperture
            else x*aperture**2/(x+math.sqrt(x*x-aperture**2))
        )
    approximate = 0.
    for a, b in zip(r[:-1], r[1:]):
        for u, v in ((a, min(b, aperture)), (max(a, aperture), b)):
            if v > u:
                approximate += quad(integrand, u, v, epsrel=1e-11, epsabs=1e-10)[0]
    assert _contains_float_approx(approximate, out)
    assert out["crossing_cells"] == 1


def test_sharp_nonmonotone_positive_density_still_enclosed():
    r = [.02, .05, .15, .5, 2., 3.5]
    rho = [1500., 40., 400., 30., 60., 15.]
    A = .17
    result = enclose_finite_cylinder_mass(r, rho, A)
    def integrand(x):
        value = np.interp(x, r, rho)
        return 4*math.pi*value*(x*x if x <= A else x*A*A/(x+math.sqrt(x*x-A*A)))
    reference = sum(
        quad(integrand, x, y, epsabs=1e-12)[0]
        for u,v in zip(r[:-1],r[1:])
        for x,y in ((u,min(v,A)),(max(u,A),v)) if y>x
    )
    assert _contains_float_approx(reference, result)


def test_pointwise_discrete_error_bound_is_one_sided_upward():
    r=np.linspace(.02,120,11520)
    rho=1e8/(r+.5)**3
    bound=enclose_finite_cylinder_mass(r,rho,2.23)
    guess=float((Decimal(bound["lower_msun"])+Decimal(bound["upper_msun"]))/2)
    measured=guaranteed_pointwise_error(guess,bound)
    error=Decimal(measured["absolute_error_upper_msun"])
    guess_exact=Decimal.from_float(guess)
    assert error >= abs(guess_exact-Decimal(bound["lower_msun"]))
    assert error >= abs(guess_exact-Decimal(bound["upper_msun"]))
    assert float(measured["relative_error_upper"]) < .01


def test_integer_square_root_bounds_are_exact_rational():
    for rational in (Fraction(2,3), Fraction(1024,81), Fraction(0), Fraction(7,333)):
        lo,hi=_sqrt_rational_bounds(rational,88)
        assert lo*lo <= rational <= hi*hi


def test_pi_is_bounded_by_alternating_rational_series():
    lower,upper=_pi_fraction_bounds()
    assert lower<upper and upper-lower < Fraction(1,10**65)
    assert format(Decimal(lower.numerator)/Decimal(lower.denominator),".15f")=="3.141592653589793"


@pytest.mark.parametrize("r,rho,aperture", [
    ([.1,.5,.4],[1,1,1],.2),
    ([.1,.2,.3],[1,-2,1],.2),
    ([.1,.3],[1,float("nan")],.2),
    ([.2,.3],[1,2],.4),
])
def test_invalid_source_inputs_fail_closed(r,rho,aperture):
    with pytest.raises(ShadowEnclosureError):
        enclose_finite_cylinder_mass(r,rho,aperture)


def test_invalid_numeric_policy_fails_closed():
    with pytest.raises(ShadowEnclosureError):
        enclose_finite_cylinder_mass([.1,.2],[1,2],.15,decimal_precision=10)
    with pytest.raises(ShadowEnclosureError):
        enclose_finite_cylinder_mass([.1,.2],[1,2],.15,sqrt_bits=7)


def _rewrite_and_rehash(folder: Path, update):
    from native_eset.evidence.receipts import canonical_json
    report=json.loads((folder/"report.json").read_bytes())
    update(report)
    raw_report=canonical_json(report)
    (folder/"report.json").write_bytes(raw_report)
    receipt=json.loads((folder/"receipt.json").read_bytes())
    receipt["report_sha256"]=hashlib.sha256(raw_report).hexdigest()
    raw_receipt=canonical_json(receipt)
    (folder/"receipt.json").write_bytes(raw_receipt)
    (folder/"receipt.sha256").write_text(hashlib.sha256(raw_receipt).hexdigest()+"\n")


def test_fake_self_rehashed_provider_claim_and_numeric_row_rejected(tmp_path,monkeypatch):
    fake={
        "schema":D.SCHEMA,"status":D.STATUS,
        "claims":dict(D.CLAIMS),"pointwise_sample_count":30,
        "synthetic_numeric_field":[42.],
    }
    monkeypatch.setattr(D,"execute",lambda source: fake)
    out=tmp_path/"run"
    receipt=D.run(SOURCE,out)
    assert D.verify(out/"receipt.json",SOURCE,receipt["receipt_sha256"])["samples"]==30

    new=tmp_path/"false_provider"
    shutil.copytree(out,new)
    _rewrite_and_rehash(new,lambda report:report["claims"].update({"physical_provider_admitted":True}))
    with pytest.raises(D.D2eDIntegrityError,match="forgery"):
        D.verify(new/"receipt.json",SOURCE)

    new2=tmp_path/"false_number"
    shutil.copytree(out,new2)
    _rewrite_and_rehash(new2,lambda report:report["synthetic_numeric_field"].__setitem__(0,99.))
    with pytest.raises(D.D2eDIntegrityError,match="source numerical reexecution differs"):
        D.verify(new2/"receipt.json",SOURCE)


def test_source_module_pinned_and_original_46_plus_three():
    from native_eset.historical.hist001_source import verify_hist001_source
    source=verify_hist001_source(SOURCE)
    assert source["source_lock_sha256"]==D.SOURCE_SHA256
    assert source["frozen_files"]==46
    assert source["archived_negative_records"]==3
    model=D._load_d2e_a()
    assert model.CLAIMS["root_uniqueness_mathematically_certified"] is False
