from __future__ import annotations

import numpy as np
import pandas as pd



def reduced_chi2(obs, pred, err, dof_offset=2):
    obs = np.asarray(obs, dtype=float)
    pred = np.asarray(pred, dtype=float)
    err = np.asarray(err, dtype=float)
    mask = np.isfinite(obs) & np.isfinite(pred) & np.isfinite(err) & (err > 0)
    n = int(mask.sum())
    if n == 0:
        return np.nan
    chi2 = float(np.sum(((obs[mask] - pred[mask]) / err[mask])**2))
    dof = max(n - dof_offset, 1)
    return chi2 / dof



def pull(pred, obs, err):
    if not np.isfinite(pred) or not np.isfinite(obs) or not np.isfinite(err) or err <= 0:
        return np.nan
    return (pred - obs) / err



def j2141_score(rotation_target, solver_output, lens_anchor, lens_output, controls):
    vel_redchi2 = reduced_chi2(rotation_target['rotation_velocity_km_s'], solver_output['predicted_velocity_km_s'], rotation_target['error_km_s'])
    re_pull = abs(pull(float(lens_output['predicted_einstein_radius_arcsec'].iloc[0]), float(lens_anchor['einstein_radius_arcsec_central'].iloc[0]), float(lens_anchor['einstein_radius_arcsec_err_plus'].iloc[0])))
    mass_pull = abs(pull(float(lens_output['predicted_lensing_mass_at_observed_re_1e10Msun'].iloc[0]), float(lens_anchor['lensing_mass_1e10Msun_central'].iloc[0]), float(lens_anchor['lensing_mass_1e10Msun_err_plus'].iloc[0])))
    eta_delta = abs(float(lens_output['predicted_eta'].iloc[0]) - 1.0)
    return pd.DataFrame([
        {'metric':'Velocity reduced chi2','value':vel_redchi2,'threshold':controls['max_reduced_chi2_velocity'],'status':'PASS' if np.isfinite(vel_redchi2) and vel_redchi2 <= controls['max_reduced_chi2_velocity'] else 'FAIL'},
        {'metric':'Einstein radius pull (sigma)','value':re_pull,'threshold':controls['max_abs_lensing_radius_pull_sigma'],'status':'PASS' if np.isfinite(re_pull) and re_pull <= controls['max_abs_lensing_radius_pull_sigma'] else 'FAIL'},
        {'metric':'Lensing mass pull (sigma)','value':mass_pull,'threshold':controls['max_abs_lensing_mass_pull_sigma'],'status':'PASS' if np.isfinite(mass_pull) and mass_pull <= controls['max_abs_lensing_mass_pull_sigma'] else 'FAIL'},
        {'metric':'|eta - 1|','value':eta_delta,'threshold':controls['max_abs_eta_minus_1'],'status':'PASS' if np.isfinite(eta_delta) and eta_delta <= controls['max_abs_eta_minus_1'] else 'FAIL'},
        {'metric':'SWELLS IV posterior mean abs pull','value':np.nan,'threshold':np.nan,'status':'MANUAL_REVIEW'},
    ])



def seta_lens_score(row: pd.Series, radius_sigma: float = 2.0, mass_sigma: float = 2.0) -> dict:
    re_pull = float(row['einstein_radius_pull_sigma'])
    mass_pull = float(row['mass_pull_sigma'])
    radius_pass = bool(abs(re_pull) <= radius_sigma)
    mass_pass = bool(abs(mass_pull) <= mass_sigma)
    return {
        'lens_id': row['lens_id'],
        'einstein_radius_pull_sigma': re_pull,
        'mass_pull_sigma': mass_pull,
        'radius_pass_abs_le_2sigma': radius_pass,
        'mass_pass_abs_le_2sigma': mass_pass,
        'both_pass': bool(radius_pass and mass_pass),
    }



def seta_suite_score(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame([{'metric': 'n_lenses_tested', 'value': 0}])
    both = df['both_pass'].astype(bool)
    radius = df['radius_pass_abs_le_2sigma'].astype(bool)
    mass = df['mass_pass_abs_le_2sigma'].astype(bool)
    failed = ';'.join(df.loc[~both, 'lens_id'].astype(str).tolist())
    return pd.DataFrame([
        {'metric': 'n_lenses_tested', 'value': int(len(df))},
        {'metric': 'n_both_pass', 'value': int(both.sum())},
        {'metric': 'n_radius_pass', 'value': int(radius.sum())},
        {'metric': 'n_mass_pass', 'value': int(mass.sum())},
        {'metric': 'mean_abs_radius_pull_sigma', 'value': float(np.mean(np.abs(df['einstein_radius_pull_sigma'])))},
        {'metric': 'mean_abs_mass_pull_sigma', 'value': float(np.mean(np.abs(df['mass_pull_sigma'])))},
        {'metric': 'failed_lenses', 'value': failed},
    ])



def compare_suite_scores(candidate: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    merged = candidate.merge(baseline, on='metric', how='outer', suffixes=('_candidate', '_baseline'))
    return merged
