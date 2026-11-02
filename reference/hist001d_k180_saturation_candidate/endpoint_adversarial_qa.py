#!/usr/bin/env python3
"""Fail-closed identity/claim/bound checks for a narrow endpoint-only math certificate."""
import hashlib,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
EXPECTED_PARENT='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
LENSES={'J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720'}
def sha(b):return hashlib.sha256(b).hexdigest()
def validate(results):
    a,b,c,d,e=results
    if sha((ROOT/'original_parent.zip').read_bytes())!=EXPECTED_PARENT:raise ValueError('source parent')
    if a.get('schema')!='HIST001D_SOURCE_FROZEN_MARCH180_K180_SATURATION_ENDPOINT_IDENTITY_PRODUCER_V1':raise ValueError('schema producer')
    if b.get('schema')!='HIST001D_MARCH180_SATURATED_K180_SELECTED_MSH_INDEPENDENT_V1':raise ValueError('schema independent')
    if c.get('schema')!='HIST001D_MARCH180_SELECTED_SMOOTH_MSH_ALL_APERTURE_BV_CONSERVATIVE_BOUND_V1':raise ValueError('schema BV')
    if d.get('schema')!='HIST001D_MARCH180_INDEPENDENT_GLOBAL_M2_BV_UPPER_V1':raise ValueError('schema BV independent')
    if e.get('schema')!='HIST001D_SOURCE_NODE_ONLY_SMOOTH_DENSITY_NONIDENTIFIABILITY_WITNESS_V1':raise ValueError('schema bump')
    if a['source_original_46plus3']!=SOURCE or b['original_source_sha256']!=SOURCE or c['source_46plus3_sha256']!=SOURCE or d['original_source']!=SOURCE or e['original_source_sha256']!=SOURCE:raise ValueError('source chain')
    if a['source_original_parent_sha256']!=EXPECTED_PARENT or b['parent_sha256']!=EXPECTED_PARENT:raise ValueError('parent chain')
    if not a['saturated_aperture_only'] or a['global_uniform_aperture_quadrature_error_proved'] or b['global_uniform_aperture_quadrature_error_proved']:raise ValueError('scope saturation')
    if c['original_source_true_physical_continuum_bound_proved'] or c['useful_full_March_H_root_error_proved'] or d['original_continuous_root_theorem_proved']:raise ValueError('scope BV')
    if e['selected_smooth_Msh_law_preserved_by_bump'] or e['physical_density_source_admitted'] or e['continuum_projected_mass_difference_exact_Msun']!='1000000000':raise ValueError('counterexample scope')
    if any(q.get('physical_provider_admitted') is not False or q.get('empirical_validation')!='NOT_ESTABLISHED' for q in [a,b,c,d]):raise ValueError('physical claim')
    if len(a['lenses'])!=len(b['lenses'])!=len(c['lenses'])!=len(d['lenses'])!=6:raise ValueError('lens length')
    if {x['lens_id'] for x in a['lenses']}!=LENSES or {x['lens_id'] for x in b['lenses']}!=LENSES:raise ValueError('lens set')
    for x,y,z,w in zip(a['lenses'],b['lenses'],c['lenses'],d['lenses']):
        if x['lens_id']!=y['lens_id'] or z['lens_id']!=x['lens_id'] or w['lens_id']!=x['lens_id']:raise ValueError('lens alignment')
        if x['source_specific_K180_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']>=100:raise ValueError('saturated error cap')
        if y['independent_K180_absolute_error_upper_milli_Msun']>x['source_specific_K180_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']:raise ValueError('producer understated')
        if y['independent_original_S0_absolute_error_upper_milli_Msun']>x['original_source_S0_at_Rmax_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']:raise ValueError('original S0 understated')
        if not w['producer_tighter_cellwise_bound_contained']:raise ValueError('BV independent containment')
        if w['independent_uniform_all_apertures_upper_integer_Msun']<z['all_real_smooth_candidate_K180_sampled_Mprime_vs_mathematical_continuum_abs_error_upper_integer_Msun']:raise ValueError('BV containment failed')
        if z['scientifically_useful_root_error_bound']:raise ValueError('BV too weak for root')
    return True

def main():
    names=['endpoint_saturation_producer.json','endpoint_saturation_independent.json','all_aperture_bv_producer.json','all_aperture_bv_independent.json','node_only_nonidentifiability.json']
    orig=[json.loads((ROOT/n).read_bytes()) for n in names]
    assert validate(orig)
    cases=[]
    def tamper(label,func):
        v=copy.deepcopy(orig);func(v)
        try:validate(v)
        except (ValueError,KeyError,AssertionError,TypeError):cases.append({'label':label,'status':'REJECTED'});return
        raise AssertionError('Tamper accepted '+label)
    tamper('physical_provider',lambda x:x[0].update(physical_provider_admitted=True))
    tamper('empirical_validation',lambda x:x[1].update(empirical_validation='VALIDATED'))
    tamper('origin_sha',lambda x:x[0].update(source_original_46plus3='0'*64))
    tamper('parent_sha',lambda x:x[1].update(parent_sha256='0'*64))
    tamper('inferred_global_from_saturation',lambda x:x[0].update(global_uniform_aperture_quadrature_error_proved=True))
    tamper('wrong_endpoint_only',lambda x:x[0].update(saturated_aperture_only=False))
    tamper('understated_saturation_bound',lambda x:x[0]['lenses'][1].update(source_specific_K180_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun=0))
    tamper('duplicate_lens',lambda x:x[0]['lenses'][0].update(lens_id=x[0]['lenses'][1]['lens_id']))
    tamper('lost_lens',lambda x:x[0]['lenses'].pop())
    tamper('false_useful_BV',lambda x:x[2]['lenses'][2].update(scientifically_useful_root_error_bound=True))
    tamper('false_approved_physical_continuum',lambda x:x[2].update(original_source_true_physical_continuum_bound_proved=True))
    tamper('fake_independent_underestimate',lambda x:x[3]['lenses'][0].update(independent_uniform_all_apertures_upper_integer_Msun=1))
    tamper('bump_falsely_claims_mass_law',lambda x:x[4].update(selected_smooth_Msh_law_preserved_by_bump=True))
    tamper('bump_claim_not_exact',lambda x:x[4].update(continuum_projected_mass_difference_exact_Msun='999999999'))
    tamper('independent_S0_more_than_producer',lambda x:x[1]['lenses'][0].update(independent_original_S0_absolute_error_upper_milli_Msun=200))
    tamper('wrong_result_schema',lambda x:x[2].update(schema='not-the-model'))
    result={'schema':'HIST001D_MARCH180_K180_SATURATION_QA_V1','cases':cases,'all_rejected':True,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    path=ROOT/'endpoint_adversarial_qa.json';path.write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print('QA',len(cases),'rejected','SHA',sha(path.read_bytes()))
if __name__=='__main__':main()
