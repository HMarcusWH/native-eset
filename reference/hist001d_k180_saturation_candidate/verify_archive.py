#!/usr/bin/env python3
"""Fail-closed integrity and scope verifier for the protected K180 saturation release.

No scientific source arrays or mathematical result data are changed by this audit repair.
All integrity checks execute even under Python -O / -OO; no assert statements.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
EXPECTED_PARENT = {
    'original_parent.zip': '3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18',
    'all180_parent.zip': '2e3c13ba68bbed98ef2c529a2e331b15c666d8927da22daf1be78d33a79f6391',
    'c3_derivative_parent.zip': '725d7ba004d1bd54fb6be2838ca995fc5ba7ce45b54213f1926f0d78bd7e7f11',
}
RESULT_STEMS = (
    'endpoint_saturation_producer', 'endpoint_saturation_independent',
    'all_aperture_bv_producer', 'all_aperture_bv_independent',
    'node_only_nonidentifiability',
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_file_map(root: Path, files: dict, *, parents: bool = True) -> int:
    """Read all declared members, reject symlink/path escape, compare exact bytes.

    `parents=False` is *only* for source-free synthetic unit fixtures; the
    real CLI always requires the pinned original parent hashes.
    """
    require(type(files) is dict and bool(files), 'MALFORMED_OR_EMPTY_FILE_MAP')
    for name, expected in files.items():
        require(type(name) is str and bool(name), 'BAD_MANIFEST_PATH')
        p = PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts and '\\' not in name,
                'MANIFEST_PATH_ESCAPE')
        require(type(expected) is str and len(expected) == 64 and
                all(c in '0123456789abcdef' for c in expected), 'BAD_SHA256_DIGEST')
        target = root.joinpath(*p.parts)
        require(target.is_file() and not target.is_symlink(), 'FILE_MISSING_OR_SYMLINK_' + name)
        require(sha(target.read_bytes()) == expected, 'FILE_SHA256_MISMATCH_' + name)
    if parents:
        require(all(files.get(n) == h for n, h in EXPECTED_PARENT.items()),
                'PINNED_PARENT_HASH_MISMATCH')
    return len(files)


def verify(root: Path = ROOT) -> int:
    manifest = json.loads((root / 'MANIFEST_SHA256.json').read_bytes())
    require(type(manifest) is dict, 'MALFORMED_MANIFEST')
    require(manifest.get('schema') == 'HIST001D_MARCH180_K180_SATURATION_SOURCE_INTEGRITY_V1',
            'WRONG_SCIENTIFIC_SCHEMA')
    require(manifest.get('physical_provider_admitted') is False and
            manifest.get('original_March_numerical_error_certified') is False and
            manifest.get('empirical_validation') == 'NOT_ESTABLISHED', 'FORBIDDEN_CLAIM_PROMOTION')
    count = verify_file_map(root, manifest.get('files'), parents=True)
    for stem in RESULT_STEMS:
        record = json.loads((root / (stem + '.json')).read_bytes())
        require(type(record) is dict, 'MALFORMED_PROTECTED_RESULT_' + stem)
        require(record.get('physical_provider_admitted', record.get('physical_density_source_admitted'))
                is False or stem == 'node_only_nonidentifiability', 'PROVIDER_PROMOTION_' + stem)
        require(record.get('empirical_validation') == 'NOT_ESTABLISHED', 'VALIDATION_PROMOTION_' + stem)
    return count


def main() -> int:
    try:
        if len(sys.argv) != 1:
            raise ValueError('INVALID_CLI_ARGUMENTS')
        count = verify()
        print('ARCHIVE_MEMBER_SHA_PASS', count)
        return 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print('UNRESOLVED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
