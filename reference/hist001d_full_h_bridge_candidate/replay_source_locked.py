#!/usr/bin/env python3
"""Protected full-H release clean replay with the original immutable March input.

Quick: re-evaluate finite-H arithmetic/coverage/QA from nested source.
Full: also rerun all six expensive interval-Bessel smooth endpoint evaluations.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()

def replay(root:Path,full=False):
    prior=root/'inputs/HIST001D_MARCH180_K180_SIX_CROSSING_BANDS_CONDITIONAL_v1r2_NONPROMOTING.zip'
    diagnostic=root/'inputs/HIST001D_K180_Root_Aperture_Six_Lens_Diagnostic_NONPROOF_v1_2026_11_02.json'
    if sha(prior.read_bytes())!='cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77':raise ValueError('wrong nested whole band ZIP')
    if sha(diagnostic.read_bytes())!='298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812':raise ValueError('wrong source diagnostic')
    folder=root/'reference/hist001d_full_h_bridge_candidate'
    def run(*args):
        subprocess.run([sys.executable,*map(str,args)],cwd=root,check=True)
    with tempfile.TemporaryDirectory() as td:
        work=Path(td)
        with zipfile.ZipFile(prior) as z:
            source=work/'saturation_v1r1.zip';source.write_bytes(z.read('inputs/HIST001D_K180_SATURATED_REVIEW_REPAIR_V1R1_NONPROMOTING_2026_11_02.zip'))
            band=work/'whole_band_certificate.json';band.write_bytes(z.read('results/whole_band_certificate.json'))
        if sha(source.read_bytes())!='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce':raise ValueError('wrong original source')
        finite=work/'finite.json';check=work/'arithmetic_check.json';aggregate=work/'aggregate.json';qa=work/'qa.json'
        run(folder/'full_h_finite_source.py','--source',source,'--diag',diagnostic,'--out',finite)
        run(folder/'verify_full_h_witness.py','--finite',finite,'--source',source,'--diag',diagnostic,'--band',band,'--out',check)
        if sha(finite.read_bytes())!=sha((root/'results/full_H_finite_receipt.json').read_bytes()):raise ValueError('finite receipt changed')
        if sha(check.read_bytes())!=sha((root/'results/independent_finite_H_witness_check.json').read_bytes()):raise ValueError('witness changed')
        endpoint=work/'selected';endpoint.mkdir()
        for i in range(6):
            name=f'selected_H_endpoint_{i}.json'
            target=endpoint/name
            if full:
                run(folder/'continuum_endpoint.py','--index',i,'--source',source,
                    '--diag',diagnostic,'--release',prior,'--out',target,'--bisects',16)
                if sha(target.read_bytes())!=sha((root/'results'/name).read_bytes()):
                    raise ValueError('selected M* endpoint full replay changed '+name)
            else:
                target.write_bytes((root/'results'/name).read_bytes())
        run(folder/'assemble_full_h_bridge.py','--finite',finite,'--source',source,
            '--diag',diagnostic,'--band-archive',prior,'--endpoint-dir',endpoint,'--out',aggregate)
        run(folder/'validate_bridge_summary.py','--receipt',aggregate,'--out',qa)
        if sha(aggregate.read_bytes())!=sha((root/'results/full_H_bridge_aggregate.json').read_bytes()):raise ValueError('aggregate changed')
        if sha(qa.read_bytes())!=sha((root/'results/QA_full_H_bridge.json').read_bytes()):raise ValueError('QA changed')
    return {'status':'PASS_CLEAN_REPLAY_MATCHES_RECORDED_BYTES',
            'mode':'FULL_BESSEL_SOURCE_INTERVAL' if full else 'QUICK_REPLAY_REUSES_SAVED_SELECTED_INTERVAL_ENDPOINTS',
            'selected_smooth_global_root_uniqueness_proved':False,'physical_provider_admitted':False,
            'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--full',action='store_true')
    a=ap.parse_args();print(json.dumps(replay(a.root,a.full),indent=2,sort_keys=True))
