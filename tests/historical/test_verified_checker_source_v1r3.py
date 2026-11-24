"""Source-free regression for v1r3 archive-vs-executable checker attestation."""
from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2] / 'reference/hist001d_k180_crossing_band_candidate/verify_release_hardened_v1r3.py'
SPEC = importlib.util.spec_from_file_location('hist001d_v1r3_attested_checker', SOURCE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class IntegrityBindings(unittest.TestCase):
    @staticmethod
    def digest(b: bytes) -> str:
        return hashlib.sha256(b).hexdigest()

    def test_exact_synthetic_source_matches(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'checker.py'
            data = b'def validate(o): return 1\n'
            p.write_bytes(data)
            self.assertEqual(MOD.attest_checker_file(p, data, self.digest(data)), data)

    def test_modified_local_checker_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'checker.py'
            good = b'def validate(o): return 1\n'
            p.write_bytes(b'def validate(o): return 999\n')
            with self.assertRaisesRegex(ValueError, 'LOCAL_CHECKER_NOT_ARCHIVE_IDENTICAL'):
                MOD.attest_checker_file(p, good, self.digest(good))

    def test_modified_archive_checker_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'checker.py'
            good = b'def validate(o): return 1\n'
            p.write_bytes(good)
            with self.assertRaisesRegex(ValueError, 'ARCHIVED_CHECKER_NOT_REVIEWED_SOURCE'):
                MOD.attest_checker_file(p, b'def validate(o): return 2\n', self.digest(good))

    def test_missing_local_checker_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'absent.py'
            b = b'valid\n'
            with self.assertRaisesRegex(ValueError, 'LOCAL_CHECKER_MISSING_OR_SYMLINK'):
                MOD.attest_checker_file(p, b, self.digest(b))

    def test_local_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'other.py'
            b = b'valid\n'
            p.write_bytes(b)
            link = Path(td)/'checker.py'
            try:
                link.symlink_to(p)
            except (OSError, NotImplementedError):
                self.skipTest('symlinks unavailable on this platform')
            with self.assertRaisesRegex(ValueError, 'LOCAL_CHECKER_MISSING_OR_SYMLINK'):
                MOD.attest_checker_file(link, b, self.digest(b))

    def test_bad_external_hash_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/'checker.py'
            p.write_bytes(b'valid\n')
            with self.assertRaisesRegex(ValueError, 'INVALID_HEX_SHA256'):
                MOD.attest_checker_file(p, b'valid\n', 'not-a-hash')

    def test_double_optimized_tamper_rejected(self):
        payload = (
            'import hashlib,tempfile;from pathlib import Path;'
            'from verify_release_hardened_v1r3 import attest_checker_file;'
            'p=Path(tempfile.mkdtemp())/"checker.py";'
            'g=b"good source";p.write_bytes(b"forged source");'
            'attest_checker_file(p,g,hashlib.sha256(g).hexdigest())'
        )
        env = os.environ.copy()
        env['PYTHONPATH'] = str(SOURCE.parent)
        r = subprocess.run([sys.executable, '-OO', '-c', payload], env=env,
                           capture_output=True, text=True, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('LOCAL_CHECKER_NOT_ARCHIVE_IDENTICAL', r.stderr)


if __name__ == '__main__':
    unittest.main()
