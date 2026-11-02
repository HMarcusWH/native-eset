"""Complete manifest and bounded exact stage runner, not a physical theorem."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def digest(b):return hashlib.sha256(b).hexdigest()
def check():
    manifest=json.loads((ROOT/'MANIFEST_SHA256.json').read_text())
    hashes=json.loads((ROOT/'RESULT_HASHES.json').read_text())
    assert manifest['schema']=='HIST001D_MARCH180_DEFINED_COMPARATOR_SOURCE_REPLAY_MANIFEST_V1'
    assert manifest['source_zip_sha256']=='8178dfb07aa4c070b5f10e7de2c1e4130ffe777efb08d57382f4aae9cfcd4132'
    assert manifest['status']=='NONPROMOTING_MATHEMATICAL_COMPARATOR_ONLY'
    for name,sha in manifest['files'].items():
        p=ROOT/name
        assert p.is_file() and p.resolve().is_relative_to(ROOT.resolve()) and digest(p.read_bytes())==sha,(name,'MANIFEST_MISMATCH')
    for name,sha in hashes.items():
        assert digest((ROOT/name).read_bytes())==sha
    assert manifest['files']['inputs/original_march_D120_q_parent.zip']==manifest['source_zip_sha256']
    print('MARCH180_MATH_BUNDLE_PASS',len(manifest['files']),'files',len(hashes),'frozen results')
def run(stage):
    scripts={'producer':'producer.py','independent':'independent_verify.py','qa':'adversarial_qa.py'}
    script=scripts[stage]
    check()
    p=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True,capture_output=True,text=True)
    print(p.stdout.strip());print(p.stderr.strip(),file=sys.stderr)
    check()
if __name__=='__main__':
    par=argparse.ArgumentParser()
    par.add_argument('--check',action='store_true')
    par.add_argument('--stage',choices=['producer','independent','qa'])
    a=par.parse_args()
    if a.stage:run(a.stage)
    else:check()
