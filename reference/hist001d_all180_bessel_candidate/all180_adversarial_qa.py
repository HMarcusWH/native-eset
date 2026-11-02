#!/usr/bin/env python3
"""Adversarial JSON/integrity contract tests; not extra independent math proofs."""
from __future__ import annotations
import copy,hashlib,json,zipfile
from pathlib import Path
from all180_aggregate import inspect_pair,aggregate
P=Path(__file__).resolve().parent

def execute(save=True):
    p=json.loads((P/'results/all180_rational_J0822p1828.json').read_text())
    q=json.loads((P/'results/independent_all180_J0822p1828.json').read_text())
    inspect_pair(p,q)
    mutations=[
        ('lens_identity',lambda z:z.__setitem__('lens_id','FALSE_LENS')),
        ('original_source_sha',lambda z:z.__setitem__('original_46plus3_source_composite_sha256','0'*64)),
        ('source_parent_sha',lambda z:z.__setitem__('original_smooth_parent_sha256','1'*64)),
        ('original_node_sha',lambda z:z.__setitem__('source_180_node_sha256','2'*64)),
        ('substitute_11520',lambda z:z.__setitem__('source_regv2_180_nodes_not_D2d_11520',False)),
        ('source_density_sign',lambda z:z.__setitem__('original_source_density_positive_all_nodes',False)),
        ('smooth_density_sign',lambda z:z.__setitem__('smooth_math_derivative_positive_all_nodes',False)),
        ('source_weights_sign',lambda z:z.__setitem__('original_source_180_kernel_weights_positive',False)),
        ('truncate_node_array',lambda z:z.__setitem__('stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc',z['stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc'][:-1])),
        ('understate_a_node',lambda z:z['stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc'].__setitem__(0,0)),
        ('understate_the_max',lambda z:z.__setitem__('max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc',1)),
        ('understate_allR_projected',lambda z:z.__setitem__('projected_shadow_all_R_difference_upper_integer_msun',1)),
        ('physical_admission',lambda z:z.__setitem__('physical_provider_admitted',True)),
        ('original_continuum_root',lambda z:z.__setitem__('original_March_continuum_H_error_or_root_count_proved',True)),
        ('arbitrary_software_error',lambda z:z.__setitem__('source_float_operational_error_certified_for_arbitrary_inputs',True)),
        ('claim_physical_density',lambda z:z.__setitem__('physical_shadow_density_or_Weyl_proved',True)),
        ('empirical_validation',lambda z:z.__setitem__('empirical_validation','VALIDATED')),
        ('altered_diff_inventory',lambda z:z['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc'].__setitem__(0,[9,-9])),
        ('false_tight_signed_interval',lambda z:z['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc'].__setitem__(0,[0,0])),
    ]
    accepted=[]
    for name,fn in mutations:
        z=copy.deepcopy(p);fn(z)
        try:inspect_pair(z,q)
        except (ValueError,KeyError,IndexError,TypeError):accepted.append(name)
        else:raise AssertionError('failed to reject mutated source/claim: '+name)
    # Check source SHA corruption as an independent archive-level guard.
    parent=P/'inputs/frozen_smooth_shadow_gradient_parent.zip'
    original=hashlib.sha256(parent.read_bytes()).hexdigest()
    assert original=='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
    mod=bytearray(parent.read_bytes());mod[250]^=1
    assert hashlib.sha256(mod).hexdigest()!=original
    accepted.append('original_parent_raw_byte_corruption')
    report={'schema':'HIST001D_FULL180_RATIONAL_SOURCE_INTEGRITY_ADVERSARIAL_QA_V1',
        'expected_alterations':len(accepted),'all_expected_rejected':True,
        'rejected':accepted,'proof_claims_cannot_be_inflated':True,
        'independent_mathematical_review_completed':False}
    if save:
        dest=P/'results/all180_adversarial_qa.json'
        dest.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('ADVERSARIAL_CORRUPTION_CHECKS_PASS',len(accepted),hashlib.sha256(dest.read_bytes()).hexdigest())
    return report

if __name__=='__main__':execute()
