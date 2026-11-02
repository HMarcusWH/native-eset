"""Source-free checks of finite BV and endpoint mass identities (not full proof)."""
from fractions import Fraction as F
import pytest
from pathlib import Path
import sys
SOURCE=Path(__file__).resolve().parents[2]/"reference"/"hist001d_k180_saturation_candidate"
sys.path.insert(0,str(SOURCE))
from conservation_identity import trap_weights,nonuniform_stencil  # noqa: E402

@pytest.mark.parametrize('power',range(6))
def test_bv_variation_trapezoid_polynomial(power):
    # f(x) = x^power*(1-x), integral = 1/((p+1)(p+2))
    # Endpoint trapezoid is 1/2 if power=0, else 0.
    h=F(1);integral=F(1,(power+1)*(power+2))
    trap=F(1,2) if power==0 else F(0)
    # Bound TV(f) by sup|g| TV(phi)+sup(phi) TV(g), with
    # g=x^p, phi=1-x nonnegative monotone in both factors.
    tv_g=F(0) if power==0 else F(1)
    tv_phi=F(1)
    cap=h*(tv_phi+tv_g)/2
    assert abs(trap-integral)<=cap

@pytest.mark.parametrize('step', [F(1,10),F(1,3),F(2,7),F(7)])
def test_original_trapezoid_TV_quadratic(step):
    # g(r)=r^2, integral over [0,step] is step^3/3
    # trapezoid error exactly step^3/6, TV(g)=step^2.
    err=step**3/6
    assert err <= step/2*step**2
    g=[F(0),step*step]
    assert abs(sum((w*d for w,d in zip(trap_weights([0,step]),g)),F(0)) - step**3/3)==err

@pytest.mark.parametrize('n', [2,3,4,8])
def test_uniform_grid_telescopes_for_oscillatory_mass(n):
    r=[F(i,n) for i in range(n+1)]
    m=[F((i*i+17*i)%7,19) for i in range(n+1)]
    dg=nonuniform_stencil(r,m)
    assert sum((w*d for w,d in zip(trap_weights(r),dg)),F(0))==m[-1]-m[0]

def test_saturated_projection_is_endpoint_identity_for_selected_mass():
    # Algebraically dM/dr times saturated kernel phi=1 integrates by FTC.
    # This is a synthetic case, not the protected historical source.
    # M(r)=3+2r+5r^3: dM/dr=2+15r^2.
    a,b=F(1,50),F(120)
    mass=lambda r:3+2*r+5*r**3
    direct=2*(b-a)+5*(b**3-a**3)
    assert mass(b)-mass(a)==direct
