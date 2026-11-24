#!/usr/bin/env python3
"""HIST-001D PR57 protected D120 seam replay with externally pinned source bytes.

The original March 119-segment sampled D120 projection, its stored first
sampled root and a NEW fixed-sample periodic-seam counterfactual are separate
numerical objects. Neither this validator nor its exact-real seam intervals
certifies the omitted physical angular integral, off-grid H, or Weyl lensing.

Threat model: the expected whole ZIP SHA-256 must come from a separate trusted
record, not from the ZIP's own manifest or attacker-controlled working tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = 'HIST001D_ORIGINAL_MARCH180_D120_PERIODIC_SEAM_RELEASE_V1'
SOURCE_46PLUS3_SHA = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SAT_SHA = '99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
H_SHA = '02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6'
FLOAT_PARENT_SHA = '313b62e2c0f790684bd6ed6ff22431c2cce1f398d79fcc590971f8814ae4706e'
SOURCE_RECEIPT_SHA = 'f43b4fbd03f625c1f41136c5a3b40193f334badbd5a83c81f0e05c03feb8c089'
QA_RECEIPT_SHA = '48b373d3acb537f5a3b81d66d7c1ad413db7fb3687d07480d44b66397c905b78'
LENSES = ('J0822+1828', 'J0915+4211', 'J0930+2855', 'J1021+2028', 'J1111+2234', 'J1135+3720')
SRC_DIR = 'reference/hist001d_d120_seam_candidate'
EXECUTED = (
    SRC_DIR + '/source_seam_replay.py',
    SRC_DIR + '/verify_seam.py',
    SRC_DIR + '/adversarial_seam.py',
    SRC_DIR + '/seam_math.py',
    SRC_DIR + '/verify_release.py',
    SRC_DIR + '/attested_replay_v1r2.py',
    'reference/hist001d_full_h_bridge_candidate/full_h_finite_source.py',
    'reference/hist001d_original_float_bridge_candidate/float_bridge.py',
)
# The patched finite-model and IEEE-754 helpers come from the *reviewed* PR55/56
# branches; the historical nested parent ZIPs are unchanged.
HARDENED_HELPER_SHA = {
    'reference/hist001d_full_h_bridge_candidate/full_h_finite_source.py': '6a985ff342a092122470dd034d5f18b3a430e80f5e563231389224de203e1ce7',
    'reference/hist001d_original_float_bridge_candidate/float_bridge.py': '00a0c4c4fa78c9b3e2507062ac716a3a723e0d606d6926856aed301443add4a9',
}
RESULT_SHA = {
    'results/seam_source_receipt.json': SOURCE_RECEIPT_SHA,
    'results/seam_adversarial.json': QA_RECEIPT_SHA,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def good_sha(value: str) -> bool:
    return type(value) is str and bool(re.fullmatch(r'[a-f0-9]{64}', value))


def good_path(name: str) -> bool:
    if type(name) is not str or not name or name.startswith('/') or '\\' in name:
        return False
    p = PurePosixPath(name)
    return p.as_posix() == name and all(s not in ('', '.', '..') for s in name.split('/'))


def verify_zip(archive: Path, external_sha: str) -> dict:
    if not good_sha(external_sha):
        raise ValueError('UNRESOLVED: external SHA-256 authority missing or malformed')
    if not archive.is_file() or sha(archive.read_bytes()) != external_sha:
        raise ValueError('UNRESOLVED: protected ZIP failed independently supplied whole-file SHA')
    with zipfile.ZipFile(archive) as z:
        members = z.infolist()
        # Reject bombs by declared uncompressed sizes *before* a CRC sweep.
        if len(members) > 64 or sum(m.file_size for m in members) > 32_000_000:
            raise ValueError('UNRESOLVED: excessive archive member count / decompressed size')
        if z.testzip() is not None:
            raise ValueError('UNRESOLVED: protected ZIP CRC mismatch')
        names = [m.filename for m in members]
        if len(names) != len(set(names)) or not all(good_path(n) for n in names):
            raise ValueError('UNRESOLVED: duplicate / invalid / traversal ZIP paths')
        if any(((m.external_attr >> 16) & 0o170000) == 0o120000 for m in members):
            raise ValueError('UNRESOLVED: symlink in protected ZIP')
        if 'MANIFEST_SHA256.json' not in names:
            raise ValueError('UNRESOLVED: missing release manifest')
        manifest = json.loads(z.read('MANIFEST_SHA256.json'))
        if manifest.get('schema') != SCHEMA or manifest.get('source_unchanged') is not True or manifest.get('counterfactual_only') is not True:
            raise ValueError('UNRESOLVED: mathematical operator or release semantics changed')
        if manifest.get('release_version') != 'v1r2' or manifest.get('source_execution_attestation') is not True:
            raise ValueError('UNRESOLVED: missing v1r2 source-execution attestation lock')
        if (manifest.get('physical_provider_admitted') is not False or
            manifest.get('empirical_validation') != 'NOT_ESTABLISHED' or
            manifest.get('full_azimuth_accuracy_proved') is not False):
            raise ValueError('UNRESOLVED: forbidden scientific authority promotion')
        if (manifest.get('original_source_46plus3_sha256') != SOURCE_46PLUS3_SHA or
            manifest.get('parent_source_float_release_sha256') != FLOAT_PARENT_SHA):
            raise ValueError('UNRESOLVED: original March source lineage changed')
        files = manifest.get('files')
        if not isinstance(files, dict) or set(names) != set(files) | {'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: untracked / missing / extra release member')
        if len(files) < 17:
            raise ValueError('UNRESOLVED: incomplete v1r2 source-attested release')
        for name, digest in files.items():
            if not good_path(name) or not good_sha(digest):
                raise ValueError('UNRESOLVED: illegal source path or digest')
            if sha(z.read(name)) != digest:
                raise ValueError('UNRESOLVED: SHA failure in protected member ' + name)
        for name, digest in {
            'inputs/saturation_v1r1.zip': SAT_SHA,
            'inputs/full_h_v1r1.zip': H_SHA,
            **HARDENED_HELPER_SHA,
            **RESULT_SHA,
        }.items():
            if files.get(name) != digest:
                raise ValueError('UNRESOLVED: pinned parent / historical receipt changed ' + name)
        for name in EXECUTED + (
            'tests/historical/test_hist001d_d120_seam_source_free.py',
            'tests/historical/test_hist001d_d120_v1r2_attestation.py',
            'docs/HIST001D_D120_SEAM_V1R2_EXECUTION_ATTESTATION_SCOPE.md',
        ):
            if name not in files:
                raise ValueError('UNRESOLVED: proof-critical executed file absent ' + name)
        return manifest


def verify_tree(archive: Path, root: Path, manifest: dict) -> int:
    root = root.resolve(strict=True)
    checked = 0
    with zipfile.ZipFile(archive) as z:
        for name, expected in manifest['files'].items():
            path = root / name
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError('UNRESOLVED: missing / redirected execution source ' + name)
            data = path.read_bytes()
            if sha(data) != expected or data != z.read(name):
                raise ValueError('UNRESOLVED: local code/data differs from authenticated ZIP ' + name)
            checked += 1
    return checked


def _call(root: Path, script: str, args: list[str], budget_seconds: int, label: str) -> str:
    entry = root / script
    # python -I removes ambient and script directories from sys.path. Inject
    # *only* the SHA-verified extracted module directory before running entry.
    boot = (
        'import sys,runpy; from pathlib import Path; '
        'p=Path(sys.argv[1]).resolve(); '
        'sys.argv=[str(p),*sys.argv[2:]]; '
        'sys.path.insert(0,str(p.parent)); '
        'runpy.run_path(str(p),run_name="__main__")'
    )
    env = {k:v for k,v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONSTARTUP','PYTHONHOME','PYTHONINSPECT')}
    env['PYTHONNOUSERSITE'] = '1'
    try:
        completed = subprocess.run([sys.executable,'-I','-B','-c',boot,str(entry),*args],
                                   cwd=root,env=env,capture_output=True,text=True,
                                   timeout=budget_seconds,check=False)
    except subprocess.TimeoutExpired as exc:
        raise ValueError('UNRESOLVED: '+label+' exceeded execution budget') from exc
    if completed.returncode != 0:
        raise ValueError('UNRESOLVED: '+label+' failed: '+completed.stderr[-800:])
    return completed.stdout


def replay(archive: Path, expected_sha: str, extracted_root: Path | None = None,
           budget_seconds: int = 120, run_source_free_tests: bool = True) -> dict:
    if type(budget_seconds) is not int or budget_seconds <= 0:
        raise ValueError('UNRESOLVED: no execution budget')
    archive = archive.resolve(strict=True)
    manifest = verify_zip(archive,expected_sha)
    if extracted_root is not None:
        verify_tree(archive,extracted_root,manifest)
    with tempfile.TemporaryDirectory(prefix='hist001d_d120_attested_') as temp:
        root = Path(temp)
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                dest = root / member.filename
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(z.read(member.filename))
        count = verify_tree(archive,root,manifest)
        sat = root/'inputs/saturation_v1r1.zip'
        h = root/'inputs/full_h_v1r1.zip'
        out = root/'replayed_source_receipt.json'
        qa = root/'replayed_seam_adversarial.json'
        source_out = _call(root,SRC_DIR+'/source_seam_replay.py',
                           ['--saturation',str(sat),'--finite-h',str(h),'--out',str(out)],
                           budget_seconds,'original-source D120 replay')
        lines = [s for s in source_out.splitlines() if s.startswith('SOURCE_D120 ')]
        if len(lines) != 6 or any(not row.startswith('SOURCE_D120 '+lens+' D,S,H 180/180')
                                   for row,lens in zip(lines,LENSES)):
            raise ValueError('UNRESOLVED: incomplete or reordered D120/S/H source replay')
        if not out.is_file() or sha(out.read_bytes()) != SOURCE_RECEIPT_SHA:
            raise ValueError('UNRESOLVED: original source-dependent receipt not byte-identical')
        independent = _call(root,SRC_DIR+'/verify_seam.py',
                            ['--saturation',str(sat),'--finite-h',str(h),'--receipt',str(out)],
                            budget_seconds,'independent alternate-series interval verifier')
        cert_lines = [s for s in independent.splitlines() if s.startswith('INDEPENDENT_POSITIVE_EXP_CERT ')]
        if cert_lines != ['INDEPENDENT_POSITIVE_EXP_CERT '+lens for lens in LENSES] or independent.count('INDEPENDENT_SEAM_OK') != 1:
            raise ValueError('UNRESOLVED: independent 6-lens proof output missing')
        qa_out = _call(root,SRC_DIR+'/adversarial_seam.py',
                       ['--receipt',str(out),'--saturation',str(sat),'--finite-h',str(h),'--out',str(qa)],
                       budget_seconds,'historical adversarial source replay')
        if 'ADVERSARIAL_QA_REJECTED 30 SHA '+QA_RECEIPT_SHA not in qa_out or not qa.is_file() or sha(qa.read_bytes()) != QA_RECEIPT_SHA:
            raise ValueError('UNRESOLVED: original 30-case adversarial receipt not byte-identical')
        if run_source_free_tests:
            tests = root/'tests/historical'
            env = {k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT')}
            env['PYTHONNOUSERSITE']='1'
            try:
                proc=subprocess.run([sys.executable,'-B','-m','pytest','-q',
                        str(tests/'test_hist001d_d120_seam_source_free.py'),
                        str(tests/'test_hist001d_d120_v1r2_attestation.py')],
                        cwd=root,env=env,text=True,capture_output=True,timeout=budget_seconds,check=False)
            except subprocess.TimeoutExpired as exc:
                raise ValueError('UNRESOLVED: source-free tests exceeded budget') from exc
            if proc.returncode != 0 or 'passed' not in proc.stdout:
                raise ValueError('UNRESOLVED: source-free tests failed: '+proc.stdout[-800:]+proc.stderr[-400:])
    return {
        'status':'CERTIFIED_CONDITIONAL_SOURCE_D120_SEAM_REPLAY',
        'attested_files':count,
        'expected_external_whole_zip_sha256':expected_sha,
        'historical_original_source_composite_sha256':SOURCE_46PLUS3_SHA,
        'historical_D120_nodes_bit_replayed':1080,
        'historical_shadow_circularization_nodes_bit_replayed':1080,
        'historical_H_nodes_bit_replayed':1080,
        'original_sampled_roots_bit_replayed':6,
        'independent_alternate_exponential_interval_lenses':6,
        'adversarial_cases_reproduced':30,
        'receipt_source_sha256':SOURCE_RECEIPT_SHA,
        'receipt_adversarial_sha256':QA_RECEIPT_SHA,
        'counterfactual_full_angle_integral_certified':False,
        'counterfactual_root_shift_interval_proved':False,
        'physical_provider_admitted':False,
        'empirical_validation':'NOT_ESTABLISHED',
        'scientific_authority_promoted':False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--archive',type=Path)
    p.add_argument('--expected-sha256')
    p.add_argument('--extracted-root','--root',dest='extracted_root',type=Path)
    p.add_argument('--budget-seconds',type=int,default=120)
    p.add_argument('--skip-source-free-tests',action='store_true')
    p.add_argument('--full',action='store_true',help='legacy compatibility; external pin remains required')
    args=p.parse_args()
    try:
        if args.archive is None or args.expected_sha256 is None:
            raise ValueError('UNRESOLVED: --archive and independently supplied --expected-sha256 required')
        outcome=replay(args.archive,args.expected_sha256,args.extracted_root,args.budget_seconds,
                       not args.skip_source_free_tests)
    except (ValueError,TypeError,KeyError,zipfile.BadZipFile,json.JSONDecodeError,OSError) as exc:
        print(json.dumps({'status':'UNRESOLVED','reason':str(exc)},sort_keys=True))
        return 2
    print(json.dumps(outcome,sort_keys=True,indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
