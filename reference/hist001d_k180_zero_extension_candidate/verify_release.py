#!/usr/bin/env python3
"""Fail-closed HIST001D three-additional-sign-witness source-release verifier.

--quick checks sealed files, mathematical claims and prior proved source locks.
--full also executes both numerical engines from fresh extraction of the
unchanged preceding protected release and checks exact output bytes.
"""
from __future__ import annotations
import argparse,hashlib,io,json,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from claim_guard import validate  # noqa: E402
from assemble_brackets import assemble  # noqa: E402
PARENT_SHA='0eec91a8e531516529a58cf811685581233aba6d5bc8150c9897b50de88ae651'
def sha(raw):return hashlib.sha256(raw).hexdigest()

def verify(full=False):
    man=json.loads((ROOT/'MANIFEST_SHA256.json').read_bytes())
    if man.get('schema')!='HIST001D_ADDITIONAL_SIX_ZERO_WITNESSES_MANIFEST_V1' or man.get('physical_provider_admitted') is not False or man.get('empirical_validation')!='NOT_ESTABLISHED' or man.get('exact_zero_count_proved') is not False or man.get('Einstein_root_count_proved') is not False or man.get('zero_lower_bound')!=16:
        raise ValueError('unsafe release manifest')
    files=man['files']
    if len(files)<8:raise ValueError('incomplete protected release')
    seen=set()
    for path,digest in files.items():
        if (path.startswith('/') or '..' in Path(path).parts or path in seen or
            not (ROOT/path).is_file() or sha((ROOT/path).read_bytes())!=digest):
            raise ValueError('missing or altered archive member '+path)
        seen.add(path)
    parraw=(ROOT/'inputs/targeted_parent_v1.zip').read_bytes()
    if sha(parraw)!=PARENT_SHA:raise ValueError('wrong protected parent source')
    z=zipfile.ZipFile(io.BytesIO(parraw));prior_manifest=json.loads(z.read('MANIFEST_SHA256.json'))
    if prior_manifest.get('selected_quadrature_remainder_zeros_lower_bound')!=10 or prior_manifest.get('quadrature_remainder_exact_zero_count_proved') is not False:
        raise ValueError('prior source proof scope changed')
    for name,digest in prior_manifest['files'].items():
        if sha(z.read(name))!=digest:raise ValueError('nested prior source member '+name)
    old=json.loads(z.read('results/targeted_aggregate.json'))
    lenses=[json.loads(z.read(f'results/targeted_lens_{j}.json')) for j in range(6)]
    shas=[sha(z.read(f'results/targeted_lens_{j}.json')) for j in range(6)]
    producer=json.loads((ROOT/'results/extra_sign_witnesses.json').read_bytes())
    independent=json.loads((ROOT/'results/extra_fraction_verify.json').read_bytes())
    result=validate(producer,independent,old,lenses,shas,PARENT_SHA)
    aggregate=assemble()
    sealed=json.loads((ROOT/'results/augmented_zero_brackets.json').read_bytes())
    if aggregate!=sealed or sum(len(v['zero_existence_brackets']) for v in aggregate['lenses'])!=16:
        raise ValueError('incomplete / altered exact rational IVT bracket assembly')
    adv=json.loads((ROOT/'results/adversarial_extra.json').read_bytes())
    if adv.get('schema')!='HIST001D_SUPPLEMENTAL_SIGN_ADVERSARIAL_V1' or adv.get('case_count')!=25 or adv.get('all_rejected') is not True or any(v.get('status')!='REJECTED' for v in adv.get('cases',[])) or len(adv['cases'])!=25:
        raise ValueError('adversarial negative controls')
    if full:
        with tempfile.TemporaryDirectory(prefix='hist001d-zero-ext-') as td:
            temp=Path(td);src=temp/'prior';src.mkdir()
            for member in z.infolist():
                path=Path(member.filename)
                if path.is_absolute() or '..' in path.parts:raise ValueError('archive path traversal')
            z.extractall(src)
            out=temp/'out';out.mkdir()
            env=os.environ.copy()
            env.update(HIST001D_PRIOR_EXTRACT_DIR=str(src),
                       HIST001D_PRIOR_ARCHIVE=str(ROOT/'inputs/targeted_parent_v1.zip'),
                       HIST001D_ZERO_OUT_DIR=str(out))
            for name,expected in [('extra_sign_producer.py','extra_sign_witnesses.json'),
                                   ('verify_extra_sign.py','extra_fraction_verify.json')]:
                command=[sys.executable,str(ROOT/'reference/hist001d_k180_zero_extension_candidate'/name)]
                subprocess.run(command,cwd=ROOT,env=env,check=True)
                if sha((out/expected).read_bytes())!=sha((ROOT/'results'/expected).read_bytes()):
                    raise ValueError('full clean-source replay was not byte-identical: '+expected)
    print('ZERO_EXTENSION_RELEASE_PASS',len(files),'SHA members','zeros>=',result['total_minimum'],
          'full_clean_replay',bool(full),flush=True)
    return True

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--full',action='store_true');q=a.parse_args()
    verify(q.full)
