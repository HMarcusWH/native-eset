#!/usr/bin/env python3
"""Strict structural claim firewall for full-H candidate aggregate; no protected data needed."""
from __future__ import annotations
import copy,json
from fractions import Fraction as F
from pathlib import Path
from full_h_finite_source import LENSES,SOURCE_SHA

def validate(r):
    if r.get('schema')!='HIST001D_MARCH180_FULL_H_PL_SOURCE_VS_SELECTED_SMOOTH_MATHEMATICAL_BRIDGE_V1':raise ValueError('schema')
    if r.get('original_source_46plus3_sha256')!=SOURCE_SHA:raise ValueError('original source sha')
    if r.get('physical_provider_admitted') is not False or r.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('scientific claim')
    if any(r.get(k) is not True for k in ('source_PL_finite_full_H_global_one_root_each_6_of_6',
                    'selected_Mstar_smooth_full_H_at_least_one_in_each_root_cell_6_of_6',
                    'selected_smooth_roots_in_original_cell_strictly_left_of_finite_PL_roots')):raise ValueError('contract missing')
    if any(r.get(k) is not False for k in ('selected_smooth_global_root_uniqueness_proved',
                    'full_original_March_arbitrary_radius_floating_H_error_proved',
                    'current_native_ESET_1_7_2_lensing_provider_validated')):raise ValueError('false promotion')
    if r.get('finite_witness',{}).get('status')!='PASS_CONDITIONAL_EXACT_RATIONAL_FINITE_H_WITNESS':raise ValueError('arithmetic witness missing')
    w=r['finite_witness']
    if w.get('global_sign_leaves',0)<6*178 or w.get('crossing_derivative_leaves',0)<6 or w.get('lenses')!=6:
        raise ValueError('witness census')
    x=r.get('lenses')
    if not isinstance(x,list) or len(x)!=6 or [v.get('lens') for v in x]!=list(LENSES):raise ValueError('lens identity/count/order')
    for t in x:
        if t.get('source_root_one_per_whole_original_180_domain') is not True:raise ValueError('finite model root not closed')
        if t.get('historical_sampled_root_not_source_PL_finite_H_root') is not True:raise ValueError('reported root identity')
        if t.get('selected_continuum_H_has_at_least_one_root_strictly_left_of_finite_root') is not True or t.get('selected_continuum_roots_in_cell_to_right_of_finite_root_excluded') is not True:raise ValueError('smooth root order')
        if t.get('selected_continuum_global_root_uniqueness_proved') is not False:raise ValueError('smooth false uniqueness')
        if t.get('global_non_crossing_H_sign_subbands',0)<178 or t.get('root_cell_derivative_subbands',0)<1:raise ValueError('missing subband coverage')
        if t['H_selected_continuum_left_lower_integer_Msun']<=0 or t['H_selected_continuum_right_upper_integer_Msun']>=0:raise ValueError('smooth endpoint sign')
        if t['full_H_source_minus_H_smooth_strictly_greater_than_integer_Msun']!=t['whole_band_QminusP_mathematical_gap_lower_integer_Msun']-1:raise ValueError('gap transfer')
        if t['full_H_source_minus_H_smooth_strictly_greater_than_integer_Msun']<=0 or t.get('source_S0_PL_minus_Q_lower_strictly_greater_than_minus_1_Msun') is not True:raise ValueError('source-PL gap')
        n,d=t['source_node_gap_upper_exact'];g=F(int(n),int(d))
        if not 0<=g<1:raise ValueError('source node interpolation error')
        if not isinstance(t['H_source_at_original_reported_root_integer_Msun'],list) or len(t['H_source_at_original_reported_root_integer_Msun'])!=2:raise ValueError('original reported source root')
        a,b=t['H_source_at_original_reported_root_integer_Msun']
        if a>b or not (a>0 or b<0):raise ValueError('source sampled root interval zero')
        pair=t['finite_source_unique_root_bracket_exact_rational']
        if len(pair)!=2 or not F(pair[0])<F(pair[1]):raise ValueError('finite root bracket')
    return True

def run_adversarial(original):
    validate(original)
    cases=[]
    def reject(name,fun):
        v=copy.deepcopy(original);fun(v)
        try:validate(v)
        except (ValueError,KeyError,TypeError,AssertionError,ZeroDivisionError):
            cases.append({'mutation':name,'rejected':True});return
        raise AssertionError('accepted adversarial mutation: '+name)
    reject('fake_provider',lambda x:x.update(physical_provider_admitted=True))
    reject('fake_empirical_validation',lambda x:x.update(empirical_validation='VALIDATED'))
    reject('wrong_source',lambda x:x.update(original_source_46plus3_sha256='0'*64))
    reject('no_global_finite_root',lambda x:x.update(source_PL_finite_full_H_global_one_root_each_6_of_6=False))
    reject('fake_smooth_global_uniqueness',lambda x:x.update(selected_smooth_global_root_uniqueness_proved=True))
    reject('fake_original_floating_cert',lambda x:x.update(full_original_March_arbitrary_radius_floating_H_error_proved=True))
    reject('fake_physical_lensing',lambda x:x.update(current_native_ESET_1_7_2_lensing_provider_validated=True))
    reject('no_full_root_arithmetic',lambda x:x['finite_witness'].update(status='UNKNOWN'))
    reject('missing_one_lens',lambda x:x['lenses'].pop())
    reject('duplicate_lens',lambda x:x['lenses'][2].update(lens=x['lenses'][1]['lens']))
    reject('wrong_lens_order',lambda x:x['lenses'].reverse())
    reject('false_finite_root',lambda x:x['lenses'][0].update(source_root_one_per_whole_original_180_domain=False))
    reject('false_selected_root_order',lambda x:x['lenses'][1].update(selected_continuum_roots_in_cell_to_right_of_finite_root_excluded=False))
    reject('fake_smooth_uniqueness_lens',lambda x:x['lenses'][2].update(selected_continuum_global_root_uniqueness_proved=True))
    reject('wrong_selected_left_sign',lambda x:x['lenses'][3].update(H_selected_continuum_left_lower_integer_Msun=-1))
    reject('wrong_selected_right_sign',lambda x:x['lenses'][4].update(H_selected_continuum_right_upper_integer_Msun=0))
    reject('missing_crossing_cert',lambda x:x['lenses'][5].update(root_cell_derivative_subbands=0))
    reject('source_gap_zero',lambda x:x['lenses'][0].update(full_H_source_minus_H_smooth_strictly_greater_than_integer_Msun=0))
    reject('invalid_node_gap',lambda x:x['lenses'][1].update(source_node_gap_upper_exact=['2','1']))
    reject('wrong_gap_relation',lambda x:x['lenses'][2].update(whole_band_QminusP_mathematical_gap_lower_integer_Msun=1))
    reject('sample_root_claim_false',lambda x:x['lenses'][3].update(H_source_at_original_reported_root_integer_Msun=[-1,1]))
    reject('backwards_finite_bracket',lambda x:x['lenses'][4].update(finite_source_unique_root_bracket_exact_rational=['2','1']))
    reject('missing_all_real_witnesses',lambda x:x['finite_witness'].update(global_sign_leaves=170))
    return {'schema':'HIST001D_FULL_H_CANDIDATE_ADVERSARIAL_QA_V1',
            'all_rejected':True,'mutations':cases,'count':len(cases),
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();v=run_adversarial(json.loads(a.receipt.read_text()))
    a.out.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
    print('QA',v['count'],'mutations rejected')
