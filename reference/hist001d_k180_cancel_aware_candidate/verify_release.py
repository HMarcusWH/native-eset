#!/usr/bin/env python3
"""Fail-closed SHA/source/claims check for selected-M* signed affine quadrature candidate.

No physical validation/metric provider is produced by this tool.
"""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def manifest():
    p=ROOT/'MANIFEST_SHA256.json'
    data=json.loads(p.read_text())
    if data.get('schema')!='HIST001D_CANCEL_AWARE_AFFINE_PROTECTED_RELEASE_V1' or data.get('physical_provider_admitted') is not False or data.get('empirical_validation')!='NOT_ESTABLISHED':
        raise ValueError('release manifest schema/claim firewall')
    paths=data.get('files',{})
    if len(paths)<17 or 'inputs/inter_node_parent_v1.zip' not in paths:
        raise ValueError('manifest missing protected parent')
    for name,expected in paths.items():
        if name.startswith('/') or '..' in Path(name).parts or sha(ROOT/name)!=expected:
            raise ValueError('archive content or SHA mismatch: '+name)
    return data

def run_full():
    from verify_affine_signed import verify_all
    from assemble_affine import assemble
    from adversarial_affine import run as adversarial
    # Verify independent signed-arithmetic aggregate & original frozen nodal Q.
    verify_all(source_check=True)
    old=[(ROOT/'results'/f'signed_lens_{j}.json').read_bytes() for j in range(6)]
    with tempfile.TemporaryDirectory() as dirname:
        td=Path(dirname)
        def reproduce(j):
            target=td/f'signed_lens_{j}.json'
            run=subprocess.run([sys.executable,str(SOURCE/'signed_affine_producer.py'),
                   '--lens',str(j),'--n','128','--out',str(target)],
                   cwd=ROOT,capture_output=True,text=True)
            if run.returncode:
                raise RuntimeError('data-dependent producer failed '+str(j)+': '+run.stderr[-2000:])
            if target.read_bytes()!=old[j]:
                raise ValueError('data-dependent producer receipt changed for lens '+str(j))
            return j
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            computed=list(pool.map(reproduce,range(6)))
        if computed!=list(range(6)):raise ValueError('missing source-dependent replay')
    saved=(ROOT/'results/aggregate.json').read_bytes()
    assemble()
    if (ROOT/'results/aggregate.json').read_bytes()!=saved:raise ValueError('aggregate not byte-identical')
    saved=(ROOT/'results/adversarial_qa.json').read_bytes()
    adversarial()
    if (ROOT/'results/adversarial_qa.json').read_bytes()!=saved:raise ValueError('adversarial QA not byte-identical')
    oldver=(ROOT/'results/verify_affine.json').read_bytes()
    verified=verify_all(source_check=True)
    rep={'schema':'HIST001D_CANCEL_AWARE_AFFINE_INDEPENDENT_FRACTION_Q_REPLAY_V1',
         'lenses':verified,'all_six_pass':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    now=(json.dumps(rep,indent=2,sort_keys=True)+'\n').encode()
    if now!=oldver:raise ValueError('independent verification receipt not reproducible')
    tests=subprocess.run([sys.executable,'-m','pytest','-q',
       'tests/historical/test_hist001d_cancel_affine_source_free.py'],cwd=ROOT,capture_output=True,text=True)
    if tests.returncode:raise ValueError('source-free tests failed: '+tests.stdout[-1000:])
    print('FULL_REPLAY_SIX_RECEIPTS_BYTE_IDENTICAL','INDEPENDENT_Q_774_ENDPOINTS_PASS',
      'SOURCE_FREE_TESTS_36_PASS','ADVERSARIAL_29_REJECTED',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');x=p.parse_args()
    m=manifest()
    from verify_affine_signed import verify_all
    from assemble_affine import assemble
    from adversarial_affine import run as adversarial
    v=verify_all(source_check=True)
    if len(v)!=6 or sum(q['subbands'] for q in v)!=768:raise ValueError('wrong subband count')
    aggregate=json.loads((ROOT/'results/aggregate.json').read_text())
    if aggregate.get('total_verified_aperture_subbands')!=768 or aggregate.get('physical_provider_admitted') is not False or aggregate.get('all_sign_definite_bands') is not False:
        raise ValueError('invalid physical/continuum claim')
    qa=json.loads((ROOT/'results/adversarial_qa.json').read_text())
    if len(qa.get('cases',[]))!=29 or not qa.get('all_rejected'):raise ValueError('adversarial QA not present')
    print('QUICK_RELEASE_SHA_PASS',len(m['files']),'SIX_LENSES',len(v),'TOTAL_SUBBANDS',768,flush=True)
    if x.full:run_full()

if __name__=='__main__':main()
