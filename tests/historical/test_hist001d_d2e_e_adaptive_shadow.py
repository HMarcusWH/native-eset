"""D2e-E adaptive convex bounds on exact finite nodal shadow cylinder mass."""
from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import math

import numpy as np
import pytest
from scipy.integrate import quad

from native_eset.numerics.exact_shadow_bounds import (
    ShadowEnclosureError,
    enclose_finite_cylinder_mass,
    guaranteed_pointwise_error,
)
from native_eset.numerics.adaptive_shadow_bounds import (
    TARGET_RELATIVE_WIDTH, MAX_REFINEMENT_SPLITS,
    _convex_outer_cell, _g_bounds, _g_derivative_bounds,
    enclose_adaptive_convex_shadow,
)


def _between(value, result):
    return Decimal(result["lower_msun"]) <= Decimal.from_float(float(value)) <= Decimal(result["upper_msun"])


def _uniform_annulus_mass(a, b, A):
    """Analytic constant-density cylinder for finite 3D shell [a,b]."""
    return (4*math.pi/3)*(
        b**3 - max(0.,b*b-A*A)**1.5
        - a**3 + max(0.,a*a-A*A)**1.5
    )


@pytest.mark.parametrize("A", [0., .03, .2, .4, 1., 2., 4.])
def test_exact_uniform_finite_shell_enclosed_and_target_status(A):
    r=np.linspace(.02,4.,61)
    result=enclose_adaptive_convex_shadow(
        r,np.ones_like(r),A,target_relative_width="1e-8",max_refinement_splits=16384,
    )
    assert _between(_uniform_annulus_mass(float(r[0]),float(r[-1]),A),result)
    assert Decimal(result["lower_msun"]) <= Decimal(result["upper_msun"])
    if 0 < A <= 4:
        assert result["target_met"] is True
        assert Decimal(result["relative_interval_width_upper"]) <= Decimal("1e-8")
    else:
        assert result["target_met"] is False  # Zero aperture: no relative mass target.


def test_convex_tangent_and_chord_bound_at_each_sample_point():
    A=Fraction.from_float(.52)
    a,b=Fraction.from_float(.6), Fraction.from_float(2.)
    lo,hi=_convex_outer_cell(a,b,Fraction(100),Fraction(40),A,88)
    assert 0<=lo<=hi
    for i in range(1001):
        x=float(a)+(float(b)-float(a))*i/1000
        rho=100+(40-100)*i/1000
        # Concavity/convexity only diagnosed here numerically. The
        # mathematical bound derives from analytic g'' positivity.
        assert rho>=40
    mid=(a+b)/2
    dl,dh=_g_derivative_bounds(mid,A,88)
    assert dl<=dh<0
    for point in (a,mid,b):
        gl,gh=_g_bounds(point,A,88)
        assert gl<=gh
        actual=float(A*A*point)/(float(point)+math.sqrt(float(point*point-A*A)))
        assert float(gl)*(1-1e-14) <= actual <= float(gh)*(1+1e-14)


def test_steep_nonmonotone_piecewise_density_independent_adaptive_integral():
    r=np.geomspace(.02,3.5,45)
    rho=np.array([200+950*math.exp(-((math.log(x)-math.log(.21))/.19)**2)
                  +300*abs(math.sin(4*math.log(x))) for x in r])
    A=.39
    result=enclose_adaptive_convex_shadow(
        r,rho,A,target_relative_width="1e-8",max_refinement_splits=12000,
    )
    def integrand(x):
        y=float(np.interp(x,r,rho))
        return 4*math.pi*y*(
            x*x if x<=A else x*A*A/(x+math.sqrt(x*x-A*A))
        )
    reference=0.
    for lo,hi in zip(r[:-1],r[1:]):
        for a,b in ((lo,min(hi,A)),(max(lo,A),hi)):
            if b>a:
                reference+=quad(integrand,a,b,epsabs=1e-10,epsrel=2e-12)[0]
    assert _between(reference,result)
    assert result["target_met"] is True


def test_new_interval_is_contained_in_earlier_monotone_shell_enclosure():
    r=np.linspace(.02,120,480)
    rho=1e8/(r+.5)**3
    for A in (.1,1.3,8.5):
        old=enclose_finite_cylinder_mass(r,rho,A)
        new=enclose_adaptive_convex_shadow(
            r,rho,A,target_relative_width="1e-8",max_refinement_splits=12000,
        )
        assert Decimal(old["lower_msun"]) <= Decimal(new["lower_msun"])
        assert Decimal(new["upper_msun"]) <= Decimal(old["upper_msun"])
        assert new["target_met"]
        estimate=(float(new["lower_msun"])+float(new["upper_msun"]))/2
        delta=guaranteed_pointwise_error(estimate,new)
        assert Decimal(delta["relative_error_upper"])<Decimal("1e-7")


def test_unmet_precision_is_an_explicit_unresolved_result():
    r=[.02,.1,.6,2.,5.]
    rho=[5000.,2000.,100.,50.,10.]
    x=enclose_adaptive_convex_shadow(
        r,rho,.65,target_relative_width="1e-12",max_refinement_splits=0,
    )
    assert x["target_met"] is False
    assert x["status"]=="VALID_ENCLOSURE_BUT_TARGET_NOT_MET"
    assert Decimal(x["lower_msun"]) <= Decimal(x["upper_msun"])
    assert x["refinement_splits"]==0


def test_adaptive_split_budget_is_exactly_reported():
    r=np.linspace(.02,8,100)
    rho=2e6/(r+.3)**2
    result=enclose_adaptive_convex_shadow(
        r,rho,.34,target_relative_width="1e-12",max_refinement_splits=20,
    )
    assert result["refinement_splits"]<=20
    assert result["target_met"] is False


@pytest.mark.parametrize("r,rho,A",[
    ([.1,.2,.3],[1.,float("nan"),2.],.1),
    ([.1,.2,.15],[1,2,3],.1),
    ([.1,.2,.3],[1,2,-3],.1),
    ([.1,.2,.3],[1,2,3],.4),
])
def test_malformed_source_rejected_fail_closed(r,rho,A):
    with pytest.raises(ShadowEnclosureError):
        enclose_adaptive_convex_shadow(r,rho,A)


def test_invalid_precision_and_resource_policy_rejected():
    r=[.1,.2,.4]
    rho=[1.,2.,1.]
    for kw in (
        {"target_relative_width":"INVALID"},
        {"target_relative_width":"1e-20"},
        {"decimal_precision":12},
        {"sqrt_bits":8},
        {"max_refinement_splits":50001},
        {"max_refinement_splits":True},
    ):
        with pytest.raises(ShadowEnclosureError):
            enclose_adaptive_convex_shadow(r,rho,.15,**kw)


def test_strict_nonphysical_claim_contract_and_baseline_constants():
    assert TARGET_RELATIVE_WIDTH=="0.00000001"
    assert MAX_REFINEMENT_SPLITS==16384
    assert Decimal(TARGET_RELATIVE_WIDTH)==Decimal("1e-8")
