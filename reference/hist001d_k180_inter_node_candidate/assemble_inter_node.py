#!/usr/bin/env python3
"""Aggregate source-locked all-real derivative witnesses and conservative BV bounds."""
from __future__ import annotations
from pathlib import Path
import json,hashlib
from inter_node_claim_guard import validate
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def sha(b):return hashlib.sha256(b).hexdigest()
def build(root:Path):
    inter=[];bv=[];locks={};summ=[]
    for i in range(6):
        a=root/f'results/continuous_lens_{i}.json';b=root/f'results/bv_band_lens_{i}.json'
        I=json.loads(a.read_text());B=json.loads(b.read_text())
        inter.append(I);bv.append(B)
        locks[str(a.relative_to(root))]=sha(a.read_bytes())
        locks[str(b.relative_to(root))]=sha(b.read_bytes())
        summ.append({'lens_id':I['lens_id'],'source_node_sha256':I['node_sha256'],
            'accepted_real_radial_panels':len(I['panels']),'extra_Bessel_integral_evaluations':len(I['midpoints']),
            'minimum_positive_Mprime_micro_Msun_per_kpc':min(x['Mprime_lower_micro'] for x in I['panels']),
            'independent_uniform_crossing_A_band_BV_upper_Msun':B['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun'],
            'P_continuum_crossing_A_band_Msun_interval':B['P_mathematical_continuum_all_A_band_integer_Msun_enclosure'],
            'BV_bound_sufficient_for_historical_full_H_root_shift':False})
    results=root/'results'
    for name in ('verify_independent.json','verify_bv.json','adversarial_qa.json'):
        obj=json.loads((results/name).read_text());locks['results/'+name]=sha((results/name).read_bytes())
        if obj.get('all_pass') is False or obj.get('physical_provider_admitted') is not False or obj.get('empirical_validation')!='NOT_ESTABLISHED':
            raise ValueError('unverified independent receipt or claim')
    meta={'schema':'HIST001D_REAL_INTEGRAL_K0K1_INTER_NODE_POSITIVITY_AND_BV_V1',
        'date':'2026-11-03','source_original_46plus3_sha256':SOURCE_SHA,
        'source_saturation_sha256':sha((root/'inputs/saturation_parent_v1r1.zip').read_bytes()),
        'source_crossing_band_sha256':sha((root/'inputs/crossing_band_parent_v1r2.zip').read_bytes()),
        'source_integral_parent_sha256':sha((root/'inputs/bessel_integral_parent.zip').read_bytes()),
        'parent_sha_lock_byte_counts':[(root/'inputs/saturation_parent_v1r1.zip').stat().st_size,(root/'inputs/crossing_band_parent_v1r2.zip').stat().st_size],
        'six_lenses':summ,'source_receipts_sha256':locks,
        'original_radial_cells_per_lens':179,
        'all_original_radial_cells_certified':True,'selected_Mstar_prime_all_real_positive':True,
        'all_six_root_band_BV_bounds_certified':True,
        'independent_Fraction_panels_verified':True,
        'independent_binary_search_BV_verified':True,
        'total_certified_subpanels':sum(len(x['panels']) for x in inter),
        'total_new_integral_Bessel_evaluations':sum(len(x['midpoints']) for x in inter),
        'total_unresolved_real_radial_subpanels':sum(len(x['unresolved']) for x in inter),
        'global_ideal_K180_vs_continuum_root_error_proved':False,
        'smooth_model_physical_Weyl_provider_admitted':False,
        'useful_for_original_March_root_gap':False,
        'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
        'selected_mathematical_Mstar_not_physical_source':True,
        'independent_external_math_referee_completed':False}
    validate(inter,bv,meta)
    if meta['total_unresolved_real_radial_subpanels']!=0 or meta['total_certified_subpanels']<6*179:raise ValueError('source cells incompletely certified')
    dest=results/'aggregate.json';dest.write_text(json.dumps(meta,sort_keys=True,indent=2)+'\n')
    print('AGGREGATE',meta['total_certified_subpanels'],'cells,',meta['total_new_integral_Bessel_evaluations'],'integral nodes; sha256',sha(dest.read_bytes()))
    return meta
if __name__=='__main__':build(Path(__file__).resolve().parents[2])
