"""Source-free nonpromoting PR59 proof-guard and executable-identity negatives.

Unit tests use unittest methods, not Python 'assert', so they remain active
when both -O and -OO strip the language-level assertion bytecode.
"""
from __future__ import annotations
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from unittest import TestCase, main, mock
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'reference/hist001d_k180_signed_stencil_candidate'
sys.path.insert(0,str(PROOF))
import finite_difference_bias as producer  # noqa: E402
import verify_signed_bias as independent  # noqa: E402
import attested_replay_v1r2 as att  # noqa: E402


class TestHIST001DPR59FailClosed(TestCase):
    def test_01_producer_nondestructive_kernel(self):
        lo,hi=producer.phi_interval(F(1),F(2))
        self.assertLessEqual(lo,hi)
        self.assertLessEqual(lo,F(1))
        self.assertLessEqual(F(0),hi)

    def test_02_producer_modified_isqrt_rejected(self):
        with mock.patch.object(producer.math,'isqrt',return_value=0):
            with self.assertRaisesRegex(ValueError,'UNRESOLVED'):
                producer.phi_interval(F(1),F(2))

    def test_03_producer_wrong_radius_rejected(self):
        with self.assertRaises(ValueError):producer.phi_interval(F(2),F(0))

    def test_04_producer_negative_aperture_rejected(self):
        with self.assertRaises(ValueError):producer.phi_interval(F(-1),F(1))

    def test_05_source_interval_truncation_rejected(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            producer.signed_node_interval(F(0),F(1),[F(1),F(2)],[F(1)],[(F(1),F(1))]*2)

    def test_06_source_interval_extra_error_rejected(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            producer.signed_node_interval(F(0),F(1),[F(1)],[F(1)],[(F(1),F(1))]*2)

    def test_07_source_interval_empty_rejected(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            producer.signed_node_interval(F(0),F(1),[],[],[])

    def test_08_source_interval_sign_order_rejected(self):
        with self.assertRaises(ValueError):
            producer.signed_node_interval(F(0),F(1),[F(1)],[F(1)],[(F(2),F(1))])

    def test_09_independent_bisection_valid(self):
        lo,hi=independent.sqrt_outward(F(1,4),bits=10)
        self.assertLessEqual(lo*lo,F(1,4))
        self.assertLessEqual(F(1,4),hi*hi)

    def test_10_independent_wrong_bisection_rejected_optimized(self):
        code=(PROOF/'verify_signed_bias.py').read_text()
        needle='lo=0;hi=(1<<bits)+1'
        self.assertEqual(code.count(needle),1)
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'verify_signed_bias.py'
            f.write_text(code.replace(needle,'lo=0;hi=1'))
            script='from fractions import Fraction as F;import sys;sys.path.insert(0,sys.argv[1]); import verify_signed_bias as v;print(v.sqrt_outward(F(1,4)))'
            p=subprocess.run([sys.executable,'-I','-OO','-B','-c',script,str(t)],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('ValueError',p.stderr)

    def test_11_independent_mismatched_lengths_rejected(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            independent.box_sum([F(1),F(2)],[F(1)],[(F(0),F(1))]*2,F(1),F(2))

    def test_12_independent_empty_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            independent.box_sum([],[],[],F(0),F(1))

    def test_13_independent_bad_sqrt_domain_rejected(self):
        with self.assertRaises(ValueError):independent.sqrt_outward(F(-1))

    def test_14_safe_archive_path(self):
        self.assertTrue(att.safe_path('reference/signed/verify.py'))

    def test_15_reject_traversal(self):
        self.assertFalse(att.safe_path('results/../../shadow.json'))

    def test_16_reject_windows_alias(self):
        self.assertFalse(att.safe_path('results/CON.txt'))

    def test_17_reject_windows_sep(self):
        self.assertFalse(att.safe_path('results\\evidence.json'))

    def test_18_reject_trailing_dot(self):
        self.assertFalse(att.safe_path('results/bad.'))

    def test_19_reject_control_char(self):
        self.assertFalse(att.safe_path('results/bad\n.json'))

    def test_20_reject_source_root_alias(self):
        self.assertFalse(att.safe_path('/etc/passwd'))

    def test_21_external_digest_is_mandatory(self):
        with self.assertRaisesRegex(ValueError,'independently supplied'):
            att.inspect_archive(Path('/missing.zip'),'')

    def test_22_malformed_digest_rejected(self):
        with self.assertRaisesRegex(ValueError,'independently supplied'):
            att.inspect_archive(Path('/missing.zip'),'G'*64)

    def test_23_zero_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'zero execution budget'):
            att.replay(Path('/missing.zip'),'0'*64,budget_seconds=0)

    def test_24_boolean_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'zero execution budget'):
            att.replay(Path('/missing.zip'),'0'*64,budget_seconds=True)

    def test_25_pinned_proof_code_hashes_are_complete(self):
        for name,digest in att.CRITICAL_SOURCE_SHA.items():
            self.assertTrue(att.is_sha(digest))
            self.assertEqual(sha256((ROOT/name).read_bytes()).hexdigest(),digest)

    def test_26_pinned_result_records_are_digest_values(self):
        self.assertEqual(len(att.RESULT_SHA),3)
        self.assertTrue(all(att.is_sha(s) for s in att.RESULT_SHA.values()))

    def test_27_wrong_whole_archive_sha_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'n.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('hello.txt','hello')
            with self.assertRaisesRegex(ValueError,'whole-ZIP SHA'):
                att.inspect_archive(p,'1'*64)

    def test_28_zip_missing_required_members_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'n.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('hello.txt','hello')
            with self.assertRaisesRegex(ValueError,'membership'):
                att.inspect_archive(p,sha256(p.read_bytes()).hexdigest())

    def test_29_zip_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'n.zip'
            with zipfile.ZipFile(p,'w') as z:
                for i in range(17):z.writestr(f'valid{i}.txt',str(i))
                z.writestr('../escape.txt','value')
            with zipfile.ZipFile(p) as z:
                with self.assertRaisesRegex(ValueError,'unsafe ZIP'):
                    att.inspect_members(z)

    def test_30_casefold_alias_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'n.zip'
            with zipfile.ZipFile(p,'w') as z:
                for i in range(16):z.writestr(f'valid{i}.txt',str(i))
                z.writestr('A.txt','one');z.writestr('a.txt','two')
            with zipfile.ZipFile(p) as z:
                with self.assertRaisesRegex(ValueError,'alias'):
                    att.inspect_members(z)

    def test_31_symlink_archive_member_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'n.zip'
            with zipfile.ZipFile(p,'w') as z:
                for i in range(17):z.writestr(f'valid{i}.txt',str(i))
                info=zipfile.ZipInfo('link.txt');info.create_system=3
                info.external_attr=(stat.S_IFLNK|0o777)<<16
                z.writestr(info,'../bad.py')
            with zipfile.ZipFile(p) as z:
                with self.assertRaisesRegex(ValueError,'symlink'):
                    att.inspect_members(z)

    def test_32_cli_without_external_hash_is_unresolved_under_oo(self):
        p=subprocess.run([sys.executable,'-I','-OO','-B',str(PROOF/'attested_replay_v1r2.py')],
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,2)
        self.assertIn('UNRESOLVED',p.stdout)

    def test_33_cli_without_budget_is_unresolved_under_oo(self):
        p=subprocess.run([sys.executable,'-I','-OO','-B',str(PROOF/'attested_replay_v1r2.py'),
                          '--archive','not-there.zip','--expected-sha256','0'*64,'--budget-seconds','0'],
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,2)
        self.assertIn('UNRESOLVED',p.stdout)


if __name__=='__main__':main()
