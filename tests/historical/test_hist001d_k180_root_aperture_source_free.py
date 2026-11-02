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
    # M(r)=r^2, a=1, b=5, A=3. P=4+9 ln(3) by exact calculus.
    # This is a numerical regression only; the actual proof is in the method note.
    from mpmath import mp
    with mp.workdps(60):
        a,b,A=mp.mpf(1),mp.mpf(5),mp.mpf(3)
        direct=mp.quad(lambda r:2*r,[a,A])+mp.quad(lambda r:2*r*(1-mp.sqrt(1-(A/r)**2)),[A,b])
        ub=mp.sqrt(1-(A/b)**2)
        ip= b*b*(1-ub)-a*a + mp.quad(lambda u:(A/mp.sqrt(1-u*u))**2,[0,ub])
        assert abs(direct-ip)<mp.mpf('1e-45')
        assert abs(ip-(4+9*mp.log(3)))<mp.mpf('1e-45')


def test_chain_rule_second_derivative_synthetic():
    # r=A/sqrt(1-u²), for M=r², d²/du² M(r(u))=2 A²(1+3u²)/(1-u²)³.
    from sympy import symbols,sqrt, simplify,diff,Rational
    A,u=symbols('A u',positive=True)
    r=A/sqrt(1-u*u)
    rp= A*u/(1-u*u)**Rational(3,2)
    rpp=A*(1+2*u*u)/(1-u*u)**Rational(5,2)
    assert simplify(2*rp*rp+2*r*rpp-2*A*A*(1+3*u*u)/(1-u*u)**3)==0
    assert simplify(diff(r*r,u,2)-2*rp*rp-2*r*rpp)==0

@pytest.mark.parametrize('x', [Q(2,3),-Q(2,3),Q(10**30,7),-Q(10**30,7),Q(0)])
def test_outward_integer_envelope(x):
    assert floor(x)<=x<=ceil(x)

@pytest.mark.parametrize('bad',[-Q(1),Q(0)])
def test_u_rejects_invalid_A(bad):
    with pytest.raises(ValueError):projected_u(bad,Q(3))
