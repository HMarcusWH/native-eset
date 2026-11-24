#!/usr/bin/env python3
"""Fail-closed structural adversarial tests; no physical or original-source promotion."""
from __future__ import annotations
import copy,json,zipfile,io
from pathlib import Path
from verify_affine_signed import ROOT,reference_inputs,check_structural,verify_all

def run():
    z,caps,bands,_=reference_inputs()
    originals=[json.loads((ROOT/'results'/f'signed_lens_{j}.json').read_text()) for j in range(6)]
    priors=[json.loads(z.read(f'results/bv_band_lens_{j}.json')) for j in range(6)]
    def validate(v):
        if len(v)!=6 or [r['lens'] for r in v]!=[x['lens_id'] for x in caps]:
            raise ValueError('missing/duplicate/reordered six-lens result')
        for j in range(6):check_structural(v[j],bands[j],caps[j],priors[j])
    validate(originals)
    cases=[]
    def change(label,j,mod):
        data=copy.deepcopy(originals)
        mod(data[j])
        try:validate(data)
        except (ValueError,TypeError,KeyError,IndexError,ZeroDivisionError):
            cases.append({'name':label,'decision':'REJECTED'});return
        raise AssertionError('accepted unsafe mutation '+label)
    change('fake_physical_provider',0,lambda x:x.update(physical_provider_admitted=True))
    change('fake_physical_source',0,lambda x:x.update(physical_source_admitted=True))
    change('fake_validation',1,lambda x:x.update(empirical_validation='VALIDATED'))
    change('fake_global_H_uniqueness',2,lambda x:x.update(global_historical_H_root_uniqueness_proved=True))
    change('fake_useful_for_root',3,lambda x:x.update(useful_for_original_March_root_gap=True))
    change('fake_signed_one_sign',4,lambda x:x.update(signed_band_remainder_one_sign_certified=True))
    change('nonselected_mathematical_source',5,lambda x:x.update(theoretical_source='PHYSICAL_Weyl'))
    change('source_sha',0,lambda x:x.update(original_parent_sha256='0'*64))
    change('node_sha',1,lambda x:x.update(original_180_source_node_sha256='1'*64))
    change('lens_duplicate',2,lambda x:x.update(lens=originals[1]['lens']))
    change('bad_schema',3,lambda x:x.update(schema='UNKNOWN'))
    change('bad_count_zero',0,lambda x:x.update(n=0))
    change('bad_count_wrong',1,lambda x:x.update(n=129))
    change('missing_endpoint',2,lambda x:x['point_values'].pop())
    change('extra_endpoint',3,lambda x:x['point_values'].append(copy.deepcopy(x['point_values'][-1])))
    change('missing_panel',4,lambda x:x['panels'].pop())
    change('false_band',5,lambda x:x['band'].reverse())
    change('changed_aperture',0,lambda x:x['point_values'][0].update(A='1/1000'))
    change('inverted_Q_box',1,lambda x:x['point_values'][0].update(Q=['3','2']))
    change('negative_P_box',2,lambda x:x['point_values'][0].update(Plin=['-1','1']))
    change('inverted_remainder',3,lambda x:x.update(proxy_remainder_interval=['1','-1']))
    change('unjustified_symmetric',4,lambda x:x.update(independently_certifiable_symmetric_peano_remainder_ceiling_Msun=1))
    change('understated_subpanel_upper',5,lambda x:x['panels'][0].update(upper=-10**20))
    change('understated_subpanel_lower',0,lambda x:x['panels'][0].update(lower=10**20))
    change('understated_global_upper',1,lambda x:x['aggregate_signed_Q_deriv_minus_P_integer'].__setitem__(1,-10**15))
    change('understated_global_lower',2,lambda x:x['aggregate_signed_Q_deriv_minus_P_integer'].__setitem__(0,10**15))
    change('understated_max_abs',3,lambda x:x.update(max_abs_new_signed_band_upper_integer_Msun=1))
    change('changed_old_BV',4,lambda x:x.update(inherited_prior_BV_upper_integer_Msun=1))
    change('fake_no_improvement',5,lambda x:x.update(inherited_prior_BV_upper_integer_Msun=1))
    if len(cases)!=29:raise AssertionError('adversarial count drift')
    obj={'schema':'HIST001D_CANCEL_AWARE_AFFINE_ADVERSARIAL_QA_V1','cases':cases,'all_rejected':True,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    path=ROOT/'results/adversarial_qa.json';path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print('QA',len(cases),'ALL_REJECTED',flush=True)
    return obj

if __name__=='__main__':run()
