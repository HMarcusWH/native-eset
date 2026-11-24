"""Tests of exact rational identities, not an original source replay."""
from fractions import Fraction as Q
from math import comb
import pytest
from pathlib import Path
import sys
SOURCE=Path(__file__).resolve().parents[2]/"reference"/"hist001d_k180_saturation_candidate"
sys.path.insert(0,str(SOURCE))
from conservation_identity import (  # noqa: E402
    trap_weights,nonuniform_stencil,exact_nonuniform_telescoping_defect,
    bump_integral_coefficient,
)

@pytest.mark.parametrize('scale', [Q(1),Q(1,3),Q(3,2),Q(17,10),Q(100)])
def test_uniform_telescoping_exact(scale):
    r=[Q(1,50)+i*scale for i in range(12)]
    m=[Q(7)+i**3*Q(3,7)-Q(11)*i**2/9 for i in range(12)]
    integral=sum((w*d for w,d in zip(trap_weights(r),nonuniform_stencil(r,m))),Q())
    assert integral == m[-1]-m[0]
    assert exact_nonuniform_telescoping_defect(r,m)==0

@pytest.mark.parametrize('r,m', [
    ([0,1,3],[2,5,19]),
    ([Q(1,50),Q(7,10),Q(11,7),Q(120)],[1,4,3,16]),
    ([2,6,13,14,42],[1,3,9,2,18]),
    ([Q(1),Q(11,10)],[2,25]),
    ([1,2,3,5,8,13],[1,2,7,2,11,7]),
])
def test_nonuniform_defect_is_exact(r,m):
    r=list(map(Q,r));m=list(map(Q,m))
    integral=sum((w*d for w,d in zip(trap_weights(r),nonuniform_stencil(r,m))),Q())
    assert integral-m[-1]+m[0] == exact_nonuniform_telescoping_defect(r,m)

@pytest.mark.parametrize('a,b',[(Q(1,50),Q(1,2)),(Q(2,3),Q(9,8)),(Q(11),Q(20)),(Q(1,5),Q(19,11))])
def test_bump_integral_rational_identity(a,b):
    h=b-a; coefficient=Q(22,7)
    expr=sum(((-1)**j*comb(4,j)*(a*a/Q(5+j)+2*a*h/Q(6+j)+h*h/Q(7+j)) for j in range(5)),Q())
    assert bump_integral_coefficient(a,b,coefficient)==coefficient*h**9*expr
    assert bump_integral_coefficient(a,b,coefficient)>0

@pytest.mark.parametrize('r',[[1],[1,1,2],[2,1],[1,2,2]])
def test_reject_invalid_mesh(r):
    with pytest.raises(ValueError): trap_weights(r)

@pytest.mark.parametrize('a,b,c',[(1,1,1),(1,2,0),(0,2,1),(-1,2,3),(1,0,2)])
def test_reject_invalid_bump(a,b,c):
    with pytest.raises(ValueError): bump_integral_coefficient(a,b,c)

def test_source_free_does_not_claim_physical_validity():
    import inspect
    from conservation_identity import bump_integral_coefficient
    assert 'physical' not in inspect.getsource(bump_integral_coefficient).lower()
    assert bump_integral_coefficient(Q(1,50),Q(3,2),Q(22,7))>0
