"""Synthetic source-free exact-dyadic and stencil identities, not original-data tests."""
from fractions import Fraction as Q
from math import sqrt
from pathlib import Path
import struct
import sys
import pytest

CODE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_upstream_bessel_candidate'
sys.path.insert(0,str(CODE))
from independent_stencil_check import decode,source_stencil,ceil  # noqa: E402

@pytest.mark.parametrize('q',[0.0,-0.0,0.02,0.6902793296089386,-5.5,100000.0,2.5e-300])
def test_decode_exact_binary64(q):
    assert decode(struct.pack('>d',q))==Q.from_float(q)

@pytest.mark.parametrize('q',[float('inf'),-float('inf'),float('nan')])
def test_decode_rejects_nonfinite(q):
    with pytest.raises(ValueError):decode(struct.pack('>d',q))

def test_decode_bad_length():
    with pytest.raises(ValueError):decode(b'bad')

def test_gradient_uniform_affine_exact():
    xs=[Q(i,5) for i in range(180)]
    ms=[7*x+Q(3,11) for x in xs]
    assert all(v==Q(7) for v in source_stencil(xs,ms))

def test_gradient_nonuniform_quadratic_interior_exact():
    xs=[Q(i,3)+Q(i*i,100) for i in range(180)]
    m=[x*x for x in xs]
    d=source_stencil(xs,m)
    for i in range(1,179):
        # np.gradient 3-point nonuniform quadratic derivative exact.
        assert d[i]==2*xs[i]
    assert d[0]==xs[0]+xs[1]
    assert d[-1]==xs[-1]+xs[-2]

def test_gradient_nonuniform_cubic_error_identity():
    xs=[Q(i,7)+Q(i*i,1000) for i in range(180)]
    m=[x**3 for x in xs]
    d=source_stencil(xs,m)
    for i in range(1,179):
        hm=xs[i]-xs[i-1];hp=xs[i+1]-xs[i]
        assert d[i]-3*xs[i]**2==hm*hp

@pytest.mark.parametrize('n',[1,2,3,10,180])
def test_gradient_rejects_invalid_dimensions(n):
    xs=[Q(k,3) for k in range(n)];ms=[Q(k,3) for k in range(n)]
    if n!=180:
        with pytest.raises(ValueError):source_stencil(xs,ms)
    else:
        assert source_stencil(xs,ms)[0]==1

def test_gradient_rejects_reversed_mesh():
    xs=[Q(i) for i in range(180)];xs[50]=xs[49]
    with pytest.raises(ValueError):source_stencil(xs,xs)

def test_Cylinder_kernel_between_zero_and_one_numeric_sanity():
    # Floating-point illustration only; actual bound is elementary analytic.
    for A in [0.,0.001,.02,.2,1.,4.,120.,240.]:
        for r in [.02,.5,1.,2.5,100.,120.]:
            phi=1. if r<=A else 1.-sqrt(1.-(A/r)**2)
            assert 0<=phi<=1.0+1e-14

def test_positive_weights_L1_bounds_all_nonnegative_phi():
    w=[Q(1,3),Q(7,8),Q(3,2)]
    errors=[Q(-1,7),Q(2,5),Q(-11,2)]
    upper=sum((a*abs(e) for a,e in zip(w,errors)),Q())
    for phi in [[Q(0),Q(0),Q(0)],[Q(1),Q(1),Q(1)],
                [Q(1,10),Q(2,3),Q(1)],[Q(1),Q(2,3),Q(1,10)]]:
        assert abs(sum((x*y*z for x,y,z in zip(w,errors,phi)),Q()))<=upper

def test_outward_microunit_ceiling():
    for frac,exp in [(Q(0),0),(Q(1,10**7),1),(Q(1,10**6),1),(Q(1001,10**9),2)]:
        assert ceil(frac*10**6)==exp
