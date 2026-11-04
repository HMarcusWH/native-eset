#!/usr/bin/env python3
"""Negative-control tests for targeted M* quadrature-zero existence claims.

Attacks the source-free witness contract, not its inherited 512-bit Bessel
implementation. The separate verify_targeted.py checks exact source arithmetic.
"""
from __future__ import annotations
import copy,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from witness_contract import validate_receipt  # noqa: E402

def sha(b):return hashlib.sha256(b).hexdigest()

def run():
    originals=[json.loads((ROOT/'results'/f'targeted_lens_{j}.json').read_bytes()) for j in range(6)]
    for j,v in enumerate(originals):validate_receipt(v,j)
    cases=[]
    def tamper(label,fn,j=0):
        d=copy.deepcopy(originals[j]);fn(d)
        try:validate_receipt(d,j)
        except (ValueError,TypeError,KeyError,ZeroDivisionError):
            cases.append({'case':label,'status':'REJECTED','lens_index':j});return
        raise AssertionError('Mutation accepted: '+label)
    tamper('wrong_source_identity',lambda d:d.update(source_46plus3_sha256='0'*64))
    tamper('wrong_cancel_parent',lambda d:d.update(protected_cancel_parent_sha256='0'*64))
    tamper('wrong_inter_parent',lambda d:d.update(protected_inter_node_parent_sha256='0'*64))
    tamper('wrong_lens_order',lambda d:d.update(lens='J0915+4211'))
    tamper('missing_node_hash',lambda d:d.update(source_node_sha256=''))
    tamper('missing_signed_parent_hash',lambda d:d.update(parent_signed_lens_sha256=''))
    tamper('physical_source_promoted',lambda d:d.update(physical_provider_admitted=True))
    tamper('empirical_claim_promoted',lambda d:d.update(empirical_validation='VALIDATED'))
    tamper('einstein_root_claim_promoted',lambda d:d.update(Einstein_residual_root_count_certified=True))
    tamper('one_sign_false_claim',lambda d:d.update(selected_smooth_quadrature_one_sign=True))
    tamper('whole_band_sign_false_claim',lambda d:d.update(all_sign_definite_whole_band=True))
    tamper('global_uniqueness_false_claim',lambda d:d.update(global_selected_smooth_root_uniqueness_proved=True))
    tamper('wrong_selected_mass_scope',lambda d:d.update(mathematical_scope='PHYSICAL_SHADOW_SOURCE'))
    tamper('negative_aperture_start',lambda d:d['A_band'].__setitem__(0,'-1'))
    tamper('reversed_aperture_band',lambda d:d['A_band'].reverse())
    tamper('missing_aperture_anchor',lambda d:d['anchors'].pop())
    tamper('duplicate_aperture_anchor',lambda d:d['anchors'][1].update(index=d['anchors'][0]['index']))
    tamper('wrong_exact_aperture',lambda d:d['anchors'][0].update(A='1'))
    tamper('wrong_anchor_sign',lambda d:d['anchors'][0].update(strict_sign=1))
    tamper('faked_endpoint_difference',lambda d:d['anchors'][0]['signed_D'].__setitem__(0,str(F(d['anchors'][0]['signed_D'][0])+1)))
    tamper('understated_integer_lower',lambda d:d['anchors'][0]['integer_D'].__setitem__(0,d['anchors'][0]['integer_D'][0]+1))
    tamper('understated_integer_upper',lambda d:d['anchors'][0]['integer_D'].__setitem__(1,d['anchors'][0]['integer_D'][1]-1))
    tamper('false_zero_count',lambda d:d.update(certified_distinct_zero_lower_bound=100))
    tamper('lost_zero_interval',lambda d:d['certified_zero_intervals'].pop())
    tamper('reversed_zero_sign',lambda d:d['certified_zero_intervals'][0].update(right_sign=-d['certified_zero_intervals'][0]['right_sign']))
    tamper('false_multiple_zero_claim',lambda d:d.update(certified_distinct_zero_lower_bound=1),j=2)
    tamper('missing_refined_midpoint',lambda d:d['split_history'].pop())
    tamper('wrong_midpoint_count',lambda d:d.update(added_integral_Bessel_midpoints=127))
    tamper('midpoint_not_dyadic',lambda d:d['split_history'][0].update(mid=d['split_history'][0]['a']))
    tamper('false_midpoint_Bessel_F_sign',lambda d:d['split_history'][0].update(F=['-1','-1']))
    tamper('false_midpoint_Mprime_sign',lambda d:d['split_history'][0].update(Mp=['-1','-1']))
    tamper('missing_leaf',lambda d:d['leaves'].pop())
    tamper('duplicate_leaf',lambda d:d['leaves'].__setitem__(1,copy.deepcopy(d['leaves'][0])))
    tamper('negative_curvature_cap',lambda d:d['leaves'][0].update(C_integer_Msecond_abs=-1))
    tamper('understated_curvature_cap',lambda d:d['leaves'][0].update(C_integer_Msecond_abs=0))
    tamper('zero_Mprime_lower',lambda d:d['leaves'][0].update(positive_Mprime_lower='0'))
    tamper('negative_Peano_kernel_weight',lambda d:d['leaves'][0].update(W_upper='-1'))
    tamper('Peano_error_understatement',lambda d:d.update(E_symmetric_ceiling_integer_Msun=0))
    tamper('Peano_no_improvement',lambda d:d.update(inherited_prior_symmetric_ceiling_integer_Msun=0))
    tamper('unsupported_peer_review_promotion',lambda d:d.update(external_peer_review_passed=True))
    output={'schema':'HIST001D_TARGETED_MSTAR_QUADRATURE_ZERO_ADVERSARIAL_QA_V1','cases':cases,
            'total_rejected':len(cases),'all_rejected':True,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    path=ROOT/'results/adversarial_targeted.json'
    path.write_text(json.dumps(output,sort_keys=True,indent=2)+'\n')
    print('TARGETED_ADVERSARIAL_QA_PASS',len(cases),'SHA',sha(path.read_bytes()))
    return output

if __name__=='__main__':run()
