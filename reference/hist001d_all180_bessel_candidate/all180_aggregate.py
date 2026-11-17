#!/usr/bin/env python3
"""Aggregate six independent source-bound fixed-node rational comparisons.

Reads previously generated verified JSONs only; DOES NOT claim source replay by itself.
"""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
IDS=('J0822p1828','J0915p4211','J0930p2855','J1021p2028','J1111p2234','J1135p3720')
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def inspect_pair(p,q):
    if p.get('schema')!='HIST001D_ORIGINAL_MARCH180_ALL_NODE_RATIONAL_BESSEL_SOURCE_AUDIT_CANDIDATE_V1':raise ValueError('producer schema')
    if q.get('schema')!='HIST001D_ALL180_INDEPENDENT_FIXED_DENSITY_COMPARISON_V1':raise ValueError('independent schema')
    if p.get('lens_id')!=q.get('lens_id') or p.get('source_180_node_sha256')!=q.get('node_sha256'):raise ValueError('source identity mismatch')
    if p.get('original_46plus3_source_composite_sha256')!=SOURCE or q.get('source_sha256')!=SOURCE or p.get('original_smooth_parent_sha256')!=PARENT:raise ValueError('external frozen-source identity changed')
    if not all(p.get(k) is True for k in ('source_regv2_180_nodes_not_D2d_11520','all_180_ideal_stencil_discrepancies_certified','original_source_density_positive_all_nodes','smooth_math_derivative_positive_all_nodes','original_source_180_kernel_weights_positive')):raise ValueError('required source gates missing')
    for k in ('physical_provider_admitted','source_float_operational_error_certified_for_arbitrary_inputs','physical_shadow_density_or_Weyl_proved','original_March_continuum_H_error_or_root_count_proved'):
        if p.get(k) is not False:raise ValueError('promoted unsupported producer science')
    for k in ('physical_provider_admitted','original_source_float_error_theorem','original_full_H_root_theorem'):
        if q.get(k) is not False:raise ValueError('promoted unsupported verifier science')
    if p.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('empirical claim inflation')
    v=p.get('stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc');w=q.get('all180_node_abs_error_upper_micro_msun_per_kpc')
    if not isinstance(v,list) or not isinstance(w,list) or len(v)!=180 or len(w)!=180:raise ValueError('incorrect source node count')
    if any(type(a) is not int or type(b) is not int or a<0 or b<0 or b>a for a,b in zip(v,w)):
        raise ValueError('independent source rational caps contradict producer')
    if type(p.get('max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc')) is not int or max(v)>p['max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc'] or p['max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc']>=1_000_000:
        raise ValueError('source ideal-stencil max bound is wrong')
    if max(w)>q['max_upper_micro_msun_per_kpc'] or q['max_upper_micro_msun_per_kpc']>p['max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc']:
        raise ValueError('independent max contradiction')
    signed=q.get('signed_source_minus_smooth_Mprime_integer_intervals')
    original=p.get('source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc')
    if not isinstance(signed,list) or len(signed)!=180 or not isinstance(original,list) or len(original)!=180:
        raise ValueError('independent signed interval inventory unavailable')
    if any(type(lo) is not int or type(hi) is not int or plo>lo or phi<hi for (plo,phi),(lo,hi) in zip(original,signed)):
        raise ValueError('producer signed per-node source gradient interval understated')
    u=p.get('projected_shadow_all_R_difference_upper_integer_msun');v=q.get('all_R_K180_density_comparison_upper_integer_msun')
    if type(u) is not int or type(v) is not int or u<=0 or v<=0 or v>u:raise ValueError('false all-R K180 source-envelope ceiling')
    dif=p.get('source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc')
    if not isinstance(dif,list) or len(dif)!=180 or any(not isinstance(x,list) or len(x)!=2 or not all(type(n) is int for n in x) or x[0]>x[1] for x in dif):
        raise ValueError('source-smooth node difference interval inventory')
    return {'lens_id':p['lens_id'],'node_sha256':p['source_180_node_sha256'],
            'stored_vs_ideal_fd_max_upper_micro_msun_per_kpc':p['max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc'],
            'all_real_frozen_K180_source_density_comparison_upper_msun':u,
            'verified_original_source_nodes':180,
            'full_continuum_error_certified':False}

def aggregate(save=True):
    rows=[];sha=[]
    for lid in IDS:
        producer=P/'results'/('all180_rational_'+lid+'.json')
        independent=P/'results'/('independent_all180_'+lid+'.json')
        p=json.loads(producer.read_text());q=json.loads(independent.read_text())
        row=inspect_pair(p,q)
        if row['lens_id'].replace('+','p')!=lid:raise ValueError('out-of-order six lenses')
        rows.append(row)
        sha.append({'lens_id':row['lens_id'],'producer_sha256':digest(producer),'independent_sha256':digest(independent)})
    report={'schema':'HIST001D_FULL_ORIGINAL_180_GRID_RATIONAL_FIXED_INPUT_DENSITY_PROJECTION_CANDIDATE_V1',
            'original_46plus3_source_sha256':SOURCE,'original_parent_sha256':PARENT,
            'exact_original_source_nodes':1080,'exact_nonuniform_ideal_stencil_comparisons':1080,
            'original_frozen_density_positive_at_all_nodes':True,'mathematical_smooth_density_positive_at_all_nodes':True,
            'independent_608bit_Bessel_Lagrange_validation':True,
            'all_real_fixed_180_node_K180_projection_difference_enclosed':True,
            'selected_smooth_source_derivative_at_original_180_nodes_only':True,
            'source_float_operation_error_certified_for_arbitrary_inputs':False,
            'new_physical_continuum_source_density_certified':False,
            'full_March_H_error_or_original_offgrid_root_count_certified':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'lenses':rows,'leaf_result_hashes':sha}
    if save:
        p=P/'results/all180_aggregate.json'
        p.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('ALL180_AGGREGATE_PASS',len(rows),'node_checks',1080,'SHA',digest(p))
    return report

if __name__=='__main__':aggregate()
