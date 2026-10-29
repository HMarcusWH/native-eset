"""D2e-C constrained density-gradient and radial-continuation sensitivity tests."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
SCRIPT = ROOT / "tools/hist001d_d2e_error_budget.py"
SPEC = importlib.util.spec_from_file_location("hist001d_d2e_c", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


def test_scientific_status_and_separate_numerical_identities():
    assert D.SOURCE_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert D.FINITE_DOMAIN == (.02, 120.)
    assert D.DENSITY_POINTS == 11520
    assert len(D.ALTERNATIVES) == 6
    assert D.CLAIMS["new_numerical_counterfactual_identities"] is True
    assert D.CLAIMS["source_gradient_changed"] is False
    assert D.CLAIMS["original_source_modified"] is False
    assert D.CLAIMS["canonical_theory_state_mutated"] is False
    for label in ("root_uniqueness_mathematically_certified",
                  "global_error_bound_established","mass_outside_finite_domain_bounded",
                  "physical_provider_admitted","physical_weyl_lensing_derived",
                  "native_v172_equivalence_proved","new_holdout_scored"):
        assert D.CLAIMS[label] is False
    assert D.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


def test_hernquist_inner_enclosed_mass_exact_under_declared_extension():
    m, re, cutoff = 1e11, 3.6306, .02
    a = re/1.8153
    actual = D.hernquist_inner_mass(m,re,cutoff)
    rho = lambda r: m*a/(2*math.pi*r*(r+a)**3)
    integrated = quad(lambda r: 4*math.pi*r*r*rho(r),0,cutoff,epsrel=1e-12)[0]
    assert actual == pytest.approx(integrated,rel=1e-12)
    assert 0 < actual < m
    with pytest.raises(D.D2eCError):
        D.hernquist_inner_mass(-1,re)


def test_external_power_law_tail_is_positive_but_not_authorized():
    A, edge_rho=2., 1e5
    p4=D.analytic_shadow_tail_cylinder(A,edge_rho,4)
    p5=D.analytic_shadow_tail_cylinder(A,edge_rho,5)
    assert p4 > p5 > 0
    assert D.CLAIMS["mass_outside_finite_domain_bounded"] is False
    for p,actual in ((4,p4),(5,p5)):
        small_aperture=2*math.pi*edge_rho*120*A*A/(p-1)
        assert actual==pytest.approx(small_aperture,rel=2e-4)


@pytest.mark.parametrize("args", [
    (121.,1e5,4), (2.,-1.,4), (2.,1e5,2), (-1.,1e5,5),
])
def test_invalid_unregistered_tail_denied(args):
    with pytest.raises(D.D2eCError):
        D.analytic_shadow_tail_cylinder(*args)


def test_alternative_derivatives_nonnegative_on_monotone_synthetic_source():
    r=np.linspace(.02,120.,601)
    m=1e10*r*r/(r+2.)**2
    rho_source=np.maximum(np.gradient(m,r)/(4*math.pi*r*r),0.)
    variants=D.alternate_densities(r,m,rho_source)
    assert set(variants)=={"SOURCE_GRADIENT","EDGE_ORDER_2","PCHIP_DERIVATIVE"}
    assert np.array_equal(variants["SOURCE_GRADIENT"],rho_source)
    assert all(np.isfinite(v).all() and (v>=0).all() for v in variants.values())
    # Edge-order 2 touches endpoints, not a new physical source model.
    assert variants["EDGE_ORDER_2"][1:-1]==pytest.approx(rho_source[1:-1])
    assert np.max(np.abs(variants["PCHIP_DERIVATIVE"]-rho_source))>0


def test_invalid_density_values_rejected():
    r=np.array([.02,.03,.04,.05])
    m=np.array([1.,2.,3.,4.])
    rho=np.array([2.,2.,2.,2.])
    with pytest.raises(D.D2eCError):
        D.alternate_densities(r,[1.,2.,float("nan"),4.],rho)
    with pytest.raises(D.D2eCError):
        D.alternate_densities(r[::-1],m,rho)


def test_dependency_source_hashes_and_original_march_bytes():
    from native_eset.historical.hist001_source import verify_hist001_source
    trusted=verify_hist001_source(SOURCE)
    assert trusted["source_lock_sha256"]==D.SOURCE_SHA256
    assert trusted["frozen_files"]==46
    assert trusted["archived_negative_records"]==3
    a=D.load_pinned("hist001d_d2e.py",D.D2E_A_SHA256)
    b=D.load_pinned("hist001d_d2e_interval.py",D.D2E_B_SHA256)
    assert a.SOURCE_SHA256==b.SOURCE_SHA256==D.SOURCE_SHA256
    assert b.CLAIMS["root_uniqueness_mathematically_certified"] is False
    with pytest.raises(D.D2eCError,match="pinned prerequisite"):
        D.load_pinned("hist001d_d2e_interval.py","0"*64)
