#!/usr/bin/env python3
"""Explicit no-claim and source integrity mutation tests; NOT proof of physics."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA='82a840767c61e1b6a838bbf3cf105d1b4ff5b854a883dfacd219e8e2b1bb67bf'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PRODUCER_SHA='072a41b69469670cc8a48089d6191160144b238363ff63cfe4ee60005b44e55f'
INDEPENDENT_SHA='c98928586228dde7e2461408a863c53224110ab4f36b5491ee0422e60b7d12e3'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
def h(b):return hashlib.sha256(b).hexdigest()
def canon(o):return (json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()

def validate(producer, independent, *, producer_raw=None, independent_raw=None):
    pkeys={'schema','source_lock_sha256','parent_source_archive_sha256','original_math_model','distinct_new_diagnostic',
           'lenses','proved_uniform_gradient_error','certified_M2_M3_derivative_suprema',
           'original_numerical_continuum_root_uniqueness','physical_Weyl','empirical_validation','source_11520_proxy_substituted'}
    if set(producer)!=pkeys:raise ValueError('unexpected or missing producer claim')
    if producer['schema']!='HIST001D_SOURCE_ANALYTIC_MSH_DERIVATIVE_V1_NONPROMOTING_DIAGNOSTIC':raise ValueError('schema')
    if producer['source_lock_sha256']!=SOURCE_SHA or producer['parent_source_archive_sha256']!=PARENT_SHA:raise ValueError('external source identity')
    for k in ('proved_uniform_gradient_error','certified_M2_M3_derivative_suprema','original_numerical_continuum_root_uniqueness',
              'physical_Weyl','source_11520_proxy_substituted'):
        if producer[k] is not False:raise ValueError('science claim inflation')
    if producer['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('empirical promotion')
    if producer['original_math_model']!='HISTORICAL_ESET3_4_MARCH_REGV2_180x120':raise ValueError('model identity')
    if [l['lens_id'] for l in producer['lenses']]!=list(LENSES):raise ValueError('source lens identity/order')
    for l in producer['lenses']:
        if l['source_gradient_relative_replay_difference_max']<0 or l['source_gradient_relative_replay_difference_max']>2e-14:raise ValueError('original source replay')
        if l['first_node_source_over_analytic_ratio']<4e6 or l['first_node_source_over_analytic_ratio']>2e7:
            raise ValueError('first-bin discrepancy mutated')
        if l['new_sampled_sign_change_count']!=1:raise ValueError('unsupported diagnostic sign chart')
        if len(l['new_replacement_density_sampled_root_kpc'])!=1:raise ValueError('diagnostic root inventory')
        if not l['epsilon_branch_no_node_clip']:raise ValueError('source gate identity')
        if not l['smooth_density_positive_AT_SOURCE_NODES_ONLY']:raise ValueError('source node sign')
        if len(l['original_180_nodal_sha256'])!=64:raise ValueError('node source SHA identity')
        if h((ROOT/l['analytic_profile_file']).read_bytes())!=l['analytic_profile_sha256']:raise ValueError('profile altered')
    if set(independent)!={'schema','source_lock_sha256','producer_result_sha256','lenses','independent_mpmath_special_function_spots',
                       'global_Bessel_interval_error_certified','physical_provider_admitted','empirical_validation'}:
        raise ValueError('independent claim shape')
    if independent['schema']!='HIST001D_INDEPENDENT_BESSEL_MP_SOURCE_DERIVATIVE_DIAGNOSTIC_V1':raise ValueError('independent schema')
    if independent['source_lock_sha256']!=SOURCE_SHA or independent['producer_result_sha256']!=PRODUCER_SHA:raise ValueError('independent source pin')
    if independent['global_Bessel_interval_error_certified'] is not False or independent['physical_provider_admitted'] is not False:
        raise ValueError('false independent physics or interval claim')
    if independent['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('false empirical promotion')
    if [l['lens_id'] for l in independent['lenses']]!=list(LENSES):raise ValueError('independent lens identity/order')
    for l in independent['lenses']:
        if l['first_source_over_mp_ratio']<4e6:raise ValueError('independent source ratio')
        if l['all_180_smooth_gradient_source_accuracy_proved'] is not False or l['continuous_root_count_established'] is not False:
            raise ValueError('global continuum proof inflation')
        if len(l['mp_spot_checks'])<5 or max(q['relative_producer_vs_mp'] for q in l['mp_spot_checks'])>2e-6:
            raise ValueError('independent high precision spot check missing')
    if producer_raw is not None and h(producer_raw)!=PRODUCER_SHA:raise ValueError('source-independent producer SHA pin')
    if independent_raw is not None and h(independent_raw)!=INDEPENDENT_SHA:raise ValueError('source-independent independent SHA pin')
    return True

def run():
    pb=(ROOT/'results/producer_analytic_source_gradient.json').read_bytes()
    ib=(ROOT/'results/independent_mp_check.json').read_bytes()
    p=json.loads(pb);i=json.loads(ib)
    validate(p,i,producer_raw=pb,independent_raw=ib)
    modifications=[
        ('original_source_lock',lambda x: x['p'].__setitem__('source_lock_sha256','0'*64)),
        ('parent_source_lock',lambda x: x['p'].__setitem__('parent_source_archive_sha256','f'*64)),
        ('physical_weyl',lambda x: x['p'].__setitem__('physical_Weyl',True)),
        ('empirical',lambda x: x['p'].__setitem__('empirical_validation','VALIDATED')),
        ('source_nodal_11520',lambda x: x['p'].__setitem__('source_11520_proxy_substituted',True)),
        ('original_root_uniqueness',lambda x: x['p'].__setitem__('original_numerical_continuum_root_uniqueness',True)),
        ('derivative_error_certification',lambda x: x['p'].__setitem__('proved_uniform_gradient_error',True)),
        ('derivative_suprema',lambda x: x['p'].__setitem__('certified_M2_M3_derivative_suprema',True)),
        ('extra_proof_claim',lambda x: x['p'].__setitem__('physically_verified_mass',True)),
        ('lens_removed',lambda x: x['p']['lenses'].pop()),
        ('lens_reordered',lambda x: x['p']['lenses'].reverse()),
        ('first_density_ratio',lambda x: x['p']['lenses'][0].__setitem__('first_node_source_over_analytic_ratio',2)),
        ('sampled_root_count',lambda x: x['p']['lenses'][0].__setitem__('new_sampled_sign_change_count',2)),
        ('epsilon_branch',lambda x: x['p']['lenses'][0].__setitem__('epsilon_branch_no_node_clip',False)),
        ('independent_physical_claim',lambda x: x['i'].__setitem__('physical_provider_admitted',True)),
        ('independent_interval',lambda x: x['i'].__setitem__('global_Bessel_interval_error_certified',True)),
        ('independent_lens_dropout',lambda x: x['i']['lenses'].pop()),
        ('independent_source_pin',lambda x: x['i'].__setitem__('producer_result_sha256','f'*64)),
    ]
    rejects=[]
    for label,change in modifications:
        x={'p':copy.deepcopy(p),'i':copy.deepcopy(i)}
        change(x)
        # Outer JSON is self-rehashed, so alone a self-consistent digest isn't authority.
        forged_producer=canon(x['p']);forged_independent=canon(x['i'])
        try:
            validate(x['p'],x['i'],producer_raw=forged_producer,independent_raw=forged_independent)
        except (ValueError,AssertionError,FileNotFoundError): rejects.append(label)
        else:raise AssertionError('self-rehashed false claim accepted: '+label)
    doc={'schema':'HIST001D_SOURCE_ANALYTIC_MSH_DIAGNOSTIC_ADVERSARIAL_QA_V1',
         'source_sha256':SOURCE_SHA,'original_producer_sha256':PRODUCER_SHA,
         'original_independent_sha256':INDEPENDENT_SHA,
         'tamper_cases':len(modifications),'tamper_rejections':rejects,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
         'uniform_gradient_bound_certified':False}
    raw=canon(doc)
    (ROOT/'results/adversarial_qa.json').write_bytes(raw)
    print('GRADIENT_ADVERSARIAL_QA_PASS',len(rejects),'/',len(modifications),h(raw))
    return h(raw)
if __name__=='__main__':run()
