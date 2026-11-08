"""Source-free optimized-interpreter integrity tests for fixed-A protected verifier."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
VERIFY = ROOT / 'reference' / 'hist001d_k180_root_aperture_candidate' / 'protected_verifier_v1r2.py'
SPEC = importlib.util.spec_from_file_location('hist001d_fixed_a_verify', VERIFY)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class FixedAIntegrity(unittest.TestCase):
    def test_valid_synthetic_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'x').write_bytes(b'correct')
            self.assertEqual(MOD.verify_file_map(root, {'x': hashlib.sha256(b'correct').hexdigest()}), 1)

    def test_modified_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'x').write_bytes(b'forged')
            with self.assertRaisesRegex(ValueError, 'MEMBER_HASH_MISMATCH'):
                MOD.verify_file_map(root, {'x': hashlib.sha256(b'correct').hexdigest()})

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, 'MANIFEST_PATH_ESCAPE'):
                MOD.verify_file_map(Path(td), {'../x': '0' * 64})

    def test_python_double_optimized_rejects_mutation(self):
        script = (
            "from protected_verifier_v1r2 import verify_file_map; from pathlib import Path; "
            "import tempfile,hashlib; root=Path(tempfile.mkdtemp()); "
            "(root/'x').write_bytes(b'forged'); "
            "verify_file_map(root, {'x':hashlib.sha256(b'correct').hexdigest()})"
        )
        env = os.environ.copy()
        env['PYTHONPATH'] = str(VERIFY.parent)
        proc = subprocess.run([sys.executable, '-OO', '-c', script], env=env,
                              capture_output=True, text=True, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('MEMBER_HASH_MISMATCH', proc.stderr)


if __name__ == '__main__':
    unittest.main()
