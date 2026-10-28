from __future__ import annotations
from pathlib import Path
import numpy as np
from .io_utils import load_json, read_csv, write_csv

def run(config_path: str, pack_root: str):
    pack_root = Path(pack_root)
    config = load_json(config_path)
    targets = read_csv(pack_root / 'cleaned' / 'swells_v_targets_b1b88c.csv')
    out = targets[['lens_id','z_deflector','Rbulge_kpc','Rdisc_kpc']].copy()
    out['predicted_einstein_radius_arcsec'] = np.nan
    out['predicted_lensing_mass_1e10Msun'] = np.nan
    out['predicted_total_velocity_km_s'] = np.nan
    out['predicted_eta'] = 1.0
    write_csv(out, pack_root / 'res' / 'example_j21_be122d' / 'swells_v_solv_out_a127c8.csv')
    return {'branch_id': config['branch_id'], 'status': 'placeholder_only', 'rows': int(len(out))}

if __name__ == '__main__':
    import argparse, json
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--pack-root', required=True)
    args = parser.parse_args()
    result = run(args.config, args.pack_root)
    print(json.dumps(result, indent=2))
