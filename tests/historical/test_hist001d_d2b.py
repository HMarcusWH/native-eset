"""HIST-001D D2b numerical source attribution, integrity and nonpromotion tests."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from native_eset.evidence.receipts import canonical_json
from native_eset.historical.hist001_source import verify_hist001_source

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
SCRIPT = ROOT / "tools/hist001d_d2b.py"
SPEC = importlib.util.spec_from_file_location("hist001d_d2b_local", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


@pytest.fixture(scope="module")
def diagnostic() -> dict:
    return D.execute(SOURCE)


def test_factorial_attribution_no_holdout(diagnostic: dict) -> None:
    assert diagnostic["source_lock_sha256"] == D.SOURCE_SHA256
    assert diagnostic["data_use"].endswith("NOT_HELDOUT")
    assert diagnostic["claims"] == D.CLAIMS
    rows = diagnostic["results"]
    assert len(rows) == 6
    failing = {"J0822+1828", "J1021+2028", "J1111+2234"}
    for row in rows:
        a = row["factorial_density_projection_grid"]
        assert a["rho180_K180"]["joint_pass"] is True
        assert a["rho360_K180"]["joint_pass"] is True
        assert a["rho180_K360"]["joint_pass"] is (row["lens_id"] not in failing)
        assert a["rho360_K360"]["joint_pass"] is (row["lens_id"] not in failing)
        assert row["fine720_self_consistent_source_proxy"]["joint_pass"] is (row["lens_id"] not in failing)
        assert row["bulge_projection_grid_reference"]["180"]["relative_error_vs_adaptive_finite_domain"] < -.03
        angles = row["source_disk_vs_periodic_angle"]
        assert angles["120"]["fractional_bias_relative_to_periodic"] < 0
        assert abs(angles["240"]["fractional_bias_relative_to_periodic"]) < abs(
            angles["120"]["fractional_bias_relative_to_periodic"]
        )
    target = {r["lens_id"]: r for r in rows}["J0822+1828"]
    root = target["factorial_density_projection_grid"]["rho180_K180"]["root_interpolation_diagnostic"]
    assert root["radius_pull_shift_from_original_root_sigma"] > 1.0


def test_report_receipt_independent_reexecution(tmp_path: Path) -> None:
    out = tmp_path / "run"
    result = D.run(SOURCE, out)
    assert result["status"] == "HIST001D_ROOT_CAUSE_DIAGNOSTIC_NO_ADMISSION"
    verified = D.verify(out / "receipt.json", SOURCE, result["receipt_sha256"])
    assert verified["status"] == "HIST001D_D2B_INDEPENDENT_SOURCE_REEXECUTION_PASS_NO_ADMISSION"
    assert verified["cases_verified"] == 6
    assert verified["claims"] == D.CLAIMS
    with pytest.raises(FileExistsError):
        D.run(SOURCE, out)


def _rehash_report_and_receipt(out: Path, report: dict | None = None,
                               receipt: dict | None = None) -> None:
    p = out / "report.json"
    r = out / "receipt.json"
    if report is not None:
        p.write_bytes(canonical_json(report))
    obj = json.loads(r.read_bytes()) if receipt is None else receipt
    obj["report_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    r.write_bytes(canonical_json(obj))
    (out / "receipt.sha256").write_text(hashlib.sha256(r.read_bytes()).hexdigest() + "\n")


def test_self_rehashed_numeric_forgery_rejected(tmp_path: Path) -> None:
    out = tmp_path / "run"
    D.run(SOURCE, out)
    data = json.loads((out / "report.json").read_bytes())
    data["results"][0]["factorial_density_projection_grid"]["rho180_K180"]["radius_pull_sigma"] += 0.25
    _rehash_report_and_receipt(out, report=data)
    with pytest.raises(D.D2bIntegrityError, match="numerical value mismatch"):
        D.verify(out / "receipt.json", SOURCE)


def test_forged_claim_and_extra_files_rejected(tmp_path: Path) -> None:
    out = tmp_path / "run"
    D.run(SOURCE, out)
    receipt = json.loads((out / "receipt.json").read_bytes())
    receipt["claims"]["physical_provider_admitted"] = True
    _rehash_report_and_receipt(out, receipt=receipt)
    with pytest.raises(D.D2bIntegrityError, match="claim mismatch"):
        D.verify(out / "receipt.json", SOURCE)
    (out / "fake_holdout.json").write_text("{}")
    with pytest.raises(D.D2bIntegrityError, match="unexpected receipt"):
        D.verify(out / "receipt.json", SOURCE)


def test_frozen_source_never_mutated(diagnostic: dict) -> None:
    a = verify_hist001_source(SOURCE)
    assert a["frozen_files"] == 46 and a["archived_negative_records"] == 3
    assert a["source_lock_sha256"] == diagnostic["source_lock_sha256"]
    assert a["physical_provider_admitted"] is False


def test_reject_invalid_source_or_unpinned_report(tmp_path: Path) -> None:
    with pytest.raises((ValueError, OSError)):
        D.execute(tmp_path)
    with pytest.raises((ValueError, OSError)):
        D.verify(tmp_path / "receipt.json", SOURCE)
