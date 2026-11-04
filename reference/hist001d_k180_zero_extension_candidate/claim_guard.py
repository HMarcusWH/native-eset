#!/usr/bin/env python3
"""Pure guard for source-conditional selected-M* additional sign witnesses.
No numerical producer imports and NO assertion of exact root count/physics.
"""
from __future__ import annotations
from fractions import Fraction as F
LENS_NAMES=('J0822+1828','J0915+4211','J0930+2855',
            'J1021+2028','J1111+2234','J1135+3720')
BASE_COUNTS=(1,2,3,1,2,1)
EXPECTED_COUNTS=(3,2,3,3,2,3)
EXTRA_INDEX={0:25,3:33,5:29}
PROD_SCHEMA='HIST001D_SELECTED_MSTAR_ADDITIONAL_STRICT_SIGN_WITNESSES_V1'
INDEP_SCHEMA='HIST001D_ADDITIONAL_ZERO_192BIT_FRACTION_VERIFY_V1'

def f(x):
    if isinstance(x,bool):raise ValueError('boolean not rational')
    return F(x)
def floor(x):return x.numerator//x.denominator
def ceil(x):return -(-x.numerator//x.denominator)
def count_sign_flips(anchors):
    if len(anchors)<2:raise ValueError('too few signed aperture witnesses')
    values=[];last=-1
    for idx,sgn in anchors:
        if type(idx) is not int or idx<=last or idx<0 or idx>128 or type(sgn) is not int or sgn not in (-1,1):
            raise ValueError('invalid / duplicate / unsorted strict sign witness')
        values.append((idx,sgn));last=idx
    if values[0][0]!=0 or values[-1][0]!=128:
        raise ValueError('original aperture band endpoints not covered')
    return sum(u[1]!=v[1] for u,v in zip(values,values[1:]))

def validate(prod,indep,prior_aggregate,old_lenses,prior_receipt_sha,parent_sha):
    if prod['schema']!=PROD_SCHEMA or indep['schema']!=INDEP_SCHEMA:
        raise ValueError('result schema')
    for item in (prod,indep):
        if (item.get('physical_provider_admitted') is not False or
                item.get('empirical_validation')!='NOT_ESTABLISHED' or
                item.get('exact_zero_count_proved') is not False or
                item.get('Einstein_root_count_proved') is not False):
            raise ValueError('unsupported scientific claim')
    if prod.get('status')!='SOURCE_CONDITIONAL_MATHEMATICAL_CANDIDATE_NONPROMOTING' or prod.get('no_new_Bessel_evaluations') is not True:
        raise ValueError('source scope')
    if prod.get('additional_witnesses_count')!=3 or prod.get('original_zero_lower_bound')!=10 or prod.get('sum_lower_bound')!=16:
        raise ValueError('claimed aggregate counts')
    if indep.get('certified_total_distinct_zeros_at_least')!=16 or indep.get('parent_release_sha256')!=parent_sha:
        raise ValueError('second arithmetic count/provenance')
    if (prior_aggregate.get('distinct_quadrature_remainder_zeros_at_least')!=10 or
        prior_aggregate.get('quadrature_remainder_unique_zeros_proved') is not False or
        prior_aggregate.get('Einstein_root_count_proved') is not False or
        len(prior_aggregate['lenses'])!=6 or len(old_lenses)!=6 or len(prior_receipt_sha)!=6):
        raise ValueError('prior 10-zero certificate')
    if len(prod['lenses'])!=3 or len(indep['extra_witnesses'])!=3:
        raise ValueError('missing or extra lens')
    cnt=list(BASE_COUNTS)
    for k,(j,idx) in enumerate(EXTRA_INDEX.items()):
        original=old_lenses[j];record=prod['lenses'][k];check=indep['extra_witnesses'][k]
        if (record.get('lens')!=LENS_NAMES[j] or check.get('lens')!=LENS_NAMES[j] or
            record.get('index')!=idx or check.get('additional_index')!=idx or
            record.get('source_parent_receipt_sha256')!=prior_receipt_sha[j] or
            check.get('prior_receipt_sha256')!=prior_receipt_sha[j] or
            prior_aggregate['lenses'][j]['receipt_sha256']!=prior_receipt_sha[j] or
            prior_aggregate['lenses'][j]['zeros_at_least']!=BASE_COUNTS[j]):
            raise ValueError('lens identity, index or prior receipt')
        A0,A1=map(f,original['A_band']);A=A0+(A1-A0)*F(idx,128)
        if not A0<A<A1 or f(record['A_exact'])!=A or f(check['A_exact'])!=A:
            raise ValueError('exact aperture value')
        E=f(record['E_symmetric_exact'])
        if E!=f(original['E_symmetric_exact']) or E<=0:
            raise ValueError('not the saved independently validated Peano remainder')
        Q0,Q1=map(f,record['Q']);L0,L1=map(f,record['Lrefined'])
        if Q0>Q1 or L0>L1:raise ValueError('inverted source intervals')
        lo,hi=Q0-L1-E,Q1-L0+E
        if lo!=f(record['D_interval'][0]) or hi!=f(record['D_interval'][1]) or lo<=0 or hi<lo or record.get('strict_sign')!=1:
            raise ValueError('extra sign interval arithmetic')
        if record['D_outward_integer_Msun']!=[floor(lo),ceil(hi)]:
            raise ValueError('missing outward rounding')
        independent_integer=check['independent_D_outward_integer_Msun']
        if independent_integer[0]>floor(lo) or independent_integer[1]<ceil(hi) or independent_integer[0]<=0:
            raise ValueError('independent arithmetic not containing first method')
        old=[(x['index'],x['strict_sign']) for x in original['anchors']]
        expanded=sorted(old+[(idx,1)])
        if count_sign_flips(old)!=BASE_COUNTS[j] or count_sign_flips(expanded)!=EXPECTED_COUNTS[j]:
            raise ValueError('old and new sign topology')
        if record.get('existing_zero_lower_bound')!=BASE_COUNTS[j] or record.get('expanded_zero_lower_bound')!=EXPECTED_COUNTS[j] or check.get('prior_zero_lower_bound')!=BASE_COUNTS[j] or check.get('augmented_zero_lower_bound')!=EXPECTED_COUNTS[j]:
            raise ValueError('wrong count from the new strict sign')
        cnt[j]=EXPECTED_COUNTS[j]
    for j in (1,2,4):
        if (prior_aggregate['lenses'][j]['lens']!=LENS_NAMES[j] or
                prior_aggregate['lenses'][j]['receipt_sha256']!=prior_receipt_sha[j] or
                prior_aggregate['lenses'][j]['zeros_at_least']!=BASE_COUNTS[j]):
            raise ValueError('untouched lens identity')
    if cnt!=list(EXPECTED_COUNTS) or sum(cnt)!=16:
        raise ValueError('six lens total')
    return {'counts':cnt,'total_minimum':16,'exact_count_established':False}
