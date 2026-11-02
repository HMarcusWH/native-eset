"""Source-free mathematical unit and claim-firewall tests; NOT a source-data replay."""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import sys
import pytest
ARCHIVE_SRC=Path(__file__).resolve().parents[1]/'src'
REPO_SRC=Path(__file__).resolve().parents[2]/'reference'/'hist001d_march_c3_candidate'
sys.path.insert(0,str(ARCHIVE_SRC if ARCHIVE_SRC.is_dir() else REPO_SRC))
from c3_envelope import (ceil_sqrt_fraction,K_half_polynomial,bound_F_derivative,
                         bound_acceleration_baryon_derivatives,bound_gate_derivatives,
                         bound_shadow_M_derivatives,split_interval,certify_mesh)

def test_sqrt_directed():
    for n in range(1,70):
        a=Q(n*n+7, n*13+3)
        root=ceil_sqrt_fraction(a,64)
        assert root**2>=a
        assert (root-Q(1,2**64))**2<a or root==0

@pytest.mark.parametrize('v',[Q(1,4),Q(1),Q(2),Q(5),Q(21)])
def test_half_integer_polynomial_recurrence(v):
    a=[K_half_polynomial(k,v) for k in range(5)]
    assert a[0]==1 and a[1]==1+v
    for n in (1,2,3):
        assert a[n+1]==a[n-1]+(2*n+1)*v*a[n]

@pytest.mark.parametrize('rlo,rhi',[(Q(1,50),Q(1,10)),(Q(1),Q(2)),(Q(3),Q(5)),(Q(11),Q(15))])
def test_positive_bessel_derivative_upper(rlo,rhi):
    d=[bound_F_derivative(i,rlo) for i in range(4)]
    assert all(x>0 for x in d)
    assert all(x.denominator>0 for x in d)


def test_derivative_baryon_and_gate_positive():
    scalar={'Mb':Q(1_000_000),'Md':Q(2_000_000),'a':Q(4,5),'Rd':Q(13,10),
            'delta':Q(19,20),'r0':Q(5),'n':Q(43,10)}
    for lo,hi in [(Q(1,50),Q(1,10)),(Q(9,10),Q(11,10)),(Q(50),Q(55))]:
        b=bound_acceleration_baryon_derivatives(lo,hi,**{k:scalar[k] for k in ('Mb','Md','a','Rd')})
        g=bound_gate_derivatives(lo,hi,**{k:scalar[k] for k in ('delta','r0','n')})
        s=bound_shadow_M_derivatives(lo,hi,scalar)
        assert len(b)==len(g)==4 and len(s)==2
        assert all(x>=0 for x in b+g+s)


def test_nongrid_integer_power_gate_inequalities():
    n=Q(43,10)
    for f in [Q(1,1000),Q(1,10),Q(1,2),Q(9,10),Q(999,1000)]:
        p=f*(1-f)
        assert p<=Q(1,4)
        assert abs(n*(1-2*f)-1)<=n+1
        z=(n*(1-2*f)-2)*(n*(1-2*f)-1)-2*n*n*p
        assert abs(z)<= (n+2)*(n+1)+2*n*n*p


def test_source_gradient_stencil_exact_remainder_cubic():
    hminus=Q(2,3);hplus=Q(5,4);r=Q(2)
    f=lambda x:x**3
    backward=(f(r)-f(r-hminus))/hminus
    forward=(f(r+hplus)-f(r))/hplus
    ideal=(hplus*backward+hminus*forward)/(hplus+hminus)
    assert ideal-3*r*r==hminus*hplus
    # f'''=6, so (hminus*hplus/6)*6 exactly saturated.


def test_source_gradient_one_sided_quadratic():
    f=lambda x:x*x
    h=Q(3,4);r=Q(2)
    left=(f(r+h)-f(r))/h
    assert left-2*r==h
    assert abs(left-2*r)==h*2/2


def test_180_node_source_contract_rejects_wrong_length():
    vals=[Q(1)+Q(i,5) for i in range(3)]
    with pytest.raises(ValueError,match='canonical 180'):
        certify_mesh(vals,{'Mb':Q(1)},parts=4)

@pytest.mark.parametrize('bad',[
    (Q(0),Q(1)),(Q(1),Q(1)),(Q(-1),Q(2)),
])
def test_invalid_source_radii_rejected(bad):
    lo,hi=bad
    with pytest.raises(ValueError):split_interval(lo,hi)


def test_gate_disallows_unvalidated_n_and_delta():
    for bad in [(Q(1),Q(2),Q(1),Q(5),Q(3)),
                (Q(1),Q(2),Q(1),Q(5),Q(11,2)),
                (Q(1),Q(2),Q(2),Q(5),Q(43,10))]:
        lo,hi,delta,r0,n=bad
        with pytest.raises(ValueError):bound_gate_derivatives(lo,hi,delta=delta,r0=r0,n=n)


def test_claim_firewall_source_free_static():
    import inspect, produce
    assert produce.EXPECTED_46P3 == 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    source=inspect.getsource(produce.build)
    for key in ('float_operation_error_certified',
                'original_March_total_H_or_root_count_certified',
                'physical_provider_admitted','full_H_root_error_guard_met',
                'source_offgrid_clip_branch_certified'):
        assert f"'{key}':False" in source
    assert "'external_mathematical_review':'NOT_DONE'" in source
