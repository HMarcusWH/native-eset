#!/usr/bin/env python3
"""Source-free 21-mutation fail-closed identity and nonclaim test."""
import argparse,copy,json
from pathlib import Path
from claim_guard import validate_claims

def run(obj):
    validate_claims(obj)
    failures=[]
    def attack(label,fn):
        v=copy.deepcopy(obj);fn(v)
        try:validate_claims(v)
        except (ValueError,KeyError,TypeError):failures.append({'label':label,'result':'REJECTED'});return
        raise AssertionError('false record accepted '+label)
    attack('physical_provider',lambda o:o.update(physical_provider_admitted=True))
    attack('empirical_validation',lambda o:o.update(empirical_validation='VALIDATED'))
    attack('offgrid_source_theorem',lambda o:o.update(arbitrary_radius_original_March_source_theorem=True))
    attack('root_rule_replaced',lambda o:o.update(actual_original_solver_root_rule='PHYSICAL_Weyl'))
    attack('wrong_schema',lambda o:o.update(schema='NOT_THIS_MODEL'))
    attack('wrong_source',lambda o:o.update(conditional_original_source_sha256='0'*64))
    attack('wrong_sat_parent',lambda o:o.update(saturation_archive_sha256='0'*64))
    attack('wrong_fullH_parent',lambda o:o.update(finite_H_parent_sha256='0'*64))
    attack('wrong_nodes_total',lambda o:o.update(source_sampled_H_grid_values_replayed=1081))
    attack('wrong_root_total',lambda o:o.update(source_sampled_roots_binary64_exact_replay_count=5))
    attack('lost_lens',lambda o:o['lenses'].pop())
    attack('duplicate_lens',lambda o:o['lenses'][0].update(lens=o['lenses'][1]['lens']))
    attack('reorder_lens',lambda o:o['lenses'].reverse())
    attack('bad_hash',lambda o:o['lenses'][0].update(source_node_sha256='not-SHA'))
    attack('wrong_root_hex',lambda o:o['lenses'][0].update(source_float_root_hex='nan'))
    attack('floating_root_false',lambda o:o['lenses'][0].update(source_float_root_exact_match_to_archived_binary64=False))
    attack('strict_original_arcsec_false',lambda o:o['lenses'][0].update(strict_original_6lens_portability_CSV_arcsec_reproduced=False))
    attack('claimed_upstream',lambda o:o['lenses'][0].update(upstream_baryon_disk_shadow_projection_floating_error_proved=True))
    attack('claimed_reported_equals_finite',lambda o:o['lenses'][0].update(reported_root_is_zero_of_offgrid_finite_PL_model=True))
    attack('understated_float_error_cap',lambda o:o['lenses'][0].update(max_source_archived_H_vs_finite_PL_node_upper_micro_Msun=-1))
    attack('lost_root_gap',lambda o:o['lenses'][0].update(sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc=0))
    attack('wrong_root_order',lambda o:o['lenses'][0].update(sampled_vs_finite_root_order='exact_same_root'))
    return {'schema':'HIST001D_ORIGINAL_MARCH_FLOAT_BRIDGE_ADVERSARIAL_QA_V1','cases':failures,'all_rejected':len(failures)==22,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--receipt',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();r=run(json.loads(a.receipt.read_text()));a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print('ADVERSARIAL',len(r['cases']),'rejected',flush=True)
