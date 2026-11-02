"""Synthetic method tests only; never call these original-source verification."""
import sys
from pathlib import Path
from fractions import Fraction
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'reference'/'hist001d_smooth_msh_gradient_candidate'))
from smooth_math import (source_mass_and_analytic_gradient,
      nonuniform_gradient_exact,conditional_finite_difference_bounds)

@pytest.mark.parametrize('x',[[0.,1.,2.,3.],[0.,1.,3.,4.],[1.,2.,5.,10.]])
def test_linear_source_gradient_is_exact(x):
    m=[3*v+2 for v in x]
    assert nonuniform_gradient_exact(m,x)==[Fraction(3)]*len(x)

@pytest.mark.parametrize('x',[[-1.,0.,1.,3.],[0.,2.,3.,5.]])
def test_quadratic_interior_exact(x):
    m=[v*v for v in x]
    g=nonuniform_gradient_exact(m,x)
    for i in range(1,len(x)-1):assert g[i]==Fraction(2*x[i])

def test_nonsymmetric_cubic_interior_remainder_is_hm_hp():
    x=[0.,1.,3.,7.];m=[r**3 for r in x]
    g=nonuniform_gradient_exact(m,x)
    for i in range(1,len(x)-1):
        hm=Fraction(x[i]-x[i-1]);hp=Fraction(x[i+1]-x[i])
        assert g[i]-Fraction(3*x[i]*x[i])==hm*hp

def test_one_sided_quadratic_remainder_is_h_m2_over_two():
    x=[0.,2.,3.];m=[r*r for r in x]
    g=nonuniform_gradient_exact(m,x)
    assert abs(g[0]-0)==Fraction(2)
    assert abs(g[-1]-6)==Fraction(1)

def test_exact_conditional_taylor_bounds():
    z=conditional_finite_difference_bounds(Fraction(1),Fraction(2),Fraction(2),Fraction(6))
    assert z['endpoint_left']==1 and z['endpoint_right']==2 and z['interior']==2

def test_absent_smooth_curvature_bounds_fail_closed():
    assert conditional_finite_difference_bounds(1,2)['status']=='UNRESOLVED_DERIVATIVE_SUPREMA_NOT_CERTIFIED'
    assert conditional_finite_difference_bounds(1,2,max_abs_M3=3)['status']=='UNRESOLVED_DERIVATIVE_SUPREMA_NOT_CERTIFIED'

def test_invalid_stencil_or_curvature_fails_closed():
    with pytest.raises(ValueError):conditional_finite_difference_bounds(0,2,1,1)
    with pytest.raises(ValueError):conditional_finite_difference_bounds(1,1,1,-2)
    with pytest.raises(ValueError):nonuniform_gradient_exact([1.,2.,3.],[1.,1.,3.])

def test_clipping_is_one_lipschitz():
    for a in range(-7,8):
        for b in range(-7,8):
            assert abs(max(0,a)-max(0,b))<=abs(a-b)

@pytest.mark.parametrize('r',[0.02,0.2,2.0,20.0,120.0])
def test_source_smooth_mass_analytic_derivative_matches_stable_fd_synthetic(r):
    params=dict(Mb=3e10,Md=2e10,a=1.2,Rd=1.5,delta=.8,r0=5.,n=4.2)
    h=max(r*1e-5,1e-7)
    M,der=source_mass_and_analytic_gradient(np.array([r]),**params)
    m_plus=source_mass_and_analytic_gradient(np.array([r+h]),**params)[0][0]
    m_minus=source_mass_and_analytic_gradient(np.array([r-h]),**params)[0][0]
    fd=(m_plus-m_minus)/(2*h)
    assert abs(der[0]-fd)/max(abs(fd),1e-20)<1e-5
    assert M[0]>=0

def test_guarded_real_epsilon_floor():
    args=dict(Mb=1e10,Md=1e10,a=1.,Rd=2.,delta=.95,r0=5.,n=4.298296)
    rr=np.geomspace(.02,120,40)
    m,mp=source_mass_and_analytic_gradient(rr,**args)
    assert np.all(np.isfinite(m)) and np.all(np.isfinite(mp))

def test_invalid_parameter_or_domain_rejected():
    args=dict(Mb=1e10,Md=1e10,a=1.,Rd=2.,delta=.8,r0=5.,n=4.)
    with pytest.raises(ValueError):source_mass_and_analytic_gradient(np.array([0.]),**args)
    with pytest.raises(ValueError):source_mass_and_analytic_gradient(np.array([2.]),**(args|{'delta':1.1}))
