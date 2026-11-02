#!/usr/bin/env python3
"""Fail-closed schema/numerical receipts tests; not a new independent proof."""
from __future__ import annotations
import copy,hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
H=lambda b:hashlib.sha256(b).hexdigest()

def check(d,ind):
    if d.get('schema')!='HIST001D_MARCH_180_FROZEN_SOURCE_STENCIL_ALL_REAL_R_PL_ENVELOPE_CANDIDATE_V1':raise ValueError('schema')
    if d.get('original_source_lock_sha256')!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':raise ValueError('source')
    if d.get('source_180_node_shadow_density_reused_unchanged') is not True:raise ValueError('source identity')
    if d.get('new_11520_source_density_used') is not False:raise ValueError('substituted density')
    if d.get('radius_domain')!='[float64(0.02), float64(120.0)] kpc':raise ValueError('domain')
    assertions={'all_real_original_K180_frozen_stencil_projection_vs_recorded_nodal_PL_enveloped':True,
      'original_total_H_error_bounded':False,'q_aperture_or_baryon_projection_error_closed':False,
      'original_continuum_root_count_proved':False,'physically_continuous_shadow_density_equivalence':False,
      'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    for k,v in assertions.items():
        if d.get('claims',{}).get(k)!=v:raise ValueError('claim '+k)
    lens=d.get('lenses')
    if not isinstance(lens,list) or len(lens)!=6 or len(ind.get('lenses',[]))!=6:raise ValueError('lens inventory')
    for row,ref in zip(lens,ind['lenses'],strict=True):
        if row.get('lens_id')!=ref.get('lens_id'):raise ValueError('lens order')
        comps=row.get('component_bounds')
        if not isinstance(comps,list) or len(comps)!=2:raise ValueError('components')
        for comp,control in zip(comps,ref['bounds'],strict=True):
            if comp.get('component')!=control.get('component'):raise ValueError('component identity')
            if int(comp['max_real_radius_source_stencil_vs_piecewise_linear_bound_upper_msun'])<int(control['max_all_real_R_interpolation_bound_integer_ceil_msun']):raise ValueError('bound forged')
            if int(comp['source_node_max_anchor_gap_upper_msun'])<int(control['max_source_node_gap_integer_ceil_msun']):raise ValueError('node bound forged')
            if comp.get('all_179_real_radius_cells_upper_bounded') is not True:raise ValueError('scope')
            if comp.get('not_original_total_H_error') is not True or comp.get('not_q_aperture_error') is not True:raise ValueError('science firewall')
    return True

def main():
    d=json.loads((ROOT/'results/frozen_stencil_all_real_envelope_producer.json').read_bytes())
    ind=json.loads((ROOT/'results/frozen_stencil_all_real_envelope_independent.json').read_bytes())
    assert check(d,ind)
    tests=[]
    def case(tag,change):
        y=copy.deepcopy(d)
        change(y)
        try:check(y,ind)
        except (ValueError,AssertionError,TypeError,KeyError):tests.append(tag);return
        raise RuntimeError('Tamper accepted: '+tag)
    case('fake_physical_provider',lambda x:x['claims'].__setitem__('physical_provider_admitted',True))
    case('fake_empirical_validation',lambda x:x['claims'].__setitem__('empirical_validation','VALIDATED'))
    case('fake_original_root',lambda x:x['claims'].__setitem__('original_continuum_root_count_proved',True))
    case('fake_full_error',lambda x:x['claims'].__setitem__('original_total_H_error_bounded',True))
    case('fake_q_aperture_closure',lambda x:x['claims'].__setitem__('q_aperture_or_baryon_projection_error_closed',True))
    case('fake_density_11520',lambda x:x.__setitem__('new_11520_source_density_used',True))
    case('fake_domain',lambda x:x.__setitem__('radius_domain','[0,∞)'))
    case('fake_source',lambda x:x.__setitem__('original_source_lock_sha256','0'*64))
    case('fake_component_zero',lambda x:x['lenses'][0]['component_bounds'][0].__setitem__('max_real_radius_source_stencil_vs_piecewise_linear_bound_upper_msun','0'))
    case('fake_node_roundoff_zero',lambda x:x['lenses'][1]['component_bounds'][1].__setitem__('source_node_max_anchor_gap_upper_msun','0'))
    case('drop_one_lens',lambda x:x['lenses'].pop())
    case('wrong_lens_order',lambda x:x['lenses'].reverse())
    case('delete_component',lambda x:x['lenses'][0]['component_bounds'].pop())
    case('component_claim_scope_change',lambda x:x['lenses'][2]['component_bounds'][1].__setitem__('not_original_total_H_error',False))
    assert len(tests)==14
    # Tamper original binary64 input by one bit: original external SHA lock detects
    # this even if someone rehashes an outer wrapper manifest.
    source=(ROOT/'inputs/March180_source_nodes_J0822p1828.be64').read_bytes()
    mutant=bytearray(source);mutant[5]^=1
    assert H(source)!=H(mutant)
    assert H(source)==d['lenses'][0]['original_source_array_record_sha256']
    result={'schema':'HIST001D_SOURCE180_STENCIL_INTEGRITY_ADVERSARIAL_QA_V1','status':'PASS_SCOPED_NEGATIVE_CLAIM_AND_INTEGRITY_TESTS','negative_claim_tests_rejected':tests,'number_rejected':len(tests),'original_source_raw_mutation_detected':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    raw=(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/frozen_stencil_adversarial_qa.json').write_bytes(raw)
    print('SOURCE180_ADVERSARIAL_QA_PASS',len(tests),H(raw))
if __name__=='__main__':main()
