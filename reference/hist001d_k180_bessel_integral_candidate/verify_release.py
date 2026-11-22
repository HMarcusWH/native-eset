#!/usr/bin/env python3
"""Release integrity and independent all-node exact-rational witness replay.

--full also reruns source-derived Bessel-integral reports; optional expensive.
"""
from __future__ import annotations
import argparse,hashlib,zipfile,json,subprocess,sys,tempfile,concurrent.futures
from pathlib import Path
from stencil_verify import verify
# Resolve the sibling guard by file identity: other historical candidates also
# define claim_guard.py, and pytest can cache a different one in sys.modules.
import importlib.util as _hist_importlib_util

def _load_local_claim_guard():
    path = Path(__file__).resolve().with_name("claim_guard.py")
    spec = _hist_importlib_util.spec_from_file_location(
        "hist001d_k180_bessel_integral_claim_guard", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("K180 sibling claim guard cannot be loaded")
    module = _hist_importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate

validate = _load_local_claim_guard()

def _load_local_adversarial_run():
    # Never trust the top-level adversarial_qa module cache.
    path = Path(__file__).resolve().with_name("adversarial_qa.py")
    spec = _hist_importlib_util.spec_from_file_location(
        "hist001d_k180_bessel_integral_adversarial_qa", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("K180 sibling adversarial QA cannot be loaded")
    module = _hist_importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run

ROOT=Path(__file__).resolve().parents[2]

def sha(data):return hashlib.sha256(data).hexdigest()

def check_zip(archive):
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failed')
        members=z.namelist()
        if len(set(members))!=len(members):raise ValueError('duplicate ZIP members')
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        if manifest.get('schema')!='HIST001D_K0K1_REAL_INTEGRAL_PROTECTED_SHA_MANIFEST_V1':raise ValueError('manifest schema')
        mp=manifest['files_sha256']
        if set(members)!=(set(mp)|{'MANIFEST_SHA256.json'}):raise ValueError('ZIP member mismatch')
        if any(n.startswith('/') or '..' in Path(n).parts or n.endswith('/') for n in mp):raise ValueError('illegal ZIP path')
        for name,expected in mp.items():
            if sha(z.read(name))!=expected:raise ValueError('SHA mismatch: '+name)
        print('ZIP_SHA256',sha(Path(archive).read_bytes()),'SHA_MEMBERS',len(mp),'CRC_PASS',flush=True)
    return manifest

def run_quick():
    out=verify(ROOT/'inputs/saturation_parent_v1r1.zip',ROOT/'results')
    expected=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode()
    stored=(ROOT/'results/stencil_summary.json').read_bytes()
    if stored!=expected:raise ValueError('independent fraction arithmetic summary replay differs')
    reports=[json.loads((ROOT/'results'/f'lens_{i}.json').read_text()) for i in range(6)]
    cross=json.loads((ROOT/'results/cross_resolution.json').read_text())
    if not validate(reports,out,cross):
        raise ValueError('independent Bessel report claim guard rejected source evidence')
    from compare_inherited import run as compare_old
    overlap=compare_old(ROOT/'inputs/saturation_parent_v1r1.zip',ROOT/'results')
    if (json.dumps(overlap,sort_keys=True,indent=2)+'\n').encode()!=(ROOT/'results/prior_power_series_overlap.json').read_bytes():
        raise ValueError('prior 512-bit power-series overlap changed')
    qa=_load_local_adversarial_run()()
    actual=(ROOT/'results/adversarial_qa.json').read_bytes()
    if actual!=(json.dumps(qa,sort_keys=True,indent=2)+'\n').encode():raise ValueError('QA result changed')
    result=subprocess.run([sys.executable,'-m','pytest','-q','tests/historical/test_hist001d_bessel_integral_source_free.py'],cwd=ROOT,check=False,capture_output=True,text=True)
    print(result.stdout)
    if result.returncode:raise ValueError('source-free pytest failed '+result.stderr[-2000:])
    print('QUICK_PASS',sha(stored),flush=True)

def run_full():
    with tempfile.TemporaryDirectory(prefix='hist001d_bessel_') as tmp:
        t=Path(tmp)
        source=ROOT/'inputs/saturation_parent_v1r1.zip'
        def one(j):
            dst=t/f'lens_{j}.json'
            script=ROOT/'reference/hist001d_k180_bessel_integral_candidate/source_audit.py'
            p=subprocess.run([sys.executable,str(script),'--source',str(source),'--lens-index',str(j),'--all','--out',str(dst)],capture_output=True,text=True,check=False)
            if p.returncode:raise ValueError('source integral replay failed '+str(j)+' '+p.stderr[-1200:])
            expected=(ROOT/'results'/f'lens_{j}.json').read_bytes()
            if dst.read_bytes()!=expected:raise ValueError('Bessel integral receipt byte mismatch '+str(j))
            return j,sha(expected)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for j,hash_value in sorted(pool.map(one,range(6))):print('FULL_SOURCE_MATH_REPLAY_PASS',j,hash_value,flush=True)
    # Reexecute the two-resolution/Wronskian crosscheck, not only its recorded labels.
    from cross_resolution import calc
    x=calc(str(source))
    if (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()!=(ROOT/'results/cross_resolution.json').read_bytes():
        raise ValueError('cross-resolution/Wronskian receipt byte mismatch')
    print('FULL_PASS')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--archive',required=True);ap.add_argument('--full',action='store_true')
    args=ap.parse_args();check_zip(args.archive);run_quick()
    if args.full:run_full()
