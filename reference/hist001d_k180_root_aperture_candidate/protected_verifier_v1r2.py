#!/usr/bin/env python3
"""Fail-closed protected fixed-aperture mathematical release verifier (v1r2).

All contract, content, lens and replay-hash checks execute under -O / -OO.
The immutable source inputs and mathematical output remain inherited unchanged.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
LENSES = ('J0822+1828', 'J0915+4211', 'J0930+2855', 'J1021+2028', 'J1111+2234', 'J1135+3720')
SCHEMA = 'HIST001D_SOURCE_LOCKED_ROOT_FIXED_A_NONPROMOTING_RELEASE_V1R1'
RESULT_SCHEMA = 'HIST001D_ORIGINAL_MARCH180_ROOT_APERTURE_SELECTED_SMOOTH_CONTINUUM_FIXED_DIAGNOSTIC_INTERVAL_V1'


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def require(flag: bool, message: str) -> None:
    if not flag:
        raise ValueError(message)


def verify_file_map(root: Path, file_map: dict) -> int:
    """Independently executable source-free integrity primitive."""
    require(type(file_map) is dict and bool(file_map), 'EMPTY_OR_INVALID_FILE_MAP')
    for name, expected in file_map.items():
        require(type(name) is str and bool(name), 'BAD_MEMBER_NAME')
        rel = PurePosixPath(name)
        require(not rel.is_absolute() and '..' not in rel.parts and '\\' not in name,
                'MANIFEST_PATH_ESCAPE')
        require(type(expected) is str and len(expected) == 64 and
                all(c in '0123456789abcdef' for c in expected), 'BAD_MANIFEST_SHA')
        p = root.joinpath(*rel.parts)
        require(p.is_file() and not p.is_symlink(), 'MISSING_OR_SYMLINK_' + name)
        require(sha(p.read_bytes()) == expected, 'MEMBER_HASH_MISMATCH_' + name)
    return len(file_map)


def verify(root: Path = ROOT, result_path: Path | None = None) -> int:
    m = json.loads((root / 'MANIFEST_SHA256.json').read_bytes())
    require(type(m) is dict and m.get('schema') == SCHEMA, 'WRONG_RELEASE_SCHEMA')
    require(m.get('all_aperture_bands_proved') is False and
            m.get('all_historical_roots_proved') is False and
            m.get('pointwise_only') is True and
            m.get('physical_provider_admitted') is False and
            m.get('empirical_validation') == 'NOT_ESTABLISHED', 'SCIENTIFIC_PROMOTION_DENIED')
    count = verify_file_map(root, m.get('files'))
    cert = json.loads((root / 'results/root_fixed_A_certificate.json').read_bytes())
    require(type(cert) is dict and cert.get('schema') == RESULT_SCHEMA, 'WRONG_CERTIFICATE_SCHEMA')
    require(cert.get('all_six_positive_fixed_A') is True and
            cert.get('all_aperture_bands_proved') is False and
            cert.get('physical_provider_admitted') is False, 'CERTIFICATE_SCOPE_VIOLATION')
    lenses = cert.get('lenses')
    require(type(lenses) is list and len(lenses) == 6 and
            tuple(x.get('lens') for x in lenses if type(x) is dict) == LENSES,
            'SIX_LENS_IDENTITY_OR_COUNT_MISMATCH')
    require(all(type(x.get('Q_March_minus_P_selected_continuum_interval_integer_Msun')) is list and
                len(x['Q_March_minus_P_selected_continuum_interval_integer_Msun']) == 2 and
                type(x['Q_March_minus_P_selected_continuum_interval_integer_Msun'][0]) is int and
                x['Q_March_minus_P_selected_continuum_interval_integer_Msun'][0] > 0
                for x in lenses), 'FIXED_A_STRICT_SIGNS_MISSING')
    if result_path is not None:
        require(sha(result_path.read_bytes()) == m.get('result_sha256'),
                'SOURCE_BOUND_RESULT_REPLAY_HASH_MISMATCH')
    return count


def main() -> int:
    try:
        if len(sys.argv) == 1:
            result_path = None
        elif len(sys.argv) == 3 and sys.argv[1] == '--result':
            result_path = Path(sys.argv[2])
        else:
            raise ValueError('BAD_CLI_ARGUMENTS')
        count = verify(result_path=result_path)
        print('RELEASE_INTEGRITY_PASS', count, 'certificate_lenses', len(LENSES),
              'original_law_not_physical')
        return 0
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print('UNRESOLVED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
