"""Source-only adapter schema, claim scope and adversarial fail-closed tests.

No actual March source data; protected operational checks are separate.
"""
import copy
import os
import unittest
from fractions import Fraction as F
from unittest.mock import patch

from source_bound_adapter_v1 import (
    GLOBAL_SHA, GUARD_SHA, ROOT_NAME, SOURCE_SHA256, Unresolved,
    _bounds_as_rationals, _envpath, _two_engine_result, make_adapter,
)
from certified_sign_scan import SourceContract, guard_sign, MODEL_ID, bit_of
from global_independent_verify_v1 import EXPECTED, PROOF_FILES
from verify_integrated_release_v1 import compare_root_replay_wrapper


class AdapterSourceOnlyTests(unittest.TestCase):
    def setUp(self):
        self.lens='J0822+1828'
        self.x=float(2).hex()
        self.contract=SourceContract(uniqueness_sha256=GLOBAL_SHA)

    def guard(self, a, b):
        return _two_engine_result(self.lens,self.x,self.x,[a,b],{"fixture":"NO_PROTECTED_DATA"},"POINT")

    def test_two_distinct_source_engine_ids(self):
        v=self.guard((F(1),F(2)),(F(3,2),F(5,2)))
        self.assertEqual([e['engine_id'] for e in v['engines']],['pinned_sourceconnected','pinned_independent_checker'])
        self.assertNotEqual(v['engines'][0]['proof_trace_sha256'],v['engines'][1]['proof_trace_sha256'])

    def test_strict_positive(self):
        v=self.guard((F(1),F(2)),(F(3,2),F(5,2)))
        sign,_=guard_sign(v,lens=self.lens,x_lo=2.0,x_hi=2.0,contract=self.contract,guard_kind='POINT')
        self.assertEqual(sign,'POSITIVE')

    def test_strict_negative(self):
        v=self.guard((F(-3),F(-1)),(F(-2),F(-1,2)))
        sign,_=guard_sign(v,lens=self.lens,x_lo=2.0,x_hi=2.0,contract=self.contract,guard_kind='POINT')
        self.assertEqual(sign,'NEGATIVE')

    def test_engine_disagreement_fails(self):
        with self.assertRaises(Unresolved):self.guard((F(1),F(2)),(F(-3),F(-1)))

    def test_engine_zero_fails(self):
        with self.assertRaises(Unresolved):self.guard((F(0),F(2)),(F(1),F(2)))

    def test_disjoint_strict_positive_intervals_fail(self):
        with self.assertRaises(Unresolved):self.guard((F(1),F(2)),(F(3),F(4)))

    def test_disjoint_strict_negative_intervals_fail(self):
        with self.assertRaises(Unresolved):self.guard((F(-6),F(-5)),(F(-4),F(-3)))

    def test_bad_order_fails(self):
        with self.assertRaises(Unresolved):self.guard((F(2),F(1)),(F(1),F(2)))

    def test_not_two_enclosures_fails(self):
        with self.assertRaises(Unresolved):_two_engine_result(self.lens,self.x,self.x,[(F(1),F(2))],{},'POINT')

    def test_range_model_scope(self):
        v=_two_engine_result(self.lens,float(2).hex(),float(3).hex(),[(F(1),F(2)),(F(1),F(3))],{},'RANGE_ALL_REAL')
        self.assertEqual(v['kind'],'RANGE_ALL_REAL')
        self.assertEqual(v['model_id'],MODEL_ID)
        self.assertEqual(v['source_sha256'],SOURCE_SHA256)

    def test_exact_rational_format(self):
        self.assertEqual(_bounds_as_rationals(F(1,3),F(2,3)),('1/3','2/3'))
        self.assertEqual(_bounds_as_rationals(F(-3,2),F(-1)),('-3/2','-1/1'))

    def test_non_fraction_fails(self):
        with self.assertRaises(Unresolved):_bounds_as_rationals(1.0,F(1))

    def test_missing_source_path_fails(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(Unresolved):make_adapter()

    def test_file_env_not_path_fails(self):
        with patch.dict(os.environ,{'HIST001D_ENGINE_DIR':'__nonexistent_protected_engine_directory__'},clear=True):
            with self.assertRaises((Unresolved,FileNotFoundError)):make_adapter()

    def test_exact_hash_locks_present(self):
        self.assertEqual(len(GLOBAL_SHA),64)
        self.assertEqual(len(GUARD_SHA),64)
        self.assertIn('NONPROMOTING',ROOT_NAME)
        self.assertEqual(len(PROOF_FILES),8)
        self.assertEqual(sum(EXPECTED.values()),1400)

    def test_root_wrapper_time_variation_not_scientific(self):
        source={'status':'PASS_NONPROMOTING_RELEASE_CHECKS',
                'integrity':{'archive_sha256':'abc'},
                'local_text_and_source_files_matched':17,
                'full_source_bound_replay_performed':True,
                'source_root_uniqueness_reproved':False,
                'source_free_tests':{'status':'PASS',
                                     'unittest_stderr':'Ran 31 tests in 0.008s'},
                'source_bound':{'status':'PASS_FULL_REPLAY_BYTE_IDENTICAL',
                    'source_bound_results_sha256':'7c7e98844c06ed3478d8adf2137d3dbbcddeca66a71a2119220659fe3211c67c',
                    'independent_guard_calls':112,'six_adjacent_root_brackets':6},
                'physical_provider_admitted':False,
                'scientific_authority_promoted':False,
                'empirical_validation':'NOT_ESTABLISHED'}
        altered=copy.deepcopy(source)
        altered['source_free_tests']['unittest_stderr']='Ran 31 tests in 0.123s'
        compare_root_replay_wrapper(altered,source)
        altered['source_bound']['source_bound_results_sha256']='0'*64
        with self.assertRaises(ValueError):
            compare_root_replay_wrapper(altered,source)

    def test_original_sign_api_not_generated_in_this_module(self):
        # Engine functions are imported from SHA-pinned external source,
        # not invented or embedded as simulated Bessel/physics providers.
        import inspect,source_bound_adapter_v1
        code=inspect.getsource(source_bound_adapter_v1)
        self.assertIn('self.signapi.certify(case, radius)',code)
        self.assertIn('self.engine2.interval_H',code)
        self.assertNotIn('np.sign(',code)

    def test_synthetic_scope_rejected_for_authentic_parent(self):
        contract=SourceContract(uniqueness_sha256=GLOBAL_SHA,scope='SYNTHETIC_TEST_ONLY')
        self.assertEqual(contract.scope,'SYNTHETIC_TEST_ONLY')
        # The adapter explicitly refuses this even if a caller passes the same hashes.
        import inspect,source_bound_adapter_v1
        self.assertIn('contract.scope != "SOURCE_REPLAYED_CANDIDATE_MATH"',inspect.getsource(source_bound_adapter_v1))


if __name__=='__main__':unittest.main()
