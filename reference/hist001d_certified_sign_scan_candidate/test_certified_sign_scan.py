"""Source-free deterministic tests. They do not test original March physical or Bessel inputs."""
import copy
import hashlib
import json
import math
import os
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from certified_sign_scan import (
    ALLOWED_STATUSES, BRACKETS_HEX, BRACKET_ZIP_SHA256, DOMAIN_HI, DOMAIN_LO,
    MODEL_ID, SOURCE_SHA256, SourceContract, SyntheticOracle, Unresolved,
    adaptive_cover_one, bit_of, canonical_json, digest, float_of, guard_sign,
    parent_attestation, rational, scan, validate_receipt, verify_partition,
    verify_source_replay,
)

C = SourceContract(uniqueness_sha256='e'*64, scope='SYNTHETIC_TEST_ONLY')

class CorruptOracle(SyntheticOracle):
    def __init__(self, change=None, **kwargs):
        super().__init__(**kwargs)
        self.change = change
    def _make(self, lens, a, b, kind):
        res = super()._make(lens,a,b,kind)
        if self.change:
            self.change(res)
        return res

class ParentCorruptOracle(SyntheticOracle):
    def __init__(self,key,value):
        self.key=key;self.value=value
    def replay_parents(self,contract):
        data=super().replay_parents(contract)
        data[self.key]=self.value
        return data

def reh(a):
    a['receipt_sha256'] = digest({k:v for k,v in a.items() if k!='receipt_sha256'})
    return a

class SourceOnlyTests(unittest.TestCase):
    def setUp(self):
        self.api=SyntheticOracle()
        self.good=scan(self.api,C)

    def test_complete_synthetic_six(self):
        self.assertEqual(self.good['status'],'CERTIFIED_CONDITIONAL')
        self.assertEqual(len(self.good['lens_results']),6)
    def test_model_identity(self):
        self.assertEqual(self.good['model_id'],MODEL_ID)
    def test_original_source_hash(self):
        self.assertEqual(self.good['source_sha256'],SOURCE_SHA256)
    def test_bracket_parent_hash(self):
        self.assertEqual(self.good['bracketing_package_sha256'],BRACKET_ZIP_SHA256)
    def test_no_physical_claim(self):
        self.assertIs(self.good['physical_provider_admitted'],False)
    def test_no_observational_validation(self):
        self.assertEqual(self.good['empirical_validation'],'NOT_ESTABLISHED')
    def test_no_compiled_float_claim(self):
        self.assertIs(self.good['original_compiled_float_signs_certified'],False)
    def test_no_original_offgrid_root(self):
        self.assertIs(self.good['original_March_offgrid_root_certified'],False)
    def test_no_canonical_change(self):
        self.assertIs(self.good['canonical_theory_state_changed'],False)
    def test_synthetic_labeled(self):
        self.assertEqual(self.good['verification_scope'],'SYNTHETIC_TEST_ONLY')
    def test_one_ulp_for_six(self):
        for a,b in BRACKETS_HEX.values():
            self.assertEqual(bit_of(float.fromhex(b))-bit_of(float.fromhex(a)),1)
    def test_valid_canonical_domain(self):
        self.assertEqual(float_of(bit_of(DOMAIN_LO)).hex(),DOMAIN_LO.hex())
        self.assertEqual(float_of(bit_of(DOMAIN_HI)).hex(),DOMAIN_HI.hex())
    def test_all_six_positive_negative(self):
        for row in self.good['lens_results']:
            self.assertEqual([s['classification'] for s in row['segments']], ['POSITIVE','NEGATIVE'])
    def test_six_each_two_endpoint_evals(self):
        self.assertEqual(sum(x['evaluations'] for x in self.good['lens_results']),12)
    def test_six_all_bits_covered(self):
        for row in self.good['lens_results']:
            verify_partition(row['segments'],bit_of(DOMAIN_LO),bit_of(DOMAIN_HI))
    def test_structure_integrity_pass(self):
        validate_receipt(self.good)
    def test_scope_cannot_claim_real(self):
        with self.assertRaises(Unresolved): validate_receipt(self.good,require_real_source=True)
    def test_exact_fraction(self):
        self.assertEqual(rational('-12/20'),Fraction(-3,5))
    def test_reject_bad_fraction(self):
        with self.assertRaises(Unresolved): rational('0.5')
    def test_reject_fraction_zero_denominator(self):
        with self.assertRaises(Unresolved): rational('1/0')
    def test_reject_nan_code(self):
        with self.assertRaises(Unresolved): bit_of(float('nan'))
    def test_reject_inf_code(self):
        with self.assertRaises(Unresolved): bit_of(float('inf'))
    def test_reject_negative_code(self):
        with self.assertRaises(Unresolved): bit_of(-1.0)
    def test_reject_negative_integer_code(self):
        with self.assertRaises(Unresolved): float_of(-5)
    def test_parent_missing_unresolved(self):
        x=scan(SyntheticOracle(unavailable=True),C)
        self.assertEqual(x['status'],'UNRESOLVED')
        self.assertTrue(all(y['status']=='UNRESOLVED' for y in x['lens_results']))
    def test_api_missing_unresolved(self):
        self.assertEqual(scan(None,C)['status'],'UNRESOLVED')
    def test_theorem_hash_missing_unresolved(self):
        self.assertEqual(scan(self.api, SourceContract(scope='SYNTHETIC_TEST_ONLY'))['status'],'UNRESOLVED')
    def test_wrong_mathematical_model_unresolved(self):
        c=SourceContract(model_id='DIFFERENT_MODEL',uniqueness_sha256='e'*64,scope='SYNTHETIC_TEST_ONLY')
        self.assertEqual(scan(self.api,c)['status'],'UNRESOLVED')
    def test_parent_source_wrong_unresolved(self):
        self.assertEqual(scan(ParentCorruptOracle('source_sha256','0'*64),C)['status'],'UNRESOLVED')
    def test_parent_theorem_wrong_unresolved(self):
        self.assertEqual(scan(ParentCorruptOracle('theorem_claim','UNIQUE_WITHOUT_PROOF'),C)['status'],'UNRESOLVED')
    def test_parent_scope_wrong_unresolved(self):
        self.assertEqual(scan(ParentCorruptOracle('scope','SOURCE_REPLAYED_CANDIDATE_MATH'),C)['status'],'UNRESOLVED')
    def test_parent_domain_wrong_unresolved(self):
        self.assertEqual(scan(ParentCorruptOracle('domain_lo_hex','0x1.0p+0'),C)['status'],'UNRESOLVED')
    def test_parent_verifier_hash_missing_unresolved(self):
        self.assertEqual(scan(ParentCorruptOracle('verifier_sha256',''),C)['status'],'UNRESOLVED')
    def test_insufficient_budget_unresolved(self):
        self.assertEqual(scan(self.api,C,max_evals_per_lens=1)['status'],'UNRESOLVED')
    def test_zero_budget_unresolved(self):
        self.assertEqual(scan(self.api,C,max_evals_per_lens=0)['status'],'UNRESOLVED')
    def test_guard_wrong_model_unresolved(self):
        self.assertEqual(scan(SyntheticOracle(malformed=True),C)['status'],'UNRESOLVED')
    def test_guard_wrong_source_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x.update(source_sha256='0'*64)),C)['status'],'UNRESOLVED')
    def test_guard_wrong_x_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x.update(lo_hex='0x1.0p+0')),C)['status'],'UNRESOLVED')
    def test_guard_missing_trace_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x['engines'][1].update(proof_trace_sha256='')),C)['status'],'UNRESOLVED')
    def test_guard_double_id_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x['engines'][1].update(engine_id='SYNTHETIC_A')),C)['status'],'UNRESOLVED')
    def test_guard_reversed_bounds_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x['engines'][0].update(lo='2/1',hi='1/1')),C)['status'],'UNRESOLVED')
    def test_guard_zero_interval_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x['engines'][0].update(lo='0/1',hi='0/1')),C)['status'],'UNRESOLVED')
    def test_guard_conflicting_engine_unresolved(self):
        self.assertEqual(scan(CorruptOracle(lambda x:x['engines'][1].update(lo='-3/1',hi='-2/1') if rational(x['engines'][0]['lo'])>0 else x['engines'][1].update(lo='2/1',hi='3/1')),C)['status'],'UNRESOLVED')
    def test_guard_forged_sign_label_ignored(self):
        a=CorruptOracle(lambda x:x.update(sign='POSITIVE')).point_guard('J0822+1828',BRACKETS_HEX['J0822+1828'][0])
        sign,trace=guard_sign(a,lens='J0822+1828',x_lo=float.fromhex(a['lo_hex']),x_hi=float.fromhex(a['hi_hex']),contract=C,guard_kind='POINT')
        self.assertEqual(sign,'POSITIVE')
    def test_receipt_deterministic(self):
        self.assertEqual(canonical_json(self.good),canonical_json(scan(SyntheticOracle(),C)))
    def test_receipt_sha_matches(self):
        self.assertEqual(digest({k:v for k,v in self.good.items() if k!='receipt_sha256'}),self.good['receipt_sha256'])
    def test_receipt_mutation_detected(self):
        a=copy.deepcopy(self.good);a['physical_provider_admitted']=True
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_physics_promotion_rejected(self):
        a=copy.deepcopy(self.good);a['physical_provider_admitted']=True;reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_observation_promotion_rejected(self):
        a=copy.deepcopy(self.good);a['empirical_validation']='VALIDATED';reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_wrong_model_rejected(self):
        a=copy.deepcopy(self.good);a['model_id']='OTHER';reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_wrong_bracket_rejected(self):
        a=copy.deepcopy(self.good);a['lens_results'][0]['segments'][0]['hi_bits']=str(bit_of(DOMAIN_LO));reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_missing_coverage_rejected(self):
        a=copy.deepcopy(self.good);a['lens_results'][0]['segments'].pop();reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_unresolved_promotion_rejected(self):
        a=scan(self.api,C,max_evals_per_lens=1);a['status']='CERTIFIED_CONDITIONAL';reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_missing_parent_rejected(self):
        a=copy.deepcopy(self.good);a['parent_attestation']=None;reh(a)
        with self.assertRaises(Unresolved):validate_receipt(a)
    def test_rehashed_changed_engine_trace_structural_only(self):
        # This tamper can structurally self-rehash: only LIVE SOURCE REPLAY catches it.
        a=copy.deepcopy(self.good)
        a['lens_results'][0]['segments'][0]['proof_links']['left_endpoint_two_engine_traces'][0]['proof_trace_sha256']='0'*64
        reh(a)
        validate_receipt(a)
        self.assertNotEqual(canonical_json(a),canonical_json(self.good))
    def test_partition_overlap_rejected(self):
        a=copy.deepcopy(self.good['lens_results'][0]['segments'])
        a[1]['lo_bits']=a[0]['hi_bits']
        with self.assertRaises(Unresolved):verify_partition(a,bit_of(DOMAIN_LO),bit_of(DOMAIN_HI))
    def test_partition_gap_rejected(self):
        a=copy.deepcopy(self.good['lens_results'][0]['segments'])
        a[1]['lo_bits']=str(int(a[1]['lo_bits'])+1)
        with self.assertRaises(Unresolved):verify_partition(a,bit_of(DOMAIN_LO),bit_of(DOMAIN_HI))
    def test_adaptive_small_window(self):
        a=float.fromhex(BRACKETS_HEX['J0822+1828'][0]);b=float.fromhex(BRACKETS_HEX['J0822+1828'][1]);
        s=adaptive_cover_one('J0822+1828',self.api,C,parent_attestation(self.api,C),lo=a,hi=b,max_evals=10)
        self.assertEqual(s['status'],'CERTIFIED_CONDITIONAL')
        self.assertEqual([x['classification'] for x in s['segments']],['POSITIVE','NEGATIVE'])
        self.assertEqual(sum(int(x['binary64_count']) for x in s['segments']),2)
    def test_adaptive_exhaustive_large_window(self):
        s=adaptive_cover_one('J0822+1828',self.api,C,parent_attestation(self.api,C),max_evals=300)
        self.assertEqual(s['status'],'CERTIFIED_CONDITIONAL')
        self.assertLess(s['evaluations'],300)
        verify_partition(s['segments'],bit_of(DOMAIN_LO),bit_of(DOMAIN_HI))
    def test_adaptive_budget_exhaustion(self):
        s=adaptive_cover_one('J0822+1828',self.api,C,parent_attestation(self.api,C),max_evals=2)
        self.assertEqual(s['status'],'UNRESOLVED')
        self.assertTrue(any(x['classification']=='UNRESOLVED' for x in s['segments']))
    def test_adaptive_outside_domain_rejected(self):
        s=adaptive_cover_one('J0822+1828',self.api,C,parent_attestation(self.api,C),lo=0.01)
        self.assertEqual(s['status'],'UNRESOLVED')
    def test_adaptive_missing_range_guard_unresolved(self):
        class NoRange(SyntheticOracle):
            range_guard=None
        s=adaptive_cover_one('J0822+1828',NoRange(),C,parent_attestation(self.api,C),max_evals=5)
        self.assertEqual(s['status'],'UNRESOLVED')
    def test_adaptive_no_root_count(self):
        s=adaptive_cover_one('J0822+1828',self.api,C,parent_attestation(self.api,C),max_evals=300)
        self.assertIsNone(s['root_bracket'])
    def test_disable_python_assertions_safe(self):
        base=Path(__file__).parent
        cmd=[sys.executable,'-O',str(base/'scan_cli.py'),'--synthetic','--mode','theorem','--max-evals-per-lens','0']
        result=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)['status'],'UNRESOLVED')
    def test_cli_without_adapter_exit_2(self):
        base=Path(__file__).parent
        result=subprocess.run([sys.executable,str(base/'scan_cli.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)['status'],'UNRESOLVED')
    def test_cli_source_only_synthetic_exit_0(self):
        base=Path(__file__).parent
        result=subprocess.run([sys.executable,str(base/'scan_cli.py'),'--synthetic'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual(json.loads(result.stdout)['verification_scope'],'SYNTHETIC_TEST_ONLY')
    def test_cli_check_receipt(self):
        base=Path(__file__).parent
        path=base/'synthetic_theorem_receipt.json'
        result=subprocess.run([sys.executable,str(base/'scan_cli.py'),'--check-receipt',str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertIn('STRUCTURE_ONLY_PASS',result.stdout)

if __name__=='__main__': unittest.main(verbosity=2)
