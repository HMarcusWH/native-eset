"""Synthetic tests of the source-only crossing-band proof mechanism.

Never uses any original March mass/radius arrays. A green test suite is not
physical admission or a six-lens empirical result.
"""
from fractions import Fraction as F
from math import sqrt,log,acosh,isclose
import sys
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[2]/'reference'
sys.path.insert(0,str(HERE/'hist001d_k180_crossing_band_candidate'))
sys.path.insert(0,str(HERE/'hist001d_k180_root_aperture_candidate'))
from crossing_band_certifier import min_quad,certify_panel,q_and_gradient  # noqa: E402
from verify_band_witness import exact_panel_floor,check_lens  # noqa: E402
from root_aperture_certifier import Iv  # noqa: E402


def test_quadratic_minimum_vertex_and_endpoints():
    assert min_quad(F(3),F(-2),2,F(0),F(4))==F(2)
    assert min_quad(F(1),F(7),2,F(0),F(4))==1
    assert min_quad(F(1),F(-7),2,F(0),F(4))==F(-45,4)


def test_correct_continuum_second_derivative_source_free():
    # M(r)=r^2, [a,b]=[1,5], A=3; the correct P'' formula is
    # 2*arcosh(5/A) - M'(b)/(b*u_b) = 2*ln(3)-5/2.
    a,b,A=1.,5.,3.
    u=sqrt(1-(A/b)**2)
    formula=2*acosh(b/A)-2/u
    assert isclose(formula,2*log(3)-2.5,rel_tol=1e-12)
    def P(x):
        return b*b-a*a - b*sqrt(b*b-x*x)+x*x*log((b+sqrt(b*b-x*x))/x)
    h=0.002
    numeric=(P(A+h)-2*P(A)+P(A-h))/(h*h)
    assert abs(formula-numeric)<2e-5


def test_geometric_sec_square_upper():
    # ∫_{theta_lo}^{theta_hi} sec(theta)^2 dθ = tan(hi)-tan(lo),
    # which is >= ∫ sec θ dθ on theta∈[0,π/2).
    for alo,ahi in [(1.,2.),(2.,4.),(5.,9.)]:
        for rlo,rhi in [(10.,15.),(15.,40.),(40.,120.)]:
            if ahi>=rlo:continue
            w=lambda A:(sqrt(rhi*rhi-A*A)-sqrt(rlo*rlo-A*A))/A
            # Fixed lo/hi, difference increases with A, and 1/A<=1/alo.
            upper=(sqrt(rhi*rhi-ahi*ahi)-sqrt(rlo*rlo-ahi*ahi))/alo
            for j in range(11):
                A=alo+(ahi-alo)*j/10
                assert w(A)<=upper*(1+1e-12)


class SyntheticLens:
    def __init__(self):
        self.r=[F(1),F(5),F(9)]
        self.w=[F(0),F(1),F(0)]
        self.rho=[F(0),F(1,25),F(0)]
        self.C4pi=F(1)


def test_convex_source_supporting_line():
    L=F(2);U=F(3);T=(L+U)/2
    Q,QP=q_and_gradient(SyntheticLens(),T)
    assert QP.low()>0
    qmid=float(Q.low()); qprime=float(QP.low())
    for n in range(31):
        A=float(L)+(float(U-L))*n/30
        actual=1-sqrt(1-(A/5)**2)
        assert actual+1e-12>=qmid+qprime*(A-float(T))


def test_exact_synthetic_panel_lower_is_safe():
    lens=SyntheticLens()
    L,U=F(2),F(3)
    low,ev=certify_panel(lens,L,U,Iv(4),Iv(9),2)
    w={'left_n':str(L.numerator),'left_d':str(L.denominator),
       'right_n':str(U.numerator),'right_d':str(U.denominator),
       'gap_lower_floor_Msun':low,**ev}
    assert exact_panel_floor(w,2)==low
    for j in range(31):
        x=2+j/30
        D=(1-sqrt(1-(x/5)**2))-x*x
        assert low<D


def test_closed_subband_coverage():
    q={'Q_mid_lower_integer':100000,'Q_slope_lower_integer':0,'Q_slope_upper_integer':0,
       'P_left_upper_integer':10,'P_right_upper_integer':10}
    l=[]
    for a,b in [(F(1),F(3,2)),(F(3,2),F(2))]:
        w={'left_n':str(a.numerator),'left_d':str(a.denominator),
           'right_n':str(b.numerator),'right_d':str(b.denominator),**q}
        w['gap_lower_floor_Msun']=exact_panel_floor(w,2)
        l.append(w)
    source={'lens':'J0822+1828','status':'PASS_POSITIVE_FOR_ENTIRE_APERTURE_BAND',
          'unknown_subbands':[],'uniform_P_second_derivative_abs_integer_Msun_per_kpc2':2,
          'A_band_left_exact_n_over_d':['1','1'],'A_band_right_exact_n_over_d':['2','1'],
          'positive_subbands':l,'minimum_gap_lower_floor_Msun':min(x['gap_lower_floor_Msun'] for x in l),
          'certification_attempts':3,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    assert check_lens(source)>0
    source['positive_subbands'].pop()
    with pytest.raises(ValueError,match='end coverage'):
        check_lens(source)
