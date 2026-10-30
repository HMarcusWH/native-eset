"""D2e-G1/G2: rigorous analytic baryonic interval proof stress tests."""
from __future__ import annotations

import math
from decimal import Decimal, localcontext
from fractions import Fraction

import numpy as np
import pytest
from scipy.integrate import quad

from native_eset.numerics.certified_baryon_mass import (
    G1_TARGET, G1_SPLIT_BUDGET,
    _disk_integral_fraction,
    _exp_minus_rational,
    certified_elliptical_disk_radius_band,
    certified_hernquist_point,
    certified_hernquist_radius_band,
)
from native_eset.numerics.exact_shadow_bounds import ShadowEnclosureError


def _inside(value, bound):
    return Decimal(bound["lower_msun"]) <= Decimal.from_float(float(value)) <= Decimal(bound["upper_msun"])


@pytest.mark.parametrize("R", [.1, .5, 1., 3., 8., 20.])
def test_finite_hernquist_mass_encloses_separate_scipy_integral(R):
    M = 1e11
    a = 2.5
    proof=certified_hernquist_point(
        R,M,a,target_width="1e-5",max_splits=4096,
    )
    in_part=quad(lambda r:2*M*a*r/(r+a)**3, .02,R,
                 epsabs=1e-3,epsrel=1e-11,limit=180)[0]
    outer_part=quad(lambda r:2*M*a/(r+a)**3*(
        R*R/(r+math.sqrt(r*r-R*R))
    ),R,120,epsabs=1e-3,epsrel=1e-11,limit=180)[0]
    assert _inside(in_part+outer_part, proof)
    assert proof["split_count"]<=4096
    assert not proof["source_numerical_error_certified"]


def test_finite_hernquist_radius_band_encloses_all_tested_radii():
    m,a=4e10,1.8
    envelope=certified_hernquist_radius_band(.7,2.2,m,a,max_splits=3072)
    assert Decimal(envelope["lower_msun"])<Decimal(envelope["upper_msun"])
    assert envelope["all_real_radii_in_band_enclosed"]
    for radius in (.7,.75,1.5,2.0,2.2):
        point=certified_hernquist_point(radius,m,a,max_splits=1024)
        # Enclosures at the same endpoint can have different widths
        # when their adaptation budgets differ: require sound overlap,
        # not unsupported nesting between independent error envelopes.
        assert Decimal(envelope["lower_msun"])<=Decimal(point["upper_msun"])
        assert Decimal(point["lower_msun"])<=Decimal(envelope["upper_msun"])


def test_hernquist_exhausted_budget_retains_valid_numeric_bounds():
    p=certified_hernquist_point(.2,1e11,3.,target_width="1e-12",max_splits=0)
    assert p["target_met"] is False
    assert p["split_count"]==0
    assert 0 < Decimal(p["lower_msun"]) <= Decimal(p["upper_msun"])


@pytest.mark.parametrize("x", [0.,.01,.5,1.,2.5,8.,31.,60.])
def test_rational_exponential_bounds_include_high_precision_decimal(x):
    exact=Fraction.from_float(x)
    lower,upper=_exp_minus_rational(exact)
    with localcontext() as ctx:
        ctx.prec=150
        e=(-Decimal.from_float(x)).exp()
        assert Decimal(lower.numerator)/Decimal(lower.denominator) <= e
        assert e <= Decimal(upper.numerator)/Decimal(upper.denominator)


@pytest.mark.parametrize("x", [0.,.1,1.,3.,10.])
def test_disk_cumulative_rational_bounds_include_reference(x):
    lo,hi=_disk_integral_fraction(Fraction.from_float(x))
    exact=1-(1+x)*math.exp(-x)
    assert float(lo)-1e-14 <= exact <= float(hi)+1e-14


def test_circular_disk_analytic_reference_almost_exact():
    M,scale=2e10,3.5
    r=2.7
    bound=certified_elliptical_disk_radius_band(r,r,M,scale,1.0)
    expected=M*(1-math.exp(-r/scale)*(1+r/scale))
    assert abs(float(bound["lower_msun"])-expected)/M<1e-12
    assert abs(float(bound["upper_msun"])-expected)/M<1e-12
    assert bound["all_real_radii_in_band_enclosed"]
    assert not bound["angular_quadrature_512_1024_error_certified"]


def test_elliptical_disk_reference_full_period_integral_is_inside_coarse_bound():
    M, scale, q = 8e10,2.,.45
    rlo, rhi=.7,3.1
    proof=certified_elliptical_disk_radius_band(rlo,rhi,M,scale,q)
    lower,upper=float(proof["lower_msun"]),float(proof["upper_msun"])
    theta=np.linspace(0,2*math.pi,4096,endpoint=False)
    g=np.sqrt(np.cos(theta)**2 + np.sin(theta)**2/q**2)
    for r in (rlo,1.,2.,rhi):
        x=g*r/scale
        fraction=-np.expm1(-x)-x*np.exp(-x)
        sampled=float(M/(2*math.pi*q)*np.mean(fraction/g**2)*2*math.pi)
        assert lower <= sampled <= upper
    assert proof["scope"].startswith("CONTINUUM_EXPONENTIAL_DISK")
    assert not proof["high_accuracy_disc_mass_proved"]


def test_disk_mass_nonnegative_monotonic_and_at_most_total():
    M,scale,q=1e11,2.,.35
    previous=0.
    for R in (.05,.2,1.,3.,10.,120.):
        bound=certified_elliptical_disk_radius_band(R,R,M,scale,q)
        lo,hi=float(bound["lower_msun"]),float(bound["upper_msun"])
        assert 0 <= lo <= hi <= M*(1+1e-14)
        assert lo>=previous
        previous=lo


@pytest.mark.parametrize("args",[
    (0.,1.,1e10,2.,.5),
    (2.,1.,1e10,2.,.5),
    (.1,1.,-1e10,2.,.5),
    (.1,1.,1e10,-2.,.5),
    (.1,1.,1e10,2.,2.),
])
def test_invalid_disk_inputs_fail_closed(args):
    with pytest.raises(ShadowEnclosureError):
        certified_elliptical_disk_radius_band(*args)


@pytest.mark.parametrize("args",[
    (.02,1e10,2.),
    (121.,1e10,2.),
    (1.,0.,2.),
    (1.,1e10,-1.),
])
def test_invalid_bulge_inputs_fail_closed(args):
    with pytest.raises(ShadowEnclosureError):
        certified_hernquist_point(*args)


def test_protocol_constants_and_separate_claim_contract():
    assert G1_TARGET=="0.000001"
    assert G1_SPLIT_BUDGET==8192
