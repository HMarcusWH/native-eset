#!/usr/bin/env python3
"""HIST001D finite full-H source-bound *quick* replay with attested code identity.

This verifier distinguishes archive integrity, actual executable source identity,
and source-dependent mathematical replay. An OUT-OF-BAND SHA-256 is required;
this module and a self-authenticating ZIP do not constitute an external signature.
The quick mode reuses the separately recorded selected-M* Bessel endpoints.
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

ORIGINAL_SOURCE_SHA = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PRIOR_BAND_SHA = 'cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'
SCHEMA = 'HIST001D_FULL_H_BRIDGE_PROTECTED_SOURCE_MANIFEST_V1'
BRIDGE_PREFIX = 'reference/hist001d_full_h_bridge_candidate/'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_path(name: str) -> bool:
    p = PurePosixPath(name)
    return (isinstance(name, str) and bool(name) and not name.startswith('/')
            and '\\' not in name and p.as_posix() == name
            and not any(x in ('.', '..', '') for x in name.split('/')))


def verify_zip_identity(archive: Path, expected_sha: str) -> dict:
    """No claim if the expected digest is missing or obtained from the same ZIP."""
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha):
        raise ValueError('UNRESOLVED: missing/malformed external archive SHA-256')
    if not archive.is_file() or digest(archive.read_bytes()) != expected_sha:
        raise ValueError('UNRESOLVED: external archive digest mismatch')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('UNRESOLVED: ZIP CRC failure')
        infos = z.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(names)) or not all(valid_path(n) for n in names):
            raise ValueError('UNRESOLVED: duplicate/noncanonical ZIP names')
        # ZIP links are not executed or materialized.
        if any(((i.external_attr >> 16) & 0o170000) == 0o120000 for i in infos):
            raise ValueError('UNRESOLVED: ZIP contains a symlink')
        manifest = json.loads(z.read('MANIFEST_SHA256.json'))
        if manifest.get('schema') != SCHEMA or manifest.get('original_source_46plus3_sha256') != ORIGINAL_SOURCE_SHA:
            raise ValueError('UNRESOLVED: source/model identity changed')
        if manifest.get('prior_six_band_archive_sha256') != PRIOR_BAND_SHA:
            raise ValueError('UNRESOLVED: band parent changed')
        if manifest.get('physical_provider_admitted') is not False or manifest.get('empirical_validation') != 'NOT_ESTABLISHED':
            raise ValueError('UNRESOLVED: forbidden scientific promotion')
        if set(names) != set(manifest['files']) | {'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: missing/extra ZIP member')
        for name, sha in manifest['files'].items():
            if not valid_path(name) or not re.fullmatch(r'[0-9a-f]{64}', sha):
                raise ValueError('UNRESOLVED: manifest has invalid file digest/path')
            if digest(z.read(name)) != sha:
                raise ValueError('UNRESOLVED: protected ZIP content changed: '+name)
        if BRIDGE_PREFIX+'replay_source_locked.py' not in manifest['files']:
            raise ValueError('UNRESOLVED: missing replay entrypoint')
        if BRIDGE_PREFIX+'verify_full_h_witness.py' not in manifest['files']:
            raise ValueError('UNRESOLVED: missing mathematical verifier')
        if BRIDGE_PREFIX+'full_h_finite_source.py' not in manifest['files']:
            raise ValueError('UNRESOLVED: missing mathematical producer')
        return manifest


def verify_local_tree(archive: Path, root: Path, manifest: dict) -> int:
    """Every executed/mathematical source and every input/result must match ZIP.

    Public review can test this independently with synthetic archives.
    """
    checked = 0
    with zipfile.ZipFile(archive) as z:
        for name, sha in manifest['files'].items():
            path = root / name
            if not path.is_file() or path.is_symlink():
                raise ValueError('UNRESOLVED: local extraction file missing/symlink: '+name)
            if digest(path.read_bytes()) != sha or path.read_bytes() != z.read(name):
                raise ValueError('UNRESOLVED: local source/receipt does not match protected archive: '+name)
            checked += 1
    return checked


def replay(archive: Path, expected_sha: str, extracted_root: Path | None = None, budget_seconds: int = 240) -> dict:
    manifest = verify_zip_identity(archive, expected_sha)
    if type(budget_seconds) is not int or budget_seconds <= 0:
        raise ValueError('UNRESOLVED: no execution budget')
    if extracted_root is not None:
        verify_local_tree(archive, extracted_root, manifest)
    with tempfile.TemporaryDirectory(prefix='hist001d_h55_attested_') as td:
        root = Path(td)
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                target = root / info.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(info.filename))
        checked = verify_local_tree(archive, root, manifest)
        target = root / BRIDGE_PREFIX / 'replay_source_locked.py'
        try:
            done = subprocess.run(
                [sys.executable, '-I', '-B', str(target), '--root', str(root)],
                cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False, timeout=budget_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError('UNRESOLVED: source replay budget exceeded') from exc
        if done.returncode:
            raise ValueError('UNRESOLVED: source replay failed: '+done.stderr[-900:])
        # Legacy replay prints subprocess notes; verify the final status string and
        # mathematical/result records via legacy code's exact-byte SHA comparisons.
        if 'PASS_CLEAN_REPLAY_MATCHES_RECORDED_BYTES' not in done.stdout or 'QUICK_REPLAY_REUSES_SAVED_SELECTED_INTERVAL_ENDPOINTS' not in done.stdout:
            raise ValueError('UNRESOLVED: replay status not independently observed')
    return {
        'status':'PASS_PROTECTED_SOURCE_BOUND_QUICK_REPLAY_CONDITIONAL',
        'replayed_source_members': checked,
        'external_archive_sha256':expected_sha,
        'source_46plus3_locked':True,
        'finite_H_source_replay':'REGENERATED_BYTE_IDENTICAL',
        'independent_finite_witness':'REGENERATED_BYTE_IDENTICAL',
        'aggregate_and_adversarial':'REGENERATED_BYTE_IDENTICAL',
        'selected_Bessel_endpoints':'ARCHIVED_REUSED_NOT_REPRODUCED',
        'selected_smooth_global_root_uniqueness_proved':False,
        'original_compiled_float_offgrid_error_proved':False,
        'physical_provider_admitted':False,
        'empirical_validation':'NOT_ESTABLISHED'
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True,type=Path)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--extracted-root',type=Path)
    p.add_argument('--budget-seconds',type=int,default=240)
    args=p.parse_args()
    try:
        result=replay(args.archive,args.expected_sha256,args.extracted_root,args.budget_seconds)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(json.dumps({'status':'UNRESOLVED','reason':str(exc)},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
