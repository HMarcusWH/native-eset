"""D2e-A root/topology/gradient/domain diagnostic — no theory or holdout promotion."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
TOOL = ROOT / "tools/hist001d_d2e.py"
SPEC = importlib.util.spec_from_file_location("hist001d_d2e_test_mod", TOOL)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


@pytest.fixture(scope="module")
def full_run(tmp_path_factory: pytest.TempPathFactory):
    output = tmp_path_factory.mktemp("hist001d_d2e") / "run"
    receipt = D.run(SOURCE, output)
    report = json.loads((output / "report.json").read_bytes())
    return output, receipt, report


def test_locked_protocol_and_nonpromotion_flags():
    assert D.ROOT_TOPOLOGY_SCAN_POINTS == (45, 181, 721)
    assert D.SOURCE_GRID_POINTS == (180, 360, 720, 1440, 2880, 5760, 11520)
    assert D.SHADOW_CUTOFF_KPC == (80., 100., 120.)
    assert D.FINITE_SOURCE_KPC == (.02, 120.)
    assert D.CLAIMS["historical_fitted_development_regression_only"] is True
    assert D.CLAIMS["shadow_gradient_clipping_absent_on_tested_grids"] is True
    for name in ("global_error_bound_established", "mass_outside_finite_domain_bounded",
                 "root_uniqueness_mathematically_certified", "physical_provider_admitted",
                 "physical_weyl_lensing_derived", "native_v172_equivalence_proved",
                 "new_holdout_scored", "canonical_theory_state_mutated"):
        assert D.CLAIMS[name] is False
    assert D.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"
    assert set(D.D2D_REFERENCE_ROOT_KPC) == set(D.LENS_IDS)


def test_all_original_46_plus_3_frozen_bytes_and_dependency_hashes(full_run):
    from native_eset.historical.hist001_source import verify_hist001_source

    report = full_run[2]
    trust = verify_hist001_source(SOURCE)
    assert trust["source_lock_sha256"] == D.SOURCE_SHA256
    assert trust["frozen_files"] == 46
    assert trust["archived_negative_records"] == 3
    assert report["source_lock_sha256"] == D.SOURCE_SHA256
    assert report["d2c_sha256"] == D.D2C_SHA256
    assert report["d2d_sha256"] == D.D2D_SHA256
    assert report["original_historical_fitted_180_120_passes"] == 6
    assert report["claims"] == D.CLAIMS


def test_sampled_root_scan_separate_from_global_uniqueness_proof(full_run):
    report = full_run[2]
    assert report["root_topology_scan_sizes"] == [45, 181, 721]
    assert "NO_INTERVAL_ENCLOSURE" in report["root_topology_verdict"]
    failed_radius_lenses = []
    for lens in report["lenses"]:
        s = lens["sampled_root_topology"]
        assert abs(s["root_vs_d2d_delta_sigma"]) < 1e-7
        assert abs(s["root_gauss48_delta_sigma"]) < 1e-7
        assert s["global_root_uniqueness_certified"] is False
        assert len(s["scans"]) == 3
        for count, scan in zip(D.ROOT_TOPOLOGY_SCAN_POINTS, s["scans"]):
            assert scan["radial_sample_count"] == count
            assert len(scan["sampled_radii_kpc"]) == count
            assert len(scan["normalized_critical_residual"]) == count
            assert scan["sampled_sign_changes"] == 1
            assert scan["sampled_exact_zeros"] == 0
            assert scan["positive_slope_intervals"] > 0
            assert scan["positive_slope_intervals"] + scan["negative_slope_intervals"] == count-1
        assert s["normalized_root_derivative_estimate_per_kpc"] < 0
        assert s["relative_local_derivative_disagreement"] < 1e-6
        # Observed radius-only screen; don't silently assert physical lens validity.
        observed_radius = s["root_from_721_scan_kpc"]
        ref = s["d2d_11520_reference_root_kpc"]
        assert abs(observed_radius-ref) < 1e-7
        if lens["lens_id"] in {"J0822+1828", "J1021+2028", "J1111+2234"}:
            failed_radius_lenses.append(lens["lens_id"])
    assert set(failed_radius_lenses) == {
        "J0822+1828", "J1021+2028", "J1111+2234",
    }


def test_original_density_clips_inactive_only_on_source_sampled_grids(full_run):
    report = full_run[2]
    for lens in report["lenses"]:
        records = lens["gradient_clipping_and_anchor_tests"]
        assert [x["radial_points"] for x in records] == list(D.SOURCE_GRID_POINTS)
        for record in records:
            assert record["negative_preclip_mshadow_count"] == 0
            assert record["negative_preclip_dm_dr_count"] == 0
            assert record["zero_after_clip_rho_count"] == 0
            assert record["source_rho_values_nonnegative"] is True
            assert record["min_preclip_dm_dr_msun_per_kpc"] > 0
        # Crucial: high-grid integrated root stability does not give pointwise
        # convergence near source inner boundary under coarse interpolation.
        coarse, fine = records[0], records[-1]
        rho_c = coarse["sampled_source_rho_at_anchors_msun_per_kpc3"]
        rho_f = fine["sampled_source_rho_at_anchors_msun_per_kpc3"]
        assert 25_000 < rho_c[0]/rho_f[0] < 55_000
        assert 130 < rho_c[1]/rho_f[1] < 160
        assert abs(rho_c[3]/rho_f[3]-1) < .01


def test_outer_source_cutoffs_are_counterfactual_not_bounds(full_run):
    report = full_run[2]
    assert report["domain_verdict"] == "SOURCE_PROVIDES_NO_MASS_CONTINUATION_OUTSIDE_0.02_TO_120_KPC"
    for lens in report["lenses"]:
        top = lens["sampled_root_topology"]
        assert top["mass_beyond_120kpc_source_constrained"] is False
        assert top["shadow_cutoff_existing_domain_empirical_screen_only"] is True
        rows = top["original_shadow_upper_cutoff_counterfactuals"]
        assert [x["shadow_density_max_kpc"] for x in rows] == [80., 100., 120.]
        assert rows[-1]["new_numerical_counterfactual"] is False
        assert abs(rows[-1]["root_shift_vs_full_sigma"]) < 1e-8
        assert abs(rows[0]["root_shift_vs_full_sigma"]) < .021
        assert abs(rows[1]["root_shift_vs_full_sigma"]) < .007
        assert rows[0]["new_numerical_counterfactual"] is True


def test_immutable_receipt_comparison_logic_with_source_verified_reference(
    full_run, monkeypatch,
):
    path, expected, source_report = full_run
    # Unit-level comparison is injected from the ONE source-verified fixture run.
    # The CI workflow separately calls the real CLI --verify in a new process,
    # which reexecutes all six sources and cannot be satisfied by this mock.
    monkeypatch.setattr(D, "execute", lambda _source: source_report)
    result = D.verify(path/"receipt.json", SOURCE, expected["receipt_sha256"])
    assert result["development_lenses_reexecuted"] == 6
    assert result["scan_sizes"] == [45, 181, 721]
    assert result["root_uniqueness_certified"] is False
    assert result["unmeasured_outer_mass_bounded"] is False
    assert result["claims"] == D.CLAIMS
    with pytest.raises(D.D2eError, match="destination exists"):
        D.run(SOURCE, path)


def _repair_hashes(out: Path, edit):
    from native_eset.evidence.receipts import canonical_json
    report = json.loads((out/"report.json").read_bytes())
    edit(report)
    report_raw = canonical_json(report)
    (out/"report.json").write_bytes(report_raw)
    rec = json.loads((out/"receipt.json").read_bytes())
    rec["report_sha256"] = hashlib.sha256(report_raw).hexdigest()
    receipt_raw = canonical_json(rec)
    (out/"receipt.json").write_bytes(receipt_raw)
    (out/"receipt.sha256").write_text(
        hashlib.sha256(receipt_raw).hexdigest()+"\n", encoding="ascii",
    )


def test_repaired_selfhashed_numeric_forgery_rejected_by_replay_comparator(tmp_path, full_run, monkeypatch):
    directory = tmp_path / "tampered-numeric"
    shutil.copytree(full_run[0], directory)

    def change(report):
        report["lenses"][0]["sampled_root_topology"]["scans"][2][
            "normalized_critical_residual"
        ][350] += 0.01

    _repair_hashes(directory, change)
    monkeypatch.setattr(D, "execute", lambda _source: full_run[2])
    with pytest.raises(D.D2eError, match="source-reexecution value mismatch"):
        D.verify(directory/"receipt.json", SOURCE)


def test_selfhashed_false_provider_claim_fails_closed(tmp_path, full_run):
    directory = tmp_path / "tampered-claim"
    shutil.copytree(full_run[0], directory)
    _repair_hashes(directory, lambda r: r["claims"].update({"physical_provider_admitted": True}))
    with pytest.raises(D.D2eError, match="claim forgery"):
        D.verify(directory/"receipt.json", SOURCE)


def test_receipt_inventory_external_hash_and_symlink_fail_closed(tmp_path, full_run):
    base = full_run[0]
    with pytest.raises(D.D2eError, match="externally pinned"):
        D.verify(base/"receipt.json", SOURCE, "0"*64)
    directory = tmp_path/"extra"
    shutil.copytree(base, directory)
    (directory/"fabricated_holdout.json").write_text("{}")
    with pytest.raises(D.D2eError, match="inventory"):
        D.verify(directory/"receipt.json", SOURCE)
    link = tmp_path/"source-link"
    link.symlink_to(SOURCE, target_is_directory=True)
    with pytest.raises(D.D2eError, match="symlinked"):
        D.execute(link)


def test_unregistered_cutoff_and_dependency_provenance_rejected(full_run):
    with pytest.raises(D.D2eError, match="unregistered"):
        D._truncated_grid([.02, .03, 120], [1.,1.,1.], 99.)
    with pytest.raises(D.D2eError, match="dependency changed"):
        D._load_pinned("hist001d_d2d.py", "0"*64)
