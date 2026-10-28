from __future__ import annotations

"""Set A portability diagnostic runner for the frozen J2141 gate and structured projection law."""

import argparse
from pathlib import Path

import pandas as pd

from .io_utils import build_run_manifest, ensure_dir, save_json, write_manifest
from .run_setA_port_cand import _build_anchor, _candidate_gate_config, _load_tables, evaluate_portability_dataframe, summarize_portability



def _embedding_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = {
        'n_lenses_tested': int(len(df)),
        'n_both_pass': int(df['both_pass'].sum()),
        'n_radius_pass': int(df['radius_pass_abs_le_2sigma'].sum()),
        'n_mass_pass': int(df['mass_pass_abs_le_2sigma'].sum()),
        'mean_abs_radius_pull_sigma': float(df['einstein_radius_pull_sigma'].abs().mean()),
        'mean_abs_mass_pull_sigma': float(df['mass_pull_sigma'].abs().mean()),
        'failed_lenses': ';'.join(df.loc[~df['both_pass'], 'lens_id'].astype(str).tolist()),
    }
    return pd.DataFrame([summary])



def run(pack_root: str, out_dir: str, *, candidate_name: str = 'portable_gate_map_candidate_v1'):
    pack_root = Path(pack_root).resolve()
    out_dir = ensure_dir(out_dir)
    anchor, _ = _build_anchor(pack_root)
    gate_config = _candidate_gate_config(anchor)
    full = evaluate_portability_dataframe(pack_root, gate_config, gate_label=candidate_name)
    full_path = out_dir / 'setA_struct_full.csv'
    full.to_csv(full_path, index=False)

    embed = _embedding_summary(full)
    embed_path = out_dir / 'setA_embed_sum.csv'
    embed.to_csv(embed_path, index=False)

    seta = _load_tables(pack_root)
    skipped_ids = sorted(set(seta['lens_id']) - set(full['lens_id']))
    skipped = pd.DataFrame({'lens_id': skipped_ids, 'reason': ['not_evaluated'] * len(skipped_ids)})
    skipped_path = out_dir / 'swells_setA_sproj_94a7c3.csv'
    skipped.to_csv(skipped_path, index=False)

    diagnostic = full[['lens_id', 'einstein_radius_pull_sigma', 'mass_pull_sigma', 'radius_pass_abs_le_2sigma', 'mass_pass_abs_le_2sigma', 'both_pass']].copy()
    diagnostic_path = out_dir / 'setA_struct_diag.csv'
    diagnostic.to_csv(diagnostic_path, index=False)

    summary = summarize_portability(full, anchor, gate_config, candidate_name=candidate_name)
    summary['outputs'] = {
        'full_csv': full_path.name,
        'embedding_summary_csv': embed_path.name,
        'skipped_lenses_csv': skipped_path.name,
        'diagnostic_csv': diagnostic_path.name,
    }
    save_json(summary, out_dir / 'setA_struct_sum.json')
    write_manifest(
        build_run_manifest(
            run_id=candidate_name,
            runner='solver.run_swells_setA_s_fc0f85',
            config='embedded portable_gate_map_candidate_v1',
            notes=['Rebuilt structured portability runner from the archived candidate-v1 portability logic.'],
        ),
        out_dir / 'run_manifest.json',
    )
    return full, summary



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-root', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument('--candidate-name', default='portable_gate_map_candidate_v1')
    args = parser.parse_args()
    full, summary = run(args.pack_root, args.out_dir, candidate_name=args.candidate_name)
    print(full.to_string(index=False))
    print(summary)
