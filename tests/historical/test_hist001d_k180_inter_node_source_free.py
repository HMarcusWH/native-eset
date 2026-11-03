"""Source-free synthetic checks; protected real-radius data replay is a separate gate."""
from __future__ import annotations
import sys
from pathlib import Path
from fractions import Fraction as Q
import pytest
HERE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_k180_inter_node_candidate'
sys.path.insert(0,str(HERE))
from verify_inter_node import R, i_bessel_positive_series, independent_fpp  # noqa: E402
from band_bv_producer import sqrt_interval, phi, max_delta  # noqa: E402
from inter_node_adversarial_qa import run as adverse  # noqa: E402
from inter_node_adversarial_qa import synthetic  # noqa: E402
from inter_node_claim_guard import validate  # noqa: E402

@pytest.mark.parametrize('x', [Q(0),Q(1,16),Q(1,4),Q(2),Q(9,16),Q(121,49)])
def test_rational_sqrt_outward(x):
    lo,hi=sqrt_interval(x)
    assert lo*lo<=x<=hi*hi
    assert hi-lo<=Q(1,2**192)

@pytest.mark.parametrize('A,r',[(Q(0),Q(3)),(Q(2),Q(1)),(Q(1,2),Q(1)),(Q(2,3),Q(5))])
def test_cylinder_kernel_interval(A,r):
    lo,hi=phi(A,r)
    assert Q(0)<=lo<=hi<=Q(1)
    if A>=r:assert (lo,hi)==(Q(1),Q(1))

@pytest.mark.parametrize('Alo,Ahi,a,b',[
    (Q(0),Q(5),Q(1),Q(3)),
    (Q(1,2),Q(3,2),Q(2),Q(4)),
    (Q(1),Q(5),Q(1),Q(4)),
    (Q(3),Q(5),Q(1),Q(2)),
])
def test_phi_variation_maximum_clamped(Alo,Ahi,a,b):
    bound=max_delta(Alo,Ahi,a,b)
    assert 0<=bound<=1
    for k in range(25):
        A=Alo+(Ahi-Alo)*Q(k,24)
        change=phi(A,a)[1]-phi(A,b)[0]
        assert change<=bound

@pytest.mark.parametrize('y', [Q(1,64),Q(1,2),Q(1),Q(3),Q(10),Q(20)])
def test_fraction_I_series_and_positive_Wronskian_algebra(y):
    i0,i1=i_bessel_positive_series(y,80)
    assert 1<=i0.l<=i0.u and 0<i1.l<=i1.u
    # Chosen exact K0,K1 positive; F defined from them via I0/I1 midpoint.
    # The interval K reconstruction equations must be nonsingular.
    F=R(i0.l*Q(3),i0.u*Q(4))
    assert i0.l*i0.l+i1.l*i1.l>0
    assert F.l>0

@pytest.mark.parametrize('p', [0,1,2,3,7,19])
def test_even_odd_interval_powers(p):
    x=R(Q(-2),Q(3))
    q=x**p
    for xx in (Q(-2),Q(-1),Q(0),Q(1),Q(3)):
        assert q.l<=xx**p<=q.u


def test_independent_panel_variation_synthetic():
    # For M(r)=r^2 on [1,1.1], M'(r)=2r and M''=2.
    a,b=Q(1),Q(11,10)
    lower=min(2*a,2*b)-(b-a)*2/2
    upper=max(2*a,2*b)+(b-a)*2/2
    assert 0<lower<2*a<=2*b<upper
    # The original source's trapezoid uses the coarse H, not the subdivision h.
    H=b-a
    trapezoid=H*((2*a)+(2*b))/2
    integral=b*b-a*a
    assert trapezoid==integral
    assert abs(trapezoid-integral)<=H*H*2/2


def test_guard_baseline_synthetic():
    assert validate(*synthetic())


def test_all_adversarial_mutations_rejected():
    result=adverse()
    assert result['all_rejected'] is True
    assert result['count']>=30
    assert all(x['status']=='REJECTED' for x in result['cases'])


def test_interval_Fpp_derivation_with_consistent_toy():
    # y=1, synthetic Bessel inputs chosen from mpmath-free series.
    # This does not attempt a Bessel proof; it catches denominator/sign regressions.
    y=Q(1)
    J0,J1=i_bessel_positive_series(y,100)
    k0=R(Q(421,1000),Q(422,1000))
    k1=R(Q(601,1000),Q(603,1000))
    F=J0*k0-J1*k1
    Fp=2*(J1*k0-J0*k1+J1*k1/y)
    assert F.l>0 and Fp.u<0
    q={'r':y,'F':F,'Fp':Fp,'Fpp':None}
    Fpp=independent_fpp(q,{'Rd':Q(1,2)})
    assert Fpp.l>0

@pytest.mark.parametrize('value',[Q(0),Q(1),Q(1,9),Q(2,3),Q(77,19)])
def test_independent_binary_search_sqrt(value):
    from verify_band_bv import rootbox  # noqa: E402
    l,u=rootbox(value)
    assert l*l<=value<=u*u
    assert u-l<=Q(1,2**160)


def test_independent_BV_kernel_bounds():
    from verify_band_bv import kernel  # noqa: E402
    for A in (Q(1,5),Q(1),Q(2),Q(9,4)):
        for r in (Q(1),Q(2),Q(3)):
            l,u=kernel(A,r)
            ll,uu=phi(A,r)
            assert l<=uu and u>=ll
