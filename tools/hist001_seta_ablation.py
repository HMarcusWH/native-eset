#!/usr/bin/env python3
"""Explicit no-refit spherical-projection intervention on the unchanged 2026-03-14 legacy solver.

This process-scoped wrapper replaces only the projection choice. It does not
rewrite any frozen source file, physical parameters, fitting rule or scorer.
Not an independently validated physical lensing prediction.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-root', required=True, type=Path)
    parser.add_argument('--out-csv', required=True, type=Path)
    parser.add_argument('--out-json', required=True, type=Path)
    args = parser.parse_args()
    pack = args.pack_root.resolve()
    sys.path.insert(0, str(pack))
    import solv.run_setA_port_cand as original

    base_projection = original.apply_shadow_projection_mode

    def use_spherical(r_grid, shadow_spherical, lens_cfg, *rest):
        return base_projection(r_grid, shadow_spherical,
                               {**lens_cfg, 'shadow_projection': 'spherical_cylindrical'}, *rest)

    original.apply_shadow_projection_mode = use_spherical
    original.run(str(pack), str(args.out_csv), str(args.out_json),
                 candidate_name='ra0_gated_geometry_sigmoid_reg_v2')
    print(json.dumps({'ablation': 'spherical_cylindrical_only', 'no_refit': True,
                      'changed_original_source_bytes': False, 'results': str(args.out_json)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
