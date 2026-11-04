"""Source-free exact-rational math and fail-closed contract regressions."""
from __future__ import annotations
import runpy
from pathlib import Path
from fractions import Fraction as F
import pytest
SOURCE=Path(__file__).resolve().parents[2]/"reference/hist001d_k180_exact_count_candidate"
contract=runpy.run_path(str(SOURCE/"knot_count_contract.py"))
independent=runpy.run_path(str(SOURCE/"independent_knot_verify.py"))

@pytest.mark.parametrize("a,b,sign", [
    ("1", "2", 1), ("-2", "-1", -1), ("-1", "1", 0),
    ("0", "1", 0), ("-1", "0", 0), ("1/4", "3/4", 1),
    ("-3/4", "-1/4", -1), ("0", "0", 0),
])
def test_signed_interval(a,b,sign):
    assert contract["signed"](a,b)==sign

@pytest.mark.parametrize("spans,left,right", [
    ([('0','1'),('1','2')],'0','2'),
    ([('1/7','3/7'),('3/7','2')],'1/7','2'),
    ([('7/9','1')],'7/9','1'),
])
def test_exact_coverage(spans,left,right):
    assert contract["covers"](spans,left,right,'synthetic') is None

@pytest.mark.parametrize("spans,left,right", [
    ([('0','1'),('1.1','2')],'0','2'),
    ([('0','1'),('0.9','2')],'0','2'),
    ([('0','1')],'0','2'),
    ([('0','0')],'0','0'),
    ([], '0','1'),
])
def test_invalid_coverage_rejected(spans,left,right):
    with pytest.raises(ValueError): contract["covers"](spans,left,right,'synthetic')

@pytest.mark.parametrize("lo,hi", [
    ("2", "1"), ("-1", "-2"),
])
def test_inverted_interval_rejected(lo,hi):
    with pytest.raises(ValueError): contract["signed"](lo,hi)

@pytest.mark.parametrize("a,b", [(1,1),(2,1),(-1,2)])
def test_bad_derivative_geometry(a,b):
    with pytest.raises(ValueError): independent["deriv_kernel"](F(a),F(b))

@pytest.mark.parametrize("x", [F(0),F(1,8),F(1,2),F(1),F(81,16)])
def test_independent_sqrt_bounds(x):
    val=independent["sqrtbox"](independent["I"](x))
    assert val.lo()*val.lo() <= x <= val.hi()*val.hi()

@pytest.mark.parametrize("x", [F(0),F(1,100),F(1,5),F(1,2),F(5,4)])
def test_independent_atan_ranges(x):
    import math
    box=independent["arctanbox"](independent["I"](x))
    actual=math.atan(float(x))
    assert float(box.lo()) - 1e-12 <= actual <= float(box.hi()) + 1e-12

@pytest.mark.parametrize("a,b,A", [
    (1,3,4),(1,4,2),(1,4,F(1,2)),
    (1,5,5),(2,10,3)
])
def test_cylinder_mass_kernel_integral_range(a,b,A):
    box=independent["cylinder_cell"](F(A),F(a),F(b))
    assert F(0)<=box.lo()<=box.hi()<=F(b)-F(a)

@pytest.mark.parametrize("a,b,A", [(1,5,F(1,2)),(1,5,2),(3,7,3),(3,7,8)])
def test_positive_derivative_kernel_integral(a,b,A):
    box=independent["weight_omega"](F(A),F(a),F(b))
    assert box.lo()>=0 and box.hi()>=box.lo()

@pytest.mark.parametrize("a,b,A", [(1,2,3),(1,2,1),(1,5,F(1,2))])
def test_full_weight_at_saturation_and_subsaturation(a,b,A):
    box=independent["cylinder_cell"](F(A),F(a),F(b))
    if A >= b: assert box.lo()==box.hi()==F(b)-F(a)
    else: assert box.lo() > 0


def test_exact_six_lens_claim_and_nonpromotion_constants():
    assert contract['COUNTS']==(3,2,3,3,2,3)
    assert sum(contract['COUNTS'])==16
    assert contract['ORIGINAL_SOURCE_SHA']=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'


def test_fraction_interval_arithmetic():
    I=independent['I']
    a=I(F(1,3));b=I(F(1,2));c=a+b
    assert c.lo()<=F(5,6)<=c.hi()
    d=I(2)/I(3)
    assert d.lo()<=F(2,3)<=d.hi()
    e=I(-2)*I(3)
    assert e.lo()<=F(-6)<=e.hi()
