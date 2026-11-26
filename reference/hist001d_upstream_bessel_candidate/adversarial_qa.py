#!/usr/bin/env python3
"""Fail-closed adversarial scope and numerical receipt guards.

Mutation rejection does not substitute for an independent mathematical proof.
"""
from __future__ import annotations
import json,copy,hashlib,argparse
from pathlib import Path
from independent_stencil_check import check, SOURCE_SHA, LENSES
sha=lambda x:hashlib.sha256(x).hexdigest()
BANNED={'physical_continuum_source_selected','source_floats_arbitrary_platforms_certified',
        'original_offgrid_root_uniqueness_proved','native_eset_v172_provider_admitted',
        'continuous_bessel_error_certified','original_march_full_h_root_count_certified',
        'original_march_Weyl_lensing_validated','blind_holdout_validation_passed'}
def validate(root,sat,a):
    if a.get('input_saturation_sha256')!='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce':raise ValueError('parent')
    if a.get('source_original_46plus3_sha256')!=SOURCE_SHA:raise ValueError('source')
    if a.get('inherited_exact_real_bessel_512bit_interval_all180_and_independent_spot_608bit') is not True:raise ValueError('source branch')
    if a.get('source_rounding_split_applies_only_to_frozen_original_radii') is not True:raise ValueError('scope original nodes')
    if a.get('all_aperture_bound_applies_only_to_frozen_K180_mass_stencil_not_continuous_projection') is not True:raise ValueError('scope K180')
    if a.get('unseen_scipy_ulps_and_alternate_platforms_certified') is not False:raise ValueError('foreign floating platforms')
    if a.get('same_source_physical_density_or_Weyl_authorized') is not False:raise ValueError('physical claim')
    if any(a.get(flag) is True for flag in BANNED):raise ValueError('prohibited claim')
    if a.get('source_scipy_version_replayed') is None or a.get('source_numpy_version_replayed') is None:raise ValueError('runtime versions')
    if len(a.get('lenses',[]))!=6 or [x['lens_id'] for x in a['lenses']]!=LENSES:raise ValueError('lens order')
    for v in a['lenses']:
        if len(v['root_neighborhood_4_node_Bessel_gbar_gate_mass_replay'])!=4:raise ValueError('spot count')
        if len(v['crossing_node_gradient_sourcefloat_vs_math_split'])!=2:raise ValueError('crossing-gradient count')
        if not v['selected_mass_not_physical_source'] or not v['per_node_512bit_prior_certificate_reused']:raise ValueError('source truth')
        if v['rounding_only_stored_rho_vs_ideal_stencil_of_current_source_float_mass_all_apertures_micro_Msun_upper']<0:raise ValueError('negative bound')
        for s in v['root_neighborhood_4_node_Bessel_gbar_gate_mass_replay']:
            for key in ('source_Mshadow_minus_selected_math_interval_integer_micro_Msun','source_bary_acc_mass_minus_selected_Bessel_math_interval_integer_micro_Msun','source_epsilon_minus_selected_math_interval_integer_femto'):
                z=s[key]
                if not isinstance(z,list) or len(z)!=2 or any(type(n) is not int for n in z) or z[0]>z[1]:raise ValueError('bad spot interval')
            if not s['independent_608bit_selected_Bessel_mass_interval_overlaps']:raise ValueError('independent Bessel')
    return check(sat,root,a)

def audit(root,sat,expected):
    validate(root,sat,expected)
    cases=[]
    def mutate(name,fn):
        a=copy.deepcopy(expected);fn(a)
        try:validate(root,sat,a)
        except (ValueError,KeyError,TypeError,AssertionError,FileNotFoundError):cases.append({'label':name,'status':'REJECTED'});return
        raise AssertionError('accepted malicious claim '+name)
    mutate('physical_provider',lambda x:x.update(physical_provider_admitted=True))
    mutate('empirical_validation',lambda x:x.update(empirical_validation='VALIDATED'))
    mutate('newly_invented_physical_density',lambda x:x.update(physical_continuum_source_selected=True))
    mutate('unseen_SciPy_ulps',lambda x:x.update(unseen_scipy_ulps_and_alternate_platforms_certified=True))
    mutate('false_continuum_projection',lambda x:x.update(continuous_radii_Bessel_or_gradient_error_certified=True))
    mutate('false_original_H_uniqueness',lambda x:x.update(original_offgrid_root_uniqueness_proved=True))
    mutate('incorrect_source_composite',lambda x:x.update(source_original_46plus3_sha256='0'*64))
    mutate('incorrect_source_parent',lambda x:x.update(input_saturation_sha256='0'*64))
    mutate('missing_lens',lambda x:x['lenses'].pop())
    mutate('duplicate_lens',lambda x:x['lenses'][1].update(lens_id=x['lenses'][0]['lens_id']))
    mutate('missing_mass_file',lambda x:x['lenses'][0].update(original_replayed_float_mass_binary_file='inputs/does_not_exist.be64'))
    mutate('wrong_mass_sha',lambda x:x['lenses'][1].update(original_replayed_float_mass_binary_sha256='0'*64))
    mutate('understated_round_error',lambda x:x['lenses'][2].update(rounding_only_stored_rho_vs_ideal_stencil_of_current_source_float_mass_all_apertures_micro_Msun_upper=0))
    mutate('understated_inherited_math',lambda x:x['lenses'][0].update(inherited_512bit_full_all180_source_vs_selected_math_stencil_all_apertures_micro_Msun_upper=0))
    mutate('understated_triangle',lambda x:x['lenses'][0].update(upstream_sourcefloat_stencil_to_selected_ideal_math_stencil_all_apertures_triangle_micro_Msun_upper=0))
    mutate('false_180_replay',lambda x:x.update(all_source_shadow_density_nodes_reproduced_bitwise=1079))
    mutate('clip_falsification',lambda x:x['lenses'][0].update(unclipped_positive_mass_gradient_density_nodes=0))
    mutate('epsilon_floor_falsification',lambda x:x['lenses'][0].update(epsilon_floor_inactive_nodes=0))
    mutate('crossing_index_falsification',lambda x:x['lenses'][3].update(original_root_cell_index=3))
    mutate('selected_mass_physical',lambda x:x['lenses'][4].update(selected_mass_not_physical_source=False))
    mutate('missing_Bessel_spot',lambda x:x['lenses'][3]['root_neighborhood_4_node_Bessel_gbar_gate_mass_replay'].pop())
    mutate('forged_Bessel_inference',lambda x:x['lenses'][5]['root_neighborhood_4_node_Bessel_gbar_gate_mass_replay'][1].update(independent_608bit_selected_Bessel_mass_interval_overlaps=False))
    mutate('spot_interval_wrong_order',lambda x:x['lenses'][1]['root_neighborhood_4_node_Bessel_gbar_gate_mass_replay'][1].update(source_Mshadow_minus_selected_math_interval_integer_micro_Msun=[10,-10]))
    mutate('node_source_sha',lambda x:x['lenses'][5].update(original_node_sha256='0'*64))
    mutate('deleted_crossing_gradient',lambda x:x['lenses'][4]['crossing_node_gradient_sourcefloat_vs_math_split'].pop())
    mutate('retroactively_claimed_holdout',lambda x:x.update(blind_holdout_validation_passed=True))
    return {'schema':'HIST001D_BESSEL_FLOAT_SOURCE_COMPONENT_ADVERSARIAL_V1',
      'cases':cases,'all_rejected':len(cases)==26,
      'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--sat',type=Path,required=True);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--receipt',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();data=json.loads(args.receipt.read_bytes())
    result=audit(args.root,args.sat,data)
    if not result['all_rejected']:raise ValueError('missing tamper rejections')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print('ADVERSARIAL',len(result['cases']),'REJECTED',sha(args.out.read_bytes()))
