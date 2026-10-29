#!/usr/bin/env python3
"""Predeclared historical RNG-schedule probes; NOT source-exact reconstruction.

Seven bounded hypotheses, original fitted law untouched, first archived
trial at each of four widths, separately SHA-verified historical source and
archived CSV oracle. No seed searching, retuning or scientific promotion.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

from native_eset.historical.hist001b_compare import read_trials
from native_eset.historical.hist001b_source import (
    ARCHIVE_PREFIX, HIST001A_SOURCE_LOCK_SHA256,
    require_no_symlink_components, verify_b_oracle,
)
from native_eset.historical.hist001_source import verify_hist001_source

WIDTHS = (0.01, 0.02, 0.05, 0.10)
SEED_ROOT = 2141
HYPOTHESES = (
    "parallel_trial_only",
    "serial_reset_each_width",
    "continuous_global_stream_across_4_campaigns",
    "seed_plus_width_index",
    "seed_plus_percent_integer",
    "seedsequence_root_width_index_trial",
    "seedsequence_root_width_percent_trial",
)


def proposed_rng(name: str, index: int, width: float) -> np.random.Generator:
    if name not in HYPOTHESES or not (0 <= index < 4) or width != WIDTHS[index]:
        raise ValueError("unregistered RNG hypothesis/width")
    if name == "parallel_trial_only":
        return np.random.default_rng(np.random.SeedSequence([SEED_ROOT, 0]))
    if name == "serial_reset_each_width":
        return np.random.default_rng(SEED_ROOT)
    if name == "continuous_global_stream_across_4_campaigns":
        rng = np.random.default_rng(SEED_ROOT)
        if index:
            # Each previous width draws 1000 trials * six lenses * six inputs.
            rng.random(1000 * 6 * 6 * index)
        return rng
    if name == "seed_plus_width_index":
        return np.random.default_rng(SEED_ROOT + index)
    if name == "seed_plus_percent_integer":
        return np.random.default_rng(SEED_ROOT + round(width * 100))
    if name == "seedsequence_root_width_index_trial":
        return np.random.default_rng(np.random.SeedSequence([SEED_ROOT, index, 0]))
    return np.random.default_rng(
        np.random.SeedSequence([SEED_ROOT, round(width * 100), 0])
    )


def _perturb(base, width: float, rng: np.random.Generator):
    from hist001b_rangefinder import FRACTIONAL, MASSES

    new = base.copy()
    for field in FRACTIONAL:
        new[field] = new[field].astype(float) * rng.uniform(
            1 - width, 1 + width, size=len(new)
        )
    for field in MASSES:
        new[field] = new[field].astype(float) + np.log10(
            rng.uniform(1 - width, 1 + width, size=len(new))
        )
    for field in ("q_bulge", "q_disc"):
        new[field] = new[field].clip(1e-3, 1.0)
    return new


def probe(source_root: str | Path, oracle_root: str | Path) -> dict:
    """Run 7 x 4 first-trial probes in a disposable verified source copy."""
    source = require_no_symlink_components(source_root)
    oracle = require_no_symlink_components(oracle_root)
    verified = verify_hist001_source(source)
    if verified["source_lock_sha256"] != HIST001A_SOURCE_LOCK_SHA256:
        raise ValueError("frozen source identity changed")
    verified_oracle = verify_b_oracle(oracle)
    expected = {}
    for width in WIDTHS:
        path = oracle / (
            ARCHIVE_PREFIX + f"w{round(width * 100):02d}pct.csv"
        )
        expected[width] = read_trials(path, n_trials=1000)[0]
    sys.dont_write_bytecode = True
    with tempfile.TemporaryDirectory(prefix="hist001b-seed-probe-") as td:
        copied_source = Path(td) / "source"
        shutil.copytree(source, copied_source)
        verify_hist001_source(copied_source)
        # Import verified source only after copying it away from frozen inputs.
        pack = copied_source / "swells_pack_v2"
        sys.path.insert(0, str(pack))
        from hist001b_rangefinder import evaluate, prepare

        prepared = prepare(pack)
        rows = []
        for name in HYPOTHESES:
            for index, width in enumerate(WIDTHS):
                result = evaluate(
                    prepared, _perturb(
                        prepared[1], width, proposed_rng(name, index, width)
                    )
                )
                original = expected[width]
                radius_diff = (
                    result["mean_abs_radius_pull_sigma"]
                    - original["mean_abs_radius_pull_sigma"]
                )
                mass_diff = (
                    result["mean_abs_mass_pull_sigma"]
                    - original["mean_abs_mass_pull_sigma"]
                )
                rows.append({
                    "hypothesis": name, "width": width, "trial": 0,
                    "radius_error": radius_diff, "mass_error": mass_diff,
                    "archived_failed_lenses": original["failed_lenses"],
                    "new_failed_lenses": result["failed_lenses"],
                    "full_first_trial_match": (
                        abs(radius_diff) <= 1e-8
                        and abs(mass_diff) <= 1e-8
                        and original["failed_lenses"] == result["failed_lenses"]
                    ),
                })
        verify_hist001_source(copied_source)
    verify_hist001_source(source)
    return {
        "schema": "HIST001B_PREDECLARED_RNG_SCHEDULE_DIAGNOSTIC_V1",
        "status": "HIST001B_RNG_SCHEDULE_HYPOTHESES_NOT_ORIGINAL_SOURCE",
        "hypotheses": list(HYPOTHESES),
        "widths": list(WIDTHS),
        "tested_trial": 0,
        "original_source_sha256": HIST001A_SOURCE_LOCK_SHA256,
        "approved_oracle_member_hashes": verified_oracle["archived_files"],
        "rows": rows,
        "all_widths_exactly_matched_by_any_hypothesis": any(
            all(x["full_first_trial_match"] for x in rows
                if x["hypothesis"] == name)
            for name in HYPOTHESES
        ),
        "first_trial_parallel_equals_serial_by_construction": True,
        "original_accelerated_producer_verified": False,
        "original_rng_schedule_verified": False,
        "original_600_prechecks_verified": False,
        "physical_provider_admitted": False,
        "source_exact_replay_authorized": False,
        "empirical_validation": "NOT_ESTABLISHED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--oracle-root", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = probe(args.source_root, args.oracle_root)
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.out is not None:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        print(encoded, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "HIST001B_RNG_PROBE_FAIL_CLOSED",
                          "error": str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
