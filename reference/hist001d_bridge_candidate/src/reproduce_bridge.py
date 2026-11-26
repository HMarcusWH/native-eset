#!/usr/bin/env python3
"""Run bounded stages of source-output / conditional proxy comparison.
Each invoked stage is separately bounded, with explicit SHA-pinned expected result.
"""
from __future__ import annotations
import argparse,hashlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGES={
 'source':('source_replay_from_archives.py',{
  'original_180_component_trace.json':'ad549d2e6aaf290a5cfeb31496928f0136191d8a05e92a1bbde6924c36610eab',
  'source_target_coefficient_witness.json':'b4bc1211623aee1e65690b2fb382a42cbd159f65c74c8f7d1a01f62dca8438ea'}),
 'producer':('bridge_exact.py',{'bridge_discrepancy_producer.json':'9997c83c281e201aee5b5dfcd26aeb1b471fef9730e1c79f0b989f5c87d56185'}),
 'independent':('bridge_independent.py',{'bridge_discrepancy_independent.json':'2c00703f6d644882a7ba8046e0c8a685f82e1b8562bd3dd833cf959315855791'}),
 'components':('component_interval.py',{'bridge_component_attribution_candidate.json':'c9d0cf9fc627ef8b7f1e955acd5799668793c01d788f6a97b0b82769b0a17302'}),
 'component_recheck':('component_independent.py',{'bridge_component_independent.json':'73cfc61585b82913265cf364e84b9b7caa006c759208e06081432e173bd07807'}),
 'target':('target_quadratic_exact.py',{'source_target_quadratic_uniform_bound.json':'1421d1eea8a43105c6c54805766c3d08924ae3db2e32aa918e52ad8a9acf38b2'}),
 'target_recheck':('target_quadratic_independent.py',{'source_target_quadratic_independent.json':'c426b782b157c41e5a7d8ce60b2d20947c5749580fd281ef5744db3be04b7650'}),
 'qa':('bridge_adversarial_qa.py',{'bridge_adversarial_qa.json':'2830c1191789b9767fd55a3bb1ebb4ffbefccffab07bf5c340aa2b891059bdcd'}),
}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(stages):
 for stage in stages:
  script,expected=STAGES[stage]
  subprocess.run([sys.executable,str(ROOT/'src'/script),str(ROOT)],cwd=ROOT,check=True,timeout=100)
  for name,hash_ in expected.items():
   raw=(ROOT/'results'/name).read_bytes()
   if sha(raw)!=hash_:raise ValueError('exact replay SHA drift: '+name)
  print('VERIFIED_STAGE',stage,'expected',len(expected))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['all',*STAGES],default='all',nargs='?');v=a.parse_args()
 run(list(STAGES) if v.stage=='all' else [v.stage])
