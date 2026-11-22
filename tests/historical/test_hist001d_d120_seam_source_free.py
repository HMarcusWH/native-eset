"""Synthetic-only D120 omitted-seam properties; no original-source arrays in public CI."""
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference'/'hist001d_d120_seam_candidate'))
from seam_math import exp_minus_alternating,exp_minus_positive,seam_interval,integer_micro_interval  # noqa: E402
from verify_seam import check_structure,LENSES  # noqa: E402
from source_seam_replay import num_crossing  # noqa: E402

@pytest.mark.parametrize('num,den',[(0,1),(1,100),(1,3),(1,1),(2,1),(17,3),(25,1),(180,1)])
def test_two_rational_exponential_enclosures_intersect(num,den):
    x=F(num,den)
    a,b=exp_minus_alternating(x)
    c,d=exp_minus_positive(x)
    assert 0<=a<=b<=1
    assert 0<=c<=d<=1
    assert max(a,c)<=min(b,d)

@pytest.mark.parametrize('radius', [F(0),F(1,100),F(1),F(7,3),F(10)])
def test_seam_nonnegative_two_methods(radius):
    args=(radius,F(151,17),F(3,5),F(1,20),F(1),F(21,20))
    a,b=seam_interval(*args,exp_minus_alternating)
    c,d=seam_interval(*args,exp_minus_positive)
    assert a>=0 and c>=0 and max(a,c)<=min(b,d)
    if radius>0:assert a>0 and c>0
    else:assert (a,b,c,d)==(0,0,0,0)


def test_seam_strict_monotonicity_over_synthetic_band():
    args=(F(100),F(3,2),F(1,11),F(1),F(7,5))
    a=seam_interval(F(1,2),*args)
    b=seam_interval(F(3,2),*args)
    assert a[1]<b[0]


def test_119_segments_dont_form_closed_120_segment_periodic_trapezoid():
    # Constant positive angular integrand, artificial 120 fixed nodes.
    # Original 119-segment sum=119*h*f; closed periodic sum=120*h*f.
    h=F(1,19);f=F(31,7)
    original=119*h*f
    seam=h*f
    assert seam/original==F(1,119)
    assert original+seam==120*h*f


def test_exact_micro_rounding_can_preserve_strict_lower():
    r=(F(2000000001,1000000),F(2000000002,1000000))
    assert integer_micro_interval(r)==[2000000001,2000000002]


def synthetic_structure():
    obj={'schema':'HIST001D_ORIGINAL_D120_PERIODIC_SEAM_SOURCE_LOCKED_DIAGNOSTIC_V1',
         'source_original_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
         'input_saturation_sha256':'99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce',
         'input_finite_H_sha256':'02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6',
         'source_float_parent_sha256':'313b62e2c0f790684bd6ed6ff22431c2cce1f398d79fcc590971f8814ae4706e',
         'frozen_D120_nodes_binary64_replayed':1080,'frozen_circularized_shadow_nodes_binary64_replayed':1080,'frozen_H_nodes_binary64_replayed':1080,
         'periodic_seam_term_analytic_positive_for_every_R_gt_zero':True,
         'periodic_seam_monotonicity_identity':'d seam/dR >0',
         'all_six_sampled_roots_with_periodic_seam_are_counterfactual_diagnostics_only':True,
         'full_azimuth_integral_error_certified':False,'historical_original_source_stencil_modified':False,
         'original_march_offgrid_physical_H_bound':False,'actual_original_March_SciPy_upstream_accuracy_proved':False,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED','lenses':[]}
    for lid in LENSES:
        obj['lenses'].append({'lens_id':lid,'source_D120_stored_binary64_exact_count':180,
                             'source_circularized_shadow_stored_binary64_exact_count':180,
                             'source_H_stored_binary64_exact_count':180,
                             'source_kpc_per_arcsec_output_exact':True,
                             'stored_shadow_density_strictly_positive_count':180,
                             'stored_density_clip_floor_inactive_at_all_source_nodes':True,
                             'new_disk_node_correction_positive':True,
                             'seam_closure_not_original_source':True,
                             'counterfactual_output_not_certified_root_shift':True,
                             'counterfactual_new_crossing_count':1,
                             'counterfactual_new_crossing_index':4,
                             'original_crossing_cell_index':3,
                             'rigorous_exact_real_periodic_seam_at_crossing_endpoints_integer_micro_Msun':[[15,16],[25,26]],
                             'source_periodic_seam_percent_of_D_source_at_crossing_endpoints_integer_micro_percent':[[3,4],[5,6]],
                             'counterfactual_root_shift_kpc_float':0.001})
    return obj


def test_source_free_claim_guard_accepts_only_synthetic_safe_shape():
    assert check_structure(synthetic_structure())

@pytest.mark.parametrize('field,bad',[
    ('physical_provider_admitted',True),('empirical_validation','VALIDATED'),('full_azimuth_integral_error_certified',True),
    ('original_march_offgrid_physical_H_bound',True),('actual_original_March_SciPy_upstream_accuracy_proved',True),
    ('frozen_D120_nodes_binary64_replayed',1079),('periodic_seam_term_analytic_positive_for_every_R_gt_zero',False)])
def test_source_free_claim_guard_rejects_misuse(field,bad):
    x=synthetic_structure();x[field]=bad
    with pytest.raises(ValueError):check_structure(x)


def test_source_free_claim_guard_rejects_missing_lens():
    x=synthetic_structure();x['lenses'].pop()
    with pytest.raises(ValueError):check_structure(x)


def test_original_first_crossing_source_math_synthetic():
    import numpy as np
    r=np.array([1.,2.,3.,4.])
    h=np.array([10.,3.,-1.,-3.])
    k,x=num_crossing(r,h)
    assert k==1 and x==2.75
