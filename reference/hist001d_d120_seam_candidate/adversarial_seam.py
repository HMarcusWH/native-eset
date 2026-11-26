#!/usr/bin/env python3
"""Source-locked negative controls for D120 seam result: fail-closed and nonpromoting."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from verify_seam import check_structure,verify_source_math

def sha(b):return hashlib.sha256(b).hexdigest()

def run(receipt,sat,h,out):
    orig=json.loads(Path(receipt).read_text())
    verify_source_math(orig,sat,h)
    cases=[]
    def reject(label,change,deep=False):
        x=copy.deepcopy(orig)
        change(x)
        try:
            if deep:verify_source_math(x,sat,h)
            else:check_structure(x)
        except (ValueError,AssertionError,ArithmeticError,KeyError,IndexError,TypeError):
            cases.append({'case':label,'status':'REJECTED','source_dependent':deep})
            return
        raise AssertionError('FAIL OPEN: '+label)
    reject('schema_wrong',lambda x:x.update(schema='fake'))
    reject('source_sha',lambda x:x.update(source_original_46plus3_sha256='0'*64))
    reject('saturation_sha',lambda x:x.update(input_saturation_sha256='0'*64))
    reject('finite_parent_sha',lambda x:x.update(input_finite_H_sha256='0'*64))
    reject('original_float_parent_sha',lambda x:x.update(source_float_parent_sha256='0'*64))
    reject('wrong_D_count',lambda x:x.update(frozen_D120_nodes_binary64_replayed=1079))
    reject('wrong_circularized_S_count',lambda x:x.update(frozen_circularized_shadow_nodes_binary64_replayed=1079))
    reject('wrong_H_count',lambda x:x.update(frozen_H_nodes_binary64_replayed=1079))
    reject('falsely_physical',lambda x:x.update(physical_provider_admitted=True))
    reject('falsely_validated',lambda x:x.update(empirical_validation='VALIDATED'))
    reject('claim_full_azimuth_certified',lambda x:x.update(full_azimuth_integral_error_certified=True))
    reject('claim_original_stencil_changed',lambda x:x.update(historical_original_source_stencil_modified=True))
    reject('claim_offgrid_auspicious',lambda x:x.update(original_march_offgrid_physical_H_bound=True))
    reject('claim_scipy_error',lambda x:x.update(actual_original_March_SciPy_upstream_accuracy_proved=True))
    reject('false_counterfactual_physical',lambda x:x.update(all_six_sampled_roots_with_periodic_seam_are_counterfactual_diagnostics_only=False))
    reject('missing_lens',lambda x:x['lenses'].pop())
    reject('duplicate_lens',lambda x:x['lenses'][0].update(lens_id=x['lenses'][1]['lens_id']))
    reject('extra_lens',lambda x:x['lenses'].append(copy.deepcopy(x['lenses'][0])))
    reject('wrong_nodal_source_count',lambda x:x['lenses'][0].update(source_D120_stored_binary64_exact_count=179))
    reject('false_density_clip',lambda x:x['lenses'][0].update(stored_density_clip_floor_inactive_at_all_source_nodes=False))
    reject('invalid_seam_sign',lambda x:x['lenses'][2]['rigorous_exact_real_periodic_seam_at_crossing_endpoints_integer_micro_Msun'][0].__setitem__(0,0))
    reject('claim_certified_root_shift',lambda x:x['lenses'][0].update(counterfactual_output_not_certified_root_shift=False))
    reject('wrong_counterfactual_root_positive',lambda x:x['lenses'][2].update(counterfactual_root_shift_kpc_float=-1))
    reject('wrong_angular_sha_deep',lambda x:x['lenses'][0].update(source_120_angle_sha256='0'*64),deep=True)
    reject('wrong_endpoint_R_deep',lambda x:x['lenses'][3]['original_crossing_cell_R_hex'].__setitem__(0,'0x1.0000000000000p+1'),deep=True)
    reject('wrong_pct_enclosure_deep',lambda x:x['lenses'][2]['source_periodic_seam_percent_of_D_source_at_crossing_endpoints_integer_micro_percent'][0].__setitem__(0,1000000),deep=True)
    reject('understated_exact_seam_bound_deep',lambda x:x['lenses'][4]['rigorous_exact_real_periodic_seam_at_crossing_endpoints_integer_micro_Msun'][0].__setitem__(1,1),deep=True)
    reject('wrong_new_float_root_deep',lambda x:x['lenses'][5].update(counterfactual_periodic_seam_sampled_first_root_hex='0x1.0000000000000p+0'),deep=True)
    reject('wrong_new_float_shift_deep',lambda x:x['lenses'][5].update(counterfactual_root_shift_kpc_float=0.0001),deep=True)
    reject('wrong_disk_node_deep',lambda x:x['lenses'][2]['source_D120_stored_Msun_at_crossing_endpoints_hex'].__setitem__(0,'0x1.0000000000000p+0'),deep=True)
    obj={'schema':'HIST001D_D120_SEAM_ADVERSARIAL_QA_V1','source_result_sha256':sha(Path(receipt).read_bytes()),'cases':cases,
         'all_rejected':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    Path(out).write_bytes((json.dumps(obj,sort_keys=True,indent=2)+'\n').encode())
    print('ADVERSARIAL_QA_REJECTED',len(cases),'SHA',sha(Path(out).read_bytes()))
    return obj

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--saturation',type=Path,required=True)
    p.add_argument('--finite-h',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    run(a.receipt,a.saturation,a.finite_h,a.out)
