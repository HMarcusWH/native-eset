#!/usr/bin/env python3
"""HIST-001. Cold, isolated legacy J2141 and six-SWELLS regression replay.

Original numerical solver and datasets are *never edited*. Runtime interventions
live exclusively in a temporary copy and are classified as non-predictive
historical ablations. This cannot authorize a Native ESET physical provider.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUNDLE = REPO / 'research' / 'legacy' / 'hist001'
FROZEN = BUNDLE / 'swells_pack_v2'
REFERENCE = BUNDLE / 'archived_rangefinder'
_LOCK = BUNDLE / 'SOURCE_LOCK.json'


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _assert_close(actual: float, expected: float, *, atol: float = 1e-8) -> None:
    if not math.isfinite(actual) or not math.isclose(actual, expected, rel_tol=0, abs_tol=atol):
        raise ValueError(f'HIST-001 regression mismatch: {actual!r} vs {expected!r}, atol={atol}')


def preflight(root: Path = FROZEN, lock_path: Path = _LOCK) -> dict:
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    listed = lock['source_filenames_sha256']
    actual_files = {p.relative_to(root).as_posix() for p in root.rglob('*')
                    if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    if actual_files != set(listed):
        raise ValueError(f'HIST-001 source inventory mismatch: missing={sorted(set(listed)-actual_files)}, '
                         f'extra={sorted(actual_files-set(listed))}')
    for rel, sha in listed.items():
        if digest(root / rel) != sha:
            raise ValueError('HIST-001 original source hash mismatch at ' + rel)
    for filename, ref in lock['archived_negative_controls'].items():
        path = REFERENCE / filename
        if not path.is_file() or digest(path) != ref['sha256']:
            raise ValueError('HIST-001 frozen negative evidence hash mismatch at ' + filename)
    if lock['physical_provider_admitted'] or lock['data_role'] != 'REGRESSION_OR_ORIGINAL_CALIBRATION_NOT_HELD_OUT':
        raise ValueError('HIST-001 invalid scientific claim cap')
    return {'status': 'FROZEN_HISTORICAL_SOURCE_LOCK_PASS', 'file_count': len(listed),
            'archived_negative_evidence_files': len(lock['archived_negative_controls']),
            'original_zip_sha256': lock['source_archive']['sha256'],
            'scope': lock['data_role'], 'physical_provider_authorized': False}


def subprocess_run(args: list[str], *, workdir: Path) -> dict:
    proc = subprocess.run(args, cwd=workdir, capture_output=True, text=True, timeout=120)
    if proc.returncode:
        raise RuntimeError(f'HIST-001 legacy run failed ({proc.returncode}): '
                           f'{proc.stderr[-1600:]} {proc.stdout[-1600:]}')
    return {'exit_code': proc.returncode, 'command': args[2:],
            'stdout_sha256': hashlib.sha256(proc.stdout.encode('utf-8')).hexdigest(),
            'stderr_sha256': hashlib.sha256(proc.stderr.encode('utf-8')).hexdigest()}


def _archive_controls() -> dict:
    neg = json.loads((REFERENCE / 'reg_v2_fixed_law_geometry_morphology_nuisance_survival_curve_summary.json').read_text())
    return {'status': 'ARCHIVED_EXECUTION_NOT_REEXECUTED_THIS_RUN',
            'n_trials_per_width': 1000, 'survival': [
                {'relative_width': row['rel_width'], 'six_of_six': row['n_at_6_of_6'],
                 'survival_fraction': row['survival_fraction_6_of_6']}
                for row in neg['summaries']]}


def replay(out: Path, *, ablation: bool = False) -> dict:
    # Verify BEFORE making any writable copy or importing historical Python.
    source = preflight()
    if out.resolve().is_relative_to(FROZEN.resolve()):
        raise ValueError('Refuse to write inside the locked historical source')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='eset-hist001-cold-') as td:
        work = Path(td) / 'swells_pack_v2'
        shutil.copytree(FROZEN, work)
        if set(p.relative_to(work).as_posix() for p in work.rglob('*')
               if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc') != set(
                json.loads(_LOCK.read_text())['source_filenames_sha256']):
            raise ValueError('Temporary work copy is incomplete')
        before = preflight(work)
        j = subprocess.run([sys.executable, '-m', 'solv.run_j2141_axisym_lens',
                            '--config', 'configs/j2141_test1_axisy_1689e9.json',
                            '--pack-root', '.', '--strict-regression'],
                           cwd=work, capture_output=True, text=True, timeout=120)
        if j.returncode:
            raise RuntimeError('Frozen J2141 strict regression failed: ' + j.stderr[-2000:])
        jdata = json.loads(j.stdout)
        frozen = json.loads((FROZEN / 'validation' / 'j2141_regression_b5afd5.json').read_text())
        for key, expected in frozen['metrics'].items():
            _assert_close(float(jdata['metrics'][key]), float(expected),
                          atol=float(frozen['tolerances'].get(key, 1e-9)))
        sa_path = out / 'setA_center.csv'
        sa_summary = out / 'setA_center.json'
        subprocess_run([sys.executable, '-m', 'solv.run_setA_port_cand', '--pack-root', '.',
                        '--candidate-name', 'ra0_gated_geometry_sigmoid_reg_v2',
                        '--out-csv', str(sa_path), '--out-json', str(sa_summary)], workdir=work)
        seta = json.loads(sa_summary.read_text())['results']
        expected = {'n_lenses_tested': 6, 'n_both_pass': 6, 'n_radius_pass': 6,
                    'n_mass_pass': 6, 'mean_abs_radius_pull_sigma': 0.975973270592819,
                    'mean_abs_mass_pull_sigma': 0.5980326367412955}
        for key, target in expected.items():
            _assert_close(float(seta[key]), float(target))
        neg = {'source': _archive_controls()}
        if ablation:
            sphere = out / 'setA_spherical.csv'
            sphere_summary = out / 'setA_spherical.json'
            wrapper = REPO / 'tools' / 'hist001_seta_ablation.py'
            subprocess_run([sys.executable, str(wrapper), '--pack-root', str(work),
                            '--out-csv', str(sphere), '--out-json', str(sphere_summary)], workdir=work)
            values = json.loads(sphere_summary.read_text())['results']
            archived = json.loads((REFERENCE / 'setA_reg_v2_projection_ablation_summary.json').read_text())
            row = next(x for x in archived['modes'] if x['projection_mode'] == 'spherical')
            for key in ['n_lenses_tested', 'n_both_pass', 'n_radius_pass', 'n_mass_pass',
                        'mean_abs_radius_pull_sigma', 'mean_abs_mass_pull_sigma']:
                _assert_close(float(values[key]), float(row['results'][key]), atol=1e-8)
            neg['spherical_setA'] = {'classification': 'REEXECUTED_NO_REFIT_ABLATION',
                                    'both_pass': int(values['n_both_pass']),
                                    'mean_abs_radius_pull_sigma': float(values['mean_abs_radius_pull_sigma']),
                                    'mean_abs_mass_pull_sigma': float(values['mean_abs_mass_pull_sigma'])}
        # Preserve the *newly computed* J2141 tables, not the previously archived ones.
        result_dir = work / 'res' / 'j2141_test1_axisym_structproj_baryonq'
        saved = out / 'j2141'
        saved.mkdir(exist_ok=True)
        expected_files = ('j2141_solver_output_filled.csv', 'j2141_lensing_output_filled.csv',
                          'j2141_acceptance_scoreboard_filled.csv', 'j2141_run_summary.json',
                          'run_manifest.json')
        for filename in expected_files:
            artifact = result_dir / filename
            if not artifact.is_file():
                raise RuntimeError('Legacy J2141 failed to emit expected product: ' + filename)
            shutil.copyfile(artifact, saved / filename)
        # Running writes only to the temporary original copy; source lock remains intact.
        preflight()
        outputs = {p.relative_to(out).as_posix(): digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
        import numpy as np
        import pandas as pd
        import scipy
        runtime = {'python': platform.python_version(), 'platform': platform.platform(),
                   'numpy': np.__version__, 'pandas': pd.__version__, 'scipy': scipy.__version__}
        receipt = {'receipt_version': 1, 'status': 'PASS_HISTORICAL_REGRESSION_ONLY',
                   'historical_identity': 'HIST-001-SWELLS-J2141-SETA-FROZEN',
                   'legacy_source_root': 'research/legacy/hist001/swells_pack_v2',
                   'science_scope': 'FITTED_AND_CALIBRATED_LEGACY_DM_A_NOT_VALIDATION',
                   'physical_provider_admitted': False,
                   'current_native_v172_equivalence_proved': False,
                   'original_source_lock': source, 'copy_preflight': before,
                   'j2141_metrics': jdata['metrics'], 'setA_metrics': seta,
                   'negative_controls': neg, 'numerical_runtime': runtime,
                   'generated_output_sha256': outputs}
        record = out / 'receipt.json'
        record.write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + '\n')
        return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--preflight-only', action='store_true')
    ap.add_argument('--out', type=Path, default=Path('runs/hist001'))
    ap.add_argument('--ablation', action='store_true')
    args = ap.parse_args()
    try:
        record = preflight() if args.preflight_only else replay(args.out, ablation=args.ablation)
        print(json.dumps(record, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, RuntimeError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'FAIL_CLOSED_HISTORICAL_EXECUTION_NOT_THEORY_FALSIFICATION',
                          'error': str(exc), 'type': type(exc).__name__}, sort_keys=True))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
