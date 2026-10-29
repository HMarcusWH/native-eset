"""HIST001D/D2c: independent quadrature and frozen nonpromoting receipt."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
SCRIPT = ROOT / "tools/hist001d_d2c.py"
SPEC = importlib.util.spec_from_file_location("hist001d_d2c", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


@pytest.fixture(scope="module")
def source_report(tmp_path_factory: pytest.TempPathFactory):
    folder = tmp_path_factory.mktemp("hist001d_d2c_source_report") / "original"
    result = D.run(SOURCE, folder)
    return folder, result


def test_source_sha_and_physical_nonpromotion() -> None:
    assert D.SOURCE_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert D.RADIAL_GRIDS == (180, 360, 720, 1440, 2880, 5760, 11520)
    assert D.GAUSS_ORDERS == (24, 48)
    assert D.CLAIMS["physical_provider_admitted"] is False
    assert D.CLAIMS["new_holdout_scored"] is False
    assert D.CLAIMS["physical_weyl_lensing_derived"] is False
    assert D.CLAIMS["native_v172_equivalence_proved"] is False
    assert D.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


def test_piecewise_constant_full_aperture_exact_integral() -> None:
    radius = np.linspace(1.0, 10.0, 53)
    density = np.full_like(radius, 2.0)
    expect = 4 * np.pi * 2 * (10**3 - 1) / 3
    assert D.integrated_shadow_piecewise_linear(10.0, radius, density) == pytest.approx(expect, rel=2e-14)
    assert D.integrated_shadow_piecewise_linear(0.0, radius, density) == 0.0
    for order in (24, 48):
        actual = D.integrated_shadow_piecewise_linear(5.0, radius, density, order=order)
        adaptive = D.adaptive_shadow_piecewise_linear(5.0, radius, density)
        assert actual == pytest.approx(adaptive, rel=1e-10)


def test_negative_density_and_unregistered_quadrature_rejected() -> None:
    r = np.linspace(0.02, 120, 40)
    rho = np.ones_like(r)
    with pytest.raises(D.D2cIntegrityError, match="unregistered"):
        D.integrated_shadow_piecewise_linear(3.0, r, rho, order=7)
    rho[1] = -1
    with pytest.raises(D.D2cIntegrityError, match="invalid finite"):
        D.integrated_shadow_piecewise_linear(3.0, r, rho)


def test_complete_six_lens_frozen_grid_projection_and_cauchy(source_report) -> None:
    folder, summary = source_report
    assert summary["cases"] == 6 and summary["radial_grids"] == 7
    report = json.loads((folder / "report.json").read_bytes())
    assert tuple(x["lens_id"] for x in report["results"]) == D.LENS_IDS
    assert report["data_role"] == "SIX_FITTED_DEVELOPMENT_LENSES_NO_HOLDOUT"
    assert report["cauchy_engineering_screen"]["classification"].startswith("RETROSPECTIVE_")
    assert report["cauchy_engineering_screen"]["not_a_rigorous_global_or_physical_error_bound"] is True
    biases = []
    for lens in report["results"]:
        values = lens["mass_by_source_density_grid"]
        assert [x["radial_grid_points"] for x in values] == list(D.RADIAL_GRIDS)
        assert lens["latest_two_pass_0p05_percent_screen"] is True
        assert lens["second_order_tail_heuristic_is_proof"] is False
        assert len(lens["latest_two_cauchy_relative_abs"]) == 2
        assert max(lens["latest_two_cauchy_relative_abs"]) <= 5e-4
        assert max(abs(x["gauss24_vs_gauss48_fractional_difference"]) for x in values) < 1e-9
        assert all(abs(x["adaptive_scipy_vs_gauss48_fractional_difference"]) < 1e-9
                   for x in values[:2])
        assert all(x["negative_density_bins"] == 0 for x in values)
        biases.append(values[0]["source_K_fractional_bias_vs_independent"])
    assert all(0 < x < 0.05 for x in biases)
    assert max(biases) > 0.03
    assert report["claims"] == D.CLAIMS


def test_independent_receipt_reexecutes_all_grids(source_report) -> None:
    folder, summary = source_report
    validated = D.verify(folder / "receipt.json", SOURCE, summary["receipt_sha256"])
    assert validated["six_development_lenses_recomputed"] == 6
    assert validated["density_grids_each"] == 7
    assert validated["claims"] == D.CLAIMS


def test_self_rehashed_forged_shadow_mass_detected(tmp_path: Path, source_report) -> None:
    from native_eset.evidence.receipts import canonical_json

    src, _ = source_report
    dest = tmp_path / "forged"
    shutil.copytree(src, dest)
    report_path = dest / "report.json"
    altered = json.loads(report_path.read_bytes())
    altered["results"][2]["mass_by_source_density_grid"][3][
        "independent_finite_piecewise_linear_shadow_msun"
    ] += 5e9
    report_path.write_bytes(canonical_json(altered))
    receipt_path = dest / "receipt.json"
    receipt = json.loads(receipt_path.read_bytes())
    receipt["report_sha256"] = hashlib.sha256(report_path.read_bytes()).hexdigest()
    receipt_path.write_bytes(canonical_json(receipt))
    (dest / "receipt.sha256").write_text(hashlib.sha256(receipt_path.read_bytes()).hexdigest() + "\n")
    with pytest.raises(D.D2cIntegrityError):
        D.verify(receipt_path, SOURCE)


def test_self_rehashed_provider_forgery_rejected(tmp_path: Path, source_report) -> None:
    from native_eset.evidence.receipts import canonical_json

    source, _ = source_report
    dest = tmp_path / "forged"
    shutil.copytree(source, dest)
    path = dest / "receipt.json"
    receipt = json.loads(path.read_bytes())
    receipt["claims"]["physical_provider_admitted"] = True
    path.write_bytes(canonical_json(receipt))
    (dest / "receipt.sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest() + "\n")
    with pytest.raises(D.D2cIntegrityError, match="promotion"):
        D.verify(path, SOURCE)


def test_extra_member_and_bad_external_sha_rejected(tmp_path: Path, source_report) -> None:
    source, _ = source_report
    dest = tmp_path / "extra"
    shutil.copytree(source, dest)
    (dest / "fake_holdout.json").write_text("{}")
    with pytest.raises(D.D2cIntegrityError, match="unexpected"):
        D.verify(dest / "receipt.json", SOURCE)
    with pytest.raises(D.D2cIntegrityError, match="external"):
        D.verify(source / "receipt.json", SOURCE, "0" * 64)


def test_frozen_source_unchanged_by_reexecution(source_report) -> None:
    from native_eset.historical.hist001_source import verify_hist001_source

    assert verify_hist001_source(SOURCE)["source_lock_sha256"] == D.SOURCE_SHA256
    assert verify_hist001_source(SOURCE)["frozen_files"] == 46
    assert verify_hist001_source(SOURCE)["archived_negative_records"] == 3


def test_no_output_overlap_and_untrusted_original_symlink(tmp_path: Path) -> None:
    with pytest.raises(D.D2cIntegrityError, match="overlaps"):
        D.run(SOURCE, SOURCE / "should-never-exist")
    link = tmp_path / "untrusted-source"
    try:
        link.symlink_to(SOURCE, target_is_directory=True)
    except OSError:
        pytest.skip("Windows symlink permission unavailable")
    with pytest.raises(D.D2cIntegrityError):
        D.run(link, tmp_path / "output")
