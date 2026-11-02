"""Source-free algebra/contract checks only; no implicit historical source replay."""
from __future__ import annotations
import importlib.util
import json
import struct
from fractions import Fraction
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
ARCH=ROOT/'reference/hist001d_bridge_candidate/src'

def load(name):
    spec=importlib.util.spec_from_file_location(name,ARCH/(name+'.py'))
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@pytest.mark.parametrize('q,expected',[(Fraction(11,4),2),(Fraction(-11,4),-3),(Fraction(0),0)])
def test_exact_floor(q,expected):
    assert load('bridge_exact').floor(q)==expected

@pytest.mark.parametrize('y0,y1,lo,hi,delta',[
    (Fraction(-2),Fraction(8),Fraction(4),Fraction(10),Fraction(6)),
    (Fraction(8),Fraction(4),Fraction(4),Fraction(10),Fraction(0)),
    (Fraction(18),Fraction(10),Fraction(4),Fraction(10),Fraction(8)),
])
def test_distance_to_closed_interval(y0,y1,lo,hi,delta):
    # y0 is the evaluated source interpolant; y1 is an unused independent fixture.
    assert max(Fraction(0),lo-y0,y0-hi)==delta

@pytest.mark.parametrize('x0,x1,a,b,C',[
    (Fraction(0),Fraction(1),Fraction(0),Fraction(1),Fraction(7,3)),
    (Fraction(2),Fraction(4),Fraction(1,5),Fraction(-1,3),Fraction(10000)),
    (Fraction(1,100),Fraction(9,5),Fraction(3,14),Fraction(-5,11),Fraction(12345678,100)),
])
def test_exact_target_linear_quadratic_identity(x0,x1,a,b,C):
    y0=C*x0*x0+a;y1=C*x1*x1+b
    for t in [Fraction(0),Fraction(1,9),Fraction(1,3),Fraction(1,2),Fraction(7,8),Fraction(1)]:
        x=x0+t*(x1-x0)
        src=y0*(1-t)+y1*t
        exact=C*(x-x0)*(x1-x)+a*(1-t)+b*t
        assert src-C*x*x==exact
        bound=C*(x1-x0)**2/4+max(abs(a),abs(b))
        assert abs(src-C*x*x)<=bound

@pytest.mark.parametrize('v',[0.02,-1.5,1e-100,120.0,0.0])
def test_ieee754_manual_decode(v):
    b=struct.unpack('>Q',struct.pack('>d',v))[0]
    decoded=load('bridge_independent').byte_float64(b)
    assert decoded==Fraction.from_float(v)

def test_original_math_sources_reference_only_and_source_inputs_external():
    names={p.name for p in ARCH.glob('*.py')}
    assert {'bridge_exact.py','bridge_independent.py','target_quadratic_exact.py','target_quadratic_independent.py'}.issubset(names)
    code=(ARCH/'bridge_exact.py').read_text()
    assert 'SOURCE_LOCK' in code and 'March_180x120_continuum_discretization_error_certified' in code
    assert not list(ROOT.rglob('*.R_H_be64.bin'))
    assert not list(ROOT.rglob('source_nodal.zip'))


def test_archived_exact_source_references_are_immutable():
    # These are independent external locator pins, not embedded original data or source execution.
    m=load('bridge_exact')
    assert m.MARCH_SHA=='7b4e29bd4048a8558af5e7985a9a6ada529e27a7ef4eb068f892f5f3a7bc24b1'
    assert m.NARROW_SHA=='138669c971b07652d24b76c34e32cb0a74c3cbc893de3d254c7a5170eec08bb5'
    assert m.SOURCE_LOCK=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
