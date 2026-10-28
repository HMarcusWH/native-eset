from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .baryons import J2141BaryonicModel, parse_pm_string
from .cosmology import FlatLCDM
from .dmalane import epsilon_rar_shell, compute_shadow_density, cumulative_potential, solve_einstein_radius
from .io_utils import load_json, read_csv, write_csv, save_json
from .constants import G_KPC_KMS2_MSUN
from .scoring import j2141_score

def build_model(config, pack_root: Path):
    t2 = read_csv(pack_root / 'raw_support' / 'swells2_table2_bu_c249ce.csv')
    scale = config['j2141_model']['scale_kpc_per_arcsec']
    bulge = t2[t2['component'].str.lower() == 'bulge'].iloc[0]
    disc = t2[t2['component'].str.lower() == 'disc'].iloc[0]
    bmass = 10**parse_pm_string(bulge['log10_Mstar_chabrier'])[0]
    dmass = 10**parse_pm_string(disc['log10_Mstar_chabrier'])[0]
    bre = parse_pm_string(bulge['R50_arcsec'])[0] * scale
    dr50 = parse_pm_string(disc['R50_arcsec'])[0] * scale
    return J2141BaryonicModel(bmass, bre, dmass, dr50), {'bulge_mass_msun': bmass, 'disk_mass_msun': dmass, 'bulge_re_kpc': bre, 'disk_r50_kpc': dr50}

def run(config_path: str, pack_root: str):
    pack_root = Path(pack_root)
    config = load_json(config_path)
    manifest = load_json(pack_root / 'templates' / 'j2141_run_manifest.json')
    rot = read_csv(pack_root / manifest['source_files']['rotation_curve'])
    anchor = read_csv(pack_root / manifest['source_files']['lensing_anchor'])
    model, model_meta = build_model(config, pack_root)
    r = rot['radius_kpc'].to_numpy(dtype=float)
    vbar = model.total_vbar(r)
    gbar = np.divide(vbar**2, r, out=np.zeros_like(r, dtype=float), where=r > 0)
    eps = epsilon_rar_shell(gbar, config['gate']['g_dagger_m_s2'], config['gate']['epsilon_floor'])
    gtot = np.where(r > 0, gbar / eps, 0.0)
    vtot = np.sqrt(np.clip(gtot * r, 0.0, None))
    rho_shadow = compute_shadow_density(r, gbar, gtot)
    phi = cumulative_potential(r, gtot)
    solver_out = pd.DataFrame({'radius_kpc': r, 'predicted_velocity_km_s': np.round(vtot, 6), 'epsilon': np.round(eps, 8), 'rho_shadow_Msun_per_kpc3': np.round(rho_shadow, 6), 'phi': np.round(phi, 6), 'psi': np.round(phi, 6)})

    r_dense = np.linspace(0.05, max(20.0, float(r.max()) * 1.5), 2000)
    vbar_dense = model.total_vbar(r_dense)
    gbar_dense = vbar_dense**2 / r_dense
    eps_dense = epsilon_rar_shell(gbar_dense, config['gate']['g_dagger_m_s2'], config['gate']['epsilon_floor'])
    gtot_dense = gbar_dense / eps_dense
    meff_dense = gtot_dense * r_dense**2 / G_KPC_KMS2_MSUN

    cosmo = FlatLCDM(**config['cosmology'])
    sigma_crit = cosmo.sigma_crit_msun_per_kpc2(float(anchor['z_deflector'].iloc[0]), float(anchor['z_source'].iloc[0]))
    re_obs_arcsec = float(anchor['einstein_radius_arcsec_central'].iloc[0])
    scale = config['j2141_model']['scale_kpc_per_arcsec']
    re_obs_kpc = re_obs_arcsec * scale
    pred_re_kpc = solve_einstein_radius(r_dense, meff_dense, sigma_crit)
    lens_out = pd.DataFrame([{
        'lens_id': 'J2141-0001',
        'predicted_einstein_radius_arcsec': round(float(pred_re_kpc / scale), 6),
        'predicted_lensing_mass_1e10Msun': round(float(np.interp(pred_re_kpc, r_dense, meff_dense) / 1.0e10), 6),
        'predicted_lensing_mass_at_observed_re_1e10Msun': round(float(np.interp(re_obs_kpc, r_dense, meff_dense) / 1.0e10), 6),
        'predicted_eta': 1.0,
        'predicted_v_vir_km_s': round(float(vtot.max()), 6),
        'predicted_gamma': np.nan,
        'predicted_c_minus2': np.nan,
        'predicted_q_h': 1.0,
        'predicted_Mstar_1e11Msun': round((model_meta['bulge_mass_msun'] + model_meta['disk_mass_msun']) / 1.0e11, 6),
        'predicted_b': np.nan,
    }])

    outdir = pack_root / 'res' / 'example_j21_be122d'
    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(solver_out, outdir / 'j2141_solver_output_filled.csv')
    write_csv(lens_out, outdir / 'j2141_lensing_output_filled.csv')
    score = j2141_score(rot, solver_out, anchor, lens_out, manifest['control_thresholds_default'])
    write_csv(score, outdir / 'j2141_acceptance_scoreboard_filled.csv')
    summary = {'branch_id': config['branch_id'], 'model_meta': model_meta, 'metrics': {'velocity_reduced_chi2': float(score.loc[score['metric']=='Velocity reduced chi2','value'].iloc[0]), 'einstein_radius_pull_sigma': float(score.loc[score['metric']=='Einstein radius pull (sigma)','value'].iloc[0]), 'lensing_mass_pull_sigma': float(score.loc[score['metric']=='Lensing mass pull (sigma)','value'].iloc[0]), 'abs_eta_minus_1': float(score.loc[score['metric']=='|eta - 1|','value'].iloc[0])}, 'notes': ['Conservative scaffold only.', 'Uses SWELLS II Table 2 baryonic proxy.', 'Uses the same-branch no-slip assumption.']}
    save_json(summary, outdir / 'j2141_run_summary.json')
    return summary

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--pack-root', required=True)
    args = parser.parse_args()
    summary = run(args.config, args.pack_root)
    print(json.dumps(summary, indent=2))
