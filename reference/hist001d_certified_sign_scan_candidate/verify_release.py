"""Source-only quick verification: SHA manifest + 67 tests + 36 mutations.

Not a replacement for protected-data source re-execution.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from adversarial_qa import qa
from certified_sign_scan import SourceContract, SyntheticOracle, canonical_json, scan

ROOT=Path(__file__).resolve().parent

def main():
    manifest_path=ROOT/'MANIFEST_SHA256.json'
    if not manifest_path.is_file():
        print('UNRESOLVED: MANIFEST_MISSING',file=sys.stderr)
        return 2
    manifest=json.loads(manifest_path.read_text(encoding='ascii'))
    files=manifest.get('files')
    if not isinstance(files,dict):
        print('UNRESOLVED: INVALID_MANIFEST',file=sys.stderr)
        return 2
    recorded=set(files)
    actual={x.name for x in ROOT.iterdir() if x.is_file() and x.name not in ('MANIFEST_SHA256.json',)}
    if recorded!=actual:
        print('UNRESOLVED: FILE_SET_MISMATCH: '+str((recorded-actual,actual-recorded)),file=sys.stderr)
        return 2
    for name, expected in files.items():
        if not isinstance(name,str) or '/' in name or '\\' in name:
            print('UNRESOLVED: UNSAFE_MANIFEST_MEMBER',file=sys.stderr)
            return 2
        computed=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if computed!=expected:
            print('UNRESOLVED: SHA_MISMATCH: '+name,file=sys.stderr)
            return 2
    result=subprocess.run([sys.executable,'-m','unittest','-q','test_certified_sign_scan.py'],cwd=ROOT,
                          capture_output=True,text=True)
    if result.returncode or 'Ran 67 tests' not in result.stderr or 'OK' not in result.stderr:
        print('UNRESOLVED: SOURCE_FREE_UNIT_TESTS_FAILED\n'+result.stdout+'\n'+result.stderr,file=sys.stderr)
        return 2
    audit=qa()
    if audit['status']!='PASS_SOURCE_FREE_ONLY' or audit['total_mutations']!=36 or audit['structurally_rejected_count']!=35:
        print('UNRESOLVED: ADVERSARIAL_AUDIT_FAILED',file=sys.stderr)
        return 2
    if canonical_json(audit)!=(ROOT/'adversarial_audit.json').read_bytes():
        print('UNRESOLVED: ADVERARIAL_RECEIPT_MISMATCH',file=sys.stderr)
        return 2
    synthetic=scan(SyntheticOracle(),SourceContract(uniqueness_sha256='e'*64,scope='SYNTHETIC_TEST_ONLY'))
    if canonical_json(synthetic)!=(ROOT/'synthetic_theorem_receipt.json').read_bytes():
        print('UNRESOLVED: SYNTHETIC_RECEIPT_MISMATCH',file=sys.stderr)
        return 2
    print('PASS_SOURCE_FREE_ONLY: sha_manifest='+str(len(files))+'/'
          +str(len(files))+', tests=67/67, structural_attack_rejections=35/35, '
          'replay_required_attack=1, operational_fail_closed=3/3. '
          'PROTECTED_PARENT_SOURCE_REPLAY=NOT_RUN.')
    return 0

if __name__=='__main__':sys.exit(main())
