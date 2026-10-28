"""Independently pinned source checks must fail before original code execution."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

import native_eset.historical.hist001_approved as anchor
from native_eset.historical import HistoricalSourceIntegrityError, verify_hist001_source

REPO = Path(__file__).resolve().parents[2]
ORIGINAL = REPO / "research/legacy/hist001"


def duplicate_original(tmp_path: Path) -> Path:
    out = tmp_path / "hist001"
    shutil.copytree(ORIGINAL, out)
    return out


def test_original_source_exact_inventory_lens_set_and_nonpromotion() -> None:
    report = verify_hist001_source(ORIGINAL)
    assert report["status"] == "HIST001_FROZEN_SOURCE_BYTES_VERIFIED_NO_EXECUTION"
    assert report["frozen_files"] == 46
    assert report["archived_negative_records"] == 3
    assert report["original_archive_sha256"] == "283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e"
    assert report["source_lock_sha256"] == anchor.SOURCE_LOCK_DIGEST
    assert report["lens_ids"] == ["J0822+1828", "J0915+4211", "J0930+2855",
                                   "J1021+2028", "J1111+2234", "J1135+3720"]
    assert report["source_history"] == "ORIGINAL_FITTED_CALIBRATION"
    assert report["data_use"] == "REGRESSION"
    assert report["capability_executable"] is False
    assert report["physical_provider_admitted"] is False
    assert report["current_native_v172_equivalence_proved"] is False
    assert report["empirical_validation"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("target", [
    "swells_pack_v2/solv/dmalane.py",
    "swells_pack_v2/configs/j2141_test1_axisy_1689e9.json",
    "swells_pack_v2/cleaned/lens_set_A_run_fo_74bb5e.csv",
    "swells_pack_v2/validation/j2141_regression_b5afd5.json",
    "archived_rangefinder/reg_v2_fixed_law_geometry_morphology_nuisance_survival_curve_summary.json",
])
def test_tampered_original_or_negative_fixture_is_denied(tmp_path: Path, target: str) -> None:
    out = duplicate_original(tmp_path)
    p = out / target
    p.write_bytes(p.read_bytes() + b"\nforged scientific result\n")
    with pytest.raises(HistoricalSourceIntegrityError):
        verify_hist001_source(out)


def test_forged_lock_and_modified_solver_pair_cannot_be_approved(tmp_path: Path) -> None:
    out = duplicate_original(tmp_path)
    file = out / "swells_pack_v2/solv/dmalane.py"
    file.write_bytes(file.read_bytes() + b"\n# modified implementation\n")
    lockfile = out / "SOURCE_LOCK.json"
    lock = json.loads(lockfile.read_text(encoding="utf-8"))
    lock["source_filenames_sha256"]["solv/dmalane.py"] = hashlib.sha256(file.read_bytes()).hexdigest()
    lockfile.write_text(json.dumps(lock, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(HistoricalSourceIntegrityError, match="SOURCE_LOCK.json"):
        verify_hist001_source(out)


@pytest.mark.parametrize("change", ["extra_file", "missing_file", "extra_directory", "missing_root_element"])
def test_source_inventory_changes_rejected(tmp_path: Path, change: str) -> None:
    out = duplicate_original(tmp_path)
    if change == "extra_file":
        (out / "swells_pack_v2/solv/injected.py").write_text("# fake\n", encoding="utf-8")
    elif change == "missing_file":
        (out / "swells_pack_v2/solv/dmalane.py").unlink()
    elif change == "extra_directory":
        (out / "unexpected").mkdir()
    else:
        shutil.rmtree(out / "archived_rangefinder")
    with pytest.raises(HistoricalSourceIntegrityError):
        verify_hist001_source(out)


def test_packaged_trust_anchor_cannot_be_replaced_by_caller(monkeypatch: pytest.MonkeyPatch) -> None:
    baseline = anchor.approved_hist001()
    assert baseline["source_lock_sha256"] == anchor.SOURCE_LOCK_DIGEST
    mutated = dict(baseline)
    mutated["physical_provider_admitted"] = True
    monkeypatch.setattr(anchor, "_read_packaged_anchor", lambda: (json.dumps(mutated) + "\n").encode())
    with pytest.raises(HistoricalSourceIntegrityError, match="approved-source anchor changed"):
        anchor.approved_hist001()


def test_missing_and_symlinked_root_rejected(tmp_path: Path) -> None:
    with pytest.raises(HistoricalSourceIntegrityError):
        verify_hist001_source(tmp_path / "nonexistent")
    link = tmp_path / "link"
    try:
        link.symlink_to(ORIGINAL, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("This environment cannot create source symlinks")
    with pytest.raises(HistoricalSourceIntegrityError, match="non-symlink"):
        verify_hist001_source(link)


def test_symlinked_original_payload_rejected(tmp_path: Path) -> None:
    out = duplicate_original(tmp_path)
    path = out / "swells_pack_v2/solv/dmalane.py"
    backup = tmp_path / "real_solver.py"
    shutil.copy2(path, backup)
    path.unlink()
    try:
        path.symlink_to(backup)
    except (OSError, NotImplementedError):
        pytest.skip("This environment cannot create source symlinks")
    with pytest.raises(HistoricalSourceIntegrityError):
        verify_hist001_source(out)
