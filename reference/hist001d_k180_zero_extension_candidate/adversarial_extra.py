#!/usr/bin/env python3
"""Mutation-based fail-closed adversarial review of supplemental IVT sign witnesses."""
from __future__ import annotations
import copy,io,json,hashlib,zipfile
from pathlib import Path
from claim_guard import validate
ROOT=Path(__file__).resolve().parents[2]
PARENT='0eec91a8e531516529a58cf811685581233aba6d5bc8150c9897b50de88ae651'
def sha(x):return hashlib.sha256(x).hexdigest()
def load():
    raw=(ROOT/'inputs/targeted_parent_v1.zip').read_bytes()
    if sha(raw)!=PARENT:raise ValueError('parent SHA')
    z=zipfile.ZipFile(io.BytesIO(raw))
    prior=json.loads(z.read('results/targeted_aggregate.json'))
    lenses=[json.loads(z.read(f'results/targeted_lens_{j}.json')) for j in range(6)]
    shas=[sha(z.read(f'results/targeted_lens_{j}.json')) for j in range(6)]
    p=json.loads((ROOT/'results/extra_sign_witnesses.json').read_text())
    i=json.loads((ROOT/'results/extra_fraction_verify.json').read_text())
    return p,i,prior,lenses,shas

def run():
    original=load();assert validate(*original,PARENT)['total_minimum']==16
    cases=[]
    def tamper(name,func):
        tup=copy.deepcopy(original);func(tup)
        try:validate(*tup,PARENT)
        except (ValueError,AssertionError,KeyError,TypeError,IndexError):
            cases.append({'name':name,'status':'REJECTED'});return
        raise AssertionError('adversarial mutation accepted: '+name)
    tamper('false_exact_count',lambda a:a[0].update(exact_zero_count_proved=True))
    tamper('false_empirical',lambda a:a[1].update(empirical_validation='VALIDATED'))
    tamper('false_physical',lambda a:a[0].update(physical_provider_admitted=True))
    tamper('false_einstein',lambda a:a[1].update(Einstein_root_count_proved=True))
    tamper('false_no_Bessel',lambda a:a[0].update(no_new_Bessel_evaluations=False))
    tamper('old_min_edited',lambda a:a[2].update(distinct_quadrature_remainder_zeros_at_least=16))
    tamper('total_edited',lambda a:a[0].update(sum_lower_bound=18))
    tamper('independent_total_edited',lambda a:a[1].update(certified_total_distinct_zeros_at_least=18))
    tamper('missing_lens',lambda a:a[0]['lenses'].pop())
    tamper('extra_lens',lambda a:a[1]['extra_witnesses'].append(copy.deepcopy(a[1]['extra_witnesses'][0])))
    tamper('duplicate_lens',lambda a:a[0]['lenses'][1].update(lens=a[0]['lenses'][0]['lens']))
    tamper('wrong_index',lambda a:a[0]['lenses'][1].update(index=32))
    tamper('altered_fraction_aperture',lambda a:a[0]['lenses'][2].update(A_exact='5'))
    tamper('falsified_positive_sign',lambda a:a[0]['lenses'][0].update(strict_sign=-1))
    tamper('understated_signed_lower',lambda a:a[0]['lenses'][0]['D_interval'].__setitem__(0,'999999999'))
    tamper('inverted_signed_interval',lambda a:a[0]['lenses'][1].update(D_interval=['10','-1']))
    tamper('bad_outward_floor',lambda a:a[0]['lenses'][0]['D_outward_integer_Msun'].__setitem__(0,999999999))
    tamper('bad_independent_floor',lambda a:a[1]['extra_witnesses'][1]['independent_D_outward_integer_Msun'].__setitem__(0,999999999))
    tamper('parent_receipt_sha',lambda a:a[0]['lenses'][0].update(source_parent_receipt_sha256='0'*64))
    tamper('prior_altered_endpoint_sign',lambda a:a[3][3]['anchors'][0].update(strict_sign=1))
    tamper('prior_peano_allowance',lambda a:a[3][5].update(E_symmetric_exact='0'))
    tamper('prior_duplicate_anchor',lambda a:a[3][0]['anchors'][1].update(index=0))
    tamper('independent_wrong_aperture',lambda a:a[1]['extra_witnesses'][0].update(A_exact='0'))
    tamper('independent_parent_sha',lambda a:a[1].update(parent_release_sha256='0'*64))
    tamper('incorrect_prior_count',lambda a:a[2]['lenses'][1].update(zeros_at_least=4))
    out={'schema':'HIST001D_SUPPLEMENTAL_SIGN_ADVERSARIAL_V1',
         'case_count':len(cases),'all_rejected':len(cases)==25,
         'cases':cases,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    if not out['all_rejected']:raise AssertionError('unexpected number of mutations')
    path=ROOT/'results'/'adversarial_extra.json';path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('ADVERSARIAL_EXTRA_PASS',len(cases),'rejected')

if __name__=='__main__':run()
