"""Source-free mathematical and fail-closed tests for independent real-integral K0,K1."""
from fractions import Fraction as Q
from pathlib import Path
import sys
import pytest

SOURCE=Path(__file__).resolve().parents[2]/"reference"/"hist001d_k180_bessel_integral_candidate"
sys.path.insert(0,str(SOURCE))
from real_integral_bessel import X, exppos, logpos, I0I1, K0K1_integral, F_and_prime  # noqa: E402
from stencil_verify import parse64, scale_interval, minus, plus, maxabs  # noqa: E402

@pytest.mark.parametrize('q', [Q(0),Q(1,16),Q(1,3),Q(1),Q(4)])
def test_exp_positive_encloses_ordinary_rational_taylor(q):
    box=exppos(q)
    s=Q(1);term=Q(1)
    for k in range(1,180):
        term=term*q/k;s+=term
    # For x<=4, omitted terms from 180 onward are nonnegative and geometrically bounded.
    next_term=term*q/180
    tail=next_term/(1-q/181)
    assert box.lower()<=s and box.upper()>=s+tail

@pytest.mark.parametrize('q', [Q(1),Q(3,2),Q(2),Q(1,17),Q(12)])
def test_log_exp_consistency_at_rationals(q):
    lo,hi=logpos(q).lower(),logpos(q).upper()
    assert lo<=hi
    if q==1:assert lo<=0<=hi
    if q==2:assert lo>0

@pytest.mark.parametrize('y', [Q(1,1000),Q(1,5),Q(1),Q(5)])
def test_integral_bessel_wr_positivity_and_recurrence(y):
    a,b=I0I1(y)
    c,d,_=K0K1_integral(y)
    assert a.lower()>0 and b.lower()>0
    assert c.lower()>0 and d.lower()>0
    wr=a*d+b*c
    assert wr.lower()<=1/y<=wr.upper()
    f,df,_=F_and_prime(y)
    assert f.lower()>0 and df.upper()<0

@pytest.mark.parametrize('y', [Q(1,3),Q(3),Q(13)])
def test_bessel_integral_two_resolutions_intersect(y):
    import real_integral_bessel as method
    saved=method.H
    try:
        method.H=Q(1,32)
        f,df,_=method.F_and_prime(y)
        method.H=Q(1,64)
        ff,dd,_=method.F_and_prime(y)
        assert ff.lower()<=f.upper() and f.lower()<=ff.upper()
        assert dd.lower()<=df.upper() and df.lower()<=dd.upper()
    finally: method.H=saved

@pytest.mark.parametrize('r', [Q(7,13),Q(-3,17),Q(2**15)])
def test_exact_rational_fixedpoint_interval_contains(r):
    v=X(r)
    assert v.lower()<=r<=v.upper()
    assert (v*X(1)).lower()<=r<=(v*X(1)).upper()

def test_manual_ieee754_decoder():
    import struct
    assert parse64(struct.pack('>d',0.5))==Q(1,2)
    assert parse64(struct.pack('>d',-0.125))==Q(-1,8)
    assert parse64(struct.pack('>d',0.02))==Q.from_float(0.02)
    with pytest.raises(ValueError):parse64(struct.pack('>d',float('inf')))
    with pytest.raises(ValueError):parse64(struct.pack('>d',float('nan')))

def test_signed_interval_arithmetic():
    a=(Q(2),Q(5));b=(Q(7),Q(11))
    assert minus(b,a)==(Q(2),Q(9))
    assert scale_interval(-2,a)==(Q(-10),Q(-4))
    assert plus(a,b)==(Q(9),Q(16))
    assert maxabs((Q(-13),Q(3)))==13

def test_trapezoid_error_upper_is_explicit_and_positive():
    _,_,meta=K0K1_integral(Q(1,2))
    assert meta['trapezoid_upper']==Q(8)/(Q(1,2)*((1<<192)-1))
    assert meta['tail_upper']>=0
    assert meta['grid_points']>=1

def test_non_promoting_source_metadata():
    from source_audit import SAT_SHA, SOURCE_SHA
    assert len(SAT_SHA)==64 and len(SOURCE_SHA)==64
