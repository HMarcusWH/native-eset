from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .io_utils import ensure_dir, save_json, write_csv
from .stagec import apply_envelope, build_closure_object, load_envelope, normalize_linear_samples

ALIASES = {
    'a': ['a', 'scale_factor', 'scalefactor'],
    'z': ['z', 'redshift'],
    'k_hMpc': ['k_hmpc', 'k_h', 'kh', 'k_over_h', 'k/h', 'k_h_mpc'],
    'k': ['k', 'k_mpc', 'k_mpcinv'],
    'epsilon': ['epsilon', 'eps'],
    'mu': ['mu'],
    'Sigma': ['Sigma', 'sigma', 'sigma_lens'],
    'eta': ['eta', 'slip'],
    'phi': ['phi', 'Phi', 'phi_metric'],
    'psi': ['psi', 'Psi', 'psi_metric'],
}


def _find_col(columns, aliases):
    norm = {c.lower().strip(): c for c in columns}
    for alias in aliases:
        key = alias.lower().strip()
        if key in norm:
            return norm[key]
    return None


def parse_args():
    p = argparse.ArgumentParser(description='Bridge CLASS/CAMB-style linear exports into the Stage C handshake schema.')
    p.add_argument('--input-csv', type=Path, required=True)
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--candidate-name', default='ra0_gated_geometry_sigmoid_reg_v2')
    p.add_argument('--envelope-json', type=Path, default=None)
    p.add_argument('--format', choices=['auto', 'class', 'camb'], default='auto')
    p.add_argument('--h', type=float, default=None, help='Needed when input uses k in 1/Mpc rather than k_hMpc.')
    p.add_argument('--source-label', default=None)
    return p.parse_args()


def standardize(df: pd.DataFrame, *, h: float | None = None, source_label: str | None = None) -> pd.DataFrame:
    out = pd.DataFrame()
    cols = list(df.columns)
    a_col = _find_col(cols, ALIASES['a'])
    z_col = _find_col(cols, ALIASES['z'])
    if a_col is not None:
        out['a'] = pd.to_numeric(df[a_col], errors='coerce')
    elif z_col is not None:
        out['a'] = 1.0 / (1.0 + pd.to_numeric(df[z_col], errors='coerce'))
    else:
        raise ValueError('Input must contain either a or z/redshift.')

    kh_col = _find_col(cols, ALIASES['k_hMpc'])
    k_col = _find_col(cols, ALIASES['k'])
    if kh_col is not None:
        out['k_hMpc'] = pd.to_numeric(df[kh_col], errors='coerce')
    elif k_col is not None:
        if h is None:
            raise ValueError('Input provides k but not k_hMpc; pass --h to convert k -> k_hMpc.')
        out['k_hMpc'] = pd.to_numeric(df[k_col], errors='coerce') / float(h)
    else:
        raise ValueError('Input must contain k_hMpc-style or k-style wavenumber column.')

    for target in ['epsilon', 'mu', 'Sigma', 'eta', 'phi', 'psi']:
        col = _find_col(cols, ALIASES[target])
        if col is not None:
            out[target] = pd.to_numeric(df[col], errors='coerce')

    if 'eta' not in out.columns and 'phi' in out.columns and 'psi' in out.columns:
        denom = out['psi'].replace(0.0, np.nan)
        out['eta'] = out['phi'] / denom

    out['source'] = source_label or 'external_linear_export'
    out['note'] = 'Standardized from CLASS/CAMB-style export for Stage C scoring.'
    keep = ['a', 'k_hMpc', 'epsilon', 'mu', 'Sigma', 'eta', 'source', 'note']
    for col in keep:
        if col not in out.columns:
            out[col] = np.nan
    out = out[keep]
    return normalize_linear_samples(out)


def main():
    args = parse_args()
    out_dir = ensure_dir(args.out_dir)
    raw = pd.read_csv(args.input_csv)
    std = standardize(raw, h=args.h, source_label=args.source_label)
    write_csv(std, out_dir / 'linear_rows_standardized.csv')

    envelope = load_envelope(args.envelope_json)
    scored = apply_envelope(std, envelope)
    write_csv(scored, out_dir / 'linear_rows_scored.csv')

    contract_rows = pd.DataFrame(columns=['regime', 'scope', 'candidate_name', 'a', 'k_hMpc', 'epsilon', 'mu', 'Sigma', 'eta', 'source', 'note'])
    closure = build_closure_object(
        candidate_name=args.candidate_name,
        envelope=envelope,
        contract_rows=contract_rows,
        linear_rows=scored,
        j2141_summary=None,
    )
    save_json(closure, out_dir / 'closure.json')


if __name__ == '__main__':
    main()
