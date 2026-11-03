"""Source-free mathematical regressions for selected-M* affine-cylinder geometry.

These synthetic checks do not by themselves validate the protected historical
source, K Bessel implementation, physical density, or historical root model.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import atan, isclose
from pathlib import Path
import sys
import pytest
SOURCE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_k180_cancel_aware_candidate'
sys.path.insert(0,str(SOURCE))
from affine_kernel import X,sqrt_interval,atan_positive,kernel,kernel_integral  # noqa: E402
from signed_affine_producer import kernel_variation_max,weighted_curvature_kernel_upper  # noqa: E402

@pytest.mark.parametrize('v',[Q(0),Q(1),Q(2),Q(25,9),Q(1,2),Q(1234567,7654321)])
def test_directed_root(v):
    r=sqrt_interval(X(v))
    assert r.lower()>=0 and r.lower()**2<=v<=r.upper()**2

@pytest.mark.parametrize('v',[Q(0),Q(1,10),Q(1,3),Q(1),Q(10),Q(100)])
def test_rational_atan(v):
    q=atan_positive(X(v))
    # Independent float regression only; interval proof rests on exact
    # alternating Taylor / monotone half-angle inequalities.
    assert float(q.lower())-1e-14<=atan(float(v))<=float(q.upper())+1e-14
    assert q.lower()>=0 and q.lower()<=q.upper()

@pytest.mark.parametrize('A,a,b',[(Q(1),Q(1),Q(2)),(Q(2),Q(1),Q(4)),
  (Q(2),Q(3),Q(4)),(Q(2),Q(1),Q(2)),(Q(3),Q(1),Q(2)),
  (Q(1,2),Q(1),Q(10)),(Q(7,5),Q(2),Q(9,4)),(Q(5),Q(3),Q(9)),
  (Q(1),Q(119),Q(120)),(Q(1,100),Q(1),Q(120))])
def test_cylinder_mass_kernel_integral(A,a,b):
    y=kernel_integral(A,a,b)
    assert Q(0)<=y.lower()<=y.upper()<=b-a
    if A>=b:assert y.lower()==y.upper()==b-a
    # Midpoint Riemann sums only as a numerical regression sanity check.
    n=512
    estimate=sum(float(kernel(A,a+(Q(2*k+1,2*n))*(b-a)).lower()) for k in range(n))*float((b-a)/n)
    assert abs(float((y.lower()+y.upper())/2)-estimate)<0.01*float(b-a)

@pytest.mark.parametrize('A,r',[(Q(0),Q(1)),(Q(1,2),Q(1)),(Q(1),Q(1)),
  (Q(2),Q(1)),(Q(3),Q(10)),(Q(1),Q(120))])
def test_positive_finite_kernel(A,r):
    v=kernel(A,r)
    assert Q(0)<=v.lower()<=v.upper()<=Q(1)

@pytest.mark.parametrize('a,b',[(Q(1),Q(2)),(Q(2),Q(3)),(Q(4),Q(5)),(Q(1,50),Q(69,100))])
def test_signed_peano_coarse_and_refined(a,b):
    band_lo,band_hi=Q(2,5),Q(16,5)
    w=weighted_curvature_kernel_upper(band_lo,band_hi,a,b,12)
    coarse=(b-a)**2*kernel_variation_max(band_lo,band_hi,a,b)/4
    assert Q(0)<=w.lower()<=w.upper()<=X(coarse).upper()
    # An M'' bound C=2 makes the signed projection error at most C*W/2.
    C=Q(2)
    assert C*w.upper()/2<=C*X(coarse).upper()/2

def test_source_free_mass_interpolant_sign():
    # For strictly convex M(r)=r², its chord overestimates the function.
    # Since -d_r phi>=0, the Peano correction P - P_affine is nonpositive.
    a,b=Q(1),Q(2)
    M=lambda r:r*r
    slope=(M(b)-M(a))/(b-a)
    assert slope>0
    for r in (Q(5,4),Q(3,2),Q(7,4)):
        err=M(r)-(M(a)+slope*(r-a))
        assert err<0
        assert err>=-(b-a)**2/4

def test_large_aperture_saturation_exact():
    for a,b in ((Q(1),Q(2)),(Q(7),Q(10)),(Q(1,50),Q(120))):
        out=kernel_integral(2*b,a,b)
        assert out.lower()<=b-a<=out.upper()

def test_half_angle_large_argument_is_bounded():
    v=atan_positive(X(Q(10**6)))
    assert 0<v.lower()<v.upper()<Q(2)
    assert isclose(float(v.lower()),atan(1e6),rel_tol=1e-12)

def test_reject_bad_domains():
    with pytest.raises(ValueError):sqrt_interval(X(-1))
    with pytest.raises(ValueError):atan_positive(X(-1))
    with pytest.raises(ValueError):kernel_integral(Q(-1),Q(1),Q(2))
    with pytest.raises(ValueError):kernel_integral(Q(1),Q(3),Q(2))
    with pytest.raises(ValueError):kernel(Q(-1),Q(2))
    with pytest.raises(ValueError):weighted_curvature_kernel_upper(Q(1),Q(2),Q(3),Q(2))
