#!/usr/bin/env python3
"""Replay source-locked conditional finite-proxy proof, in bounded stages.

Use --stage for one independent bounded execution; run each stage after clean
archive extraction, then --stage audit to verify hashes and manifest. --stage all
is for hosts with an unrestricted execution budget. Nothing promotes science.
"""
from __future__ import annotations
import argparse,json,hashlib,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED={
 'G4b1c_Global_Six_Lens_Exactly_One_Finite_Proxy_Real_Root_Candidate_v1.json':'97f2146f48c2c7fa3af5d8cb021f68fef0e28e5ce5544d3113e3166c43b53b99',
 'G4b1c_Independent_Global_Root_Count_Exact_Rational_Verifier_v1.json':'8b36bb01b728c8a957d1eb96a1f330fef74516054ff6057a60c8f376db6eae6a',
 'G4b1c_Global_Adversarial_Tamper_QA_v1.json':'c0f364f2d6dbec550d628166077cdd7ecc77c045c57b40721c48b4483cf07895'}
STAGES={
 'inner_v3':('HIST001_G4b1c_Independent_Sextic_Bernstein_Verifier_v3.py','antecedents/prepeak',None),
 'outer_v4':('HIST001_G4b1c_Independent_Exact_Shadow_Moment_Outer_Band_Verifier_v4.py','antecedents/prepeak',None),
 'narrow':('g4b1c_uniqueness_independent_verifier.py','antecedents/narrow',None),
 'producer':('g4b1c_global_rootcount_producer.py','.',list(EXPECTED)[0]),
 'independent':('g4b1c_global_independent_verifier.py','.',list(EXPECTED)[1]),
 'tamper':('g4b1c_global_adversarial_qa.py','.',list(EXPECTED)[2]),
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit_manifest():
 declared=json.loads((ROOT/'MANIFEST.json').read_bytes());expected=declared['files']
 actual={f.relative_to(ROOT).as_posix():sha(f) for f in ROOT.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='MANIFEST.json' and f.suffix!='.pyc'}
 if actual!=expected:
  raise ValueError('MANIFEST differs from current source: extra='+str(sorted(set(actual)-set(expected)))+' missing='+str(sorted(set(expected)-set(actual)))+' altered='+str(sorted(k for k in set(actual)&set(expected) if actual[k]!=expected[k])))
 return len(actual)
def one(stage):
 exe,wd,out=STAGES[stage]
 t=time.monotonic();cwd=ROOT/wd
 res=subprocess.run([sys.executable,exe],cwd=cwd,capture_output=True,text=True,timeout=240)
 if res.returncode:raise ValueError(f'{stage}: {res.stdout[-2400:]} {res.stderr[-2400:]}')
 if stage=='inner_v3':
  j=json.loads(res.stdout)
  if j.get('status')!='PASS_CONDITIONAL_LOCAL_FINITE_PROXY_SEXTIC_ONLY_NOT_ORIGINAL_NUMERIC_ROOT' or j.get('positive_Bernstein_coefficients')!=42:raise ValueError('inherited inner v3 not passed')
 if stage=='outer_v4':
  j=json.loads(res.stdout)
  if j.get('status')!='PASS_LOCAL_CONDITIONAL_FINITE_PROXY_OUTER_BANDS_ONLY' or j.get('cell_count')!=125:raise ValueError('inherited outer v4 not passed')
 if stage=='narrow' and '6b47c9a013f522be52ffe4afad09a03eb797ddb2b7fffaafbca29996ec82ef84' not in res.stdout:raise ValueError('independent narrow derivative not passed')
 if out and sha(ROOT/out)!=EXPECTED[out]:raise ValueError(f'{stage}: expected output SHA altered')
 return {'stage':stage,'status':'PASS_SCOPED_CANDIDATE_ONLY','output_sha256':EXPECTED.get(out),'elapsed_seconds':round(time.monotonic()-t,2)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=[*STAGES,'audit','all'],default='all');q=p.parse_args()
 total=audit_manifest()
 print(json.dumps({'stage':'source_sha_manifest','status':'PASS','files':total}),flush=True)
 if q.stage=='audit':
  for name,dig in EXPECTED.items():
   if sha(ROOT/name)!=dig:raise ValueError('expected scientific output SHA differs on archive readback: '+name)
  print(json.dumps({'status':'PASS_MANIFEST_AND_THREE_SCIENTIFIC_RESULT_HASHES','claims':{'mathematical_candidate_only':True,'physical_provider_admitted':False,'original_march_numeric_root_theorem':False}}),flush=True)
 elif q.stage=='all':
  for name in STAGES:
   print(json.dumps(one(name)),flush=True)
 else:
  print(json.dumps(one(q.stage)),flush=True)
if __name__=='__main__':main()
