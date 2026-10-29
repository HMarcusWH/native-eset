"""Width-pair RNG signature diagnostics; NOT source-exact replay or validation."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from statistics import fmean

from native_eset.historical.hist001b_compare import read_trials
from native_eset.historical.hist001b_source import (
    ARCHIVE_PREFIX, require_no_symlink_components, verify_b_oracle,
)

WIDTH_PCTS = (1, 2, 5, 10)
METRICS = ("mean_abs_radius_pull_sigma", "mean_abs_mass_pull_sigma", "n_both_pass")
EXPECTED_TRIALS = 1000


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 4:
        raise ValueError("paired series must have equal length >=4")
    a = [float(x) for x in xs]
    b = [float(x) for x in ys]
    if not all(math.isfinite(z) for z in (*a, *b)):
        raise ValueError("non-finite width-pair metric")
    u, v = fmean(a), fmean(b)
    ca = [x - u for x in a]
    cb = [y - v for y in b]
    denominator = math.sqrt(
        math.fsum(x * x for x in ca) * math.fsum(y * y for y in cb)
    )
    if denominator == 0:
        raise ValueError("constant metric series has undefined correlation")
    result = math.fsum(x * y for x, y in zip(ca, cb)) / denominator
    return max(-1.0, min(1.0, result))


def fisher_95_interval(r: float, *, n: int = EXPECTED_TRIALS) -> list[float]:
    """Descriptive approximation for independently paired observations only."""
    if not math.isfinite(r) or abs(r) > 1 or n <= 3:
        raise ValueError("invalid correlation or trial count")
    if abs(r) == 1:
        return [r, r]
    z = math.atanh(r)
    half = 1.959963984540054 / math.sqrt(n - 3)
    return [math.tanh(z - half), math.tanh(z + half)]


def _pairs(tables: dict[int, list[dict]], field: str) -> dict:
    pairs = []
    for i, width_a in enumerate(WIDTH_PCTS):
        for width_b in WIDTH_PCTS[i + 1:]:
            xs = [row[field] for row in tables[width_a]]
            ys = [row[field] for row in tables[width_b]]
            r = pearson(xs, ys)
            pairs.append({
                "widths_percent": [width_a, width_b], "pearson_r": r,
                "fisher95_ci": fisher_95_interval(r, n=len(xs)),
            })
    return {
        "pairs": pairs,
        "max_abs_crosswidth_pearson": max(abs(p["pearson_r"]) for p in pairs),
        "min_crosswidth_pearson": min(p["pearson_r"] for p in pairs),
    }


def inspect_width_streams(*, oracle_root: str | Path,
                          diagnostic_root: str | Path | None = None) -> dict:
    """Compare 4 SHA-verified archived CSVs to new, separate diagnostic rows.

    This does NOT recover the original RNG seed/width schedule, executed
    accelerator, or original 600-case precheck corpus. Correlations are
    descriptive evidence about trial-number alignment, not source authority.
    """
    oracle = require_no_symlink_components(oracle_root)
    verify_b_oracle(oracle)
    root = (
        require_no_symlink_components(diagnostic_root)
        if diagnostic_root is not None else None
    )
    if root is not None and not root.is_dir():
        raise ValueError("diagnostic replay root must exist")
    archived, replay, original_sha, new_sha = {}, {}, {}, {}
    for width in WIDTH_PCTS:
        original_file = oracle / (ARCHIVE_PREFIX + f"w{width:02d}pct.csv")
        archived[width] = read_trials(original_file, n_trials=EXPECTED_TRIALS)
        original_sha[str(width)] = hashlib.sha256(original_file.read_bytes()).hexdigest()
        if root is not None:
            new_file = root / f"width_{width:02d}pct.csv"
            replay[width] = read_trials(new_file, n_trials=EXPECTED_TRIALS)
            new_sha[str(width)] = hashlib.sha256(new_file.read_bytes()).hexdigest()
    return {
        "schema": "HIST001B_WIDTH_PAIRED_RNG_FORENSIC_V1",
        "status": "HIST001B_RNG_WIDTH_DEPENDENCE_DIAGNOSTIC_ONLY",
        "widths_percent": list(WIDTH_PCTS),
        "trials_per_width": EXPECTED_TRIALS,
        "verified_archived_file_sha256": original_sha,
        "replay_file_sha256": new_sha,
        "metrics": {
            name: {
                "archived": _pairs(archived, name),
                "replay": _pairs(replay, name) if root is not None else None,
            } for name in METRICS
        },
        "interpretation": (
            "Near-zero archived cross-width correlations versus high replay "
            "correlations indicate different width-specific draws or trial "
            "index mapping. Neither original RNG nor accelerator is recovered."
        ),
        "original_accelerated_producer_verified": False,
        "original_rng_schedule_verified": False,
        "original_600_prechecks_verified": False,
        "source_exact_replay_authorized": False,
        "physical_provider_admitted": False,
        "native_v172_equivalence_proved": False,
        "empirical_validation": "NOT_ESTABLISHED",
    }
