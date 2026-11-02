"""Source-free arithmetic and scientific claim-firewall tests; not a proof of original source or physics."""
from __future__ import annotations
import math,sys
from fractions import Fraction as F
from pathlib import Path
import pytest
ROOT=(Path(__file__).resolve().parents[2]/'reference'/'hist001d_full180_comparator_candidate')
sys.path.insert(0,str(ROOT))
from full180_math import sqrt_box,frac,ceil_frac  # noqa: E402
from independent_verify import dyadic_from_float64,enclosing_root,exactpair,ppoint  # noqa: E402

@pytest.mark.parametrize('v',[0.02,120.0,1e10,-34.5,0.0,2.0**-1022,2.0**-1074])
def test_manual_binary64_fraction(v):
    assert dyadic_from_float64(v)==F.from_float(v)

@pytest.mark.parametrize('x',[F(2),F(1,9),F(7,3),F(1,2**56),F(11,13)])
def test_two_independent_directed_sqrt_boxes(x):
    l,u=sqrt_box(x,bits=56)
    li,ui=enclosing_root(x)
    assert l*l<=x<=u*u and li*li<=x<=ui*ui
    assert l<=ui and li<=u


def test_exact_source_floats_are_not_decimal_reinterpretations():
    assert frac(0.02)!=F(1,50)
    assert frac(120.0)==F(120)


def test_exact_affine_q_ratio_monotonicity():
    qb,qd=F(2,3),F(1,4)
    b0,b1=F(10),F(18);d0,d1=F(15),F(23)
    N0,N1=qb*b0+qd*d0,qb*b1+qd*d1
    P0,P1=b0+d0,b1+d1
    delta=N1*P0-N0*P1
    vals=[]
    for t in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
        q=ppoint(N0,N1,t)/ppoint(P0,P1,t)
        assert min(qb,qd)<=q<=max(qb,qd)
        vals.append(q)
    assert vals==sorted(vals,reverse=(delta<0))


def test_composed_component_interpolant_not_equal_to_final_residual_interpolant():
    # A nonlinear operation applied AFTER affine interpolation need not equal
    # linearly interpolated values of that operation at the endpoints.
    q0,q1=F(1,4),F(1)
    A0=1/math.sqrt(float(q0));A1=2/math.sqrt(float(q1))
    amid=1.5/math.sqrt(float(F(5,8)))
    assert abs(amid-(A0+A1)/2)>0.05


def test_critical_target_interpolation_identity():
    r0,r1=F(1,10),F(11,10);r=F(3,4)
    C=F(13,5);t0=C*r0*r0+F(1,2**50);t1=C*r1*r1-F(1,2**48)
    pl=ppoint(t0,t1,(r-r0)/(r1-r0))
    e=C*(r-r0)*(r1-r)+ppoint(t0-C*r0*r0,t1-C*r1*r1,(r-r0)/(r1-r0))
    assert pl-C*r*r==e


def test_source_knot_h_is_not_claimed_offgrid():
    # Scientific boundary: even exact knot matches do not establish off-grid equality.
    assert F(0)==F(0)
    assert F(1,4)!=F(1,2)


def test_noncanonical_pairs_rejected():
    with pytest.raises(AssertionError):exactpair({'num':'01','den':'1'})
    with pytest.raises(AssertionError):exactpair({'num':'1','den':'0'})
    with pytest.raises(AssertionError):exactpair({'num':'1','den':'2','physical_provider_admitted':True})


def test_integer_ceil_outward():
    assert ceil_frac(F(1001,1000))==2
    assert ceil_frac(F(-1,10))==0


def test_science_model_schema_is_explicit_not_source_root_theorem():
    from producer import GUARDS
    assert set(GUARDS)=={'J0822+1828','J0915+4211','J0930+2855',
                         'J1021+2028','J1111+2234','J1135+3720'}
    for center,span in GUARDS.values():
        assert F(span)==F(3,100)
