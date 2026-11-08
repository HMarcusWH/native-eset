#!/usr/bin/env python3
"""HIST-001D PR56 protected-source IEEE-754 final-postprocessing replay.

External SHA-256 must be supplied independently of this ZIP. SHA-256/ZIP CRC
and source path integrity, executed code provenance, unmodified original data,
and fresh source-dependent 1080-node / 6-root replay are different gates.
This is NOT an offgrid floating-source error certificate or physical model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = 'HIST001D_MARCH_ORIGINAL_FINAL_FLOAT_POSTPROCESSING_SOURCE_LOCKED_V1'
SOURCE_SHA = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SAT_SHA = '99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
H_SHA = '02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6'
RESULT_SHA = {
    'results/original_float_bridge_receipt.json':'00ee91c9d018610d0b4cbbf08a1143ad562b3209961639ebb62a6910d60fd3ee',
    'results/independent_float_bridge_receipt.json':'bd404058f0429ab363e4c7a529a13f3f742bca0e5cbc8a82b1700cb4887b6a35',
    'results/adversarial_float_qa.json':'e4127f04bf9a1f40a1d880ec3ebb7a4972e50e8816d5a2f310fdf0aed067a04a',
}
EXECUTED = ('reference/hist001d_original_float_bridge_candidate/float_bridge.py',
            'reference/hist001d_original_float_bridge_candidate/independent_float_check.py',
            'reference/hist001d_original_float_bridge_candidate/verify_release.py',
            'reference/hist001d_original_float_bridge_candidate/claim_guard.py',
            'reference/hist001d_original_float_bridge_candidate/adversarial_qa.py',
            'reference/hist001d_full_h_bridge_candidate/full_h_finite_source.py')


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def valid_path(name:str)->bool:
    if not isinstance(name,str) or not name or name.startswith('/') or '\\' in name:
        return False
    p=PurePosixPath(name)
    return p.as_posix()==name and all(s not in ('','.', '..') for s in name.split('/'))


def verify_zip(archive:Path, expected_sha:str)->dict:
    if not re.fullmatch(r'[a-f0-9]{64}',expected_sha):
        raise ValueError('UNRESOLVED: missing or invalid independently supplied SHA-256')
    if not archive.is_file() or digest(archive.read_bytes())!=expected_sha:
        raise ValueError('UNRESOLVED: archive mismatches independently pinned SHA-256')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('UNRESOLVED: bad ZIP CRC')
        infos=z.infolist();names=[x.filename for x in infos]
        if len(names)!=len(set(names)) or not all(valid_path(n) for n in names):
            raise ValueError('UNRESOLVED: ZIP path collision / traversal / duplicate')
        if any(((i.external_attr>>16)&0o170000)==0o120000 for i in infos):
            raise ValueError('UNRESOLVED: symlink in proof ZIP')
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        if manifest.get('schema')!=SCHEMA or manifest.get('physical_provider_admitted') is not False or manifest.get('empirical_validation')!='NOT_ESTABLISHED':
            raise ValueError('UNRESOLVED: manifest scope changed')
        files=manifest.get('files')
        if not isinstance(files,dict) or set(names)!=set(files)|{'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: untracked, missing or extra ZIP file')
        for name,sha in files.items():
            if not valid_path(name) or not isinstance(sha,str) or not re.fullmatch(r'[a-f0-9]{64}',sha):
                raise ValueError('UNRESOLVED: malformed file hash/path')
            if digest(z.read(name))!=sha:
                raise ValueError('UNRESOLVED: protected file hash mismatch '+name)
        for name,sha in RESULT_SHA.items():
            if files.get(name)!=sha:raise ValueError('UNRESOLVED: sealed original result changed '+name)
        if files.get('inputs/HIST001D_K180_SATURATED_REVIEW_REPAIR_V1R1.zip')!=SAT_SHA or files.get('inputs/HIST001D_FULL_H_BRIDGE_v1r1.zip')!=H_SHA:
            raise ValueError('UNRESOLVED: original mathematical parent changed')
        for name in EXECUTED:
            if name not in files:raise ValueError('UNRESOLVED: required executable source missing '+name)
        if 'reference/hist001d_original_float_bridge_candidate/attested_replay_v1r2.py' not in files:
            raise ValueError('UNRESOLVED: attested replay tool absent')
        if 'tests/historical/test_hist001d_original_float_bridge_v1r2_failclosed.py' not in files:
            raise ValueError('UNRESOLVED: optimized-python tests absent')
        if files.get('reference/hist001d_full_h_bridge_candidate/full_h_finite_source.py') == '4aa7ad25bd41cb06d25399780d1d2b35625ea600bc84de9002ccfa526661fe79':
            raise ValueError('UNRESOLVED: inherited pre-repair finite helper source')
        return manifest


def verify_tree(archive:Path,root:Path,manifest:dict)->int:
    checked=0
    with zipfile.ZipFile(archive) as z:
        for name,digest_expected in manifest['files'].items():
            path=root/name
            if not path.is_file() or path.is_symlink():
                raise ValueError('UNRESOLVED: missing local executed evidence '+name)
            raw=path.read_bytes()
            if digest(raw)!=digest_expected or raw!=z.read(name):
                raise ValueError('UNRESOLVED: local proof/evidence differs from attested source '+name)
            checked+=1
    return checked


def replay(archive:Path,expected_sha:str,extracted_root:Path|None=None,budget_seconds:int=240)->dict:
    manifest=verify_zip(archive,expected_sha)
    if type(budget_seconds) is not int or budget_seconds<=0:
        raise ValueError('UNRESOLVED: no execution budget')
    if extracted_root is not None:verify_tree(archive,extracted_root,manifest)
    with tempfile.TemporaryDirectory(prefix='hist001d_56_attested_') as td:
        root=Path(td)
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                target=root/info.filename;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(z.read(info.filename))
        checked=verify_tree(archive,root,manifest)
        entry=root/'reference/hist001d_original_float_bridge_candidate/verify_release.py'
        try:
            # -I intentionally removes script-directory implicit imports. Re-add
            # only the SHA-attested, freshly extracted code directory, not the
            # ambient PYTHONPATH or any caller-controlled module search path.
            isolated_bootstrap = (
                'import sys,runpy; from pathlib import Path; '
                'entry=Path(sys.argv[1]).resolve(); '
                'sys.argv=[str(entry),*sys.argv[2:]]; '
                'sys.path.insert(0,str(entry.parent)); '
                'runpy.run_path(str(entry),run_name="__main__")'
            )
            proc=subprocess.run([sys.executable,'-I','-B','-c',isolated_bootstrap,
                                 str(entry),'--root',str(root),'--full'],
                                cwd=root,text=True,capture_output=True,timeout=budget_seconds,check=False)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('UNRESOLVED: source replay execution budget exceeded') from exc
        if proc.returncode!=0:
            raise ValueError('UNRESOLVED: protected source-dependent replay failed '+proc.stderr[-1200:])
        if '"status": "PASS_NONPROMOTING"' not in proc.stdout or '"full_source_replay": true' not in proc.stdout:
            raise ValueError('UNRESOLVED: full source replay PASS not observed')
        if f'"receipt_sha256": "{RESULT_SHA["results/original_float_bridge_receipt.json"]}"' not in proc.stdout:
            raise ValueError('UNRESOLVED: replayed result not the pinned one')
        lines=[x.strip() for x in proc.stdout.splitlines() if ' H matched 180 root ' in x]
        lens=['J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720']
        if len(lines)!=6 or any(not line.startswith(name+' H matched 180 root ') for line,name in zip(lines,lens)):
            raise ValueError('UNRESOLVED: absent or reordered lens source replay')
    return {
        'status':'PASS_CONDITIONAL_ORIGINAL_MARCH_SAMPLED_IEEE754_REPLAY',
        'attested_members':checked,
        'independently_pinned_archive_sha256':expected_sha,
        'original_source_composite_sha256':SOURCE_SHA,
        'sampled_H_values_replayed':1080,
        'archived_binary64_sampled_roots_replayed':6,
        'producer_and_independent_and_QA':'REGENERATED_BYTE_IDENTICAL',
        'upstream_Bessel_gradients_density_or_arbitrary_real_H_error_proved':False,
        'finite_mathematical_PL_root_is_original_sampled_interpolant':False,
        'physical_provider_admitted':False,
        'empirical_validation':'NOT_ESTABLISHED',
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True,type=Path)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--extracted-root',type=Path)
    p.add_argument('--budget-seconds',type=int,default=240)
    args=p.parse_args()
    try:
        outcome=replay(args.archive,args.expected_sha256,args.extracted_root,args.budget_seconds)
    except (ValueError,TypeError,KeyError,zipfile.BadZipFile,json.JSONDecodeError,OSError) as exc:
        print(json.dumps({'status':'UNRESOLVED','reason':str(exc)},sort_keys=True))
        return 2
    print(json.dumps(outcome,indent=2,sort_keys=True))
    return 0

if __name__=='__main__':sys.exit(main())
