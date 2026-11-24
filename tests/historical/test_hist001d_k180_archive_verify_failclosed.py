"""Source-free optimized-Python hash/verifier safety regression for PR #51."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / 'reference' / 'hist001d_k180_saturation_candidate' / 'verify_archive.py'
SPEC = importlib.util.spec_from_file_location('hist001d_saturation_verify_archive', VERIFY)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def digest(b):
    return hashlib.sha256(b).hexdigest()


class SaturationArchiveFailClosedTests(unittest.TestCase):
    def test_valid_synthetic_byte_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'sample').write_bytes(b'good')
            self.assertEqual(MOD.verify_file_map(root, {'sample': digest(b'good')}, parents=False), 1)

    def test_altered_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'sample').write_bytes(b'forgery')
            with self.assertRaisesRegex(ValueError, 'FILE_SHA256_MISMATCH'):
                MOD.verify_file_map(root, {'sample': digest(b'good')}, parents=False)

    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, 'MANIFEST_PATH_ESCAPE'):
                MOD.verify_file_map(Path(td), {'../secret': '0' * 64}, parents=False)

    def test_missing_original_parent_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'sample').write_bytes(b'good')
            with self.assertRaisesRegex(ValueError, 'PINNED_PARENT_HASH_MISMATCH'):
                MOD.verify_file_map(root, {'sample': digest(b'good')}, parents=True)

    def test_optimized_interpreter_does_not_bypass_integrity(self):
        code = (
            "import hashlib,tempfile; from pathlib import Path; "
            "from verify_archive import verify_file_map; "
            "root=Path(tempfile.mkdtemp()); (root/'part').write_bytes(b'bad'); "
            "verify_file_map(root, {'part':hashlib.sha256(b'good').hexdigest()},parents=False)"
        )
        env = os.environ.copy()
        env['PYTHONPATH'] = str(VERIFY.parent)
        proc = subprocess.run([sys.executable, '-OO', '-c', code], env=env,
                              capture_output=True, text=True, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('FILE_SHA256_MISMATCH', proc.stderr)


if __name__ == '__main__':
    unittest.main()
