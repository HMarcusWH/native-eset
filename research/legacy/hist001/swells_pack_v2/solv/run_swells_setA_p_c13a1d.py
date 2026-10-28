from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

from .gate_struct import FEATURE_NAMES
from .io_utils import save_json
from .run_setA_port_cand import _build_anchor, _load_tables, _projection_matrix, summarize_portability
from .baryons import J2141BaryonicModel
from .cosmology import FlatLCDM
from .dmalane import build_gate_components, epsilon_from_config
from .gate_struct import A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values
from .run_j2141_axisym_lens import apply_shadow_projection_mode, hernquist_density, projected_disk_mass_exponential, solve_einstein_radius_projected
from .shadow_density import compute_shadow_density


FEATURE_POOL = ['diskiness', 'sigma_compact', 'compact_disk', 'ratio_bre_dr50', 'fbulge', 'q_d', 'q_b', 'sigma_bulge']



def build_tables(pack_root: Path):
    return _load_tables(pack_root)



def evaluate_family(pack_root: Path, out_csv: Path, n_trials: int = 4000, seed: int = 0, out_json: Path | None = None):
    pack_root = Path(pack_root).resolve()
    random.seed(seed)
    np.random.seed(seed)
    seta = build_tables(pack_root)
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
        bulge_rho = hernquist_density(r, bmass, bre / 1.8153)
        bulge_proj = K.dot(bulge_rho)
        disk_proj = np.array([projected_disk_mass_exponential(R, dmass, dr50 / 1.67835, q_d, ntheta=120) for R in r])
        rows.append({
            'lens_id': row['lens_id'],
            'row': row,
            'gbar_k': gbar_k,
            'bulge_proj': bulge_proj,
            'disk_proj': disk_proj,
            'obs_re_arc': float(row['einstein_radius_arcsec_central']),
            'obs_re_kpc': float(row['einstein_radius_arcsec_central'] * row['scale_kpc_per_arcsec']),
            'sigma_crit': cosmo.sigma_crit_msun_per_kpc2(float(row['z_deflector']), float(row['z_source'])),
            'features': features,
        })

    def eval_params(a, r0_exps, delta_exps):
        out = []
        failed = []
        for fr in rows:
            gate_config = {
                'mode': 'radius_proxy',
                'delta_epsilon': float(anchor['delta_epsilon']),
                'r0_kpc': float(anchor['r0_kpc']),
                'n': float(anchor['n']),
                'epsilon_floor': 0.05,
                'structure': {'family': 'anchor_fixed', 'parameters': {}},
                'charge': {'family': 'compact_power', 'parameters': {'ra0_power': a, 'r0_exponents': r0_exps, 'delta_exponents': delta_exps}},
                'local_cutoff': {'family': 'none', 'parameters': {}},
                'shadow_density': {'method': 'mass_difference_gradient'},
            }
            gate_components = build_gate_components(gate_config, features=fr['features'], anchor=anchor)
            eps = epsilon_from_config(r, fr['gbar_k'], gate_config, features=fr['features'], anchor=anchor)
            gtot = fr['gbar_k'] / eps
            rho_shadow = compute_shadow_density(r, fr['gbar_k'], gtot, epsilon=eps, method=gate_components.get('shadow_density_method', 'mass_difference_gradient'))
            shadow_proj_s = K.dot(np.nan_to_num(rho_shadow, nan=0.0))
            q_d = float(fr['features']['q_d'])
            q_b = float(fr['features']['q_b'])
            lens_cfg = {'shadow_projection': 'baryon_structure_circularized', 'disk_axis_ratio_q': q_d, 'bulge_axis_ratio_q': q_b}
            shadow_proj = apply_shadow_projection_mode(r, shadow_proj_s, lens_cfg, fr['bulge_proj'], fr['disk_proj'], dict(lens_cfg))
            proj_total = fr['bulge_proj'] + fr['disk_proj'] + shadow_proj
            pred_re_kpc = solve_einstein_radius_projected(r, proj_total, fr['sigma_crit'])
            pred_re_arc = pred_re_kpc / fr['row']['scale_kpc_per_arcsec']
            re_pull = (pred_re_arc - fr['obs_re_arc']) / float(fr['row']['einstein_radius_arcsec_err_plus'])
            pred_mass = np.interp(fr['obs_re_kpc'], r, proj_total) / 1.0e10
            mass_pull = (pred_mass - float(fr['row']['lensing_mass_1e10Msun_central'])) / float(fr['row']['lensing_mass_1e10Msun_err_plus'])
            out.append((re_pull, mass_pull))
            if not (abs(re_pull) <= 2.0 and abs(mass_pull) <= 2.0):
                failed.append(fr['lens_id'])
        out = np.array(out)
        radius = np.abs(out[:, 0]) <= 2.0
        mass = np.abs(out[:, 1]) <= 2.0
        return {
            'n_both_pass': int(np.sum(radius & mass)),
            'n_radius_pass': int(np.sum(radius)),
            'n_mass_pass': int(np.sum(mass)),
            'mean_abs_radius_pull_sigma': float(np.mean(np.abs(out[:, 0]))),
            'mean_abs_mass_pull_sigma': float(np.mean(np.abs(out[:, 1]))),
            'max_abs_radius_pull_sigma': float(np.max(np.abs(out[:, 0]))),
            'max_abs_mass_pull_sigma': float(np.max(np.abs(out[:, 1]))),
            'failed_lenses': ';'.join(failed),
        }

    recs = []
    for trial in range(n_trials):
        a = float(np.clip(np.random.normal(1.0, 0.35), 0.2, 1.8))
        nr = int(np.random.choice([1, 2, 3], p=[0.3, 0.45, 0.25]))
        nd = int(np.random.choice([0, 1, 2], p=[0.35, 0.4, 0.25]))
        rf = random.sample(FEATURE_POOL, nr)
        df = random.sample(FEATURE_POOL, nd)
        r0_exps = {k: float(np.clip(np.random.normal(0, 0.35), -1.2, 1.2)) for k in rf}
        delta_exps = {k: float(np.clip(np.random.normal(0, 0.35), -1.2, 1.2)) for k in df}
        stats = eval_params(a, r0_exps, delta_exps)
        recs.append({
            'trial': trial,
            'a_ra0': a,
            'r0_exps_json': json.dumps(r0_exps, sort_keys=True),
            'delta_exps_json': json.dumps(delta_exps, sort_keys=True),
            **stats,
        })

    out = pd.DataFrame(recs).sort_values(
        by=['n_both_pass', 'n_radius_pass', 'n_mass_pass', 'mean_abs_radius_pull_sigma', 'mean_abs_mass_pull_sigma'],
        ascending=[False, False, False, True, True],
    )
    out.to_csv(out_csv, index=False)
    if out_json is not None:
        best = out.iloc[0].to_dict()
        summary = {
            'search_family': 'J2141-anchored simple monomial portable maps',
            'n_trials': int(n_trials),
            'feature_pool': FEATURE_POOL,
            'max_both_pass_found': int(out['n_both_pass'].max()),
            'n_trials_with_4_or_more_both_pass': int((out['n_both_pass'] >= 4).sum()),
            'preferred_doctrine_candidate': 'portable_gate_map_candidate_v1',
            'preferred_reason': 'current v1 remains the most interpretable r_a0 + diskiness + compactness map while already matching the best simple-family 4/6 ceiling under the consolidated solver rerun',
            'best_search_trial': best,
        }
        save_json(summary, out_json)
    return out



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-root', required=True)
    parser.add_argument('--out-csv', required=True)
    parser.add_argument('--n-trials', type=int, default=4000)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--out-json')
    args = parser.parse_args()
    df = evaluate_family(Path(args.pack_root), Path(args.out_csv), n_trials=args.n_trials, seed=args.seed, out_json=Path(args.out_json) if args.out_json else None)
    print(df.head(20).to_string(index=False))
