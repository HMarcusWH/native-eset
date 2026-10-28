"""HIST-001A/2: exact process-local spherical intervention on untouched solver.

This module is an execution adapter, not a physics model. It changes only the
projection callable within the child process; all fitted source bytes are frozen.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-root", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    opts = parser.parse_args()
    root = opts.pack_root.resolve(strict=True)
    sys.path.insert(0, str(root))
    import solv.run_setA_port_cand as original  # The source root was SHA-checked by the parent.

    original_projection = original.apply_shadow_projection_mode

    def spherical(r_grid, shadow_spherical, lens_cfg, *rest):
        return original_projection(
            r_grid, shadow_spherical,
            {**lens_cfg, "shadow_projection": "spherical_cylindrical"}, *rest,
        )

    original.apply_shadow_projection_mode = spherical
    original.run(str(root), str(opts.out_csv), str(opts.out_json),
                 candidate_name="ra0_gated_geometry_sigmoid_reg_v2")
    print(json.dumps({"ablation": "spherical_cylindrical_only", "no_refit": True,
                      "source_bytes_modified": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
