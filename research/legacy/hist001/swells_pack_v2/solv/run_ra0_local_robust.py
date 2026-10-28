from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .run_setA_port_cand import (
    _build_anchor,
    _candidate_gate_config,
    candidate_parameters,
    evaluate_portability_dataframe,
)
from .scoring import seta_suite_score


def _perturb_parameters(base: dict[str, float], rng: np.random.Generator, rel_width: float) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, value in base.items():
        if isinstance(value, dict):
            out[key] = value
            continue
        width = abs(float(value)) * rel_width
        if width == 0.0:
            width = rel_width
        trial = float(value) + rng.uniform(-width, width)
        if key in {'contrast_width', 'ra0_width'}:
            trial = max(trial, 1e-6)
        out[key] = trial
    return out


def run(pack_root: str, out_csv: str, out_json: str | None = None, *, candidate_name: str = 'ra0_gated_geometry_sigmoid_v1', n_trials: int = 1000, rel_width: float = 0.10, seed: int = 2141):
    pack_root = Path(pack_root).resolve()
    out_csv = Path(out_csv)
    anchor, _ = _build_anchor(pack_root)
    charge = candidate_parameters(candidate_name)
    base = dict(charge['parameters'])
    rng = np.random.default_rng(seed)

    rows: list[dict[str, float | int | str]] = []
    for trial in range(int(n_trials)):
        params = _perturb_parameters(base, rng, float(rel_width))
        gate_config = _candidate_gate_config(anchor, candidate_name=candidate_name)
        gate_config['charge']['parameters'] = params
        df = evaluate_portability_dataframe(pack_root, gate_config, gate_label=f'{candidate_name}_local_{trial:04d}')
        suite = {row['metric']: row['value'] for _, row in seta_suite_score(df).iterrows()}
        rows.append({
            'trial': trial,
            **{k: float(v) for k, v in params.items() if not isinstance(v, dict)},
            'n_lenses_tested': int(suite['n_lenses_tested']),
            'n_both_pass': int(suite['n_both_pass']),
            'n_radius_pass': int(suite['n_radius_pass']),
            'n_mass_pass': int(suite['n_mass_pass']),
            'mean_abs_radius_pull_sigma': float(suite['mean_abs_radius_pull_sigma']),
            'mean_abs_mass_pull_sigma': float(suite['mean_abs_mass_pull_sigma']),
            'failed_lenses': str(suite['failed_lenses']),
        })

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_csv, index=False)

    if out_json is not None:
        summary = {
            'candidate_family': str(candidate_name),
            'n_trials': int(n_trials),
            'rel_width': float(rel_width),
            'seed': int(seed),
            'n_at_6_of_6': int((out_df['n_both_pass'] == 6).sum()),
            'n_at_5_or_more': int((out_df['n_both_pass'] >= 5).sum()),
            'best_trial_by_radius_mass_sum': out_df.assign(score=out_df['mean_abs_radius_pull_sigma'] + out_df['mean_abs_mass_pull_sigma']).sort_values('score').iloc[0].to_dict(),
        }
        Path(out_json).write_text(pd.Series(summary).to_json(indent=2))
    return out_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-root', required=True)
    parser.add_argument('--out-csv', required=True)
    parser.add_argument('--out-json')
    parser.add_argument('--candidate-name', default='ra0_gated_geometry_sigmoid_v1')
    parser.add_argument('--n-trials', type=int, default=1000)
    parser.add_argument('--rel-width', type=float, default=0.10)
    parser.add_argument('--seed', type=int, default=2141)
    args = parser.parse_args()
    df = run(args.pack_root, args.out_csv, out_json=args.out_json, candidate_name=args.candidate_name, n_trials=args.n_trials, rel_width=args.rel_width, seed=args.seed)
    print(df.to_string(index=False))
