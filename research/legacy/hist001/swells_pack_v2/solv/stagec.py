from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import math
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class EnvelopeSpec:
    version: str
    bounds: dict[str, float | None]
    notes: list[str]


DEFAULT_BOUNDS = {
    'max_abs_mu_minus_1': None,
    'max_abs_sigma_minus_1': None,
    'max_abs_eta_minus_1': None,
}


DEFAULT_NOTES = [
    'Populate these near-GR bounds from the external Stage C survey-scale solver/data harness.',
    'Leaving a bound null means the pack can audit the interface but cannot pass/fail that observable numerically.',
    'Accepted inputs are either epsilon directly, or mu/Sigma/eta columns from an external linear solver export.',
]


def observable_map_from_epsilon(epsilon, *, eta_value: float = 1.0):
    eps = np.asarray(epsilon, dtype=float)
    eps = np.clip(eps, 1e-12, None)
    mu = 1.0 / eps
    sigma = 1.0 / eps
    eta = np.full_like(mu, float(eta_value), dtype=float)
    return mu, sigma, eta


def build_default_envelope() -> dict[str, Any]:
    return {
        'version': 'stageC_envelope_template_v1',
        'required_axes': ['a', 'k_hMpc'],
        'accepted_value_columns': ['epsilon', 'mu', 'Sigma', 'eta'],
        'bounds': dict(DEFAULT_BOUNDS),
        'notes': list(DEFAULT_NOTES),
    }


def load_envelope(path: str | Path | None) -> EnvelopeSpec:
    if path is None:
        obj = build_default_envelope()
    else:
        obj = json.loads(Path(path).read_text())
    bounds = dict(DEFAULT_BOUNDS)
    bounds.update(obj.get('bounds', {}))
    return EnvelopeSpec(
        version=str(obj.get('version', 'stageC_envelope_template_v1')),
        bounds=bounds,
        notes=list(obj.get('notes', DEFAULT_NOTES)),
    )


def normalize_linear_samples(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if 'epsilon' in out.columns and out['epsilon'].notna().any():
        mask = out['epsilon'].notna()
        mu, sigma, eta = observable_map_from_epsilon(out.loc[mask, 'epsilon'].to_numpy(dtype=float))
        out.loc[mask, 'mu'] = mu
        out.loc[mask, 'Sigma'] = sigma
        if 'eta' not in out.columns:
            out['eta'] = np.nan
        eta_mask = mask & out['eta'].isna()
        if eta_mask.any():
            out.loc[eta_mask, 'eta'] = np.full(int(eta_mask.sum()), 1.0, dtype=float)
    else:
        missing = [c for c in ['mu', 'Sigma', 'eta'] if c not in out.columns]
        if missing:
            raise ValueError(f'Linear sample file must contain epsilon or mu/Sigma/eta; missing {missing}')
    for col in ['mu', 'Sigma', 'eta']:
        out[col] = pd.to_numeric(out[col], errors='coerce')
    out['abs_mu_minus_1'] = (out['mu'] - 1.0).abs()
    out['abs_sigma_minus_1'] = (out['Sigma'] - 1.0).abs()
    out['abs_eta_minus_1'] = (out['eta'] - 1.0).abs()
    return out


def apply_envelope(df: pd.DataFrame, envelope: EnvelopeSpec) -> pd.DataFrame:
    out = df.copy()
    mapping = {
        'max_abs_mu_minus_1': 'abs_mu_minus_1',
        'max_abs_sigma_minus_1': 'abs_sigma_minus_1',
        'max_abs_eta_minus_1': 'abs_eta_minus_1',
    }
    enforced = []
    for bound_name, metric_col in mapping.items():
        limit = envelope.bounds.get(bound_name)
        pass_col = f'pass_{metric_col}'
        if limit is None or (isinstance(limit, float) and not math.isfinite(limit)):
            out[pass_col] = pd.NA
            continue
        enforced.append(pass_col)
        out[pass_col] = out[metric_col] <= float(limit)
    if enforced:
        out['all_enforced_bounds_pass'] = out[enforced].fillna(True).all(axis=1)
    else:
        out['all_enforced_bounds_pass'] = pd.NA
    return out


def build_contract_rows(*, j2141_summary: dict[str, Any] | None = None, candidate_name: str = 'ra0_gated_geometry_sigmoid_reg_v2') -> pd.DataFrame:
    rows: list[dict[str, Any]] = [
        {
            'regime': 'homogeneous_frw_off',
            'scope': 'contract',
            'candidate_name': candidate_name,
            'a': 1.0,
            'k_hMpc': 0.1,
            'epsilon': 1.0,
            'eta': 1.0,
            'source': 'doctrine_off_state',
            'note': 'FRW-off contract row; not a survey fit.',
        },
        {
            'regime': 'local_precision_off',
            'scope': 'contract',
            'candidate_name': candidate_name,
            'a': 1.0,
            'k_hMpc': 1.0,
            'epsilon': 1.0,
            'eta': 1.0,
            'source': 'doctrine_off_state',
            'note': 'Local-off contract row; not a survey fit.',
        },
    ]
    if j2141_summary is not None:
        masses = j2141_summary.get('component_masses_at_observed_re_1e10Msun', {})
        bary = float(masses.get('bulge_projected', 0.0)) + float(masses.get('disk_projected', 0.0))
        total = float(masses.get('total_projected', 0.0))
        mu_proxy = total / bary if bary > 0 else np.nan
        metrics = j2141_summary.get('metrics', {})
        rows.append({
            'regime': 'j2141_same_solution_proxy',
            'scope': 'nonlinear_proxy',
            'candidate_name': candidate_name,
            'a': np.nan,
            'k_hMpc': np.nan,
            'epsilon': np.nan,
            'mu': mu_proxy,
            'Sigma': mu_proxy,
            'eta': 1.0 - float(metrics.get('abs_eta_minus_1', 0.0)),
            'source': 'j2141_same_solution_summary',
            'note': 'Nonlinear galaxy-regime enhancement proxy at observed Einstein radius; not a survey-scale mu/Sigma/eta point.',
        })
    out = pd.DataFrame(rows)
    if 'mu' not in out.columns:
        mu, sigma, eta = observable_map_from_epsilon(out['epsilon'].fillna(1.0).to_numpy(dtype=float))
        out['mu'] = mu
        out['Sigma'] = sigma
        out['eta'] = eta
    else:
        mask = out['mu'].isna() & out['epsilon'].notna()
        if mask.any():
            mu, sigma, eta = observable_map_from_epsilon(out.loc[mask, 'epsilon'].to_numpy(dtype=float))
            out.loc[mask, 'mu'] = mu
            out.loc[mask, 'Sigma'] = sigma
            out.loc[mask, 'eta'] = eta
    return normalize_linear_samples(out)


def build_closure_object(*, candidate_name: str, envelope: EnvelopeSpec, contract_rows: pd.DataFrame, linear_rows: pd.DataFrame | None = None, j2141_summary: dict[str, Any] | None = None) -> dict[str, Any]:
    linear_present = linear_rows is not None and len(linear_rows) > 0
    bounds_configured = {k: v for k, v in envelope.bounds.items() if v is not None}
    closure = {
        'harness_id': 'stageC_linear_handshake_scaffold_v1',
        'candidate_name': candidate_name,
        'envelope_version': envelope.version,
        'notes': list(envelope.notes),
        'checks': {
            'interface_defined': True,
            'linear_dataset_present': bool(linear_present),
            'survey_bounds_configured': bool(bounds_configured),
            'contract_rows_emitted': int(len(contract_rows)),
            'linear_rows_emitted': int(len(linear_rows)) if linear_rows is not None else 0,
        },
        'contract_summary': {
            'frw_off_present': bool((contract_rows['regime'] == 'homogeneous_frw_off').any()),
            'local_off_present': bool((contract_rows['regime'] == 'local_precision_off').any()),
            'nonlinear_proxy_present': bool((contract_rows['scope'] == 'nonlinear_proxy').any()),
        },
        'missing_inputs': [],
        'status': 'BLOCKED_ON_EXTERNAL_LINEAR_DATA',
    }
    if not linear_present:
        closure['missing_inputs'].append('linear_samples_csv')
    if not bounds_configured:
        closure['missing_inputs'].append('survey_envelope_bounds')
    if j2141_summary is None:
        closure['missing_inputs'].append('optional_j2141_same_solution_summary_for_proxy_row')
    if linear_present and bounds_configured:
        enforced = linear_rows['all_enforced_bounds_pass'].dropna() if 'all_enforced_bounds_pass' in linear_rows else pd.Series(dtype=bool)
        closure['status'] = 'PASS' if len(enforced) and bool(enforced.all()) else 'FAIL'
    elif linear_present:
        closure['status'] = 'INTERFACE_READY_BOUNDS_MISSING'
    return closure
