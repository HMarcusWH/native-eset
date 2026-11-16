"""Source-free targeted Peano/IVT arithmetic and mixed-leaf origin regressions.

No source-frozen March arrays, Bessel result receipts or observational data.
"""
from fractions import Fraction as F
from pathlib import Path
import sys
import pytest

REF=Path(__file__).resolve().parents[2]/'reference'
sys.path.insert(0,str(REF/'hist001d_k180_targeted_candidate'))
sys.path.insert(0,str(REF/'hist001d_k180_inter_node_candidate'))
sys.path.insert(0,str(REF/'hist001d_k180_cancel_aware_candidate'))
sys.path.insert(0,str(REF/'hist001d_k180_bessel_integral_candidate'))
from witness_contract import ceil,floor,span,require,EXPECTED_MIN_ZEROS,INDICES  # noqa: E402
from verify_targeted import canonical_active_leaf_set,jprim,Y,phi,sqrtx,W_upper  # noqa: E402
from affine_kernel import kernel_integral  # noqa: E402

@pytest.mark.parametrize('q,down,up',[(F(1,3),0,1),(F(-1,3),-1,0),
                                     (F(5),5,5),(F(-5),-5,-5),
                                     (F(7,2),3,4),(F(-7,2),-4,-3)])
def test_integer_outward_rounding(q,down,up):
    assert floor(q)==down and ceil(q)==up

@pytest.mark.parametrize('box,good',[(['1','2'],True),(['1/7','8/7'],True),
                                     (['1/3','1/3'],True),(['2','1'],False),
                                     (['0'],False),(['0','1','2'],False)])
def test_rational_interval_validation(box,good):
    if good:assert span(box)[0]<=span(box)[1]
    else:
        with pytest.raises(ValueError):span(box)

def test_mixed_refined_and_untouched_leaf_indices():
    # In a prior verifier, the dictionary-comprehension used a stale loop k
    # instead of the untouched integer key, causing all six false failures.
    active={11:(F(1),F(2),0),(24,'1','3'):(F(2),F(5,2),1),
            (24,'3','5'):(F(5,2),F(3),1),39:(F(3),F(4),0)}
    ids=canonical_active_leaf_set(active)
    assert ids=={(11,'1','2',0),(24,'2','5/2',1),(24,'5/2','3',1),(39,'3','4',0)}

def test_root_witness_indices_and_distinct_count():
    signs=((-1,-1,1,1),(-1,1,-1),(1,-1,1,-1),(-1,-1,1,1),(-1,1,-1,-1),(-1,-1,1,1))
    assert len(signs)==len(EXPECTED_MIN_ZEROS)==len(INDICES)==6
    assert [sum(s[i]!=s[i-1] for i in range(1,len(s))) for s in signs]==list(EXPECTED_MIN_ZEROS)
    assert sum(EXPECTED_MIN_ZEROS)==10
    for ii in INDICES:
        assert ii[0]==0 and ii[-1]==128 and sorted(set(ii))==list(ii)

def test_disjoint_ivt_brackets_from_alternating_signs():
    xs=(F(1),F(2),F(3),F(4))
    signs=(-1,1,-1,1)
    brackets=[(xs[i-1],xs[i]) for i in range(1,len(xs)) if signs[i-1]!=signs[i]]
    assert len(brackets)==3
    assert all(a<b for a,b in brackets)
    assert all(brackets[i-1][1]<=brackets[i][0] for i in range(1,len(brackets)))

def test_nonzero_strict_sign_is_required():
    for x in (False,0,None):
        with pytest.raises(ValueError):require(x,'expected strict positive')

@pytest.mark.parametrize('val,expected',[(F(4,9),F(2,3)),(F(0),F(0)),(F(25,16),F(5,4))])
def test_independent_integer_square_root_enclosure(val,expected):
    v=sqrtx(Y(val))
    assert v.lower()<=expected<=v.upper()

@pytest.mark.parametrize('A', [F(2),F(3),F(4),F(9)])
def test_cylinder_saturation(A):
    a,b=F(1),F(2)
    assert A>=b
    j=jprim(A,a,b)
    assert j.lower()<=b-a<=j.upper()
    assert 0<=phi(A,a).lower()<=phi(A,a).upper()<=1

@pytest.mark.parametrize('A',[F(1,2),F(1),F(2),F(3),F(4)])
def test_cylinder_integral_independent_methods_overlap(A):
    a,b=F(1),F(5)
    u=jprim(A,a,b)
    v=kernel_integral(A,a,b)
    assert max(u.lower(),v.lower())<=min(u.upper(),v.upper())
    assert 0<=u.lower()<=u.upper()<=b-a

@pytest.mark.parametrize('Alo,Ahi,expected_zero',[(F(3),F(4),True),
                                                   (F(1),F(2),False)])
def test_positive_kernel_curvature_weight(Alo,Ahi,expected_zero):
    w=W_upper(Alo,Ahi,F(1),F(5))
    if expected_zero:
        # At 3..4 aperture the radial cell 1..5 is only partly saturated.
        assert w>0
    else:
        assert w>=0

def test_curvature_variation_zero_above_support():
    assert W_upper(F(5),F(6),F(1),F(4))==0

def test_mass_interpolation_quadratic_peano_shape():
    # For M(r)=r**2 on [a,b], (M-M_affine)=(r-a)(r-b).
    # Bound |M-Maffine| <= (max |M''|)/2*(b-a)^2/4 exactly.
    for a,b in ((F(1),F(2)),(F(0),F(5,7)),(F(2),F(13,3))):
        h=b-a;slope=a+b
        for k in range(9):
            r=a+h*F(k,8)
            error=r*r-(a*a+slope*(r-a))
            assert error==(r-a)*(r-b)
            assert abs(error)<=h*h/4
