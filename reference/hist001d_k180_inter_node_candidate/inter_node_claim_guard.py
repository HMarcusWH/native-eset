#!/usr/bin/env python3
"""Fast structural/claim firewall; NOT a substitute for Fraction witness proof."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
EXPECTED_CELLS=179
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def validate(inter,bv,meta):
    if len(inter)!=6 or len(bv)!=6:raise ValueError('exactly six lenses required')
    if [x.get('lens_id') for x in inter]!=list(LENSES) or [x.get('lens') for x in bv]!=list(LENSES):raise ValueError('wrong lens identities/order')
    if meta.get('source_original_46plus3_sha256')!=SOURCE_SHA or meta.get('physical_provider_admitted') is not False or meta.get('empirical_validation')!='NOT_ESTABLISHED' or meta.get('global_ideal_K180_vs_continuum_root_error_proved') is not False or meta.get('smooth_model_physical_Weyl_provider_admitted') is not False:
        raise ValueError('source or forbidden claim')
    if meta.get('selected_Mstar_prime_all_real_positive') is not True or meta.get('all_six_root_band_BV_bounds_certified') is not True or meta.get('useful_for_original_March_root_gap') is not False:
        raise ValueError('missing proof classification')
    if any(type(y)!=int or y<=0 for y in meta.get('parent_sha_lock_byte_counts',[])) or len(meta.get('parent_sha_lock_byte_counts',[]))!=2:
        raise ValueError('source parent metadata')
    for j,(l,b) in enumerate(zip(inter,bv)):
        if l.get('schema')!='HIST001D_SELECTED_MSTAR_REAL_INTEGRAL_BESSEL_INTER_NODE_MPRIME_V1' or l.get('source_scope')!='SELECTED_HISTORICAL_ACCELERATION_EQUIVALENT_MSTAR_NOT_PHYSICAL':
            raise ValueError('inter-node schema/scope')
        if l.get('all_real_selected_Mprime_positive') is not True or l.get('nodes')!=180 or l.get('unresolved')!=[]:
            raise ValueError('uncertified inter-node result')
        if l.get('physical_provider_admitted') is not False or l.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('inter-node claim violation')
        if len(l.get('panels',[]))!=l.get('accepted_panels') or len(l.get('midpoints',[]))!=l.get('extra_points') or len(l['panels'])<179:
            raise ValueError('panel / midpoint counts')
        if len(l.get('node_sha256',''))!=64:raise ValueError('node hash not bound')
        grouped={i:[] for i in range(179)}
        for row in l['panels']:
            if row.get('cell') not in grouped or type(row.get('Mprime_lower_micro')) is not int or row['Mprime_lower_micro']<=0 or type(row.get('Mprime_upper_micro')) is not int or row['Mprime_upper_micro']<row['Mprime_lower_micro'] or type(row.get('Msecond_abs_ceil')) is not int or row['Msecond_abs_ceil']<0:
                raise ValueError('bad signed panel witness')
            grouped[row['cell']].append(row)
        if any(not grouped[i] for i in grouped):raise ValueError('missing source cell')
        if b.get('accepted_original_radial_cells')!=EXPECTED_CELLS or b.get('accepted_subpanels')!=len(l['panels']) or b.get('source_scope')!='SELECTED_MSTAR_ONLY_NOT_PHYSICAL_SOURCE' or b.get('useful_for_full_root_gap') is not False:
            raise ValueError('BV scope / counts')
        if b.get('physical_provider_admitted') is not False or b.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('BV forbidden claim')
        if b.get('uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun',0)<=0 or b.get('uniform_band_error_kernel_variation_ceiling_Msun',0)<0 or b.get('uniform_band_error_Mprime_variation_ceiling_Msun',0)<0 or b.get('uniform_band_original_weight_rounding_ceiling_micro_Msun',0)<0:
            raise ValueError('invalid BV enclosure')
        pbox=b.get('P_mathematical_continuum_all_A_band_integer_Msun_enclosure',[])
        if len(pbox)!=2 or not 0<pbox[0]<pbox[1]:raise ValueError('invalid positive P interval')
    return True

def digest(data):return hashlib.sha256(data).hexdigest()
def load(root:Path):
    inter=[json.loads((root/f'results/continuous_lens_{i}.json').read_text()) for i in range(6)]
    bv=[json.loads((root/f'results/bv_band_lens_{i}.json').read_text()) for i in range(6)]
    meta=json.loads((root/'results/aggregate.json').read_text())
    validate(inter,bv,meta)
    return inter,bv,meta
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args()
    load(a.root);print('CLAIM_GUARD_PASS')
