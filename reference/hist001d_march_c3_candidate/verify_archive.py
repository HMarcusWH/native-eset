#!/usr/bin/env python3
"""Verify closed-form mathematical archive manifest and its immutable stage hashes."""
from __future__ import annotations
import argparse,hashlib,json,stat,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'


def h(b:bytes):return hashlib.sha256(b).hexdigest()

def verify_files(root:Path):
    manifest=json.loads((root/'MANIFEST_SHA256.json').read_text())
    if manifest.get('schema')!='HIST001D_MARCH_C3_SOURCE_MATH_FULL_ARCHIVE_SHA_MANIFEST_V1':raise ValueError('wrong schema')
    expected=manifest.get('files')
    if type(expected) is not dict:raise ValueError('invalid file inventory')
    observed={x.relative_to(root).as_posix():h(x.read_bytes()) for x in root.rglob('*')
              if x.is_file() and x.name not in {'MANIFEST_SHA256.json','make_release.py'} and '__pycache__' not in x.parts and '.pytest_cache' not in x.parts and x.suffix!='.pyc'}
    if observed!=expected:
        raise ValueError('manifest mismatch '+str({'missing':list(set(expected)-set(observed)),
                               'additional':list(set(observed)-set(expected)),
                               'different':[p for p in expected if p in observed and expected[p]!=observed[p]]}))
    result_hashes=json.loads((root/'RESULT_HASHES.json').read_text())
    for name,hex_hash in result_hashes['results_sha256'].items():
        if h((root/name).read_bytes())!=hex_hash:raise ValueError('result SHA mismatch '+name)
    if h((root/'inputs/frozen_smooth_shadow_gradient_parent.zip').read_bytes())!=SOURCE_SHA:
        raise ValueError('original source parent archive mismatch')
    return {'status':'PASS_SOURCE_MATH_ARTIFACT_INTEGRITY_ONLY', 'source_sha256':SOURCE_SHA,
            'file_count':len(expected), 'result_count':len(result_hashes['results_sha256']),
            'original_numerical_root_count_certified':False,'physical_provider_admitted':False}

def verify_zip(file:Path):
    with zipfile.ZipFile(file) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or z.testzip():raise ValueError('duplicate or corrupted ZIP')
        for inf in z.infolist():
            p=Path(inf.filename)
            if p.is_absolute() or '..' in p.parts or not inf.filename or inf.is_dir():
                raise ValueError('unsafe archive entry')
            if (inf.external_attr>>16)&0o170000==stat.S_IFLNK:
                raise ValueError('ZIP symlink')
        data={n:z.read(n) for n in names}
    if 'MANIFEST_SHA256.json' not in data:raise ValueError('missing manifest')
    m=json.loads(data['MANIFEST_SHA256.json'])
    if m.get('schema')!='HIST001D_MARCH_C3_SOURCE_MATH_FULL_ARCHIVE_SHA_MANIFEST_V1' or m.get('files')!={n:h(b) for n,b in data.items() if n!='MANIFEST_SHA256.json'}:
        raise ValueError('archive file inventory SHA mismatch')
    if h(data['inputs/frozen_smooth_shadow_gradient_parent.zip'])!=SOURCE_SHA:
        raise ValueError('changed parent source')
    d=json.loads(data['RESULT_HASHES.json'])
    for k,v in d['results_sha256'].items():
        if h(data[k])!=v:raise ValueError('result output changed')
    return {'status':'PASS_ARCHIVED_SOURCE_MATH_BYTES_ONLY','sha256':h(file.read_bytes()),
            'members':len(data),'source_sha256':SOURCE_SHA,
            'original_March_source_float_error_proved':False,'physical_provider_admitted':False}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--archive',type=Path);options=a.parse_args()
    print(json.dumps(verify_zip(options.archive) if options.archive else verify_files(ROOT),indent=2))
