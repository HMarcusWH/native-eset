#!/usr/bin/env python3
"""Source/hash-bound assembly of six signed selected-M* aperture-band receipts."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from verify_affine_signed import ROOT,reference_inputs,check_structural,sha
LENS_COUNT=6

def assemble():
    z,caps,bands,_=reference_inputs()
    output=[]
    for j in range(LENS_COUNT):
        p=ROOT/'results'/f'signed_lens_{j}.json'
        v=json.loads(p.read_text())
        prior=json.loads(z.read(f'results/bv_band_lens_{j}.json'))
        check_structural(v,bands[j],caps[j],prior)
        old=prior['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun']
        new=v['max_abs_new_signed_band_upper_integer_Msun']
        if old<=new or new<=0:raise ValueError('nonimproving signed bound')
        output.append({'lens':caps[j]['lens_id'],'source_node_sha256':caps[j]['node_sha256'],
            'aperture_subbands':v['n'],
            'Qsampled_derivative_minus_Pselected_all_band_integer_Msun_enclosure':v['aggregate_signed_Q_deriv_minus_P_integer'],
            'symmetric_Peano_remainder_ceiling_integer_Msun':v['independently_certifiable_symmetric_peano_remainder_ceiling_Msun'],
            'inherited_broad_BV_ceil_integer_Msun':old,
            'new_max_abs_enclosure_integer_Msun':new,'old_to_new_improvement_factor_floor':old//new,
            'receipt_SHA256':sha(p.read_bytes()),
            'full_band_sign_definite':False})
    out={'schema':'HIST001D_MARCH180_AFFINE_MASS_CANCELLATION_AWARE_BAND_V1',
        'original_source_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
        'protected_parent_sha256':'63c4df7dcc4e5493fe9e2ea667ebb1a7d8ec418a8d03400096eb5fedf53d4691',
        'six_lenses':output,'total_verified_aperture_subbands':sum(x['aperture_subbands'] for x in output),
        'conditional_real_radial_mass_derivative_certificate_inherited':True,
        'derived_from_selected_acceleration_equivalent_Mstar_only':True,
        'all_sign_definite_bands':False,
        'all_root_displacements_or_smooth_uniqueness_proved':False,
        'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
        'claims_no_new_original_off_grid_source_implementation':True,
        'scientifically_useful_root_error_threshold_passed':False,
        'method':'SIGNED_MASS_AFFINE_J_EXACT_INTERVAL_PLUS_PEANO_RADIAL_CURVATURE'}
    dest=ROOT/'results/aggregate.json'
    dest.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('SIGNED_AFFINE_ASSEMBLED',len(output),'subbands',out['total_verified_aperture_subbands'],'SHA',sha(dest.read_bytes()))
    return out

if __name__=='__main__':assemble()
