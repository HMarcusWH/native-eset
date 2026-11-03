#!/usr/bin/env python3
"""Authenticated clean-archive and optional full recomputation gate, nonpromoting.

The protected archive is self-contained; public GitHub contains only text source/tests.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,tempfile,shutil,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from inter_node_claim_guard import load  # noqa: E402
SAT='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
BAND='cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'
BESSEL='5ce43bc85234279ff0ceceecdad4c92e033e38c50f3bdb7ad048e6d97d9ed5d3'

def sha(b):return hashlib.sha256(b).hexdigest()

def check(root:Path):
    man=json.loads((root/'MANIFEST_SHA256.json').read_text())
    if man.get('schema')!='HIST001D_INTER_NODE_PROTECTED_RELEASE_SHA256_V1' or not isinstance(man.get('files'),dict):
        raise ValueError('release manifest invalid')
    expected=set(man['files'])
    actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file() and not any(seg.startswith('.') for seg in f.relative_to(root).parts) and '__pycache__' not in f.parts}
    if actual!=expected|{'MANIFEST_SHA256.json'}:
        raise ValueError('archive file set changed (missing or unexpected files): '+str(sorted(actual^ (expected|{'MANIFEST_SHA256.json'}))[:10]))
    for rel,digest in man['files'].items():
        p=(root/rel).resolve()
        if not p.is_relative_to(root.resolve()) or not p.is_file() or sha(p.read_bytes())!=digest:
            raise ValueError('content SHA mismatch '+rel)
    for name,required in [('saturation_parent_v1r1.zip',SAT),('crossing_band_parent_v1r2.zip',BAND),('bessel_integral_parent.zip',BESSEL)]:
        if sha((root/'inputs'/name).read_bytes())!=required:raise ValueError('protected scientific source parent changed')
    inter,bv,meta=load(root)
    if (meta['total_certified_subpanels']!=sum(len(x['panels']) for x in inter) or
        meta['total_new_integral_Bessel_evaluations']!=sum(len(x['midpoints']) for x in inter) or
        meta['total_unresolved_real_radial_subpanels']!=0 or
        meta['physical_provider_admitted'] is not False or meta['independent_external_math_referee_completed'] is not False):
        raise ValueError('aggregate status overstated')
    for rel,digest in meta['source_receipts_sha256'].items():
        if sha((root/rel).read_bytes())!=digest:raise ValueError('signed receipt differs '+rel)
    for name in ('verify_independent.json','verify_bv.json'):
        if json.loads((root/'results'/name).read_text()).get('all_pass') is not True:
            raise ValueError('independent verifier outcome absent')
    adverse=json.loads((root/'results/adversarial_qa.json').read_text())
    if adverse.get('count')!=32 or adverse.get('all_rejected') is not True:raise ValueError('adversarial QA false')
    print('RELEASE_CHECK_PASS',len(expected),'SHA entries',meta['total_certified_subpanels'],'panels',flush=True)
    return man

def runner(root:Path,args:list[str]):
    cmd=[sys.executable,str(root/'reference/hist001d_k180_inter_node_candidate'/args[0]),*args[1:]]
    print('RUN',*args,flush=True)
    subprocess.run(cmd,cwd=root,check=True)

def full_replay(root:Path,man:dict):
    old={rel:sha((root/rel).read_bytes()) for rel in man['files'] if rel.startswith('results/')}
    # Reproduce source-locked 512-bit integral calls across all six original grids,
    # with deterministic per-lens JSON output and no mutation of original source.
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures=[pool.submit(runner,root,['inter_node_producer.py','--lens',str(i)]) for i in range(6)]
        for f in futures:f.result()
    runner(root,['verify_inter_node.py'])
    runner(root,['band_bv_producer.py'])
    runner(root,['verify_band_bv.py'])
    runner(root,['inter_node_adversarial_qa.py'])
    runner(root,['assemble_inter_node.py'])
    subprocess.run([sys.executable,'-m','pytest','-q','tests/historical/test_hist001d_k180_inter_node_source_free.py'],cwd=root,check=True)
    for rel,digest in old.items():
        if sha((root/rel).read_bytes())!=digest:raise ValueError('clean-source replay is not byte-identical: '+rel)
    print('FULL_CLEAN_REPLAY_ALL_RESULTS_BYTE_IDENTICAL',len(old),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--full',action='store_true',help='full protected source and independent Fraction replay')
    a=p.parse_args();man=check(a.root)
    if a.full:full_replay(a.root,man);check(a.root)
    print('NONPROMOTING_ONLY')
if __name__=='__main__':main()
