#!/usr/bin/env python3
"""Verify immutable file bytes + scoped claims only; NOT replay of scientific maths."""
import hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED_PARENT={
'original_parent.zip':'3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18',
'all180_parent.zip':'2e3c13ba68bbed98ef2c529a2e331b15c666d8927da22daf1be78d33a79f6391',
'c3_derivative_parent.zip':'725d7ba004d1bd54fb6be2838ca995fc5ba7ce45b54213f1926f0d78bd7e7f11'
}
def sha(x):return hashlib.sha256(x).hexdigest()
def verify():
    manifest=json.loads((ROOT/'MANIFEST_SHA256.json').read_bytes())
    assert manifest['schema']=='HIST001D_MARCH180_K180_SATURATION_SOURCE_INTEGRITY_V1'
    found={}
    for path,expect in manifest['files'].items():
        f=ROOT/path
        assert f.is_file() and sha(f.read_bytes())==expect, f'file integrity failure: {path}'
        found[path]=expect
    for path,s in EXPECTED_PARENT.items():assert manifest['files'][path]==s
    for name in ['endpoint_saturation_producer','endpoint_saturation_independent','all_aperture_bv_producer','all_aperture_bv_independent','node_only_nonidentifiability']:
        d=json.loads((ROOT/(name+'.json')).read_bytes())
        assert d.get('physical_provider_admitted',d.get('physical_density_source_admitted')) is False or name=='node_only_nonidentifiability'
        assert d.get('empirical_validation')=='NOT_ESTABLISHED'
    print('ARCHIVE_MEMBER_SHA_PASS',len(found))
if __name__=='__main__':verify()
