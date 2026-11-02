"""Validate immutable archive hashes or replay exactly one bounded stage."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def file_map():
 return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name not in {'MANIFEST_SHA256.json','RESULT_HASHES.json'} and '__pycache__' not in p.parts}

def check():
 expected=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
 live=file_map()
 assert expected['schema']=='HIST001D_D120_Q_ORIGINAL_MARCH180_CANDIDATE_SHA_MANIFEST_v1'
 assert live==expected['files'],f'file mismatch {set(expected["files"])^set(live)}'
 assert sha(ROOT/'inputs/original_march180_parent_v1r1.zip')=='0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1'
 for name,h in json.loads((ROOT/'RESULT_HASHES.json').read_text())['files'].items():assert sha(ROOT/name)==h,(name,'result sha mismatch')
 print('MANIFEST_AND_RESULT_HASHES_PASS',len(live));return True

def stage(which):
 if which=='capture':code='work/capture_disk120.py';env={}
 elif which=='q':code='work/q_producer.py';env={}
 elif which=='disk':code='work/disk120_math.py';env={}
 elif which=='aggregate':code='work/aggregate.py';env={}
 elif which=='qa':code='work/adversarial_qa.py';env={}
 elif which in ['J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720']:
  code='work/independent_verify.py';env={'LENS_ONLY':which}
 else:raise ValueError('unknown stage')
 x=subprocess.run([sys.executable,str(ROOT/code)],cwd=ROOT,env={**os.environ,**env},capture_output=True,text=True,timeout=100,check=False)
 if x.returncode:raise RuntimeError(f'replay failed {which}: {x.stderr[-1100:]}')
 expected=json.loads((ROOT/'RESULT_HASHES.json').read_text())['files']
 if which=='capture':names=['results/source120_capture.json']+[f'inputs/disk120_frozen_{a}.be64' for a in ['J0822p1828','J0915p4211','J0930p2855','J1021p2028','J1111p2234','J1135p3720']]
 elif which=='q':names=['results/q_aperture_producer.json']
 elif which=='disk':names=['results/disk120_math_producer.json']
 elif which=='aggregate':names=['results/independent_six_lens_aggregate.json']
 elif which=='qa':names=['results/adversarial_qa.json']
 else:names=['results/independent_verifier_'+which.replace('+','p')+'.json']
 for name in names:assert sha(ROOT/name)==expected[name],(which,name,'replay SHA mismatch')
 print('STAGE_REPLAY_PASS',which,'outputs',len(names))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--stage')
 args=ap.parse_args();assert args.check!=bool(args.stage)
 if args.check:check()
 else:stage(args.stage)
if __name__=='__main__':main()
