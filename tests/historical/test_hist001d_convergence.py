"""HIST001D: original-source mesh sensitivity, immutable diagnostic receipt, claim caps."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
FILE = ROOT / "tools/hist001d_convergence.py"
SPEC = importlib.util.spec_from_file_location("hist001d_convergence", FILE)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


def test_unfitted_historical_protocol_and_holdout_firewall() -> None:
    assert D.CANDIDATE == "ra0_gated_geometry_sigmoid_reg_v2"
    assert D.REGIMES == (
        ("radial_coarse", 90, 120),
        ("frozen_baseline", 180, 120),
        ("radial_fine", 360, 120),
        ("angle_coarse", 180, 60),
        ("angle_fine", 180, 240),
        ("combined_fine", 360, 240),
    )
    spec = json.loads((ROOT / "registry/hist001d_holdout_preregistration_v1.json").read_text())
    assert spec["schema"] == "HIST001D_NONCANONICAL_HOLDOUT_PLAN_V1"
    assert spec["holdout_status"] == "NOT_SELECTED_NOT_FROZEN_NOT_SCORED"
    assert spec["proposed_holdout_ids"] == []
    assert spec["outcomes_inspected_for_selection"] is False
    assert spec["historical_dev_lens_ids"] == list(D.LENS_IDS)
    assert spec["physical_provider_admitted"] is False
    assert spec["native_v172_equivalence_proved"] is False
    assert D.CLAIM["empirical_validation"] == "NOT_ESTABLISHED"


def test_reject_unregistered_numerical_pair() -> None:
    with pytest.raises(D.Hist001DIntegrityError, match="unregistered"):
        D.evaluate(SOURCE / "swells_pack_v2", 235, 120)


def test_original_source_reproduction_and_immutable_receipt(tmp_path: Path) -> None:
    result = D.run(SOURCE, tmp_path / "run")
    summaries = result["summary"]
    assert [item["joint_passes"] for item in summaries] == [2, 6, 3, 6, 6, 3]
    assert summaries[2]["changed_joint_pass_lenses"] == [
        "J0822+1828", "J1021+2028", "J1111+2234"
    ]
    assert summaries[5]["changed_joint_pass_lenses"] == summaries[2][
        "changed_joint_pass_lenses"
    ]
    assert result["claim_boundary"] == D.CLAIM
    verified = D.verify_receipt(
        tmp_path / "run/receipt.json", SOURCE,
        expected_sha256=result["receipt_sha256"],
    )
    assert verified["original_rows_reexecuted"] == 36
    assert verified["claim_boundary"] == D.CLAIM
    with pytest.raises(FileExistsError):
        D.run(SOURCE, tmp_path / "run")


def test_modified_self_rehashed_numerical_results_fail_source_replay(
    tmp_path: Path,
) -> None:
    from native_eset.evidence.receipts import canonical_json

    out = tmp_path / "run"
    D.run(SOURCE, out)
    report_path = out / "report.json"
    obj = json.loads(report_path.read_bytes())
    obj["results"]["combined_fine"][0]["radius_pull_sigma"] += 0.75
    obj["summary"] = D.summarize(obj["results"])
    report_path.write_bytes(canonical_json(obj))
    receipt_path = out / "receipt.json"
    rec = json.loads(receipt_path.read_bytes())
    rec["report_sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
    receipt_path.write_bytes(canonical_json(rec))
    (out / "receipt.sha256").write_text(
        hashlib.sha256(receipt_path.read_bytes()).hexdigest() + "\n"
    )
    with pytest.raises(D.Hist001DIntegrityError, match="not reproduced"):
        D.verify_receipt(receipt_path, SOURCE)


def test_claim_forgery_with_rehashed_files_still_rejected(tmp_path: Path) -> None:
    from native_eset.evidence.receipts import canonical_json

    out = tmp_path / "run"
    D.run(SOURCE, out)
    receipt_path = out / "receipt.json"
    rec = json.loads(receipt_path.read_bytes())
    rec["claim_boundary"]["physical_provider_admitted"] = True
    receipt_path.write_bytes(canonical_json(rec))
    (out / "receipt.sha256").write_text(
        hashlib.sha256(receipt_path.read_bytes()).hexdigest() + "\n"
    )
    with pytest.raises(D.Hist001DIntegrityError):
        D.verify_receipt(receipt_path, SOURCE)


def test_unexpected_member_rejected_even_if_receipt_unchanged(tmp_path: Path) -> None:
    out = tmp_path / "run"
    D.run(SOURCE, out)
    (out / "fake_heldout_results.json").write_text("{}")
    with pytest.raises(D.Hist001DIntegrityError, match="missing/extra"):
        D.verify_receipt(out / "receipt.json", SOURCE)


def test_source_not_modified_by_grid_study(tmp_path: Path) -> None:
    from native_eset.historical.hist001_source import verify_hist001_source

    before = verify_hist001_source(SOURCE)
    D.run(SOURCE, tmp_path / "run")
    after = verify_hist001_source(SOURCE)
    assert after["source_lock_sha256"] == before["source_lock_sha256"]
    assert after["frozen_files"] == 46
    assert after["archived_negative_records"] == 3


def test_original_slow_api_agrees_with_finer_grid_without_fitting() -> None:
    """Independent source-path check, not a new scientific validation suite."""
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    pack = SOURCE / "swells_pack_v2"
    sys.path.insert(0, str(pack))
    try:
        import solv.run_setA_port_cand as original

        anchor, _ = original._build_anchor(pack)
        gate = original._candidate_gate_config(anchor, candidate_name=D.CANDIDATE)
        expected = D.evaluate(pack, 360, 120)
        original_linspace = original.np.linspace

        def fine_grid(start, stop, num=50, *args, **kwargs):
            if start == 0.02 and stop == 120.0 and num == 180:
                return original_linspace(start, stop, 360, *args, **kwargs)
            return original_linspace(start, stop, num, *args, **kwargs)

        original.np.linspace = fine_grid
        try:
            slow = original.evaluate_portability_dataframe(pack, gate)
        finally:
            original.np.linspace = original_linspace
        assert list(slow.lens_id) == list(D.LENS_IDS)
        for actual, source_row in zip(expected, slow.to_dict("records")):
            assert actual["radius_pull_sigma"] == pytest.approx(
                source_row["einstein_radius_pull_sigma"], abs=1e-9
            )
            assert actual["mass_pull_sigma"] == pytest.approx(
                source_row["mass_pull_sigma"], abs=1e-9
            )
            assert actual["joint_pass"] == bool(source_row["both_pass"])
    finally:
        sys.path.remove(str(pack))
        sys.dont_write_bytecode = old
