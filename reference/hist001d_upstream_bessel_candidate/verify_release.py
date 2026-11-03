#!/usr/bin/env python3
"""Protected source+mathematical candidate archive verifier (no promotion)."""
from __future__ import annotations
import hashlib,json,sys,subprocess,tempfile,argparse
from pathlib import Path
from independent_stencil_check import check,PARENT_SHA
from adversarial_qa import audit
sha=lambda b:hashlib.sha256(b).hexdigest()
PUBLIC_DIR='reference/hist001d_upstream_bessel_candidate'

def verify(root:Path,full:bool=False):
    manifest=json.loads((root/'MANIFEST_SHA256.json').read_bytes())
    if manifest.get('schema')!='HIST001D_BESSEL_SOURCE_GRADIENT_K180_PROTECTED_RELEASE_V1':raise ValueError('wrong manifest schema')
    files=manifest.get('files',{})
    if not files or len(files)!=len(set(files)):raise ValueError('missing or duplicate release files')
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts}
    expected=set(files)|{'MANIFEST_SHA256.json'}
    if actual!=expected:raise ValueError('membership mismatch: missing '+str(expected-actual)+' extra '+str(actual-expected))
    for path,h in files.items():
        p=(root/path)
        if not p.is_file() or not p.resolve().is_relative_to(root.resolve()) or sha(p.read_bytes())!=h:
            raise ValueError('file SHA256 '+path)
    sat=root/'inputs/saturation_parent.zip'
    if sha(sat.read_bytes())!=PARENT_SHA:raise ValueError('source parent hash')
    data=json.loads((root/'results/upstream_float_split_v1.json').read_bytes())
    out=check(sat,root,data)
    expected_independent=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode()
    if (root/'results/independent_stencil_check_v1.json').read_bytes()!=expected_independent:
        raise ValueError('independent witness mismatch')
    qa=audit(root,sat,data)
    expected_qa=(json.dumps(qa,sort_keys=True,indent=2)+'\n').encode()
    if (root/'results/adversarial_qa_v1.json').read_bytes()!=expected_qa:
        raise ValueError('QA witness mismatch')
    if not qa['all_rejected']:raise ValueError('tamper QA not passed')
    if full:
        with tempfile.TemporaryDirectory(prefix='hist001d-bessel-source-replay-') as td:
            td=Path(td)
            (td/'reference/hist001d_upstream_bessel_candidate').mkdir(parents=True)
            (td/'reference/hist001d_k180_saturation_candidate').mkdir(parents=True)
            for part in ('all180_math.py','all180_independent.py'):
                (td/'reference/hist001d_k180_saturation_candidate'/part).write_bytes(
                    (root/'reference/hist001d_k180_saturation_candidate'/part).read_bytes())
            newcode=td/'reference/hist001d_upstream_bessel_candidate/upstream_float_split.py'
            newcode.write_bytes((root/PUBLIC_DIR/'upstream_float_split.py').read_bytes())
            outjson=td/'results/upstream_float_split_v1.json'
            subprocess.run([sys.executable,str(newcode),'--sat',str(sat),'--out',str(outjson)],check=True,cwd=td)
            if outjson.read_bytes()!=(root/'results/upstream_float_split_v1.json').read_bytes():
                raise ValueError('full source replay JSON byte mismatch')
            for lens in data['lenses']:
                rel=lens['original_replayed_float_mass_binary_file']
                if (td/rel).read_bytes()!=(root/rel).read_bytes():raise ValueError('float mass sample replay differs '+lens['lens_id'])
    print('BESSEL_SOURCE_RELEASE_PASS',len(files),'paths',len(data['lenses']),'lenses',
          '26 QA rejected','source replay',full)
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--full',action='store_true')
    a=p.parse_args();verify(a.root.resolve(),a.full)
