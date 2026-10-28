"""Cold historical J2141 / SWELLS Set A tests; never evaluate as new physical validation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'research' / 'legacy' / 'hist001'
TOOL = ROOT / 'tools' / 'replay_hist001.py'


def _load_module():
    spec = importlib.util.spec_from_file_location('hist001_replay', TOOL)
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def test_hist001_source_lock_and_negative_records() -> None:
    module = _load_module()
    record = module.preflight()
    assert record['file_count'] == 46
    assert record['archived_negative_evidence_files'] == 3
    assert not record['physical_provider_authorized']
    assert record['original_zip_sha256'] == '283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
    bad = json.loads((LEGACY / 'archived_rangefinder' /
                      'reg_v2_fixed_law_geometry_morphology_nuisance_survival_curve_summary.json').read_text())
    assert [(x['rel_width'], x['n_at_6_of_6']) for x in bad['summaries']] == [
        (0.01, 323), (0.02, 140), (0.05, 23), (0.10, 3)]


def test_hist001_tampered_solver_is_denied(tmp_path: Path) -> None:
    module = _load_module()
    original = LEGACY / 'swells_pack_v2'
    copy = tmp_path / 'untampered_copy'
    shutil.copytree(original, copy)
    target = copy / 'solv' / 'dmalane.py'
    target.write_bytes(target.read_bytes() + b'\n# invalid alteration\n')
    with pytest.raises(ValueError, match='original source hash mismatch'):
        module.preflight(copy)
    (copy / 'unrecognized.json').write_text('{}')
    with pytest.raises(ValueError, match='source inventory mismatch'):
        module.preflight(copy)


def test_hist001_frozen_regression_and_no_refit_spherical_ablation(tmp_path: Path) -> None:
    out = tmp_path / 'outputs'
    proc = subprocess.run([sys.executable, str(TOOL), '--out', str(out), '--ablation'],
                          cwd=ROOT, text=True, capture_output=True, timeout=180)
    assert proc.returncode == 0, proc.stderr + '\n' + proc.stdout[-1500:]
    result = json.loads((out / 'receipt.json').read_text())
    assert result['status'] == 'PASS_HISTORICAL_REGRESSION_ONLY'
    assert result['science_scope'] == 'FITTED_AND_CALIBRATED_LEGACY_DM_A_NOT_VALIDATION'
    assert result['physical_provider_admitted'] is False
    assert result['current_native_v172_equivalence_proved'] is False
    assert result['setA_metrics']['n_both_pass'] == 6
    assert 'j2141/j2141_solver_output_filled.csv' in result['generated_output_sha256']
    assert 'j2141/j2141_lensing_output_filled.csv' in result['generated_output_sha256']
    assert 'j2141/j2141_acceptance_scoreboard_filled.csv' in result['generated_output_sha256']
    assert 'j2141/j2141_run_summary.json' in result['generated_output_sha256']
    assert 'numpy' in result['numerical_runtime']
    assert result['setA_metrics']['n_mass_pass'] == 6
    assert result['setA_metrics']['n_radius_pass'] == 6
    assert result['negative_controls']['spherical_setA']['both_pass'] == 2
    assert result['negative_controls']['source']['status'] == 'ARCHIVED_EXECUTION_NOT_REEXECUTED_THIS_RUN'
    assert result['j2141_metrics']['velocity_reduced_chi2'] == pytest.approx(1.1087208637638946, abs=1e-9)
    assert result['j2141_metrics']['einstein_radius_pull_sigma'] == pytest.approx(1.2456888888888888, abs=1e-9)
    assert result['j2141_metrics']['lensing_mass_pull_sigma'] == pytest.approx(0.20461194029850702, abs=1e-9)
    assert result['setA_metrics']['mean_abs_radius_pull_sigma'] == pytest.approx(0.975973270592819, abs=1e-8)
    assert result['setA_metrics']['mean_abs_mass_pull_sigma'] == pytest.approx(0.5980326367412955, abs=1e-8)
    assert result['negative_controls']['spherical_setA']['mean_abs_radius_pull_sigma'] == pytest.approx(8.168644014357623, abs=1e-8)
    assert result['negative_controls']['spherical_setA']['mean_abs_mass_pull_sigma'] == pytest.approx(3.234216692852517, abs=1e-8)
