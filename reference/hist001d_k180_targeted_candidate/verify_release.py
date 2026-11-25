#!/usr/bin/env python3
"""SHA/identity/claim/IVT verification of sealed HIST001D targeted witness archive.

Quick mode validates all sealed files, protected provenance and source-free
receipt arithmetic; --full repeats all six expensive independent Fraction
verifications. Neither mode proves a physically selected Weyl lens model.
"""
from __future__ import annotations
import argparse,hashlib,io,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from assemble_targeted import assemble  # noqa: E402
from witness_contract import LENSES,PARENT,EXPECTED_MIN_ZEROS  # noqa: E402

def sha(b):return hashlib.sha256(b).hexdigest()

def verify(full=False):
    mpath=ROOT/'MANIFEST_SHA256.json'
    man=json.loads(mpath.read_bytes())
    if man.get('schema')!='HIST001D_TARGETED_MSTAR_SIGN_REVERSE_RELEASE_MANIFEST_V1':raise ValueError('manifest schema')
    if man.get('physical_provider_admitted') is not False or man.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('manifest false scientific authority')
    if man.get('selected_quadrature_remainder_zeros_lower_bound')!=10 or man.get('Einstein_root_count_proved') is not False:raise ValueError('manifest numerical claim')
    if len(man['files'])<20 or len(set(man['files']))!=len(man['files']):raise ValueError('manifest completeness')
    for path,digest in man['files'].items():
        pp=ROOT/path
        if path.startswith('/') or '..' in Path(path).parts or not pp.is_file() or sha(pp.read_bytes())!=digest:
            raise ValueError('missing / corrupted sealed release member: '+path)
    if sha((ROOT/'inputs/cancel_parent_v1.zip').read_bytes())!=PARENT:raise ValueError('protected parent SHA')
    z=zipfile.ZipFile(io.BytesIO((ROOT/'inputs/cancel_parent_v1.zip').read_bytes()))
    old=json.loads(z.read('MANIFEST_SHA256.json'))
    for path,digest in old['files'].items():
        if sha(z.read(path))!=digest:raise ValueError('protected parent member SHA '+path)
    reports=[json.loads((ROOT/'results'/f'targeted_lens_{j}.json').read_bytes()) for j in range(6)]
    fresh=assemble(reports)
    saved=json.loads((ROOT/'results/targeted_aggregate.json').read_bytes())
    if fresh!=saved or [x['zeros_at_least'] for x in saved['lenses']]!=list(EXPECTED_MIN_ZEROS):
        raise ValueError('source-conditional aggregate mismatch')
    ad=json.loads((ROOT/'results/adversarial_targeted.json').read_bytes())
    if ad.get('all_rejected') is not True or ad.get('total_rejected')!=40 or any(x.get('status')!='REJECTED' for x in ad['cases']):
        raise ValueError('adversarial negative controls missing')
    audit=json.loads((ROOT/'results/independent_fraction_audit.json').read_bytes())
    if audit.get('schema')!='HIST001D_TARGETED_ALL_SIX_INDEPENDENT_FRACTION_AUDIT_V1' or audit.get('all_pass') is not True or audit.get('total_distinct_zeros_at_least')!=10:
        raise ValueError('independent audit manifest')
    for j,datum in enumerate(audit['lenses']):
        if datum['lens']!=LENSES[j] or datum['zeros_at_least']!=EXPECTED_MIN_ZEROS[j] or datum['source_receipt_sha256']!=sha((ROOT/'results'/f'targeted_lens_{j}.json').read_bytes()):
            raise ValueError('independent audit lens mismatch')
        log=(ROOT/'logs'/f'independent_lens_{j}.txt').read_text()
        if log.strip()!=f'INDEPENDENT_TARGETED_PASS 1 lenses zeros>= {EXPECTED_MIN_ZEROS[j]}':
            raise ValueError('independent run ledger not complete')
    if full:
        for j in range(6):
            call=[sys.executable,str(ROOT/'reference/hist001d_k180_targeted_candidate/verify_targeted.py'),'--lens',str(j)]
            subprocess.run(call,cwd=ROOT,check=True)
    print('TARGETED_RELEASE_PASS',len(man['files']),'SHA-controlled files','6 lenses','10 zeros minimum',
          'full_independent_replay',bool(full),flush=True)
    return True

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--quick',action='store_true',help='SHA and recorded independent evidence (default)')
    a.add_argument('--full',action='store_true',help='replay all six expensive independent Fraction checks')
    x=a.parse_args()
    verify(full=x.full)
