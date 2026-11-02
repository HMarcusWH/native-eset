"""Mathematical unit/negative checks. Source-free, not six-lens original archival replay."""
from __future__ import annotations
import sys
from fractions import Fraction as Q
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parent
# For a repository PR this test can live in tests/ and reference code in reference/.
repo_math=Path(__file__).resolve().parents[2]/'reference'/'hist001d_first_node_rational_candidate'
sys.path.insert(0,str(HERE if (HERE/'first_node_certificate.py').exists() else repo_math))
from first_node_certificate import (  # noqa: E402 - path set to exact reference source above
    Iv, ln_pos, gamma_iv, positive_series, bessel_values,
    gate, source_mass_derivative, exp_pos, down, up,
)

def test_interval_directed_quantization():
    for q in (Q(1,3),Q(-1,7),Q(4441,211),Q(0)):
        assert down(q)<=q<=up(q)

def test_exact_log_one_and_positive():
    x=ln_pos(Q(1));assert x.l<=0<=x.u
    for n in (2,3,7,300):
        a=ln_pos(Q(n));assert a.l>0 and a.l<a.u

def test_log_add_inverse_guard():
    for x in (Q(2),Q(3,4),Q(11,7)):
        a=ln_pos(x);b=ln_pos(1/x)
        assert a.l+b.l<=0<=a.u+b.u

def test_euler_interval_known_loose_range():
    e=gamma_iv(500)
    assert Q(577,1000)<e.l<e.u<Q(578,1000)
    assert e.u-e.l < Q(1,10**11)

def test_positive_series_tail_enclosure():
    for y in (Q(1,100),Q(1,5),Q(1,2)):
        i0,i1,s,s1=positive_series(y)
        assert all(x.l>=0 and x.u>=x.l for x in (i0,i1,s,s1))
        assert i0.l>1 and i1.l>0

def test_bessel_log_series_positive_K():
    for y in (Q(1,200),Q(1,30),Q(1,10),Q(1,3),Q(1,2)):
        f,fp,k=bessel_values(y)
        assert k['K0'].l>0 and k['K1'].l>0 and f.l>0
        assert f.u-f.l<Q(1,10**9)

def test_exponent_range_reduction():
    a=exp_pos(Iv(Q(0)))
    b=exp_pos(Iv(Q(20)))
    assert a.l<=1<=a.u
    assert b.l>1 and b.u>b.l

def test_gate_value_and_positive_derivative():
    p=gate(Q(1,50),Q(5),Q(43,10),Q(9,10))
    assert p[0].l>0 and p[1].l>0

def test_synthetic_shadow_mass_smooth_derivative_positive():
    p={'Mb':Q(10**10),'Md':Q(2*10**10),'a':Q(4,5),'Rd':Q(13,10),
       'delta':Q(93,100),'r0':Q(5),'n':Q(43,10)}
    v,meta=source_mass_derivative(Q(1,50),p)
    assert v.l>0 and meta['positive_derivative'] is True
    assert meta['smooth_M'].l>0

def test_reject_bad_bessel_domain():
    with pytest.raises(ValueError):positive_series(Q(0))
    with pytest.raises(ValueError):positive_series(Q(2))

def test_reject_invalid_log_domain():
    for q in (Q(0),Q(-1)):
        with pytest.raises(ValueError):ln_pos(q)

def test_reject_negative_exponent_argument():
    with pytest.raises(ValueError):exp_pos(Iv(Q(-1)))

def test_reject_source_gate_wrong_domain():
    with pytest.raises(ValueError):gate(Q(10),Q(5),Q(43,10),Q(9,10))

def test_reject_invalid_ratio_denominator():
    with pytest.raises(ValueError):Iv(Q(-1),Q(1)).inv()

def test_model_claim_firewall_source_free():
    import inspect
    import first_node_certificate as p
    s=inspect.getsource(p.produce)
    for field in ('same_source_physical_density_proved','original_float_operation_error_certified',
                  'original_full_H_or_root_count_certified','physical_provider_admitted'):
        assert "'"+field+"':False" in s
    assert "'empirical_validation':'NOT_ESTABLISHED'" in s
