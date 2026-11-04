#!/usr/bin/env python3
"""Strictly negative claim/geometry mutations; no original data replay needed."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from knot_count_contract import verify_all
from assemble_exact_count import source_receipts
ROOT=Path(__file__).resolve().parents[2]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run():
    src=source_receipts();verify_all(*src)
    rejects=[]
    def tamper(tag,which,idx,fn):
        m=[copy.deepcopy(v) for v in src]
        fn(m[which][idx])
        try:verify_all(*m)
        except (ValueError,KeyError,TypeError,IndexError,AssertionError,ZeroDivisionError):
            rejects.append({'case':tag,'result':'REJECTED'});return
        raise AssertionError('BAD mutation accepted '+tag)
    tamper('provider_admitted',0,0,lambda x:x.update(physical_provider_admitted=True))
    tamper('empirical_validation_claim',1,0,lambda x:x.update(empirical_validation='VALIDATED'))
    tamper('wrong_original_46_sha',0,0,lambda x:x.update(source_46plus3_sha256='0'*64))
    tamper('wrong_parent_sha',0,0,lambda x:x.update(protected_parent_sha256='0'*64))
    tamper('wrong_node_sha_in_local',1,0,lambda x:x.update(original_source_node_sha256='0'*64))
    tamper('wrong_node_sha_in_exclusion',2,0,lambda x:x.update(original_node_sha256='0'*64))
    tamper('extra_physical_scope',0,0,lambda x:x.update(selected_mathematical_mass_only=False))
    tamper('missing_node',0,0,lambda x:x['nodes'].pop())
    tamper('duplicated_node_r',0,0,lambda x:x['nodes'][0].update(r=x['nodes'][1]['r']))
    tamper('missing_radial_panel',0,0,lambda x:x.update(leaves=[]))
    tamper('misnamed_lens',3,0,lambda x:x.update(lens='EXTRA'))
    tamper('bad_local_schema',1,0,lambda x:x.update(schema='FAKE'))
    tamper('bad_gap_schema',2,0,lambda x:x.update(schema='FAKE'))
    tamper('claim_local_global_exact',1,0,lambda x:x.update(exact_full_band_zero_count_proved=True))
    tamper('claim_local_all_gaps_excluded',1,0,lambda x:x.update(all_other_band_subintervals_excluded=True))
    tamper('missing_root',1,0,lambda x:x['roots'].pop())
    tamper('fake_root_total',1,0,lambda x:x.update(certified_nonoverlapping_local_unique_zero_brackets=17))
    tamper('zero_derivative_claim',1,0,lambda x:x['roots'][0].update(expected_monotone_derivative=0))
    tamper('wrong_left_endpoint_sign',1,0,lambda x:x['roots'][0].update(D_a=['1','2']))
    tamper('wrong_right_endpoint_sign',1,0,lambda x:x['roots'][0].update(D_b=['-2','-1']))
    tamper('root_interval_inverted',1,0,lambda x:x['roots'][0].update(a=x['roots'][0]['b']))
    tamper('root_panel_removed',1,0,lambda x:x['roots'][0]['derivative_panels'].pop())
    tamper('root_bad_derivative_floor',1,0,lambda x:x['roots'][0]['derivative_panels'][0].update(Dprime_lower_integer_Msun_per_kpc=0))
    tamper('root_nonmatching_panel_count',1,0,lambda x:x['roots'][0].update(accepted_panels=-1))
    tamper('root_panel_gap',1,0,lambda x:x['roots'][0]['derivative_panels'][0].update(b='3'))
    tamper('root_hits_knot',1,0,lambda x:x['roots'][0].update(b=x['roots'][1]['b']))
    tamper('exclusion_gap_removed',2,0,lambda x:x['gap_blocks'].pop())
    tamper('exclusion_wrong_sign',2,0,lambda x:x['gap_blocks'][0].update(sign=-x['gap_blocks'][0]['sign']))
    tamper('exclusion_panel_missing',2,0,lambda x:x['gap_blocks'][0]['subpanels'].pop())
    tamper('exclusion_panel_gap',2,0,lambda x:x['gap_blocks'][0]['subpanels'][0].update(b='999'))
    tamper('exclusion_wrong_bound',2,0,lambda x:x['gap_blocks'][0]['subpanels'][0].update(bound_integer_msun=[-1,1]))
    tamper('exclusion_unknown_method',2,0,lambda x:x['gap_blocks'][0]['subpanels'][0].update(method='PHYSICAL_WAVE'))
    tamper('missing_knot',2,0,lambda x:x.update(source_knots_in_band=[]))
    tamper('unsupported_global_gap_promotion',2,0,lambda x:x.update(all_gaps_excluded=False))
    tamper('independent_false',3,0,lambda x:x.update(all_real_A_band_excluded_outside_unique_brackets=False))
    tamper('independent_count_changed',3,0,lambda x:x.update(selected_mathematical_D_exact_zero_count=4))
    tamper('independent_method_counts_changed',3,0,lambda x:x.update(proof_methods={'P':0,'D':0,'X':0}))
    tamper('one_source_band_endpoint_changed',0,0,lambda x:x.update(A_band=['3','4']))
    tamper('nonmonotone_original_nodes',0,0,lambda x:x['nodes'][0].update(r=x['nodes'][10]['r']))
    tamper('zero_lens_source',0,0,lambda x:x.update(lens=''))
    obj={'schema':'HIST001D_EXACT16_KNOT_SAFE_ADVERSARIAL_V1','cases':rejects,
       'all_rejected':True,'count':len(rejects),'physical_provider_admitted':False,
       'empirical_validation':'NOT_ESTABLISHED'}
    p=ROOT/'results/adversarial_exact_count.json'
    p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    print('ADVERSARIAL_REJECT',len(rejects),'SHA',sha(p.read_bytes()))
if __name__=='__main__':run()
