#!/usr/bin/env python3
"""Mutate one protected receipt, summary or cross-grid record; insist fail-closed."""
from __future__ import annotations
import json,copy,hashlib
from pathlib import Path
from claim_guard import validate
BASE=Path(__file__).resolve().parents[2]

def load():
    reports=[json.loads((BASE/'results'/f'lens_{j}.json').read_text()) for j in range(6)]
    return (reports,json.loads((BASE/'results/stencil_summary.json').read_text()),
            json.loads((BASE/'results/cross_resolution.json').read_text()))

def run():
    original=load();assert validate(*original)
    cases=[]
    def tamper(label,mutate):
        x=copy.deepcopy(original);mutate(x)
        try:validate(*x)
        except (ValueError,TypeError,KeyError,IndexError,AssertionError,ZeroDivisionError):
            cases.append({'label':label,'verdict':'REJECTED'});return
        raise AssertionError('tamper accepted: '+label)
    tamper('missing_lens',lambda x:x[0].pop())
    tamper('duplicate_lens',lambda x:x[0][1]['lenses'][0].update(lens_id=x[0][0]['lenses'][0]['lens_id']))
    tamper('empty_nodes',lambda x:x[0][2]['lenses'][0].update(nodes=[]))
    tamper('missing_one_node',lambda x:x[0][4]['lenses'][0]['nodes'].pop())
    tamper('duplicate_node_index',lambda x:x[0][0]['lenses'][0]['nodes'][1].update(index=0))
    tamper('bad_node_radius_grid',lambda x:x[0][0]['lenses'][0]['nodes'][0].update(grid_points_used=0))
    tamper('wrong_Bessel_engine',lambda x:x[0][0].update(engine='old_series'))
    tamper('wrong_schema',lambda x:x[0][0].update(schema='fake'))
    tamper('wrong_source_digest',lambda x:x[0][0].update(source_original_46plus3_SHA256='0'*64))
    tamper('old_source_noshare',lambda x:x[0][0].update(source_saturation_SHA256='f'*64))
    tamper('claim_physical',lambda x:x[0][0].update(physical_provider_admitted=True))
    tamper('claim_empirical',lambda x:x[0][0].update(empirical_validation='VALIDATED'))
    tamper('claim_lens_complete',lambda x:x[0][0].update(all180_nodes_certified=False))
    tamper('claim_six_in_one',lambda x:x[0][0].update(all_six_lenses_in_this_receipt=True))
    tamper('invert_mass',lambda x:x[0][0]['lenses'][0]['nodes'][0].update(selected_M_interval=['2','1']))
    tamper('invert_derivative',lambda x:x[0][0]['lenses'][0]['nodes'][0].update(selected_Mprime_interval=['1','-1']))
    tamper('zero_derivative',lambda x:x[0][0]['lenses'][0]['nodes'][0].update(selected_Mprime_interval=['0','0']))
    tamper('invalid_K_error',lambda x:x[0][0]['lenses'][0]['nodes'][0].update(trapezoid_K_upper_bound='-1'))
    tamper('invalid_tail',lambda x:x[0][0]['lenses'][0]['nodes'][0].update(tail_K_upper_bound='-1'))
    tamper('understated_stencil',lambda x:x[1]['lenses'][0].update(new_integral_K_all_aperture_source_to_ideal_stencil_bound_micro_Msun=9999999999))
    tamper('promote_summary',lambda x:x[1].update(physical_provider_admitted=True))
    tamper('wrong_summary_node_scope',lambda x:x[1].update(six_lenses_all_180_nodes=False))
    tamper('wrong_cross_schema',lambda x:x[2].update(schema='fake'))
    tamper('wrong_cross_step',lambda x:x[2]['checks'][0].update(two_grid_step_h=['1/2','1/3']))
    tamper('wrong_cross_count',lambda x:x[2].update(two_grid_cross_checks=0))
    tamper('false_Wronskian',lambda x:x[2]['checks'][0].update(I0K1_plus_I1K0_contains_exact_inverse_y_on_both_grids=False))
    tamper('cross_claim_phys',lambda x:x[2].update(physical_provider_admitted=True))
    out={'schema':'HIST001D_BESSEL_REAL_INTEGRAL_ADVERSARIAL_V1','all_rejected':True,'cases':cases,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    path=BASE/'results/adversarial_qa.json';dat=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode();path.write_bytes(dat)
    print('QA_REJECTED',len(cases),'SHA256',hashlib.sha256(dat).hexdigest())
    return out
if __name__=='__main__':run()
