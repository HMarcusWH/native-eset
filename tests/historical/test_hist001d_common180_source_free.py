"""No-data tests for exact March original-180 frozen stencil candidate proof code.
Do NOT treat these synthetic fixtures as six-lens physical or original-data replay.
"""
from __future__ import annotations
import runpy
import struct
from fractions import Fraction as Q
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[2]
SRC=HERE/'reference/hist001d_common180_candidate'
K=runpy.run_path(str(SRC/'frozen_kernel_exact_producer.py'))
I=runpy.run_path(str(SRC/'frozen_kernel_independent_checker.py'))
A=runpy.run_path(str(SRC/'frozen_kernel_adversarial_qa.py'))


def test_exact_directed_square_root_two():
    lo,hi=K['sqrt_band'](Q(2))
    assert lo*lo<=2<=hi*hi and hi-lo<=Q(1,1<<72)


def test_exact_square_root_fraction():
    lo,hi=K['sqrt_band'](Q(9,25))
    assert lo<=Q(3,5)<=hi and hi-lo<=Q(1,1<<72)
    assert I['exact_sqrt_enclose'](Q(9,25))==(Q(3,5),Q(3,5))


def test_irrational_kernel_interval():
    lo,hi=K['kernel_band'](Q(1),Q(3))
    assert 0<=lo<=hi<9


def test_kernel_equal_radius_returns_full_shell():
    lo,hi=K['kernel_band'](Q(2),Q(2))
    assert lo==hi==4


def test_kernel_source_monotonic_toy():
    arr=[K['kernel_band'](Q(x,4),Q(2)) for x in (1,2,3,4)]
    assert all(arr[i][1]<arr[i+1][0] for i in range(len(arr)-1))


def test_small_3_node_stencil_source_nonnegative():
    r=[Q(1,5),Q(1),Q(2)]
    m=K['make_matrix'](r)
    assert len(m)==3 and all(len(row)==3 for row in m)
    assert m[2]==[(x*x,x*x) for x in r]
    vals=K['calculate_ideal_nodes'](r,[Q(1)]*3,[Q(1)]*3,Q(4),m)
    assert all(vals[i][1] <= vals[i+1][0] for i in range(2))


def test_producer_and_independent_irrational_sqrt_agree():
    z=Q(8723,144)
    x1,x2=K['sqrt_band'](z)
    y1,y2=I['exact_sqrt_enclose'](z)
    assert x1*x1<=z<=x2*x2
    assert y1*y1<=z<=y2*y2
    assert x1<=y2 and y1<=x2


@pytest.mark.parametrize('f', [0.,-.0,.02,120.,1e-99,1e88,-13.125])
def test_independent_manual_ieee754_decoding(f):
    assert I['fdecode'](struct.pack('>d',f))==Q.from_float(f)


def test_independent_decoder_reject_nonfinite():
    for f in (float('inf'),float('nan')):
        with pytest.raises(ValueError):I['fdecode'](struct.pack('>d',f))


def test_independent_shell_positive():
    a,b=I['shell'](Q(1),Q(2))
    assert 0<=a<=b<Q(4)


def test_schema_synthetic_six_lens_controls():
    source='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    f={
        'schema':'HIST001D_MARCH_180_FROZEN_SOURCE_STENCIL_ALL_REAL_R_PL_ENVELOPE_CANDIDATE_V1',
        'original_source_lock_sha256':source,
        'source_180_node_shadow_density_reused_unchanged':True,
        'new_11520_source_density_used':False,
        'radius_domain':'[float64(0.02), float64(120.0)] kpc',
        'claims':{
            'all_real_original_K180_frozen_stencil_projection_vs_recorded_nodal_PL_enveloped':True,
            'original_total_H_error_bounded':False,
            'q_aperture_or_baryon_projection_error_closed':False,
            'original_continuum_root_count_proved':False,
            'physically_continuous_shadow_density_equivalence':False,
            'physical_provider_admitted':False,
            'empirical_validation':'NOT_ESTABLISHED'},
        'lenses':[]}
    checker={'lenses':[]}
    for i in range(6):
        comp=[];ref=[]
        for name in ('BULGE_K180','SHADOW_SPHERICAL_K180'):
            comp.append({'component':name,'source_node_max_anchor_gap_upper_msun':'2',
                         'max_real_radius_source_stencil_vs_piecewise_linear_bound_upper_msun':'8',
                         'all_179_real_radius_cells_upper_bounded':True,
                         'not_original_total_H_error':True,'not_q_aperture_error':True})
            ref.append({'component':name,'max_source_node_gap_integer_ceil_msun':'1',
                        'max_all_real_R_interpolation_bound_integer_ceil_msun':'7'})
        f['lenses'].append({'lens_id':f'L{i}','component_bounds':comp})
        checker['lenses'].append({'lens_id':f'L{i}','bounds':ref})
    assert A['check'](f,checker)
    f['claims']['physical_provider_admitted']=True
    with pytest.raises(ValueError):A['check'](f,checker)
    f['claims']['physical_provider_admitted']=False
    f['lenses'][0]['component_bounds'][0]['max_real_radius_source_stencil_vs_piecewise_linear_bound_upper_msun']='0'
    with pytest.raises(ValueError):A['check'](f,checker)
