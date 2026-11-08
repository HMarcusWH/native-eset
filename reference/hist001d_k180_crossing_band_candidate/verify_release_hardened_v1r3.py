#!/usr/bin/env python3
"""Strict archive + attested executable mathematical-witness verifier (v1r3).

A SHA-controlled ZIP and the local mathematical checker are separate inputs.
Never import an unverified local checker. The single accepted checker SHA here
is pinned to the independently reviewed v1r2 historical mathematical checker.
This replays saved witness arithmetic only, not source-dependent Bessel proofs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = 'HIST001D_K180_SIX_CROSSING_BAND_MATHEMATICAL_SOURCE_ARCHIVE_V1'
CHECKER = 'reference/hist001d_k180_crossing_band_candidate/verify_band_witness.py'
CHECKER_SHA256 = '791243223a074b3026cd824e17ad2aa23faac4ac3a3eacb1c1b15b28b7a36375'
PARENT = 'inputs/HIST001D_K180_SATURATED_REVIEW_REPAIR_V1R1_NONPROMOTING_2026_11_02.zip'
PARENT_SHA256 = '99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
DIAGNOSTIC = 'inputs/HIST001D_K180_Root_Aperture_Six_Lens_Diagnostic_NONPROOF_v1_2026_11_02.json'
DIAGNOSTIC_SHA256 = '298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812'
RESULT = 'results/whole_band_certificate.json'
RESULT_SHA256 = 'd4c44e8eca66985acf347455fcce7f5e72b01d1dacd09507c62e1250f2398e5a'
LENSES = ('J0822+1828', 'J0915+4211', 'J0930+2855', 'J1021+2028', 'J1111+2234', 'J1135+3720')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def strict_hash(value: object) -> None:
    require(type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value),
            'INVALID_HEX_SHA256')


def attest_checker_file(local_path: Path, verified_bytes: bytes, expected_sha256: str = CHECKER_SHA256) -> bytes:
    """Fail closed on a stale/mutated local checker even if the ZIP itself passes.

    Returns the exact already-hashed archive bytes; callers execute precisely
    these bytes rather than resolving an import name through sys.path or pyc.
    """
    strict_hash(expected_sha256)
    require(sha(verified_bytes) == expected_sha256, 'ARCHIVED_CHECKER_NOT_REVIEWED_SOURCE')
    require(local_path.is_file() and not local_path.is_symlink(), 'LOCAL_CHECKER_MISSING_OR_SYMLINK')
    require(local_path.read_bytes() == verified_bytes, 'LOCAL_CHECKER_NOT_ARCHIVE_IDENTICAL')
    return verified_bytes


def validate_zip(zip_path: Path, source_root: Path, *, expected_zip_sha256: str | None = None) -> dict:
    if expected_zip_sha256 is not None:
        strict_hash(expected_zip_sha256)
        require(sha(zip_path.read_bytes()) == expected_zip_sha256, 'EXTERNAL_ARCHIVE_SHA256_MISMATCH')
    with zipfile.ZipFile(zip_path) as z:
        require(z.testzip() is None, 'ZIP_CRC_FAIL')
        names = z.namelist()
        require(len(set(names)) == len(names) and 'MANIFEST_SHA256.json' in names, 'ZIP_MEMBER_COLLISION')
        for info in z.infolist():
            rel = PurePosixPath(info.filename)
            require(not rel.is_absolute() and '..' not in rel.parts and '\\' not in info.filename,
                    'ZIP_MEMBER_PATH_ESCAPE')
            require(not stat.S_ISLNK(info.external_attr >> 16), 'ZIP_SYMLINK_DISALLOWED')
        m = json.loads(z.read('MANIFEST_SHA256.json'))
        require(type(m) is dict and m.get('schema') == SCHEMA and m.get('archive_revision') == 'v1r3',
                'WRONG_RELEASE_IDENTITY')
        require(m.get('physical_provider_admitted') is False and
                m.get('empirical_validation') == 'NOT_ESTABLISHED', 'FORBIDDEN_SCIENTIFIC_PROMOTION')
        require(type(m.get('files')) is dict and bool(m['files']) and
                set(m['files']) == set(names) - {'MANIFEST_SHA256.json'}, 'ZIP_MANIFEST_MISMATCH')
        for name, expected in m['files'].items():
            strict_hash(expected)
            require(sha(z.read(name)) == expected, 'ZIP_MEMBER_SHA256_MISMATCH:' + name)
        for name, expected in ((PARENT, PARENT_SHA256), (DIAGNOSTIC, DIAGNOSTIC_SHA256),
                               (RESULT, RESULT_SHA256), (CHECKER, CHECKER_SHA256)):
            require(sha(z.read(name)) == expected, 'PINNED_PARENT_RESULT_OR_CHECKER_CHANGED:' + name)
        doc = json.loads(z.read(RESULT))
        require(type(doc) is dict and doc.get('all_six_crossing_aperture_bands_positive') is True and
                doc.get('original_off_grid_H_root_count_proved') is False and
                doc.get('same_source_physical_lensing_proved') is False and
                doc.get('physical_provider_admitted') is False and
                doc.get('empirical_validation') == 'NOT_ESTABLISHED', 'RESULT_SCOPE_INVALID')
        lens_rows = doc.get('lenses')
        require(type(lens_rows) is list and len(lens_rows) == 6 and
                all(type(row) is dict for row in lens_rows) and
                tuple(row.get('lens') for row in lens_rows) == LENSES,
                'RESULT_LENS_SET_MISMATCH')
        qa = json.loads(z.read('results/adversarial_qa.json'))
        cases = qa.get('cases')
        require(qa.get('all_rejected') is True and type(cases) is list and len(cases) == 16 and
                all(type(case) is dict and case.get('rejected') is True for case in cases) and
                len(set(str(c.get('case')) for c in cases)) == 16, 'ADVERSARIAL_RECEIPT_INVALID')
        verified = attest_checker_file(source_root / CHECKER, z.read(CHECKER))
        # Execute exact SHA-pinned archive source directly. No sys.path/module/pyc substitution.
        symbols = {'__name__': 'hist001d_verified_witness_arithmetic', '__file__': str(source_root / CHECKER)}
        exec(compile(verified, str(source_root / CHECKER), 'exec'), symbols)  # noqa: S102
        validator = symbols.get('validate')
        require(callable(validator), 'ATTESTED_WITNESS_VALIDATE_MISSING')
        minimum = validator(doc)
        require(type(minimum) is int and minimum > 0, 'ATTESTED_WITNESS_NOT_STRICT_POSITIVE')
        return {
            'status': 'ARCHIVE_INTEGRITY_AND_ATTESTED_WITNESS_ARITHMETIC_PASS_NONPROMOTING',
            'external_archive_sha_attested': expected_zip_sha256 is not None,
            'zip_members': len(names), 'sha_manifest_entries': len(m['files']),
            'lens_count': len(lens_rows), 'positive_subbands': sum(len(x['positive_subbands']) for x in lens_rows),
            'witness_source_sha256': sha(verified), 'strict_minimum_gap_floor_Msun': minimum,
            'adversarial_records_checked': len(cases), 'whole_band_receipt_sha256': sha(z.read(RESULT)),
            'physical_provider_admitted': False, 'empirical_validation': 'NOT_ESTABLISHED',
            'producer_replayed_by_this_verifier': False,
        }


def default_source_root() -> Path:
    script = Path(__file__).resolve()
    return script.parents[1] if script.parent.name == 'tools' else script.parents[2]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--zip', required=True, type=Path)
    p.add_argument('--source-root', type=Path,
                   default=default_source_root())
    p.add_argument('--expected-zip-sha256', default=None)
    args = p.parse_args()
    try:
        receipt = validate_zip(args.zip, args.source_root, expected_zip_sha256=args.expected_zip_sha256)
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError, zipfile.BadZipFile,
            OverflowError, ZeroDivisionError, AssertionError) as error:
        print('UNRESOLVED: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
