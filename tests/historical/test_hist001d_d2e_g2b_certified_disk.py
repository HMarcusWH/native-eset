"""D2e-G2b: certified full-azimuth analytic disk enclosure tests."""
from __future__ import annotations

import math
from decimal import Decimal, localcontext
from fractions import Fraction

import pytest
from scipy.integrate import quad

from native_eset.numerics.certified_baryon_mass import (
    certified_elliptical_disk_radius_band,
)
from native_eset.numerics.certified_disk_angular import (
    MESH_MIDPOINTS, TARGET_RELATIVE_WIDTH,
    _sin_rational_bounds,
    certified_periodic_exponential_disk_point,
    certified_periodic_exponential_disk_radius_band,
)
from native_eset.numerics.exact_shadow_bounds import ShadowEnclosureError


def _contains(bound, sample):
    return Decimal(bound["lower_msun"]) <= Decimal.from_float(float(sample)) <= Decimal(bound["upper_msun"])


def test_rational_sine_encloses_high_precision_decimal_reference():
    # Decimal has no sin(); support claim with a separate 100-term Decimal
    # Taylor summation (this independent finite check is NOT the proof).
    for x in [Fraction(0),Fraction(1,20),Fraction(1,2),
              Fraction(1),Fraction(3,2)]:
        lo, hi = _sin_rational_bounds(x)
        with localcontext() as ctx:
            ctx.prec = 110
            z = Decimal(x.numerator)/Decimal(x.denominator)
            val = term = z
            for j in range(1,80):
                term *= -(z*z)/Decimal((2*j)*(2*j+1))
                val += term
            assert Decimal(lo.numerator)/Decimal(lo.denominator) <= val
            assert val <= Decimal(hi.numerator)/Decimal(hi.denominator)


def test_circular_disk_high_precision_exact_binary64_continuum():
    mass=1e10
    scale=3.7
    R=2.4
    out=certified_periodic_exponential_disk_point(
        R,mass,scale,1.,midpoints=16,
    )
    with localcontext() as ctx:
        ctx.prec=110
        x=Decimal.from_float(R)/Decimal.from_float(scale)
        exact=Decimal.from_float(mass)*(1-(1+x)*(-x).exp())
        lo,hi=Decimal(out["lower_msun"]),Decimal(out["upper_msun"])
        assert lo <= exact <= hi
    assert out["target_met"]
    assert out["source_periodic1024_floating_quadrature_error_certified"] is False


@pytest.mark.parametrize("q,x,n", [
    (.2,.8,128),(.35,1.2,256),(.6,2.,128),(.8,.7,128),
])
def test_independent_continuum_quadrature_contained(q,x,n):
    mass=7e10
    scale=2.
    radius=x*scale
    out=certified_periodic_exponential_disk_point(
        radius,mass,scale,q,midpoints=n,
    )
    def integrand(phi):
        d=math.cos(phi)**2 + q*q*math.sin(phi)**2
        z=x/math.sqrt(d)
        h=-math.expm1(-z)-z*math.exp(-z)
        return (2/math.pi)*h
    mean=quad(integrand,0,math.pi/2,epsabs=1e-12,epsrel=2e-12)[0]
    assert _contains(out,mass*mean)
    assert not out["source_periodic1024_floating_quadrature_error_certified"]
    assert Decimal(out["lower_msun"])>=0
    assert Decimal(out["upper_msun"])<=Decimal.from_float(mass)


def test_analytic_continuum_interval_nesting_with_coarse_g2_bound():
    M=3e10
    q=.42
    scale=2.1
    R=3.4
    coarse=certified_elliptical_disk_radius_band(R,R,M,scale,q)
    fine=certified_periodic_exponential_disk_point(
        R,M,scale,q,midpoints=256,
    )
    # Both enclose the same exact analytic object. Here the precise
    # enclosure is expected inside this intentionally coarse bound.
    assert Decimal(coarse["lower_msun"])<=Decimal(fine["lower_msun"])
    assert Decimal(fine["upper_msun"])<=Decimal(coarse["upper_msun"])


def test_midpoint_mesh_refinement_contract_tightens_interval():
    small=certified_periodic_exponential_disk_point(
        2.4,3e10,1.8,.55,midpoints=64,
    )
    large=certified_periodic_exponential_disk_point(
        2.4,3e10,1.8,.55,midpoints=256,
    )
    # Independent certified midpoint meshes need not yield nested
    # intervals, though they must overlap and have a smaller width.
    assert Decimal(large["lower_msun"]) <= Decimal(small["upper_msun"])
    assert Decimal(small["lower_msun"]) <= Decimal(large["upper_msun"])
    assert Decimal(large["relative_interval_width_upper"]) < Decimal(
        small["relative_interval_width_upper"]
    )
    assert large["midpoint_normalized_error_upper"]!=small["midpoint_normalized_error_upper"]


def test_nonmet_target_still_returns_valid_nonpromoting_interval():
    out=certified_periodic_exponential_disk_point(
        .7,1e11,2.,.2,midpoints=8,target_relative_width="0.000001",
    )
    assert not out["target_met"]
    assert 0<=Decimal(out["lower_msun"])<=Decimal(out["upper_msun"])
    assert out["source_cosmological_physics_certified"] is False


def test_continuum_band_covers_independent_radii():
    bound=certified_periodic_exponential_disk_radius_band(
        .5,2.5,8e10,2.,.55,midpoints=128,
    )
    assert bound["all_real_radii_in_band_enclosed"]
    lo,hi=Decimal(bound["lower_msun"]),Decimal(bound["upper_msun"])
    for R in (.5,.8,1.,2.,2.5):
        child=certified_periodic_exponential_disk_point(
            R,8e10,2.,.55,midpoints=32,
        )
        # Compare against the child's independent, potentially wider
        # interval; require compatible nonempty intersection, not nesting.
        assert lo <= Decimal(child["upper_msun"])
        assert Decimal(child["lower_msun"]) <= hi


@pytest.mark.parametrize("inputs", [
    (-1.,1e10,2.,.5), (1.,0.,2.,.5),
    (1.,1e10,-2.,.5),(1.,1e10,2.,0.),
    (1.,1e10,2.,1.5), (121.,1e10,2.,.5),
])
def test_invalid_model_inputs_fail_closed(inputs):
    with pytest.raises(ShadowEnclosureError):
        certified_periodic_exponential_disk_point(*inputs)


@pytest.mark.parametrize("kwargs", [
    {"midpoints":0},{"midpoints":True},{"midpoints":5000},
    {"target_relative_width":"invalid"},
    {"target_relative_width":"1e-20"},
])
def test_invalid_precision_policy_denied(kwargs):
    with pytest.raises(ShadowEnclosureError):
        certified_periodic_exponential_disk_point(
            1.,1e10,2.,.4,**kwargs
        )


def test_source_independent_protocol():
    assert MESH_MIDPOINTS==1024
    assert TARGET_RELATIVE_WIDTH=="0.01"
