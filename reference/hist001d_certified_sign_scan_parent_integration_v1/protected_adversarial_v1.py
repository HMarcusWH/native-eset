"""Source-bound adversarial reviewer (does NOT ship protected case values).

Each numbered case must either be rejected or return explicit UNRESOLVED.
The numerically self-rehashed receipt forgeries require fresh source replay.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import copy
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

from certified_sign_scan import (
    BRACKETS_HEX, SourceContract, Unresolved, bit_of, digest, scan,
    validate_receipt, verify_source_replay,
)
from source_bound_adapter_v1 import GLOBAL_SHA, make_adapter


def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(o):return (json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=True)+'\n').encode()

def run(*, expected:Path, engine:Path, parents:Path, root:Path, global_audit:Path, scanner_dir:Path):
    env={"HIST001D_ENGINE_DIR":str(engine),"HIST001D_PARENT_DIR":str(parents),
         "HIST001D_ROOT_ZIP":str(root),"HIST001D_GLOBAL_AUDIT":str(global_audit)}
    contract=SourceContract(uniqueness_sha256=GLOBAL_SHA)
    sealed=json.loads(expected.read_bytes())
    validate_receipt(sealed,require_real_source=True)
    outcomes=[]
    def check(name,fn,*,expect_unresolved=True):
        try:
            result=fn()
        except (Unresolved,ValueError,RuntimeError,FileNotFoundError,KeyError) as exc:
            success=True  # rejected before any admissible proof was produced
        else:
            # A successful returned object, including a signed forged receipt,
            # MUST be marked as an adversarial failure.  Only explicit
            # UNRESOLVED is a permissible non-exception result.
            success=(result == 'UNRESOLVED') if isinstance(result,str) else False
        outcomes.append({"case":name,"rejected_or_unresolved":success})
        if not success:raise RuntimeError('ADVERSARIAL_CASE_PASSED_WHEN_SHOULD_FAIL:'+name)

    def scoped_replace(**overrides):
        return patch.dict(os.environ, {**env,**overrides},clear=True)

    # First independently source-replay the sealed baseline and compare bytes.
    with scoped_replace():
        trusted=make_adapter()
        verify_source_replay(sealed,trusted,contract,mode='THEOREM_COVER',max_evals_per_lens=128)
        for k,active in [('baseline_source_replay',True)]:
            outcomes.append({"case":k,"rejected_or_unresolved":True,"meaning":"SOURCE_REPLAY_BYTE_IDENTICAL_PASS"})
        budget=scan(trusted,contract,max_evals_per_lens=1)
        if budget['status']!='UNRESOLVED' or not all(x['status']=='UNRESOLVED' for x in budget['lens_results']):
            raise RuntimeError('BUDGET_FAILURE_WAS_PROMOTED')
        outcomes.append({"case":"insufficient_guard_budget_returns_UNRESOLVED", "rejected_or_unresolved":True})
        # Direct source-bound ALL-REAL adaptive range check, no inference about whole domain.
        real=scan(trusted,contract,mode='ADAPTIVE_COVER',lenses=('J0822+1828',),lo=10.0,hi=10.00000000001,max_evals_per_lens=3)
        validate_receipt(real,require_real_source=True)
        if real['status']!='CERTIFIED_CONDITIONAL' or real['lens_results'][0]['segments'][0]['method']!='DIRECT_TWO_ENGINE_ENCLOSURE':
            raise RuntimeError('ALL_REAL_RANGE_GUARD_FAILED')
        outcomes.append({"case":"narrow_all_real_two_engine_range_signed", "rejected_or_unresolved":True,
                         "meaning":"SCOPED_REAL_INTERVAL_GUARD_PASS"})
        unresolved=scan(trusted,contract,mode='ADAPTIVE_COVER',lenses=('J0822+1828',),lo=1.8,hi=1.9,max_evals_per_lens=1)
        if unresolved['status']!='UNRESOLVED':raise RuntimeError('AMBIGUOUS_REAL_RANGE_WAS_PROMOTED')
        outcomes.append({"case":"budget_capped_ambiguous_real_range_UNRESOLVED","rejected_or_unresolved":True})

        # Numerically *rehashed* strict-sign forgeries: structural self-digest
        # alone must not confer source certification; independent replay rejects.
        for key in ('lo','hi'):
            altered=copy.deepcopy(sealed)
            tr=altered['lens_results'][0]['segments'][0]['proof_links']['left_endpoint_two_engine_traces'][0]
            original=F(tr[key]); shifted=original+(F(1) if key=='lo' else F(2))
            tr[key]=str(shifted.numerator)+'/'+str(shifted.denominator)
            altered['receipt_sha256']=digest({k:v for k,v in altered.items() if k!='receipt_sha256'})
            def verify_tamper():
                try:
                    validate_receipt(altered,require_real_source=True)
                except Unresolved:
                    return 'UNRESOLVED'
                verify_source_replay(altered,trusted,contract,mode='THEOREM_COVER',max_evals_per_lens=128)
                return 'ACCEPTED_FORGERY'
            check('source_replayed_rehashed_'+key+'_interval_forgery',verify_tamper)

    # Structural receipt mutations: preserve recomputed wrapper SHA to test
    # semantic/coverage guards, never write these back into source archives.
    field_cases=[
        ('physical_provider_true',('physical_provider_admitted',True)),
        ('old_float_sign_true',('original_compiled_float_signs_certified',True)),
        ('old_march_offgrid_true',('original_March_offgrid_root_certified',True)),
        ('canonical_state_true',('canonical_theory_state_changed',True)),
        ('empirical_validation_forged',('empirical_validation','VALIDATED')),
        ('source_hash_forged',('source_sha256','0'*64)),
        ('bracket_hash_forged',('bracketing_package_sha256','0'*64)),
        ('uniqueness_hash_forged',('uniqueness_parent_sha256','0'*64)),
        ('model_id_forged',('model_id','NATIVE_ADMITTED_PHYSICAL_WEYL')),
        ('scope_forged',('mathematical_claim_scope','NATIVE_PHYSICAL_LENS')),
    ]
    for name,(key,value) in field_cases:
        a=copy.deepcopy(sealed);a[key]=value;a['receipt_sha256']=digest({k:v for k,v in a.items() if k!='receipt_sha256'})
        check(name,lambda aa=a:validate_receipt(aa,require_real_source=True) or 'ACCEPTED_FORGERY')
    for name,mutate in [
        ('endpoint_bits_forged',lambda a:a['lens_results'][0]['segments'][0].__setitem__('hi_bits','42')),
        ('coverage_count_forged',lambda a:a['lens_results'][0]['segments'][0].__setitem__('binary64_count','1')),
        ('lens_removed',lambda a:a['lens_results'].pop()),
        ('engine_identity_duplicated',lambda a:a['lens_results'][0]['segments'][0]['proof_links']['left_endpoint_two_engine_traces'][1].__setitem__('engine_id','pinned_sourceconnected')),
        ('false_sign_positive_to_negative',lambda a:a['lens_results'][0]['segments'][0].__setitem__('classification','NEGATIVE')),
        ('no_parent_attestation',lambda a:a.__setitem__('parent_attestation',None)),
        ('no_proof_links',lambda a:a['lens_results'][0]['segments'][0].__setitem__('proof_links',{})),
    ]:
        a=copy.deepcopy(sealed);mutate(a);a['receipt_sha256']=digest({k:v for k,v in a.items() if k!='receipt_sha256'})
        check(name,lambda aa=a:validate_receipt(aa,require_real_source=True) or 'ACCEPTED_FORGERY')

    # Prohibit external-source/root archive modification, even when the user
    # supplies the same path/shape; SHA pins are not self-selected by the data.
    with tempfile.TemporaryDirectory(prefix='hist001d-adversarial-parent-') as tmp:
        directory=Path(tmp)
        fake_root=directory/'root_tampered.zip'
        fake_root.write_bytes(root.read_bytes()[:-3]+b'BAD')
        with scoped_replace(HIST001D_ROOT_ZIP=str(fake_root)):
            check('altered_root_bracketing_archive_rejected',lambda:make_adapter() or 'ACCEPTED_FORGERY')
        fake_audit=directory/'global_tampered.json'
        audit=json.loads(global_audit.read_bytes());audit['independent_exclusion_panels_recomputed']=1399
        audit['receipt_sha256']=sha(canonical({k:v for k,v in audit.items() if k!='receipt_sha256'}))
        fake_audit.write_bytes(canonical(audit))
        with scoped_replace(HIST001D_GLOBAL_AUDIT=str(fake_audit)):
            check('rehashed_global_independent_audit_rejected',lambda:make_adapter().replay_parents(contract) or 'ACCEPTED_FORGERY')
        no_guards=directory/'parents'
        no_guards.mkdir()
        for path in parents.glob('*.zip'):
            if path.name!='HIST001D_EXACT_REAL_FAIL_CLOSED_SIGN_API_FULL_v1_2026_11_07_NONPROMOTING.zip':
                (no_guards/path.name).hardlink_to(path)
        with scoped_replace(HIST001D_PARENT_DIR=str(no_guards)):
            check('missing_strict_sign_api_parent_rejected',lambda:make_adapter() or 'ACCEPTED_FORGERY')
        enginecopy=directory/'engine'
        enginecopy.mkdir()
        for path in engine.glob('*.py'):
            (enginecopy/path.name).write_bytes(path.read_bytes())
        (enginecopy/'strict_sign_api.py').write_bytes((enginecopy/'strict_sign_api.py').read_bytes()+b'\n# attacker\n')
        with scoped_replace(HIST001D_ENGINE_DIR=str(enginecopy)):
            check('modified_proof_engine_source_rejected',lambda:make_adapter() or 'ACCEPTED_FORGERY')

    # Optimized Python must *never* bypass the original protected parent's
    # disable-assertion refusal, and must not produce a real source root claim.
    envO={**os.environ,**env}
    cp=subprocess.run([sys.executable,'-O',str(scanner_dir/'scan_cli.py'),
                       '--adapter','source_bound_adapter_v1:make_adapter',
                       '--uniqueness-parent-sha256',GLOBAL_SHA,'--mode','theorem'],
                      cwd=scanner_dir,env=envO,capture_output=True,text=True,timeout=100)
    if cp.returncode!=2 or 'UNRESOLVED' not in cp.stdout+cp.stderr:
        raise RuntimeError('PYTHON_OPTIMIZED_MODE_DID_NOT_FAIL_CLOSED')
    outcomes.append({'case':'python_optimized_assertions_disabled_fails_closed','rejected_or_unresolved':True})

    if any(x['rejected_or_unresolved'] is not True for x in outcomes):
        raise RuntimeError('ADVERSARIAL_CASE_NOT_REJECTED')
    return {'schema':'HIST001D_SOURCE_BOUND_SCANNER_ADVERSARIAL_V1',
            'status':'PASS_SCOPED_NONPROMOTING','adversarial_check_count':len(outcomes),
            'cases':outcomes,
            'source_bound_reference_sha256':sha(expected.read_bytes()),
            'global_independent_audit_sha256':sha(global_audit.read_bytes()),
            'original_46plus3_source_sha256':contract.source_sha256,
            'bracketing_zip_sha256':contract.bracket_sha256,
            'global_uniqueness_zip_sha256':GLOBAL_SHA,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'scientific_authority_promoted':False}


def main(argv=None):
    p=argparse.ArgumentParser()
    for name in ('expected','engine','parents','root','global-audit','scanner-dir','out'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args(argv)
    try:
        receipt=run(expected=a.expected,engine=a.engine,parents=a.parents,root=a.root,global_audit=a.global_audit,scanner_dir=a.scanner_dir)
        code=0
    except Exception as e:
        receipt={'schema':'HIST001D_SOURCE_BOUND_SCANNER_ADVERSARIAL_V1',
                 'status':'UNRESOLVED','reason':type(e).__name__+':'+str(e)[:200],
                 'physical_provider_admitted':False,'scientific_authority_promoted':False}
        code=2
    receipt['receipt_sha256']=sha(canonical(receipt))
    a.out.write_bytes(canonical(receipt))
    print(receipt['status'], 'checks',receipt.get('adversarial_check_count',0),flush=True)
    return code

if __name__=='__main__':sys.exit(main())
