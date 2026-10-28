from __future__ import annotations

import argparse
import json
from pathlib import Path

from .run_j2141_axisym_lens import run as run_j2141_axisym
from .run_setA_port_cand import run as run_candidate
from .run_ra0_local_robust import run as run_local_robustness


def _load_json(path: Path):
    return json.loads(path.read_text())


def run(pack_root: str, out_dir: str, *, candidate_name: str = 'ra0_gated_geometry_sigmoid_reg_v2', robust_trials: int = 200, robust_width: float = 0.05, robust_seed: int = 2141):
    pack_root_p = Path(pack_root).resolve()
    out_dir_p = Path(out_dir).resolve()
    out_dir_p.mkdir(parents=True, exist_ok=True)

    j2141_summary = run_j2141_axisym(
        config_path=str(pack_root_p / 'configs' / 'j2141_test1_axisy_1689e9.json'),
        pack_root=str(pack_root_p),
        strict_regression=True,
    )
    compact_csv = out_dir_p / 'compact_power_v1.csv'
    compact_json = out_dir_p / 'compact_power_v1_summary.json'
    run_candidate(str(pack_root_p), str(compact_csv), out_json=str(compact_json), candidate_name='compact_power_v1')

    v1_csv = out_dir_p / 'ra0_gated_geometry_sigmoid_v1.csv'
    v1_json = out_dir_p / 'ra0_gated_geometry_sigmoid_v1_summary.json'
    run_candidate(str(pack_root_p), str(v1_csv), out_json=str(v1_json), candidate_name='ra0_gated_geometry_sigmoid_v1')

    reg_csv = out_dir_p / f'{candidate_name}.csv'
    reg_json = out_dir_p / f'{candidate_name}_summary.json'
    run_candidate(str(pack_root_p), str(reg_csv), out_json=str(reg_json), candidate_name=candidate_name)

    robust_csv = out_dir_p / f'{candidate_name}_local_robustness.csv'
    robust_json = out_dir_p / f'{candidate_name}_local_robustness_summary.json'
    run_local_robustness(str(pack_root_p), str(robust_csv), out_json=str(robust_json), candidate_name=candidate_name, n_trials=int(robust_trials), rel_width=float(robust_width), seed=int(robust_seed))

    summary = {
        'j2141_strict_regression': j2141_summary,
        'compact_power_v1': _load_json(compact_json),
        'ra0_gated_geometry_sigmoid_v1': _load_json(v1_json),
        candidate_name: _load_json(reg_json),
        f'{candidate_name}_local_robustness': _load_json(robust_json),
        'paths': {
            'out_dir': str(out_dir_p),
            'compact_csv': str(compact_csv),
            'v1_csv': str(v1_csv),
            'regularized_csv': str(reg_csv),
            'robust_csv': str(robust_csv),
        },
    }
    (out_dir_p / 'v7_regression_suite_summary.json').write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-root', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--candidate-name', default='ra0_gated_geometry_sigmoid_reg_v2')
    parser.add_argument('--robust-trials', type=int, default=200)
    parser.add_argument('--robust-width', type=float, default=0.05)
    parser.add_argument('--robust-seed', type=int, default=2141)
    args = parser.parse_args()
    summary = run(args.pack_root, args.out_dir, candidate_name=args.candidate_name, robust_trials=args.robust_trials, robust_width=args.robust_width, robust_seed=args.robust_seed)
    print(json.dumps(summary, indent=2))
