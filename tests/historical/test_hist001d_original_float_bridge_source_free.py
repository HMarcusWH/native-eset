"""Finite source-free identities only. Does not replay confidential March arrays."""
import sys
from fractions import Fraction as Q
from pathlib import Path
import pytest

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE/'reference'/'hist001d_original_float_bridge_candidate'))
from float_bridge import rounded,float_sample_H,float_sample_root,rational_sample_root  # noqa: E402
from independent_float_check import floor_sqrt_different  # noqa: E402
from claim_guard import validate_claims  # noqa: E402

@pytest.mark.parametrize('k',[0,1,2,3,10,20])
def test_nearest_float_ties_even(k):
    # exact midpoint from 1 to next up is 1+2^-53 (rounds to 1)
    # next midpoint (between 1+2^-52 and 1+2*2^-52) rounds to the even second successor.
    assert rounded(Q(1)+Q(1,2**53))==Q(1)
    assert rounded(Q(1)+Q(3,2**53))==Q(1)+Q(1,2**51)
    assert rounded(Q(1)+Q(1,2**(54+k)))==Q(1)

@pytest.mark.parametrize('x',[Q(1),Q(2),Q(7,11),Q(5,16),Q(2**111+37,2**107+19)])
def test_independent_sqrt_bracket(x):
    lo,hi=floor_sqrt_different(x)
    assert lo**2<=x<hi**2
    assert hi-lo==Q(1,2**120)

@pytest.mark.parametrize('a,b,c,d',[(Q(1),Q(3),Q(10),Q(-10)),(Q(1,3),Q(4,3),Q(5,2),Q(-3,4)),(Q(10),Q(12),Q(9),Q(-13))])
def test_exact_sampled_root(a,b,c,d):
    root=rational_sample_root(a,b,c,d)
    assert a<root<b
    assert c+(d-c)*(root-a)/(b-a)==0
    assert abs(float_sample_root(a,b,c,d)-root)<Q(1,10**12)

def test_exact_float_order_produces_source_path():
    R=Q.from_float(0.6902793296089386)
    B=Q.from_float(15388947150.616577)
    D=Q.from_float(5884570624.784004)
    S=Q.from_float(12920638220.460384)
    pi=Q.from_float(float.fromhex('0x1.921fb54442d18p+1'))
    sigma=Q.from_float(float.fromhex('0x1.123aeb5f7ce8dp+32'))
    exact=float_sample_H(B,D,S,R,pi,sigma)
    assert isinstance(exact,Q)
    assert float(exact)==float(float(float(B)+float(D)+float(S))-(float(pi)*float(R)**2*float(sigma)))

def test_invalid_exact_root_flat():
    with pytest.raises(ValueError):rational_sample_root(Q(1),Q(2),Q(5),Q(5))

@pytest.mark.parametrize('v',[Q(-1),Q(-1,8)])
def test_negative_sqrt_rejected(v):
    with pytest.raises(ValueError):floor_sqrt_different(v)

def test_claim_guard_rejects_missing_required_fields():
    with pytest.raises(ValueError):validate_claims({})
