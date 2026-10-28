from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .baryons import J2141BaryonicModel
from .cosmology import FlatLCDM
from .dmalane import build_gate_components, epsilon_from_config
from .gate_struct import A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values
from .io_utils import build_run_manifest, ensure_dir, save_json, write_manifest
from .run_j2141_axisym_lens import (
    apply_shadow_projection_mode,
    hernquist_density,
    projected_disk_mass_exponential,
    solve_einstein_radius_projected,
)
from .scoring import seta_suite_score
from .shadow_density import compute_shadow_density



def _trapz_weights(x):
    x = np.asarray(x, dtype=float)
    dx = np.diff(x)
    w = np.zeros_like(x)
    w[0] = dx[0] / 2.0
    w[-1] = dx[-1] / 2.0
    w[1:-1] = (dx[:-1] + dx[1:]) / 2.0
    return w



def _projection_matrix(r):
    r = np.asarray(r, dtype=float)
    w = _trapz_weights(r)
    R = r[:, None]
    rr = r[None, :]
    inside = np.where(rr <= R, rr**2, 0.0)
    outside = np.where(rr > R, rr * (rr - np.sqrt(np.clip(rr**2 - R**2, 0.0, None))), 0.0)
    return 4.0 * np.pi * (inside + outside) * w[None, :]



def _resolve_scale_table(pack_root: Path) -> pd.DataFrame:
    local_candidates = [
        pack_root / 'cleaned' / 'setA_scale_kpc_per_arcsec.csv',
        pack_root / 'cleaned' / 'setA_struct_full.csv',
    ]
    for candidate in local_candidates:
        if candidate.exists():
            df = pd.read_csv(candidate)
            required = {'lens_id', 'scale_kpc_per_arcsec'}
            if not required.issubset(df.columns):
                raise ValueError(f'Scale support file missing required columns {required}: {candidate}')
            return df[['lens_id', 'scale_kpc_per_arcsec']].drop_duplicates()

    for parent in [pack_root, *pack_root.parents]:
        candidate = parent / '12_conv_art' / 'setA_struct_full.csv'
        if candidate.exists():
            df = pd.read_csv(candidate)
            return df[['lens_id', 'scale_kpc_per_arcsec']].drop_duplicates()

    raise FileNotFoundError(
        'Could not resolve Set A scale support table. Expected either '
        f"{pack_root / 'cleaned' / 'setA_scale_kpc_per_arcsec.csv'} or an ancestor 12_conv_art/setA_struct_full.csv"
    )


def _load_tables(pack_root: Path):
    seta = pd.read_csv(pack_root / 'cleaned' / 'lens_set_A_run_fo_74bb5e.csv')
    struct = pd.read_csv(pack_root / 'raw_support' / 'swells3_table3_structure.csv')
    struct['lens_id'] = struct['lens_id_norm']
    scales = _resolve_scale_table(pack_root)
    seta = seta.merge(struct[['lens_id', 'q_bulge', 'q_disc']], on='lens_id', how='left').merge(scales, on='lens_id', how='left')
    return seta



def _build_anchor(pack_root: Path):
    cfg = json.loads((pack_root / 'configs' / 'j2141_test1_axisy_1689e9.json').read_text())
    bo = cfg['j2141_model']['baryon_override']
    mod = J2141BaryonicModel(bo['bulge_mass_msun'], bo['bulge_re_kpc'], bo['disk_mass_msun'], bo['disk_r50_kpc'])
    anchor_features = extract_gate_features_from_values(
        bo['bulge_mass_msun'],
        bo['bulge_re_kpc'],
        bo['disk_mass_msun'],
        bo['disk_r50_kpc'],
        bo['bulge_axis_ratio_q'],
        bo['disk_axis_ratio_q'],
        ra0_kpc=compute_transition_radius_kpc(mod, a0_mps2=A0_MPS2),
    )
    anchor_features.update({
        'r0_kpc': float(cfg['gate']['r0_kpc']),
        'delta_epsilon': float(cfg['gate']['delta_epsilon']),
        'n': float(cfg['gate']['n']),
    })
    return anchor_features, cfg



BEST_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS = {
    'ra0_power': 0.974370971032392,
    'baseline_r0_exponents': {'diskiness': -0.1, 'sigma_compact': 0.2},
    'baseline_delta_exponents': {'sigma_compact': -0.2},
    'w_cd': 0.23032172719339888,
    'w_ratio': 0.5311399556637991,
    'w_qb': 0.12334249200328373,
    'w_qd': 1.394172515292972,
    'contrast_width': 0.6038854207927864,
    'ra0_turn': 1.3554987468752857,
    'ra0_width': 0.09656329472665355,
    'beta_r0': 0.6821754138897426,
    'beta_delta': -0.05468387420019705,
}

REGULARIZED_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS = {
    'ra0_power': 0.966123,
    'baseline_r0_exponents': {'diskiness': -0.1, 'sigma_compact': 0.2},
    'baseline_delta_exponents': {'sigma_compact': -0.2},
    'w_cd': 0.231075,
    'w_ratio': 0.580959,
    'w_qb': 0.115235,
    'w_qd': 1.307183,
    'contrast_width': 0.567322,
    'ra0_turn': 1.376725,
    'ra0_width': 0.094268,
    'beta_r0': 0.724591,
    'beta_delta': -0.058136,
}

WQB_75PCT_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS = {
    **REGULARIZED_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS,
    'w_qb': round(REGULARIZED_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS['w_qb'] * 0.75, 12),
}

DROP_WQB_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS = {
    **REGULARIZED_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS,
    'w_qb': 0.0,
}


def candidate_parameters(candidate_name: str = 'ra0_gated_geometry_sigmoid_v1') -> dict:
    candidate_name = str(candidate_name or 'ra0_gated_geometry_sigmoid_v1').lower()
    if candidate_name in {'portable_gate_map_candidate_v1', 'compact_power_v1', 'compact_power'}:
        return {
            'family': 'compact_power',
            'parameters': {
                'ra0_power': 1.0,
                'r0_exponents': {'diskiness': -0.1, 'sigma_compact': 0.2},
                'delta_exponents': {'sigma_compact': -0.2},
            },
        }
    if candidate_name in {'ra0_gated_geometry_sigmoid_v1', 'ra0_gated_geometry_sigmoid'}:
        return {
            'family': 'ra0_gated_geometry_sigmoid',
            'parameters': dict(BEST_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS),
        }
    if candidate_name in {'ra0_gated_geometry_sigmoid_reg_v2', 'ra0_gated_geometry_sigmoid_regularized_v2', 'ra0_gated_geometry_sigmoid_v2'}:
        return {
            'family': 'ra0_gated_geometry_sigmoid',
            'parameters': dict(REGULARIZED_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS),
        }
    if candidate_name in {'ra0_gated_geometry_sigmoid_reg_v2_wqb_75pct', 'w_qb_75pct', 'qb75', 'reg_v2_wqb_75pct'}:
        return {
            'family': 'ra0_gated_geometry_sigmoid',
            'parameters': dict(WQB_75PCT_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS),
        }
    if candidate_name in {'ra0_gated_geometry_sigmoid_reg_v3_drop_wqb', 'drop_wqb', 'dropwqb', 'reg_v3_drop_wqb'}:
        return {
            'family': 'ra0_gated_geometry_sigmoid',
            'parameters': dict(DROP_WQB_RA0_GATED_GEOMETRY_SIGMOID_PARAMETERS),
        }
    raise ValueError(f'Unsupported candidate_name: {candidate_name}')


def _candidate_gate_config(anchor: dict, candidate_name: str = 'ra0_gated_geometry_sigmoid_v1'):
    charge = candidate_parameters(candidate_name)
    return {
        'mode': 'radius_proxy',
        'delta_epsilon': float(anchor['delta_epsilon']),
        'r0_kpc': float(anchor['r0_kpc']),
        'n': float(anchor['n']),
        'epsilon_floor': 0.05,
        'structure': {'family': 'anchor_fixed', 'parameters': {}},
        'charge': charge,
        'local_cutoff': {'family': 'none', 'parameters': {}},
        'shadow_density': {'method': 'mass_difference_gradient'},
        'legacy_compat': {
            'delta_epsilon': float(anchor['delta_epsilon']),
            'r0_kpc': float(anchor['r0_kpc']),
            'n': float(anchor['n']),
            'epsilon_floor': 0.05,
        },
    }



def evaluate_portability_dataframe(pack_root: Path, gate_config: dict, *, gate_label: str = 'portable_gate_map_candidate_v1') -> pd.DataFrame:
    seta = _load_tables(pack_root)
    anchor, _ = _build_anchor(pack_root)
    cosmo = FlatLCDM(70.0, 0.3)
    r = np.linspace(0.02, 120.0, 180)
    K = _projection_matrix(r)

    rows = []
    for _, row in seta.iterrows():
        bmass = 10**row['logM_bulge_chabrier_central']
        dmass = 10**row['logM_disc_chabrier_central']
        bre = row['Re_bulge_arcsec'] * row['scale_kpc_per_arcsec']
        dr50 = row['Re_disc_arcsec'] * row['scale_kpc_per_arcsec']
        q_b = float(row['q_bulge'])
        q_d = float(row['q_disc'])
        mod = J2141BaryonicModel(bmass, bre, dmass, dr50)
        features = extract_gate_features_from_values(bmass, bre, dmass, dr50, q_b, q_d, ra0_kpc=compute_transition_radius_kpc(mod, a0_mps2=A0_MPS2))

        vbar = mod.total_vbar(r)
        gbar_k = vbar**2 / r
        gate_components = build_gate_components(gate_config, features=features, anchor=anchor)
        eps = epsilon_from_config(r, gbar_k, gate_config, features=features, anchor=anchor)
        gtot = gbar_k / eps
        rho_shadow = compute_shadow_density(r, gbar_k, gtot, epsilon=eps, method=gate_components.get('shadow_density_method', 'mass_difference_gradient'))

        bulge_rho = hernquist_density(r, bmass, bre / 1.8153)
        bulge_proj = K.dot(bulge_rho)
        disk_proj = np.array([projected_disk_mass_exponential(R, dmass, dr50 / 1.67835, q_d, ntheta=120) for R in r])
        shadow_proj_s = K.dot(np.nan_to_num(rho_shadow, nan=0.0))
        lens_cfg = {'shadow_projection': 'baryon_structure_circularized', 'disk_axis_ratio_q': q_d, 'bulge_axis_ratio_q': q_b}
        shadow_proj = apply_shadow_projection_mode(r, shadow_proj_s, lens_cfg, bulge_proj, disk_proj, dict(lens_cfg))
        proj_total = bulge_proj + disk_proj + shadow_proj

        sigma_crit = cosmo.sigma_crit_msun_per_kpc2(float(row['z_deflector']), float(row['z_source']))
        pred_re_kpc = solve_einstein_radius_projected(r, proj_total, sigma_crit)
        pred_re_arc = pred_re_kpc / row['scale_kpc_per_arcsec']
        obs_re_arc = float(row['einstein_radius_arcsec_central'])
        re_pull = (pred_re_arc - obs_re_arc) / float(row['einstein_radius_arcsec_err_plus'])
        obs_re_kpc = obs_re_arc * row['scale_kpc_per_arcsec']
        pred_mass = np.interp(obs_re_kpc, r, proj_total) / 1.0e10
        mass_pull = (pred_mass - float(row['lensing_mass_1e10Msun_central'])) / float(row['lensing_mass_1e10Msun_err_plus'])

        rows.append({
            'lens_id': row['lens_id'],
            'gate_label': gate_label,
            'ra0_kpc': features['ra0_kpc'],
            'diskiness': features['diskiness'],
            'sigma_compact': features['sigma_compact'],
            'sigma_bulge': features['sigma_bulge'],
            'compact_disk': features['compact_disk'],
            'ratio_bre_dr50': features['ratio_bre_dr50'],
            'q_b': q_b,
            'q_d': q_d,
            'fbulge': features['fbulge'],
            'derived_r0_kpc': gate_components['r0_kpc'],
            'derived_delta_epsilon': gate_components['delta_epsilon'],
            'predicted_einstein_radius_arcsec': pred_re_arc,
            'observed_einstein_radius_arcsec': obs_re_arc,
            'einstein_radius_pull_sigma': re_pull,
            'predicted_mass_at_obs_re_1e10Msun': pred_mass,
            'observed_mass_at_obs_re_1e10Msun': float(row['lensing_mass_1e10Msun_central']),
            'mass_pull_sigma': mass_pull,
            'radius_pass_abs_le_2sigma': abs(re_pull) <= 2.0,
            'mass_pass_abs_le_2sigma': abs(mass_pull) <= 2.0,
            'both_pass': abs(re_pull) <= 2.0 and abs(mass_pull) <= 2.0,
        })
    return pd.DataFrame(rows)



def summarize_portability(df: pd.DataFrame, anchor: dict, gate_config: dict, *, candidate_name: str):
    suite = seta_suite_score(df)
    charge_family = gate_config.get('charge', {}).get('family', 'compact_power')
    if charge_family == 'ra0_gated_geometry_sigmoid':
        formula = {
            'baseline_r0_scale': '(ra0/ra0_J2141)^a * (D/D_J2141)^(-0.1) * (Sigma_compact/Sigma_compact_J2141)^(0.2)',
            'baseline_delta_scale': '(Sigma_compact/Sigma_compact_J2141)^(-0.2)',
            'geometry_contrast': 'w_cd ln(compact_disk/compact_disk_J2141) + w_ratio ln((Re_bulge/Re_disc)/(...)_J2141) + w_qb ln(q_b/q_b,J2141) - w_qd ln(q_d/q_d,J2141)',
            'high_ra_gate': 'sigmoid((ln(ra0/ra0_J2141) - t)/s)',
            'correction': 'high_ra_gate * tanh(geometry_contrast / c)',
            'r0_scale': 'baseline_r0_scale * exp(beta_r0 * correction)',
            'delta_scale': 'baseline_delta_scale * exp(beta_delta * correction)',
            'definitions': {
                'ra0': 'radius where baryonic acceleration g_bar(r) crosses a0 = 1.1e-10 m s^-2',
                'D': 'global diskiness = f_disk * (1 - q_disk)',
                'Sigma_compact': 'total stellar mass / (2*pi*R_e,bulge^2)',
            },
        }
    else:
        formula = {
            'r0_kpc': 'r0_J2141 * (r_a0 / r_a0_J2141) * (D / D_J2141)^(-0.1) * (Sigma_compact / Sigma_compact_J2141)^(0.2)',
            'delta_epsilon': 'clip(delta_J2141 * (Sigma_compact / Sigma_compact_J2141)^(-0.2), 0.05, 0.95)',
            'definitions': {
                'r_a0': 'radius where baryonic acceleration g_bar(r) crosses a0 = 1.1e-10 m s^-2',
                'D': 'global diskiness = f_disk * (1 - q_disk)',
                'Sigma_compact': 'total stellar mass / (2*pi*R_e,bulge^2)',
            },
        }
    summary = {
        'candidate_name': candidate_name,
        'formula': formula,
        'anchor': {
            'J2141_r0_kpc': anchor['r0_kpc'],
            'J2141_delta_epsilon': anchor['delta_epsilon'],
            'J2141_r_a0_kpc': anchor['ra0_kpc'],
            'J2141_diskiness': anchor['diskiness'],
            'J2141_sigma_compact_Msun_per_kpc2': anchor['sigma_compact'],
        },
        'gate_config': gate_config,
        'results': {row['metric']: row['value'] for _, row in suite.iterrows()},
    }
    summary['results']['failed_lenses'] = df.loc[~df['both_pass'], 'lens_id'].tolist()
    return summary



def run(pack_root: str, out_csv: str, out_json: str | None = None, *, candidate_name: str = 'ra0_gated_geometry_sigmoid_v1'):
    pack_root = Path(pack_root).resolve()
    out_csv = Path(out_csv)
    anchor, _ = _build_anchor(pack_root)
    gate_config = _candidate_gate_config(anchor, candidate_name=candidate_name)
    df = evaluate_portability_dataframe(pack_root, gate_config, gate_label=candidate_name)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    if out_json is not None:
        summary = summarize_portability(df, anchor, gate_config, candidate_name=candidate_name)
        save_json(summary, out_json)
    return df



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-root', required=True)
    parser.add_argument('--out-csv', required=True)
    parser.add_argument('--out-json')
    parser.add_argument('--candidate-name', default='ra0_gated_geometry_sigmoid_v1')
    args = parser.parse_args()
    df = run(args.pack_root, args.out_csv, out_json=args.out_json, candidate_name=args.candidate_name)
    print(df.to_string(index=False))
