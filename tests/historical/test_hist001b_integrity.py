"""HIST-001B P0/P1 authority, row oracle, receipt and isolation attacks."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from native_eset.historical.hist001b_compare import (
    COLUMNS, LENS_IDS, Hist001BComparisonError,
    compare_rows, read_trials, recompute_summary,
)
from native_eset.historical.hist001b_prechecks import (
    OriginalPrechecksUnavailable, require_original_600_prechecks,
)
from native_eset.historical.hist001b_receipt import (
    Hist001BReceiptError, verify_hist001b_receipt,
)
from native_eset.historical.hist001b_source import (
    Hist001BSourceError, HISTORICAL_PRODUCER_STATUS, PRECHECK_STATUS,
    require_no_symlink_components, verify_b_oracle,
)
from native_eset.historical.hist001b_spec import (
    HistoricalRobustnessRunSpec,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
RUNNER = ROOT / "tools/hist001b_run.py"


def _row(index: int, radius_mean: float = 1.1) -> dict:
    return {
        "trial": index, "n_both_pass": 5, "n_radius_pass": 5,
        "n_mass_pass": 6, "mean_abs_radius_pull_sigma": radius_mean,
        "mean_abs_mass_pull_sigma": 0.6,
        "failed_lenses": LENS_IDS[0],
        **{f"fail_{k}": k == LENS_IDS[0] for k in LENS_IDS},
    }


def _csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(COLUMNS))
        w.writeheader()
        w.writerows(rows)


def test_no_counts_only_source_exact_success() -> None:
    a = [_row(i, 1.1) for i in range(3)]
    b = [_row(i, 1.1) for i in range(3)]
    b[1] = _row(1, 2.7)
    assert recompute_summary(a)["n_at_5_or_more"] == recompute_summary(b)["n_at_5_or_more"]
    assert recompute_summary(a)["n_at_6_of_6"] == recompute_summary(b)["n_at_6_of_6"]
    result = compare_rows(a, b)
    assert result["all_rows_match"] is False
    assert result["differing_rows"] == 1
    assert result["matching_failure_vectors"] == 3


def test_ordered_rows_flags_nonfinite_and_completeness(tmp_path: Path) -> None:
    normal = [_row(i) for i in range(3)]
    csvfile = tmp_path / "trial.csv"
    _csv(csvfile, normal)
    assert read_trials(csvfile, n_trials=3) == normal
    for defect in (
        lambda rows: rows.__setitem__(1, _row(0)),
        lambda rows: rows[0].update({"failed_lenses": LENS_IDS[1]}),
        lambda rows: rows[1].update({"fail_" + LENS_IDS[1]: True}),
        lambda rows: rows[2].update({"mean_abs_radius_pull_sigma": float("nan")}),
        lambda rows: rows[2].update({"n_both_pass": 6}),
    ):
        changed = [dict(x) for x in normal]
        defect(changed)
        _csv(csvfile, changed)
        with pytest.raises(Hist001BComparisonError):
            read_trials(csvfile, n_trials=3)


def test_source_authority_is_separate_and_prechecks_never_forged(tmp_path: Path) -> None:
    with pytest.raises(Hist001BSourceError):
        verify_b_oracle(tmp_path)
    with pytest.raises(OriginalPrechecksUnavailable):
        require_original_600_prechecks(
            producer_sha256="0" * 64, case_manifest_sha256="0" * 64,
            claimed_matches=600,
        )
    assert "NOT_RECOVERED" in HISTORICAL_PRODUCER_STATUS
    assert "NOT_REEXECUTED" in PRECHECK_STATUS


def test_b_spec_prevents_seed_role_or_provider_override() -> None:
    spec = HistoricalRobustnessRunSpec.build(smoke=True, trials=3)
    assert HistoricalRobustnessRunSpec.parse(spec.raw) == spec
    assert spec.raw["physical_provider_admitted"] is False
    for key, value in (
        ("original_producer_authorized", True),
        ("empirical_validation", "PASS"),
        ("seed_root", 999),
        ("data_use", "HELD_OUT_VALIDATION"),
        ("original_rng_schedule_proved", True),
    ):
        forged = {**spec.raw, key: value}
        with pytest.raises(ValueError):
            HistoricalRobustnessRunSpec.parse(forged)
    with pytest.raises(ValueError):
        HistoricalRobustnessRunSpec.build(trials=4)
    with pytest.raises(ValueError):
        HistoricalRobustnessRunSpec.build(smoke=True, trials=10)


@pytest.fixture(scope="module")
def isolated_smoke(tmp_path_factory: pytest.TempPathFactory) -> dict:
    target = tmp_path_factory.mktemp("hist001b_isolated") / "runs"
    p = subprocess.run(
        [sys.executable, str(RUNNER), "--source-root", str(SOURCE),
         "--out", str(target), "--smoke", "--trials", "3"],
        cwd=ROOT, capture_output=True, text=True, timeout=180,
    )
    assert p.returncode == 0, p.stderr + "\n" + p.stdout[-2000:]
    result = json.loads(p.stdout)
    assert result["status"] == "HIST001B_SMOKE_ONLY_NOT_REEXECUTED"
    return result


def test_isolated_smoke_receipt_is_a_diagnostic_only(isolated_smoke: dict) -> None:
    root = Path(isolated_smoke["output_dir"])
    receipt = root / "receipt.json"
    verified = verify_hist001b_receipt(
        receipt, source_root=SOURCE,
        expected_sha256=isolated_smoke["receipt_sha256"],
    )
    assert verified["status"] == "VERIFIED_HIST001B_DIAGNOSTIC_OR_FAILURE_BYTES_ONLY"
    assert verified["original_producer_verified"] is False
    assert verified["original_600_prechecks_verified"] is False
    assert verified["physical_provider_admitted"] is False
    assert verified["empirical_validation"] == "NOT_ESTABLISHED"


def _forge_receipt(path: Path, value: dict) -> None:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    (path / "receipt.json").write_bytes(raw)
    (path / "receipt.sha256").write_text(hashlib.sha256(raw).hexdigest() + "\n")


def test_receipt_rejects_forged_promotion_even_with_new_selfhash(
    isolated_smoke: dict, tmp_path: Path,
) -> None:
    root = Path(isolated_smoke["output_dir"])
    target = tmp_path / root.name
    shutil.copytree(root, target)
    obj = json.loads((target / "receipt.json").read_text())
    obj["claim_boundary"]["physical_provider_admitted"] = True
    _forge_receipt(target, obj)
    with pytest.raises(Hist001BReceiptError, match="unauthorized promotion"):
        verify_hist001b_receipt(target / "receipt.json", source_root=SOURCE)


def test_receipt_rejects_modified_row_with_repaired_hash(
    isolated_smoke: dict, tmp_path: Path,
) -> None:
    root = Path(isolated_smoke["output_dir"])
    target = tmp_path / root.name
    shutil.copytree(root, target)
    out = target / "width_01pct.csv"
    content = out.read_text(encoding="utf-8")
    assert "1.400481" in content or "1.4" in content
    out.write_text(content.replace("1.4", "1.9", 1), encoding="utf-8")
    receipt = json.loads((target / "receipt.json").read_text())
    receipt["output_files"][out.name] = hashlib.sha256(out.read_bytes()).hexdigest()
    _forge_receipt(target, receipt)
    with pytest.raises((Hist001BReceiptError, Hist001BComparisonError)):
        verify_hist001b_receipt(target / "receipt.json", source_root=SOURCE)


def test_b_runner_rejects_source_overlap_and_symlink_root(tmp_path: Path) -> None:
    symlink = tmp_path / "source-link"
    try:
        symlink.symlink_to(SOURCE, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("this platform does not permit unprivileged symlinks")
    with pytest.raises(Hist001BSourceError):
        require_no_symlink_components(symlink)
    with pytest.raises(Hist001BSourceError):
        require_no_symlink_components(symlink / "swells_pack_v2")


def test_b_verifier_unsupported_schema_or_missing_oracle(
    isolated_smoke: dict, tmp_path: Path,
) -> None:
    root = Path(isolated_smoke["output_dir"])
    with pytest.raises(Hist001BReceiptError):
        verify_hist001b_receipt(
            root / "receipt.json", source_root=SOURCE,
            oracle_root=tmp_path / "not_a_real_oracle",
        )
    target = tmp_path / root.name
    shutil.copytree(root, target)
    obj = json.loads((target / "receipt.json").read_text())
    obj["schema"] = "NATIVE_ESET_RUN_RECEIPT_V2"
    _forge_receipt(target, obj)
    with pytest.raises(Hist001BReceiptError):
        verify_hist001b_receipt(target / "receipt.json", source_root=SOURCE)
