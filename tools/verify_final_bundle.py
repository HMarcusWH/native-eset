#!/usr/bin/env python3
"""Verify a Native ESET final bundle without executing code from that bundle.

An independently retained expected ZIP digest supplies the integrity anchor.
Without it, internal checks do not authenticate the publisher or the science.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import tarfile
import zipfile

MAX_ARCHIVE_BYTES = 20_000_000
MAX_TOTAL_BYTES = 50_000_000
MAX_ENTRIES = 2000


def safe_name(name: object) -> str:
    if not isinstance(name, str) or not name or '\\' in name or '\x00' in name:
        raise ValueError('unsafe artifact name')
    if any(part in {'', '.', '..'} or ':' in part for part in name.split('/')):
        raise ValueError('unsafe artifact path')
    return name


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_hash(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('invalid SHA-256')
    return value


def _pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ValueError('duplicate JSON member')
        out[key] = value
    return out


def _json(data: bytes):
    return json.loads(data.decode('utf-8'), object_pairs_hook=_pairs)


def zip_bytes(data: bytes) -> dict[str, bytes]:
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ValueError('archive byte budget exceeded')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_ENTRIES or sum(i.file_size for i in infos) > MAX_TOTAL_BYTES:
            raise ValueError('archive expansion budget exceeded')
        seen = set()
        out = {}
        for info in infos:
            name = safe_name(info.filename)
            if name.casefold() in seen or info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('duplicate, directory or symlink archive member')
            seen.add(name.casefold())
            out[name] = archive.read(info)  # also checks the ZIP CRC
        return out


def verify(path: Path, expected_sha256: str | None = None) -> dict:
    if path.is_symlink() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError('archive is a symlink or exceeds the size budget')
    raw = path.read_bytes()
    actual = digest(raw)
    if expected_sha256 is not None and actual != require_hash(expected_sha256):
        raise ValueError('ZIP does not match the external expected SHA-256')
    blobs = zip_bytes(raw)
    inventory_name = 'release/ARTIFACTS_SHA256.json'
    inventory = _json(blobs[inventory_name])
    if set(inventory) != {'schema', 'files'} or inventory['schema'] != 'NATIVE_ESET_BUNDLE_INVENTORY_V1':
        raise ValueError('invalid artifact inventory schema')
    files = inventory['files']
    if not isinstance(files, dict) or set(files) != set(blobs) - {inventory_name}:
        raise ValueError('artifact inventory differs from ZIP members')
    for name, expected in files.items():
        safe_name(name)
        if digest(blobs[name]) != require_hash(expected):
            raise ValueError('artifact checksum mismatch: ' + name)
    source_manifest = _json(blobs['native-eset/MANIFEST_SHA256.json'])
    if source_manifest.get('manifest_version') != 1 or not isinstance(source_manifest.get('files'), dict):
        raise ValueError('invalid source manifest')
    sources = source_manifest['files']
    source_names = {name.removeprefix('native-eset/') for name in blobs if name.startswith('native-eset/')}
    if source_names != set(sources) | {'MANIFEST_SHA256.json'}:
        raise ValueError('source subtree differs from source manifest')
    for name, expected in sources.items():
        safe_name(name)
        if digest(blobs['native-eset/' + name]) != require_hash(expected):
            raise ValueError('source checksum mismatch: ' + name)
    package_sources = {name.removeprefix('src/'): blobs['native-eset/' + name]
                       for name in sources if name.startswith('src/native_eset/') and name.endswith(('.py', '.json'))}
    wheels = [name for name in blobs if name.startswith('release/dist/') and name.endswith('.whl')]
    sdists = [name for name in blobs if name.startswith('release/dist/') and name.endswith('.tar.gz')]
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError('exactly one wheel and one sdist required')
    wheel = zip_bytes(blobs[wheels[0]])
    actual_package = {name: data for name, data in wheel.items() if name.startswith('native_eset/')}
    if actual_package != package_sources:
        raise ValueError('installed wheel package sources differ from the audited source')
    with tarfile.open(fileobj=io.BytesIO(blobs[sdists[0]]), mode='r:gz') as archive:
        members = archive.getmembers()
        if len(members) > MAX_ENTRIES or sum(m.size for m in members) > MAX_TOTAL_BYTES:
            raise ValueError('sdist expansion budget exceeded')
        sdist_files = {}
        seen = set()
        for member in members:
            name = safe_name(member.name)
            if name.casefold() in seen:
                raise ValueError('duplicate sdist member')
            seen.add(name.casefold())
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('nonregular sdist member')
            relative = name.split('/', 1)[1]
            sdist_files[relative] = archive.extractfile(member).read()
    for name in sources:
        if sdist_files.get(name) != blobs['native-eset/' + name]:
            raise ValueError('sdist does not preserve source bytes: ' + name)
    extras = set(sdist_files) - set(sources) - {'MANIFEST_SHA256.json', 'PKG-INFO', 'setup.cfg'}
    if any(not name.startswith('src/native_eset.egg-info/') for name in extras):
        raise ValueError('unexpected source-distribution payload')
    b0 = blobs['native-eset/provenance/B0_2026-10-27_original.zip']
    if digest(b0) != 'dc8a5ed8e67273e58e825a744658bd2b938696bd10faac707037ee17357a0a06':
        raise ValueError('original B0 changed')
    if any(name.endswith(('.jsonl', '.fits', '.sqlite', '.pem')) for name in blobs):
        raise ValueError('private/raw scientific or credential payload in bundle')
    return {'status': 'FINAL_BUNDLE_INTEGRITY_PASS', 'archive_sha256': actual,
            'archive_bytes': len(raw), 'zip_entries': len(blobs), 'source_files': len(sources),
            'package_source_files': len(package_sources), 'wheel_source_match': True, 'sdist_source_match': True,
            'anchor': 'EXTERNAL_EXPECTED_DIGEST_MATCHED' if expected_sha256 else 'INTERNAL_INTEGRITY_ONLY',
            'claim_boundary': 'NOT_A_SIGNATURE_CI_RESULT_OR_SCIENTIFIC_VALIDATION'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--expected-sha256')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.archive, args.expected_sha256), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, zipfile.BadZipFile, tarfile.TarError) as exc:
        print(json.dumps({'status': 'FAIL_CLOSED', 'error_type': type(exc).__name__, 'message': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
