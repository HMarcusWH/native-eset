import importlib.util
import io
from pathlib import Path
import zipfile
import pytest


def verifier():
    p = Path(__file__).resolve().parents[1] / 'tools/verify_final_bundle.py'
    spec = importlib.util.spec_from_file_location('bundle_verifier', p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('value', ['../x', '/x', 'a//b', 'C:/x', 'a\\b', 'a/./b', ''])
def test_bundle_rejects_unsafe_names(value):
    with pytest.raises(ValueError):
        verifier().safe_name(value)


def test_bundle_crc_and_duplicate_casefold():
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as z:
        z.writestr('A.txt', b'a')
        z.writestr('a.txt', b'b')
    with pytest.raises(ValueError):
        verifier().zip_bytes(output.getvalue())


def test_bundle_duplicate_json_and_digest_grammar():
    v = verifier()
    with pytest.raises(ValueError):
        v._json(b'{"a":1,"a":2}')
    with pytest.raises(ValueError):
        v.require_hash('sha256')
