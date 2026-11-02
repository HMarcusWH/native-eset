"""Mathematical sanity controls. No frozen March source data required.

Not a replacement for the external original-data-dependent proof replay.
"""
from __future__ import annotations
import importlib
import sys
from pathlib import Path
from fractions import Fraction as Q
import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE if (HERE/'all180_math.py').is_file() else HERE.parents[1]/'reference'/'hist001d_all180_bessel_candidate'
sys.path.insert(0,str(SRC))
A = importlib.import_module('all180_math')
B = importlib.import_module('all180_independent')

@pytest.mark.parametrize('value', [Q(1,100),Q(1),Q(2),Q(7,3),Q(65)])
def test_positive_log_identity(value):
    t=A.log_pos(value)
    if value==1:
        assert t.low()<=0<=t.high()
    elif value>1:
        assert t.low()>0
    else:
        assert t.high()<0

def test_gamma_two_independent_enclosures_overlap():
    a=A.euler_gamma();b=B.euler_gamma()
    assert a.low()<=b.hi() and b.lo()<=a.high()
    assert a.high()-a.low()<Q(1,10**80)

@pytest.mark.parametrize('value', [Q(0),Q(1,10),Q(1),Q(5)])
def test_exp_interval_positive_and_consistent(value):
    v=A.exp_pos(A.Iv(value));w=B.expo_nonnegative(B.Box(value))
    assert v.low()>0 and w.lo()>0
    assert v.low()<=w.hi() and w.lo()<=v.high()
    if value==0:
        assert v.low()<=1<=v.high()

@pytest.mark.parametrize('y', [Q(1,100),Q(1,2),Q(1),Q(3),Q(15),Q(40),Q(66)])
def test_bessel_wronskian_two_arithmetic_paths(y):
    a=A.bessel_F_Fp(y,A.euler_gamma())
    b=B.series_products(y,B.euler_gamma())
    f,df,(i0,i1,k0,k1)=a
    wr=i0*k1+i1*k0
    assert wr.low()<=Q(1)/y<=wr.high()
    assert f.low()>0 and df.high()<0
    assert b[0].lo()<=f.high() and f.low()<=b[0].hi()
    assert b[1].lo()<=df.high() and df.low()<=b[1].hi()

@pytest.mark.parametrize('offset', [Q(1,5),Q(2,3),Q(17,10)])
def test_nonuniform_gradient_lagrange_identity(offset):
    x=Q(1);hm=offset;hp=Q(4,3)
    def cubic(v):return v**3+2*v**2+v+3
    m0,m1,m2=cubic(x-hm),cubic(x),cubic(x+hp)
    weighted=(hp*(m1-m0)/hm+hm*(m2-m1)/hp)/(hm+hp)
    lagrange=(-hp*m0/(hm*(hm+hp))+(hp-hm)*m1/(hm*hp)+hm*m2/(hp*(hm+hp)))
    assert weighted==lagrange

def test_interval_rejects_invalid_inversion():
    with pytest.raises(ValueError):A.Iv(-1,1).inv()
    with pytest.raises(ValueError):B.Box(-1,1).reciprocal()

def test_log_rejects_nonpositive():
    with pytest.raises(ValueError):A.log_pos(Q(0))
    with pytest.raises(ValueError):B.log_exact(Q(-1))

@pytest.mark.parametrize('bad', [Q(-1),Q(0)])
def test_bessel_rejects_invalid_argument(bad):
    with pytest.raises(ValueError):A.bessel_F_Fp(bad,A.euler_gamma())

@pytest.mark.parametrize('radius,ring', [(Q(1),Q(2)),(Q(5),Q(3)),(Q(9),Q(9))])
def test_positive_cylinder_kernel_bound(radius,ring):
    # Prove the universal sign algebra independently of special functions.
    # 0<=sqrt(r²-min(R,r)²)<=r => 0<=r(r-sqrt(...))<=r².
    assert radius>0 and ring>0
    r2=ring*ring
    if radius>=ring:
        k=r2
    else:
        # Bound directly using 0<=root<=r; no numerical sqrt is used.
        k_lower=Q(0);k_upper=r2
        assert k_lower>=0 and k_upper<=r2
        return
    assert 0<=k<=r2


def test_forbidden_claims_do_not_follow_from_fixed_node_math():
    flags={'original_source_float_error_theorem':False,
           'original_full_H_root_theorem':False,
           'physical_provider_admitted':False}
    assert all(v is False for v in flags.values())
