"""HIST-001B independent 4,000-trial archival comparator.

Counts-only agreement is never sufficient. Archived data are immutable
regression evidence, not a new blind dataset or physical validation.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from native_eset.historical.hist001b_source import (
    ARCHIVE_PREFIX, ARCHIVED_COUNTS, verify_b_oracle,
    require_no_symlink_components,
)

WIDTHS = (0.01, 0.02, 0.05, 0.10)
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
COLUMNS = (
    "trial", "n_both_pass", "n_radius_pass", "n_mass_pass",
    "mean_abs_radius_pull_sigma", "mean_abs_mass_pull_sigma",
    "failed_lenses", *(f"fail_{name}" for name in LENS_IDS),
)
FLOAT_FIELDS = ("mean_abs_radius_pull_sigma", "mean_abs_mass_pull_sigma")


class Hist001BComparisonError(ValueError):
    pass


def _strict_json(path: Path) -> dict:
    from native_eset.serialization import strict_loads
    obj = strict_loads(path.read_bytes())
    if not isinstance(obj, dict):
        raise Hist001BComparisonError("expected an object summary")
    return obj


def _integer(s: str, column: str) -> int:
    if not s.isascii() or not s.isdecimal():
        raise Hist001BComparisonError("invalid integer: " + column)
    return int(s)


def _float(s: str, column: str) -> float:
    try:
        value = float(s)
    except (ValueError, TypeError, OverflowError) as exc:
        raise Hist001BComparisonError("non-numeric " + column) from exc
    if not math.isfinite(value) or value < 0:
        raise Hist001BComparisonError("nonfinite/negative " + column)
    return value


def read_trials(path: Path, *, n_trials: int) -> list[dict]:
    path = require_no_symlink_components(path)
    if not path.is_file() or path.stat().st_size > 250_000:
        raise Hist001BComparisonError("missing/oversized trial CSV")
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != list(COLUMNS):
            raise Hist001BComparisonError("duplicate, reordered or extra trial columns")
        rows = []
        for index, source in enumerate(reader):
            if None in source or set(source) != set(COLUMNS):
                raise Hist001BComparisonError("invalid trial columns")
            trial = _integer(source["trial"], "trial")
            if trial != index:
                raise Hist001BComparisonError("nonconsecutive/duplicate trial index")
            counts = {key: _integer(source[key], key) for key in (
                "n_both_pass", "n_radius_pass", "n_mass_pass")}
            if any(not (0 <= v <= 6) for v in counts.values()):
                raise Hist001BComparisonError("unphysical trial pass count")
            if (counts["n_both_pass"] > min(counts["n_radius_pass"], counts["n_mass_pass"]) or
                    counts["n_both_pass"] < counts["n_radius_pass"] + counts["n_mass_pass"] - 6):
                raise Hist001BComparisonError("internally inconsistent pass counts")
            booleans = {}
            for lens in LENS_IDS:
                raw = source["fail_" + lens]
                if raw not in ("True", "False"):
                    raise Hist001BComparisonError("nonboolean failure flag")
                booleans[lens] = raw == "True"
            failed = ";".join(k for k, v in booleans.items() if v)
            if source["failed_lenses"] != failed:
                raise Hist001BComparisonError("failed-lens list disagrees with flags")
            if 6 - sum(booleans.values()) != counts["n_both_pass"]:
                raise Hist001BComparisonError("pass count disagrees with failure vector")
            rows.append({
                "trial": trial, **counts,
                **{key: _float(source[key], key) for key in FLOAT_FIELDS},
                "failed_lenses": failed, **{f"fail_{k}": v for k, v in booleans.items()},
            })
            if len(rows) > n_trials:
                raise Hist001BComparisonError("excess trial rows")
    if len(rows) != n_trials:
        raise Hist001BComparisonError("missing trial rows")
    return rows


def recompute_summary(rows: list[dict]) -> dict:
    if not rows:
        raise Hist001BComparisonError("empty trial set")
    n = len(rows)
    return {
        "n_trials": n,
        "n_at_6_of_6": sum(r["n_both_pass"] == 6 for r in rows),
        "n_at_5_or_more": sum(r["n_both_pass"] >= 5 for r in rows),
        "mean_abs_radius_pull_sigma_mean": sum(
            r["mean_abs_radius_pull_sigma"] for r in rows) / n,
        "mean_abs_mass_pull_sigma_mean": sum(
            r["mean_abs_mass_pull_sigma"] for r in rows) / n,
        "per_lens_failure_fraction": {
            lens: sum(r["fail_" + lens] for r in rows) / n for lens in LENS_IDS
        },
    }


def _check_archive_summary(summary: dict, calculated: dict, width: float) -> None:
    for key in ("n_trials", "n_at_6_of_6", "n_at_5_or_more"):
        if type(summary.get(key)) is not int or summary[key] != calculated[key]:
            raise Hist001BComparisonError("frozen archive summary invalid: " + key)
    if summary.get("rel_width") != width:
        raise Hist001BComparisonError("frozen summary wrong width")
    if (summary["n_at_6_of_6"], summary["n_at_5_or_more"]) != ARCHIVED_COUNTS[width]:
        raise Hist001BComparisonError("frozen archive count authority mismatch")
    for key in FLOAT_FIELDS:
        sk = key + "_mean"
        if not math.isclose(float(summary[sk]), calculated[sk],
                            rel_tol=0, abs_tol=1e-10):
            raise Hist001BComparisonError("frozen summary arithmetic inconsistent: " + sk)
    for lens in LENS_IDS:
        if not math.isclose(
            float(summary["per_lens_failure_fraction"][lens]),
            calculated["per_lens_failure_fraction"][lens], abs_tol=1e-12, rel_tol=0
        ):
            raise Hist001BComparisonError("frozen per-lens summary arithmetic inconsistent")


def compare_rows(actual: list[dict], expected: list[dict], *,
                 tolerance: float = 1e-8) -> dict:
    if len(actual) != len(expected):
        raise Hist001BComparisonError("row count differs")
    differences = 0
    equal_failure_vector = 0
    first = None
    for index, (a, b) in enumerate(zip(actual, expected)):
        status_equal = all(a[col] == b[col] for col in COLUMNS if col not in FLOAT_FIELDS)
        pulls_equal = all(
            math.isclose(a[col], b[col], abs_tol=tolerance, rel_tol=0)
            for col in FLOAT_FIELDS
        )
        if all(a["fail_" + name] == b["fail_" + name] for name in LENS_IDS):
            equal_failure_vector += 1
        if not (status_equal and pulls_equal):
            differences += 1
            if first is None:
                first = {
                    "trial": index,
                    "archived_mean_abs_radius_pull_sigma": b["mean_abs_radius_pull_sigma"],
                    "new_mean_abs_radius_pull_sigma": a["mean_abs_radius_pull_sigma"],
                    "failure_vector_equal": status_equal,
                }
    return {
        "row_count": len(actual),
        "identical_rows": len(actual) - differences,
        "matching_failure_vectors": equal_failure_vector,
        "differing_rows": differences,
        "first_difference": first,
        "all_rows_match": differences == 0,
    }


def inspect_output(root: Path, *, n_trials: int, smoke: bool,
                   oracle_root: Path | None = None) -> dict:
    """Independently recompute generated rows and optionally compare to pinned archive."""
    root = require_no_symlink_components(root)
    if not root.is_dir():
        raise Hist001BComparisonError("output folder not found")
    if oracle_root is not None:
        verify_b_oracle(oracle_root)
        oracle_root = require_no_symlink_components(oracle_root)
    result = []
    for width in ((0.01,) if smoke else WIDTHS):
        name = f"width_{round(width * 100):02d}pct.csv"
        actual = read_trials(root / name, n_trials=n_trials)
        computed = recompute_summary(actual)
        entry = {"width": width, **computed}
        if oracle_root is not None:
            archived_name = ARCHIVE_PREFIX + f"w{round(width * 100):02d}pct.csv"
            expected = read_trials(oracle_root / archived_name, n_trials=1000)
            summary = _strict_json(
                oracle_root / (ARCHIVE_PREFIX + f"w{round(width * 100):02d}pct_summary.json")
            )
            _check_archive_summary(summary, recompute_summary(expected), width)
            if smoke:
                entry["archival_comparison"] = "NOT_RUN_SMOKE_ONLY"
            else:
                entry["archival_comparison"] = compare_rows(actual, expected)
                entry["original_summary"] = {
                    key: summary[key] for key in (
                        "n_at_6_of_6", "n_at_5_or_more",
                        "mean_abs_radius_pull_sigma_mean",
                        "mean_abs_mass_pull_sigma_mean"
                    )
                }
        else:
            entry["archival_comparison"] = "ORACLE_NOT_SUPPLIED"
        result.append(entry)
    return {
        "status": "HIST001B_INDEPENDENT_ROW_AUDIT_NOT_SCIENTIFIC_ADMISSION",
        "widths": result,
        "oracle_verified": oracle_root is not None,
        "complete_archival_row_match": (
            not smoke and oracle_root is not None and
            all(x["archival_comparison"]["all_rows_match"] for x in result)
        ),
        "original_accelerated_producer_verified": False,
        "original_600_prechecks_verified": False,
        "physical_provider_admitted": False,
    }
