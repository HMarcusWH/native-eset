from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .baryons import J2141BaryonicModel, parse_pm_string
from .cosmology import FlatLCDM
from .dmalane import build_gate_components, cumulative_potential, epsilon_from_config
from .gate_struct import compute_transition_radius_kpc, extract_gate_features_from_values
from .io_utils import build_run_manifest, ensure_dir, load_json, read_csv, save_json, write_csv, write_manifest
from .scoring import j2141_score
from .shadow_density import compute_shadow_density
from .constants import G_KPC_KMS2_MSUN


def build_model(config, pack_root: Path):
    model_cfg = config['j2141_model']
    override = model_cfg.get('baryon_override')
    if override:
        bmass = float(override['bulge_mass_msun'])
        dmass = float(override['disk_mass_msun'])
        bre = float(override['bulge_re_kpc'])
        dr50 = float(override['disk_r50_kpc'])
        dq = float(override.get('disk_axis_ratio_q', model_cfg.get('disk_axis_ratio_q', 0.31)))
        bq = float(override.get('bulge_axis_ratio_q', model_cfg.get('bulge_axis_ratio_q', 1.0)))
    else:
        t2 = read_csv(pack_root / 'raw_support' / 'swells2_table2_bu_c249ce.csv')
        scale = model_cfg['scale_kpc_per_arcsec']
        bulge = t2[t2['component'].str.lower() == 'bulge'].iloc[0]
        disc = t2[t2['component'].str.lower() == 'disc'].iloc[0]
        bmass = 10**parse_pm_string(bulge['log10_Mstar_chabrier'])[0]
        dmass = 10**parse_pm_string(disc['log10_Mstar_chabrier'])[0]
        bre = parse_pm_string(bulge['R50_arcsec'])[0] * scale
        dr50 = parse_pm_string(disc['R50_arcsec'])[0] * scale
        dq = parse_pm_string(disc['q'])[0]
        bq = parse_pm_string(bulge['q'])[0]
    model = J2141BaryonicModel(bmass, bre, dmass, dr50)
    meta = {
        'bulge_mass_msun': bmass,
        'disk_mass_msun': dmass,
        'bulge_re_kpc': bre,
        'disk_r50_kpc': dr50,
        'disk_axis_ratio_q': dq,
        'bulge_axis_ratio_q': bq,
        'baryon_source': 'override' if override else 'swells2_table2_chabrier'
    }
    return model, meta



def solve_einstein_radius_projected(r_grid_kpc, projected_mass_msun, sigma_crit):
    target = np.pi * r_grid_kpc**2 * sigma_crit
    vals = projected_mass_msun - target
    sign = np.sign(vals)
    idx = np.where(np.diff(sign))[0]
    if idx.size == 0:
        return float(r_grid_kpc[int(np.argmin(np.abs(vals)))])
    i = int(idx[0])
    x0, x1 = float(r_grid_kpc[i]), float(r_grid_kpc[i+1])
    y0, y1 = float(vals[i]), float(vals[i+1])
    return float(x0 - y0 * (x1 - x0) / (y1 - y0))



def hernquist_density(r_kpc, total_mass_msun, scale_kpc):
    r = np.asarray(r_kpc, dtype=float)
    a = float(scale_kpc)
    with np.errstate(divide='ignore', invalid='ignore'):
        rho = total_mass_msun * a / (2.0 * np.pi * np.clip(r, 1e-12, None) * (r + a)**3)
    return rho



def spherical_density_projected_mass(R_kpc, r_grid_kpc, rho_grid_msun_per_kpc3):
    r = np.asarray(r_grid_kpc, dtype=float)
    rho = np.asarray(rho_grid_msun_per_kpc3, dtype=float)
    mask = np.isfinite(r) & np.isfinite(rho) & (r > 0)
    r = r[mask]
    rho = rho[mask]
    if r.size == 0:
        return 0.0
    R = float(np.clip(R_kpc, 0.0, r.max()))
    inside = r <= R
    m_inside = 4.0 * np.pi * np.trapezoid(rho[inside] * r[inside]**2, r[inside]) if inside.sum() >= 2 else 0.0
    outside = r > R
    if outside.sum() >= 2:
        rout = r[outside]
        term = rout * (rout - np.sqrt(np.clip(rout**2 - R**2, 0.0, None)))
        m_out = 4.0 * np.pi * np.trapezoid(rho[outside] * term, rout)
    else:
        m_out = 0.0
    return float(m_inside + m_out)



def projected_disk_mass_exponential(R_kpc, disk_mass_msun, disk_scale_kpc, disk_axis_ratio_q, ntheta=720):
    R = float(max(R_kpc, 0.0))
    Md = float(disk_mass_msun)
    Rd = float(disk_scale_kpc)
    q = float(np.clip(disk_axis_ratio_q, 1e-3, 1.0))
    thetas = np.linspace(0.0, 2.0 * np.pi, int(ntheta), endpoint=False)
    a = np.sqrt(np.cos(thetas) ** 2 + np.sin(thetas) ** 2 / q**2)
    x = a * R / Rd
    inner = np.where(a > 0, Rd**2 / a**2 * (1.0 - np.exp(-x) * (1.0 + x)), 0.5 * R**2)
    sigma0 = Md / (2.0 * np.pi * q * Rd**2)
    return float(sigma0 * np.trapezoid(inner, thetas))



def apply_shadow_projection_mode(r_grid_kpc, shadow_proj_spherical_msun, lens_cfg, bulge_proj_msun=None, disk_proj_msun=None, model_meta=None):
    mode = str(lens_cfg.get('shadow_projection', 'spherical_cylindrical')).lower()
    r = np.asarray(r_grid_kpc, dtype=float)
    m = np.asarray(shadow_proj_spherical_msun, dtype=float)
    if mode in {'spherical', 'spherical_cylindrical', 'spherical_proxy'}:
        return m
    if mode in {'radial_concentration_proxy', 'concentrated_projection_proxy'}:
        factor = float(lens_cfg.get('shadow_projection_scale_factor', 1.0))
        factor = float(np.clip(factor, 1e-3, 1.0))
        return np.interp(r / factor, r, m, left=m[0], right=m[-1])
    if mode in {'baryon_structure_circularized', 'structured_baryon_q_circularized', 'qeff_circularized'}:
        if bulge_proj_msun is None or disk_proj_msun is None or model_meta is None:
            raise ValueError('Structured baryon projection requires bulge/disk projected mass arrays and model metadata.')
        bulge_proj = np.asarray(bulge_proj_msun, dtype=float)
        disk_proj = np.asarray(disk_proj_msun, dtype=float)
        q_disk = float(lens_cfg.get('disk_axis_ratio_q', model_meta.get('disk_axis_ratio_q', 1.0)))
        q_bulge = float(lens_cfg.get('bulge_axis_ratio_q', model_meta.get('bulge_axis_ratio_q', 1.0)))
        baryon_proj = np.clip(bulge_proj + disk_proj, 1e-30, None)
        q_eff = np.clip((q_bulge * bulge_proj + q_disk * disk_proj) / baryon_proj, 1e-3, 1.0)
        circularized_factor = np.sqrt(q_eff)
        return np.interp(r / circularized_factor, r, m, left=m[0], right=m[-1])
    raise ValueError(f'Unsupported shadow_projection mode: {mode}')



def _load_regression_baseline(pack_root: Path):
    baseline_path = pack_root / 'validation' / 'j2141_regression_b5afd5.json'
    if baseline_path.exists():
        return load_json(baseline_path)
    return None



def _assert_regression(summary: dict, baseline: dict):
    expected = baseline['metrics']
    tolerances = baseline.get('tolerances', {})
    for key, expected_value in expected.items():
        actual = float(summary['metrics'][key])
        tol = float(tolerances.get(key, 0.0))
        if abs(actual - float(expected_value)) > tol:
            raise RuntimeError(f'Regression failure for {key}: actual={actual} baseline={expected_value} tol={tol}')



def run(config_path: str, pack_root: str, *, strict_regression: bool = False):
    pack_root = Path(pack_root).resolve()
    config = load_json(config_path)
    manifest = load_json(pack_root / 'templates' / 'j2141_run_manifest.json')
    rot = read_csv(pack_root / manifest['source_files']['rotation_curve'])
    anchor = read_csv(pack_root / manifest['source_files']['lensing_anchor'])
    model, model_meta = build_model(config, pack_root)

    anchor_features = extract_gate_features_from_values(
        model_meta['bulge_mass_msun'],
        model_meta['bulge_re_kpc'],
        model_meta['disk_mass_msun'],
        model_meta['disk_r50_kpc'],
        model_meta['bulge_axis_ratio_q'],
        model_meta['disk_axis_ratio_q'],
        ra0_kpc=compute_transition_radius_kpc(model),
    )
    gate_components = build_gate_components(config['gate'], features=anchor_features, anchor=anchor_features)

    r = rot['radius_kpc'].to_numpy(dtype=float)
    vbar = model.total_vbar(r)
    gbar = np.divide(vbar**2, r, out=np.zeros_like(r, dtype=float), where=r > 0)
    eps = epsilon_from_config(r, gbar, config['gate'], features=anchor_features, anchor=anchor_features)
    gtot = np.where(r > 0, gbar / eps, 0.0)
    vtot = np.sqrt(np.clip(gtot * r, 0.0, None))
    rho_shadow = compute_shadow_density(r, gbar, gtot, epsilon=eps, method=gate_components.get('shadow_density_method', 'mass_difference_gradient'))
    phi = cumulative_potential(r, gtot)
    solver_out = pd.DataFrame({
        'radius_kpc': r,
        'predicted_velocity_km_s': np.round(vtot, 6),
        'epsilon': np.round(eps, 8),
        'rho_shadow_Msun_per_kpc3': np.round(rho_shadow, 6),
        'phi': np.round(phi, 6),
        'psi': np.round(phi, 6),
    })

    lens_cfg = config['lensing']
    r_dense = np.linspace(0.01, float(lens_cfg.get('r_dense_max_kpc', 120.0)), int(lens_cfg.get('r_dense_n', 4000)))
    vbar_dense = model.total_vbar(r_dense)
    gbar_dense = vbar_dense**2 / r_dense
    eps_dense = epsilon_from_config(r_dense, gbar_dense, config['gate'], features=anchor_features, anchor=anchor_features)
    gtot_dense = gbar_dense / eps_dense
    meff_spherical_dense = gtot_dense * r_dense**2 / G_KPC_KMS2_MSUN
    rho_shadow_dense = compute_shadow_density(r_dense, gbar_dense, gtot_dense, epsilon=eps_dense, method=gate_components.get('shadow_density_method', 'mass_difference_gradient'))

    bulge_rho_dense = hernquist_density(r_dense, model_meta['bulge_mass_msun'], model.bulge_scale_kpc)
    q_disk = float(lens_cfg.get('disk_axis_ratio_q', model_meta['disk_axis_ratio_q']))

    bulge_proj = np.array([spherical_density_projected_mass(R, r_dense, bulge_rho_dense) for R in r_dense])
    shadow_proj_spherical = np.array([spherical_density_projected_mass(R, r_dense, rho_shadow_dense) for R in r_dense])
    disk_proj = np.array([projected_disk_mass_exponential(R, model_meta['disk_mass_msun'], model.disk_scale_kpc, q_disk) for R in r_dense])
    shadow_proj = apply_shadow_projection_mode(
        r_dense,
        shadow_proj_spherical,
        lens_cfg,
        bulge_proj_msun=bulge_proj,
        disk_proj_msun=disk_proj,
        model_meta=model_meta,
    )
    proj_total = bulge_proj + disk_proj + shadow_proj

    cosmo = FlatLCDM(**config['cosmology'])
    sigma_crit = cosmo.sigma_crit_msun_per_kpc2(float(anchor['z_deflector'].iloc[0]), float(anchor['z_source'].iloc[0]))
    scale = config['j2141_model']['scale_kpc_per_arcsec']
    re_obs_arcsec = float(anchor['einstein_radius_arcsec_central'].iloc[0])
    re_obs_kpc = re_obs_arcsec * scale
    pred_re_kpc = solve_einstein_radius_projected(r_dense, proj_total, sigma_crit)

    mass_at_pred = float(np.interp(pred_re_kpc, r_dense, proj_total))
    mass_at_obs = float(np.interp(re_obs_kpc, r_dense, proj_total))
    bulge_obs = float(np.interp(re_obs_kpc, r_dense, bulge_proj))
    disk_obs = float(np.interp(re_obs_kpc, r_dense, disk_proj))
    shadow_obs = float(np.interp(re_obs_kpc, r_dense, shadow_proj))
    spherical_eff_obs = float(np.interp(re_obs_kpc, r_dense, meff_spherical_dense))

    lens_out = pd.DataFrame([{
        'lens_id': 'J2141-0001',
        'predicted_einstein_radius_arcsec': round(float(pred_re_kpc / scale), 6),
        'predicted_lensing_mass_1e10Msun': round(mass_at_pred / 1.0e10, 6),
        'predicted_lensing_mass_at_observed_re_1e10Msun': round(mass_at_obs / 1.0e10, 6),
        'predicted_eta': 1.0,
        'predicted_v_vir_km_s': round(float(vtot.max()), 6),
        'predicted_gamma': np.nan,
        'predicted_c_minus2': np.nan,
        'predicted_q_h': round(q_disk, 6),
        'predicted_Mstar_1e11Msun': round((model_meta['bulge_mass_msun'] + model_meta['disk_mass_msun']) / 1.0e11, 6),
        'predicted_b': np.nan,
        'projected_bulge_mass_at_observed_re_1e10Msun': round(bulge_obs / 1.0e10, 6),
        'projected_disk_mass_at_observed_re_1e10Msun': round(disk_obs / 1.0e10, 6),
        'projected_shadow_mass_at_observed_re_1e10Msun': round(shadow_obs / 1.0e10, 6),
        'spherical_effective_mass_at_observed_re_1e10Msun': round(spherical_eff_obs / 1.0e10, 6),
    }])

    outdir = ensure_dir(pack_root / 'res' / config.get('results_subdir', 'j2141_axisym_lensing'))
    write_csv(solver_out, outdir / 'j2141_solver_output_filled.csv')
    write_csv(lens_out, outdir / 'j2141_lensing_output_filled.csv')
    score = j2141_score(rot, solver_out, anchor, lens_out, manifest['control_thresholds_default'])
    write_csv(score, outdir / 'j2141_acceptance_scoreboard_filled.csv')

    summary = {
        'branch_id': config['branch_id'],
        'model_meta': model_meta,
        'gate_mode': config['gate'].get('mode', 'rar_shell'),
        'gate_components': gate_components,
        'gate_features': anchor_features,
        'projection_mode': lens_cfg.get('shadow_projection', 'spherical_cylindrical'),
        'metrics': {
            'velocity_reduced_chi2': float(score.loc[score['metric'] == 'Velocity reduced chi2', 'value'].iloc[0]),
            'einstein_radius_pull_sigma': float(score.loc[score['metric'] == 'Einstein radius pull (sigma)', 'value'].iloc[0]),
            'lensing_mass_pull_sigma': float(score.loc[score['metric'] == 'Lensing mass pull (sigma)', 'value'].iloc[0]),
            'abs_eta_minus_1': float(score.loc[score['metric'] == '|eta - 1|', 'value'].iloc[0]),
        },
        'component_masses_at_observed_re_1e10Msun': {
            'bulge_projected': bulge_obs / 1.0e10,
            'disk_projected': disk_obs / 1.0e10,
            'shadow_projected': shadow_obs / 1.0e10,
            'total_projected': mass_at_obs / 1.0e10,
            'spherical_effective_proxy': spherical_eff_obs / 1.0e10,
        },
        'notes': config.get('notes', []),
    }
    save_json(summary, outdir / 'j2141_run_summary.json')
    write_manifest(
        build_run_manifest(
            run_id=config.get('branch_id', 'j2141_axisym_lensing'),
            runner='solver.run_j2141_axisym_lens',
            config=str(config_path),
            notes=['Generated by the modular DM-A gate refactor.'],
            extra={'projection_mode': summary['projection_mode'], 'gate_mode': summary['gate_mode']},
        ),
        outdir / 'run_manifest.json',
    )

    if strict_regression:
        baseline = _load_regression_baseline(pack_root)
        if baseline is None:
            raise RuntimeError('Strict regression requested but no validation/j2141_regression_b5afd5.json file exists.')
        _assert_regression(summary, baseline)
    return summary



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--pack-root', required=True)
    parser.add_argument('--strict-regression', action='store_true')
    args = parser.parse_args()
    summary = run(args.config, args.pack_root, strict_regression=args.strict_regression)
    print(json.dumps(summary, indent=2))
