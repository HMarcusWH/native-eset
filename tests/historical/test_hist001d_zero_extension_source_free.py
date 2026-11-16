"""Pure mathematical/claim/coverage tests without access to frozen March data."""
from __future__ import annotations
import math
from fractions import Fraction as F
from pathlib import Path
from runpy import run_path
import pytest
SOURCE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_k180_zero_extension_candidate'
# This checkout has several historical modules named claim_guard.py. Resolve
# THIS one by exact path to avoid sys.modules import-cache collisions in CI.
_guard=run_path(str(SOURCE/'claim_guard.py'))
count_sign_flips=_guard['count_sign_flips']
EXTRA_INDEX=_guard['EXTRA_INDEX']
BASE_COUNTS=_guard['BASE_COUNTS']
EXPECTED_COUNTS=_guard['EXPECTED_COUNTS']
ceil=_guard['ceil']
floor=_guard['floor']

@pytest.mark.parametrize('old,new,witness',[
    ([(0,-1),(89,-1),(118,1),(128,1)],[(0,-1),(25,1),(89,-1),(118,1),(128,1)],25),
    ([(0,-1),(92,-1),(114,1),(128,1)],[(0,-1),(33,1),(92,-1),(114,1),(128,1)],33),
    ([(0,-1),(83,-1),(107,1),(128,1)],[(0,-1),(29,1),(83,-1),(107,1),(128,1)],29),
])
def test_one_extra_positive_sign_adds_two_disjoint_ivt_brackets(old,new,witness):
    assert witness in EXTRA_INDEX.values()
    assert count_sign_flips(old)==1
    assert count_sign_flips(new)==3
    loc=[i for i,v in enumerate(new) if v[0]==witness][0]
    assert loc>0 and loc<len(new)-1
    assert new[loc-1][1]==-1 and new[loc][1]==1 and new[loc+1][1]==-1
    # The two open intervals only share a strictly nonzero positive endpoint.
    assert new[loc-1][0]<witness<new[loc+1][0]

@pytest.mark.parametrize('bad',[
    [(0,-1),(0,1),(128,-1)],
    [(0,-1),(12,0),(128,1)],
    [(0,-1),(45,1),(40,-1),(128,1)],
    [(1,-1),(128,1)],
    [(0,-1),(127,1)],
    [(0,False),(128,1)],
    [(0,-1),(129,1)],
    [(0,-1)],
])
def test_malformed_sign_coverage_fails_closed(bad):
    with pytest.raises(ValueError):count_sign_flips(bad)

@pytest.mark.parametrize('v', [F(3,2),F(19,5),F(-7,3),F(-11,2),F(0)])
def test_exact_rational_outward_rounding(v):
    assert F(floor(v))<=v<=F(ceil(v))
    assert ceil(v)-floor(v)<=1

def test_expected_six_lens_lower_bounds():
    assert tuple(BASE_COUNTS)==(1,2,3,1,2,1)
    assert tuple(EXPECTED_COUNTS)==(3,2,3,3,2,3)
    assert sum(BASE_COUNTS)==10 and sum(EXPECTED_COUNTS)==16

def phi(A,r):
    return 1.0 if A>=r else 1-math.sqrt(1-A*A/(r*r))

def phi_aperture_derivative(A,r):
    return 0.0 if A>r else A/(r*math.sqrt(r*r-A*A))

@pytest.mark.parametrize('r', [F(3,2),F(5,2),F(17,3)])
def test_kernel_continuity_but_one_sided_derivative_singularity(r):
    x=float(r)
    assert phi(x,x)==1.0
    previous=0
    for n in (4,6,8,10):
        v=phi_aperture_derivative(x*(1-10**(-n)),x)
        assert v>previous
        previous=v
    assert phi_aperture_derivative(x*1.001,x)==0

def test_discontinuous_derivative_rules_out_global_smooth_interval_newton():
    r=F(2);A=F(2)
    assert phi(float(A),float(r))==1
    assert phi_aperture_derivative(2.1,2)==0
    assert phi_aperture_derivative(1.99999,2)>100
