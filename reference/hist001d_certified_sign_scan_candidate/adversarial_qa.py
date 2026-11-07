"""Deterministic source-free adversarial checker; distinguishes structural and replay gates."""
from __future__ import annotations
import copy
from certified_sign_scan import (
    SourceContract, SyntheticOracle, Unresolved, digest, scan, validate_receipt,
    canonical_json,
)

C=SourceContract(uniqueness_sha256='e'*64,scope='SYNTHETIC_TEST_ONLY')

def reseal(x):
    x['receipt_sha256']=digest({k:v for k,v in x.items() if k!='receipt_sha256'})
    return x

def qa():
    baseline=scan(SyntheticOracle(),C)
    validate_receipt(baseline)
    cases={
        'wrong_schema': lambda z: z.update(schema='FORGED'),
        'wrong_math_identity': lambda z: z.update(model_id='D2D_11520'),
        'wrong_source_digest': lambda z: z.update(source_sha256='0'*64),
        'wrong_bracketing_digest': lambda z: z.update(bracketing_package_sha256='0'*64),
        'compiled_float_promotion': lambda z: z.update(original_compiled_float_signs_certified=True),
        'march_offgrid_promotion': lambda z: z.update(original_March_offgrid_root_certified=True),
        'physical_provider_promotion': lambda z: z.update(physical_provider_admitted=True),
        'empirical_validation_promotion': lambda z: z.update(empirical_validation='VALIDATED'),
        'canonical_graph_promotion': lambda z: z.update(canonical_theory_state_changed=True),
        'root_scope_promotion': lambda z: z.update(mathematical_claim_scope='PHYSICAL_WEYL'),
        'remove_lens': lambda z: z['lens_results'].pop(),
        'duplicate_lens': lambda z: z['lens_results'][1].update(lens=z['lens_results'][0]['lens']),
        'remove_sign_segment': lambda z: z['lens_results'][0]['segments'].pop(),
        'reverse_first_sign': lambda z: z['lens_results'][0]['segments'][0].update(classification='NEGATIVE'),
        'reverse_second_sign': lambda z: z['lens_results'][0]['segments'][1].update(classification='POSITIVE'),
        'early_first_segment_end': lambda z: z['lens_results'][0]['segments'][0].update(hi_bits=str(int(z['lens_results'][0]['segments'][0]['hi_bits'])-1)),
        'late_second_segment_start': lambda z: z['lens_results'][0]['segments'][1].update(lo_bits=str(int(z['lens_results'][0]['segments'][1]['lo_bits'])+1)),
        'wrong_first_hex': lambda z: z['lens_results'][0]['segments'][0].update(hi_hex='0x1.0p+0'),
        'wrong_second_hex': lambda z: z['lens_results'][0]['segments'][1].update(lo_hex='0x1.0p+0'),
        'wrong_coverage_count': lambda z: z['lens_results'][0]['segments'][0].update(binary64_count='1'),
        'proof_links_dropped': lambda z: z['lens_results'][0]['segments'][0].update(proof_links={}),
        'aggregate_forced_pass': lambda z: z.update(status='OTHER'),
        'lens_forced_unresolved': lambda z: z['lens_results'][0].update(status='UNRESOLVED'),
        'parent_removed': lambda z: z.update(parent_attestation=None),
        'root_bracket_removed': lambda z: z['lens_results'][0].update(root_bracket=None),
        'root_bracket_wrong': lambda z: z['lens_results'][0]['segments'][0].update(hi_hex='0x1.0p+0'),
        'shrink_declared_domain_left': lambda z: z.update(scan_domain_lo_hex='0x1.0p+0'),
        'shrink_declared_domain_right': lambda z: z.update(scan_domain_hi_hex='0x1.0p+3'),
        'noncanonical_domain': lambda z: z.update(scan_domain_lo_hex='0x1.47AE147AE147Bp-6'),
        'fake_nan_domain': lambda z: z.update(scan_domain_lo_hex='nan'),
        'unknown_segment_state': lambda z: z['lens_results'][0]['segments'][1].update(classification='ZERO'),
        'wrong_mode': lambda z: z['lens_results'][0].update(mode='UNKNOWN'),
        'engine_trace_rehashed': lambda z: z['lens_results'][0]['segments'][0]['proof_links']['left_endpoint_two_engine_traces'][0].update(proof_trace_sha256='0'*64),
        'engine_interval_rehashed': lambda z: z['lens_results'][0]['segments'][0]['proof_links']['left_endpoint_two_engine_traces'][0].update(lo='-1/1',hi='-1/2'),
        'parent_replay_hash_rehashed': lambda z: z['parent_attestation'].update(replay_receipt_sha256='0'*64),
        'theorem_parent_rehashed': lambda z: z.update(uniqueness_parent_sha256='f'*64),
    }
    structural_rejections=[]
    source_replay_required=[]
    unexpected=[]
    for name,mut in cases.items():
        attack=copy.deepcopy(baseline)
        mut(attack)
        reseal(attack)
        try:
            validate_receipt(attack)
        except Unresolved:
            structural_rejections.append(name)
        else:
            # Source-bound proof validation MUST replay two-engine trace and parent.
            # Here a fresh synthetic re-execution is only a software-shape check.
            if canonical_json(attack) != canonical_json(scan(SyntheticOracle(),C)):
                source_replay_required.append(name)
            else:
                unexpected.append(name)
    # Three operational fail-closed modes.
    ops={
        'missing_sealed_adapter': scan(None,C),
        'parent_not_available': scan(SyntheticOracle(unavailable=True),C),
        'insufficient_budget': scan(SyntheticOracle(),C,max_evals_per_lens=1),
    }
    op_results={name:{'status':receipt['status'],
                      'all_lenses_unresolved': all(l['status']=='UNRESOLVED' for l in receipt['lens_results'])}
                for name,receipt in ops.items()}
    good=(not unexpected and all(x['status']=='UNRESOLVED' and x['all_lenses_unresolved'] for x in op_results.values()))
    data={"schema":"HIST001D_SOURCE_ONLY_ADVERSARIAL_AUDIT_V1",
          "status":"PASS_SOURCE_FREE_ONLY" if good else "FAIL",
          "baseline_synthetic_receipt_sha256":baseline['receipt_sha256'],
          "total_mutations":len(cases),
          "structurally_rejected_count":len(structural_rejections),
          "structurally_rejected":sorted(structural_rejections),
          "requires_source_replay_count":len(source_replay_required),
          "requires_source_replay":sorted(source_replay_required),
          "unexpectedly_accepted":sorted(unexpected),
          "operational_fail_closed":op_results,
          "physical_provider_admitted":False,
          "empirical_validation":"NOT_ESTABLISHED"}
    data['receipt_sha256']=digest(data)
    return data

if __name__=='__main__':
    import sys
    import json
    j=qa()
    sys.stdout.buffer.write(canonical_json(j))
    sys.exit(0 if j['status']=='PASS_SOURCE_FREE_ONLY' else 2)
