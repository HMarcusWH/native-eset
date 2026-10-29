"""HIST001D/D2d: fully radius-dependent structured lensing *numerical* audit.

Six original fitted lenses, not holdout data. Source SHA remains immutable.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
SCRIPT = ROOT / "tools/hist001d_d2d.py"
ref = importlib.util.spec_from_file_location("hist001d_d2d", SCRIPT)
assert ref is not None and ref.loader is not None
D = importlib.util.module_from_spec(ref)
ref.loader.exec_module(D)


@pytest.fixture(scope="module")
def original_run(tmp_path_factory: pytest.TempPathFactory):
    out = tmp_path_factory.mktemp("hist001d_d2d_numerical") / "run"
    receipt = D.run(SOURCE, out)
    return out, receipt, json.loads((out / "report.json").read_bytes())


def test_protocol_is_frozen_and_physically_nonpromoting() -> None:
    assert D.SOURCE_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert D.SOURCE_GRID_POINTS == (180, 360, 720, 1440, 2880, 5760, 11520)
    assert D.ROOT_SCAN_POINTS == 45
    assert D.ANGULAR_POINTS == 1024
    assert D.ROOT_SIGMA_SCREEN == 0.05
    assert D.MASS_RELATIVE_SCREEN == 0.0005
    assert D.CLAIMS["new_numerical_execution_identity"] is True
    assert D.CLAIMS["historical_fitted_development_regression_only"] is True
    assert D.CLAIMS["new_holdout_scored"] is False
    assert D.CLAIMS["physical_provider_admitted"] is False
    assert D.CLAIMS["physical_weyl_lensing_derived"] is False
    assert D.CLAIMS["native_v172_equivalence_proved"] is False
    assert D.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


def test_analytic_reference_crosschecks_at_fixed_development_apertures(original_run) -> None:
    _, _, report = original_run
    for lens in report["new_numerical_identity_results"]:
        assert abs(lens["independent_bulge_reference_relative_error"]) < 2e-9
        assert abs(lens["independent_disc_reference_relative_error"]) < 1e-8
        for grid in lens["grid_results"]:
            check = grid["independent_integration_crosscheck"]
            if check is not None:
                assert abs(check["shadow_gauss24_48_relative"]) < 5e-10
                assert abs(check["adaptive_bulge_vs_gauss_relative"]) < 2e-9
                assert abs(check["periodic_disc_vs_adaptive_relative"]) < 1e-8
                if check["adaptive_shadow_vs_gauss48_relative"] is not None:
                    assert abs(check["adaptive_shadow_vs_gauss48_relative"]) < 5e-9


def test_original_fitted_six_and_new_corrected_three_remain_separate(original_run) -> None:
    _, _, report = original_run
    assert report["status"] == D.STATUS
    assert report["source_model_role"] == "EXISTING_SIX_FITTED_SET_A_DEVELOPMENT_LENSES"
    assert [x["lens_id"] for x in report["new_numerical_identity_results"]] == list(D.LENS_IDS)
    assert sum(x["original_frozen_180_120_joint_pass"]
               for x in report["historical_original_reference"]) == 6
    assert all(len(x["grid_results"]) == 7 for x in report["new_numerical_identity_results"])
    for i, n in enumerate(D.SOURCE_GRID_POINTS):
        fail = {lens["lens_id"] for lens in report["new_numerical_identity_results"]
                if not lens["grid_results"][i]["joint_pass_abs_le_2sigma"]}
        assert fail == {"J0822+1828", "J1021+2028", "J1111+2234"}, n
    final_pulls = [x["grid_results"][-1]["einstein_radius_pull_sigma"]
                   for x in report["new_numerical_identity_results"]]
    assert final_pulls == pytest.approx(
        [3.176947, 0.577819, -0.615349, 2.720688, 3.142609, 1.651731], abs=5e-4,
    )
    assert report["claims"] == D.CLAIMS
    assert report["numeric_screen"]["all_six_pass"] is True


def test_mass_and_root_residuals_with_fine_grid_engineering_screen(original_run) -> None:
    _, _, report = original_run
    for lens in report["new_numerical_identity_results"]:
        assert lens["two_step_root_and_mass_engineering_screen"] is True
        assert all(abs(delta) < 0.05 for delta in lens["latest_two_root_delta_sigma"])
        assert all(abs(delta) < 0.0005 for delta in lens["latest_two_observed_mass_relative"])
        for record in lens["grid_results"]:
            assert record["number_of_sign_crossings"] == 1
            assert record["root_critical_relative_residual"] < D.ROOT_EPS_ABSOLUTE
            assert record["root_components_msun"]["total"] == pytest.approx(
                sum(record["root_components_msun"][name]
                    for name in ("bulge", "disk", "structured_shadow"))
            )
            assert 0 < record["root_qeff"] <= 1
    assert report["numeric_screen"]["classification"] == (
        "FIXED_BEFORE_LOCAL_RUN_NOT_EXTERNAL_PREREG_NOT_RIGOROUS_BOUND"
    )


def test_invalid_bulge_quadrature_is_rejected() -> None:
    with pytest.raises(D.D2dError, match="unregistered"):
        D.alternate_finite_hernquist(1.0, 1e11, 2.0, order=17)
    with pytest.raises(D.D2dError, match="invalid independent"):
        D.alternate_finite_hernquist(121.0, 1e11, 2.0)


def test_receipt_verifier_performs_fresh_original_source_reexecution(original_run) -> None:
    out, summary, _ = original_run
    result = D.verify(out / "receipt.json", SOURCE, summary["receipt_sha256"])
    assert result["status"] == "HIST001D_D2D_SOURCE_REEXECUTION_PASS_NO_ADMISSION"
    assert result["six_fitted_lenses"] == 6
    assert result["source_grids"] == 7
    assert result["claims"] == D.CLAIMS


def _rewrite_report_and_receipt(folder: Path, update) -> None:
    from native_eset.evidence.receipts import canonical_json

    report = json.loads((folder / "report.json").read_bytes())
    update(report)
    raw_report = canonical_json(report)
    (folder / "report.json").write_bytes(raw_report)
    receipt = json.loads((folder / "receipt.json").read_bytes())
    receipt["report_sha256"] = hashlib.sha256(raw_report).hexdigest()
    raw_receipt = canonical_json(receipt)
    (folder / "receipt.json").write_bytes(raw_receipt)
    (folder / "receipt.sha256").write_text(
        hashlib.sha256(raw_receipt).hexdigest() + "\n", encoding="ascii",
    )


def test_self_rehashed_numerical_forgery_rejected(tmp_path: Path, original_run) -> None:
    reference, _, _ = original_run
    out = tmp_path / "forged"
    shutil.copytree(reference, out)

    def change(report):
        report["new_numerical_identity_results"][2]["grid_results"][3][
            "predicted_einstein_radius_kpc"
        ] += 0.19

    _rewrite_report_and_receipt(out, change)
    with pytest.raises(D.D2dError, match="numerical reexecution differs"):
        D.verify(out / "receipt.json", SOURCE)


def test_self_rehashed_physical_provider_claim_rejected(tmp_path: Path, original_run) -> None:
    reference, _, _ = original_run
    out = tmp_path / "forged"
    shutil.copytree(reference, out)

    def change(report):
        report["claims"]["physical_provider_admitted"] = True

    _rewrite_report_and_receipt(out, change)
    with pytest.raises(D.D2dError, match="claim forgery"):
        D.verify(out / "receipt.json", SOURCE)


def test_malformed_extra_member_and_external_sha_are_rejected(tmp_path: Path, original_run) -> None:
    reference, _, _ = original_run
    out = tmp_path / "extra"
    shutil.copytree(reference, out)
    (out / "fabricated_holdout.json").write_text("{}", encoding="utf-8")
    with pytest.raises(D.D2dError, match="inventory mismatch"):
        D.verify(out / "receipt.json", SOURCE)
    with pytest.raises(D.D2dError, match="externally pinned"):
        D.verify(reference / "receipt.json", SOURCE, "0" * 64)


def test_original_source_46_plus_three_immutable_and_path_guard(tmp_path: Path, original_run) -> None:
    from native_eset.historical.hist001_source import verify_hist001_source

    assert verify_hist001_source(SOURCE)["source_lock_sha256"] == D.SOURCE_SHA256
    assert verify_hist001_source(SOURCE)["frozen_files"] == 46
    assert verify_hist001_source(SOURCE)["archived_negative_records"] == 3
    with pytest.raises(D.D2dError, match="cannot write into source"):
        D.run(SOURCE, SOURCE / "forbidden_source_output")
    alias = tmp_path / "source_symlink"
    try:
        alias.symlink_to(SOURCE, target_is_directory=True)
    except OSError:
        pytest.skip("Windows symlinks not permitted")
    with pytest.raises(D.D2dError, match="symlink"):
        D.run(alias, tmp_path / "new-output")
