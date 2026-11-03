"""Strict source-only claim/status and receipt-shape guard, not data replay."""
from __future__ import annotations
import math
from float_bridge import LENSES,SAT_SHA,H_SHA,SOURCE_SHA

SCHEMA='HIST001D_ORIGINAL_MARCH180_IEEE754_SAMPLED_H_POSTPROCESSING_AND_FINITE_PL_GAP_V1'
HEX64=set('0123456789abcdef')

def hash_ok(s):return isinstance(s,str) and len(s)==64 and set(s)<=HEX64

def validate_claims(o):
    if o.get('schema')!=SCHEMA:raise ValueError('schema')
    if o.get('conditional_original_source_sha256')!=SOURCE_SHA:raise ValueError('source authority')
    if o.get('saturation_archive_sha256')!=SAT_SHA or o.get('finite_H_parent_sha256')!=H_SHA:raise ValueError('parents')
    if o.get('source_sampled_H_grid_values_replayed')!=1080 or o.get('source_sampled_roots_binary64_exact_replay_count')!=6:raise ValueError('counts')
    if o.get('physical_provider_admitted') is not False or o.get('empirical_validation')!='NOT_ESTABLISHED' or o.get('arbitrary_radius_original_March_source_theorem') is not False:raise ValueError('scientific promotion')
    if o.get('actual_original_solver_root_rule')!='FIRST_SIGN_CHANGE_PLUS_BINARY64_LINEAR_RESIDUAL_INTERPOLATION':raise ValueError('root rule')
    lenses=o.get('lenses')
    if not isinstance(lenses,list) or len(lenses)!=6 or [v.get('lens') for v in lenses]!=list(LENSES):raise ValueError('lens set or order')
    for x in lenses:
        if not hash_ok(x.get('source_node_sha256')) or not hash_ok(x.get('archived_source_R_H_pair_sha256')):raise ValueError('source array hash')
        if (x.get('all_180_archived_H_exactly_reproduced_from_final_stored_source_columns') is not True or
            x.get('source_float_root_exact_match_to_archived_binary64') is not True or
            x.get('strict_original_6lens_portability_CSV_arcsec_reproduced') is not True or
            x.get('all_source_R_nodes_have_same_sign_as_explicit_finite_PL_extension') is not True):raise ValueError('audit status')
        if (x.get('original_floating_offgrid_source_error_bound_proved') is not False or
            x.get('upstream_baryon_disk_shadow_projection_floating_error_proved') is not False or
            x.get('reported_root_is_zero_of_offgrid_finite_PL_model') is not False):raise ValueError('false scope')
        if x.get('sampled_vs_finite_root_order') not in ('sampled_left_of_finite','sampled_right_of_finite'):raise ValueError('root ordering')
        if not isinstance(x.get('source_crossing_index'),int) or not 0<=x['source_crossing_index']<179:raise ValueError('crossing index')
        try:root=float.fromhex(x['source_float_root_hex'])
        except (TypeError,ValueError):raise ValueError('root encoding') from None
        if not math.isfinite(root) or not 0.02<root<120:raise ValueError('root range')
        for key,upper_bound in [
            ('max_exact_real_postprocessing_vs_binary64_archived_H_upper_micro_Msun',100000),
            ('max_source_archived_H_vs_finite_PL_node_upper_micro_Msun',100000),
            ('max_frozen_geometric_Snode_vs_selected_PL_S0_upper_micro_Msun',1000),
            ('source_float_root_vs_exact_archived_sampled_PL_root_upper_atto_kpc',2000),
            ('source_float_root_vs_exact_stored_component_algebra_nodal_PL_root_upper_atto_kpc',2000),
        ]:
            val=x.get(key)
            if type(val) is not int or not 0<=val<upper_bound:raise ValueError('unbounded claim '+key)
        if not isinstance(x.get('sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc'),int) or x['sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc']<100000:raise ValueError('claimed separation')
        bracket=x.get('original_selected_finite_root_bracket')
        if not isinstance(bracket,list) or len(bracket)!=2 or not all(isinstance(y,str) and '/' in y for y in bracket):raise ValueError('finite bracket omitted')
    return True
