from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .io_utils import ensure_dir, save_json, write_csv
from .stagec import (
    apply_envelope,
    build_closure_object,
    build_contract_rows,
    build_default_envelope,
    load_envelope,
    normalize_linear_samples,
)


def parse_args():
    p = argparse.ArgumentParser(description='Run the Stage C linear-handshake scaffold for the current DM-A working law.')
    p.add_argument('--pack-root', type=Path, required=True)
    p.add_argument('--candidate-name', default='ra0_gated_geometry_sigmoid_reg_v2')
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--envelope-json', type=Path, default=None)
    p.add_argument('--linear-samples-csv', type=Path, default=None)
    p.add_argument('--j2141-summary-json', type=Path, default=None)
    return p.parse_args()


def main():
    args = parse_args()
    pack_root = args.pack_root.resolve()
    out_dir = ensure_dir(args.out_dir)

    if args.envelope_json is None:
        default_env = build_default_envelope()
        env_path = out_dir / 'stagec_envelope_template.json'
        env_path.write_text(json.dumps(default_env, indent=2), encoding='utf-8')
        envelope = load_envelope(env_path)
    else:
        envelope = load_envelope(args.envelope_json)
        env_path = args.envelope_json

    j2141_summary = None
    if args.j2141_summary_json is not None and args.j2141_summary_json.exists():
        j2141_summary = json.loads(args.j2141_summary_json.read_text())

    contract_rows = build_contract_rows(j2141_summary=j2141_summary, candidate_name=args.candidate_name)
    contract_rows = apply_envelope(contract_rows, envelope)
    write_csv(contract_rows, out_dir / 'stagec_contract_rows.csv')

    if args.linear_samples_csv is None:
        template = pd.DataFrame(columns=['a', 'k_hMpc', 'epsilon', 'mu', 'Sigma', 'eta', 'source', 'note'])
        template.to_csv(out_dir / 'stagec_linear_samples_template.csv', index=False)
        linear_rows = None
    else:
        linear_in = pd.read_csv(args.linear_samples_csv)
        linear_rows = apply_envelope(normalize_linear_samples(linear_in), envelope)
        write_csv(linear_rows, out_dir / 'stagec_linear_rows_scored.csv')

    closure = build_closure_object(
        candidate_name=args.candidate_name,
        envelope=envelope,
        contract_rows=contract_rows,
        linear_rows=linear_rows,
        j2141_summary=j2141_summary,
    )
    save_json(closure, out_dir / 'closure.json')

    md = [
        '# Stage C linear-handshake scaffold run',
        '',
        f'- candidate: `{args.candidate_name}`',
        f'- pack_root: `{pack_root}`',
        f'- envelope: `{env_path}`',
        f'- contract rows emitted: **{len(contract_rows)}**',
        f'- linear rows emitted: **{0 if linear_rows is None else len(linear_rows)}**',
        f'- status: **{closure["status"]}**',
        '',
        '## What this run means',
        '',
        'This scaffold makes the Stage C interface explicit and machine-readable.',
        'It does **not** by itself complete the survey-scale linear acceptance unless an external linear sample file and populated near-GR envelope are supplied.',
    ]
    (out_dir / 'README_stagec_run.md').write_text('\n'.join(md) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
