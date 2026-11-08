"""Synthetic, source-free exact rational full-H extension and claim guard tests."""
from __future__ import annotations
import sys
from fractions import Fraction as F
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[2]/'reference'/'hist001d_full_h_bridge_candidate'
if not HERE.is_dir():HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from full_h_finite_source import FiniteLens,sqrt_rational_bounds  # noqa: E402
from verify_full_h_witness import sqrt_bnd  # noqa: E402
from validate_bridge_summary import validate,run_adversarial  # noqa: E402
from full_h_finite_source import LENSES  # noqa: E402

def synthetic():
    rows=[]
    for z in range(1,181):
        r=float(z)
        # Four rational mass columns: B=10r, D=5r, S0=S=4r;
        # q_b=q_d=1 => A(R)=R, target coefficient Cpi*sigma=2.
        rows.append((r,1.0,0.0,0.0,10*r,4*r,5*r,4*r))
    return FiniteLens('SYNTHETIC',rows,F(1),F(1),F(2),F(4))

@pytest.mark.parametrize('v', [F(0),F(1),F(2),F(3,7),F(123,100),F(128,25)])
def test_two_independent_rational_sqrts(v):
    for lo,hi in (sqrt_rational_bounds(v),sqrt_bnd(v)):
        assert lo*lo<=v<=hi*hi
        assert 0<=lo<=hi

@pytest.mark.parametrize('r,expect',[(F(9),F(9)),(F(19,2),F(19,2)),(F(10),F(10))])
def test_pl_q_synthetic_aperture(r,expect):
    obj=synthetic();lower,upper=obj.A_box(r)
    assert lower==upper==expect

@pytest.mark.parametrize('r', [F(9),F(37,4),F(19,2),F(39,4),F(10)])
def test_source_quadratic_exact_H(r):
    obj=synthetic();a,b=obj.source_H_box(r)
    assert a==b==19*r-2*r*r

def test_synthetic_crossing_cell_strict_decreasing():
    obj=synthetic();k,a,b=obj.source_cell(F(19,2))
    assert (k,a,b)==(8,F(9),F(10))
    leaves,unknown=obj.certify_cell_decreasing(k,a,b)
    assert leaves and not unknown and max(z['Hprime_upper_integer_ceiling_Msun_per_kpc'] for z in leaves)<0
    assert obj.source_H_box(a)[0]>0 and obj.source_H_box(b)[1]<0
    assert obj.sampled_crossings()==[(8,'positive_to_negative')]

def test_synthetic_all_source_domain_other_cells_excluded():
    obj=synthetic()
    assert obj.q_monotonic_global()>0
    leaves,unknown=obj.certify_global_exclusion(8,max_depth=14)
    assert not unknown and len(leaves)>=178
    assert set(v[0] for v in leaves)==set(range(179))-{8}

def toy_receipt():
    result={'schema':'HIST001D_MARCH180_FULL_H_PL_SOURCE_VS_SELECTED_SMOOTH_MATHEMATICAL_BRIDGE_V1',
            'original_source_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
            'source_PL_finite_full_H_global_one_root_each_6_of_6':True,
            'selected_Mstar_smooth_full_H_at_least_one_in_each_root_cell_6_of_6':True,
            'selected_smooth_roots_in_original_cell_strictly_left_of_finite_PL_roots':True,
            'selected_smooth_global_root_uniqueness_proved':False,
            'full_original_March_arbitrary_radius_floating_H_error_proved':False,
            'current_native_ESET_1_7_2_lensing_provider_validated':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'finite_witness':{'status':'PASS_CONDITIONAL_EXACT_RATIONAL_FINITE_H_WITNESS',
                              'global_sign_leaves':1150,'crossing_derivative_leaves':8,'lenses':6},
            'lenses':[]}
    for name in LENSES:
        result['lenses'].append({'lens':name,
            'source_root_one_per_whole_original_180_domain':True,
            'historical_sampled_root_not_source_PL_finite_H_root':True,
            'selected_continuum_H_has_at_least_one_root_strictly_left_of_finite_root':True,
            'selected_continuum_roots_in_cell_to_right_of_finite_root_excluded':True,
            'selected_continuum_global_root_uniqueness_proved':False,
            'global_non_crossing_H_sign_subbands':179,
            'root_cell_derivative_subbands':1,
            'H_selected_continuum_left_lower_integer_Msun':1,
            'H_selected_continuum_right_upper_integer_Msun':-1,
            'full_H_source_minus_H_smooth_strictly_greater_than_integer_Msun':1000,
            'whole_band_QminusP_mathematical_gap_lower_integer_Msun':1001,
            'source_S0_PL_minus_Q_lower_strictly_greater_than_minus_1_Msun':True,
            'source_node_gap_upper_exact':['1','2'],
            'H_source_at_original_reported_root_integer_Msun':[5,6],
            'finite_source_unique_root_bracket_exact_rational':['1','2']})
    return result

def test_summary_claim_guard_rejects_all_adversaries():
    v=toy_receipt()
    assert validate(v)
    qa=run_adversarial(v)
    assert qa['all_rejected'] and qa['count']==23

def test_summary_not_implicitly_promoting_smooth_unique():
    v=toy_receipt();v['selected_smooth_global_root_uniqueness_proved']=True
    with pytest.raises(ValueError):validate(v)

def test_summary_crossing_gap_outward_integer_relation():
    v=toy_receipt();v['lenses'][0]['full_H_source_minus_H_smooth_strictly_greater_than_integer_Msun']=1001
    with pytest.raises(ValueError):validate(v)
