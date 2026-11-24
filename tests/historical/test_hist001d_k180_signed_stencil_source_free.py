"""Source-free exact-rational mathematical tests: no external original arrays."""
from fractions import Fraction as F
import sys
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_k180_signed_stencil_candidate'
sys.path.insert(0,str(HERE))
from finite_difference_bias import phi_interval,signed_node_interval,from_pair  # noqa: E402
from verify_signed_bias import decoded_binary64,sqrt_outward,phi_box,box_sum  # noqa: E402

@pytest.mark.parametrize('A,r',[(F(0),F(5)),(F(1),F(5)),(F(3),F(5)),(F(4),F(5)),(F(5),F(5)),(F(7),F(5))])
def test_cylinder_kernel_bounds(A,r):
    lower,upper=phi_interval(A,r)
    l2,u2=phi_box(A,r)
    assert F(0)<=lower<=upper<=1
    assert F(0)<=l2<=u2<=1
    assert not (lower>u2 or upper<l2)
    if A==0:assert lower==upper==0
    if A>=r:assert lower==upper==1
    if A==3 and r==5:assert lower<=F(1,5)<=upper

@pytest.mark.parametrize('v', [F(0),F(1,9),F(7,16),F(1),F(2,7)])
def test_independent_sqrt_squared_enclosures(v):
    lo,hi=sqrt_outward(v,bits=32)
    assert lo*lo<=v<=hi*hi
    assert hi-lo<=F(1,1<<32)

@pytest.mark.parametrize('raw,q',[
(bytes.fromhex('3ff0000000000000'),F(1)),
(bytes.fromhex('bfe0000000000000'),F(-1,2)),
(bytes.fromhex('0000000000000001'),F(1,1<<1074)),
(bytes.fromhex('7fefffffffffffff'),F((1<<53)-1,1)*2**971),
(bytes.fromhex('0000000000000000'),F(0))])
def test_manual_binary64_decode(raw,q):
    assert decoded_binary64(raw)==q

def test_conservative_signed_mixed_stencil_quadrature():
    r=[F(1),F(2),F(4)];w=[F(1,2),F(1),F(1,2)]
    e=[(F(10),F(10)),(F(-7),F(-6)),(F(2),F(3))]
    for a,b in [(F(0),F(0)),(F(2),F(2)),(F(4),F(4)),(F(1),F(4))]:
        pl,pu=signed_node_interval(a,b,r,w,e)
        ql,qu=box_sum(r,w,e,a,b)
        assert pl<=qu and ql<=pu
        assert pl<=pu
    assert signed_node_interval(F(0),F(0),r,w,e)==(F(0),F(0))
    assert signed_node_interval(F(4),F(4),r,w,e)==(F(-1),F(1,2))

def test_rational_pair_precision():
    assert from_pair(['27','64'])==F(27,64)
    assert from_pair(['5','3'])==F(5,3)

@pytest.mark.parametrize('bad', [F(-1,4),F(6,5)])
def test_independent_sqrt_rejects_invalid_domain(bad):
    with pytest.raises(ValueError):sqrt_outward(bad)

@pytest.mark.parametrize('a,b',[(F(-1),F(1)),(F(3),F(2))])
def test_signed_node_band_rejects_inverted_range(a,b):
    with pytest.raises(ValueError):signed_node_interval(a,b,[F(1)],[F(1)],[(F(1),F(1))])
