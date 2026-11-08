"""Synthetic, source-free mathematical identities; not six-lens certification."""
from fractions import Fraction as Q
from pathlib import Path
import sys
import pytest

SOURCE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_k180_root_aperture_candidate'
sys.path.insert(0,str(SOURCE))
from root_aperture_certifier import sqrt_outward,projected_u,cylinder_phi,ceil,floor  # noqa: E402
from all180_math import Iv  # noqa: E402


def test_sqrt_rational_inclusion():
    for x in [Q(0),Q(1,13),Q(1,2),Q(2),Q(25,36),Q(5)]:
        s=sqrt_outward(Iv(x))
        assert s.low()**2<=x<=s.high()**2
        assert s.low()>=0

@pytest.mark.parametrize('A,r',[(Q(1),Q(1)),(Q(7,2),Q(3)),(Q(1),Q(5)),(Q(6),Q(5)),(Q(3),Q(5))])
def test_weight_in_0_1_and_u(A,r):
    phi=cylinder_phi(A,r)
    assert 0<=phi.low()<=phi.high()<=1
    if r>A:
        assert 0<=projected_u(A,r).low()<=projected_u(A,r).high()<1
    else:
        assert projected_u(A,r).low()==projected_u(A,r).high()==0


def test_phi_decreases_with_r():
    A=Q(3)
    values=[cylinder_phi(A,Q(r)) for r in [Q(1),Q(2),Q(3),Q(4),Q(6),Q(10)]]
    assert all(values[i].low()>=values[i+1].high() for i in range(len(values)-1))


def test_finite_cylinder_quadratic_integral_identity():
    # For M(r)=r^2, [a,b]=[1,5], A=3, exact u_b=4/5.
    # Both the direct radial anti-derivative and transformed formula give
    # 4+9*log(3), without requiring an external numerical integrator.
    from math import log, isclose
    a,b,A=Q(1),Q(5),Q(3)
    ub=Q(4,5)
    boundary=b*b*(1-ub)-a*a
    transformed_log_ratio=(1+ub)/(1-ub)
    assert boundary==Q(4)
    assert transformed_log_ratio==Q(9)
    transformed=float(boundary)+float(A*A)/2*log(float(transformed_log_ratio))
    direct_antiderivative=4+9*log(3)
    assert isclose(transformed,direct_antiderivative,rel_tol=1e-14,abs_tol=1e-14)


def test_chain_rule_second_derivative_synthetic():
    # Exact rational identity: M(r)=r^2 and r=A/sqrt(1-u^2).
    # r'^2=A^2*u^2/(1-u^2)^3;
    # r*r''=A^2*(1+2*u^2)/(1-u^2)^3.
    for A in [Q(1),Q(3),Q(11,2)]:
        for u in [Q(0),Q(1,5),Q(2,3),Q(7,8)]:
            denom=(1-u*u)**3
            chain=2*(A*A*u*u/denom+A*A*(1+2*u*u)/denom)
            direct=2*A*A*(1+3*u*u)/denom
            assert chain==direct

@pytest.mark.parametrize('x', [Q(2,3),-Q(2,3),Q(10**30,7),-Q(10**30,7),Q(0)])
def test_outward_integer_envelope(x):
    assert floor(x)<=x<=ceil(x)

@pytest.mark.parametrize('bad',[-Q(1),Q(0)])
def test_u_rejects_invalid_A(bad):
    with pytest.raises(ValueError):projected_u(bad,Q(3))
