"""G4a source-locked FlatLCDM runner, exact scope, adversarial receipts."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
RUNNER = ROOT / "tools/hist001d_d2e_g4a_flatlcdm_sigma.py"
SPEC = importlib.util.spec_from_file_location("hist001d_g4a_sigma_tests", RUNNER)
assert SPEC is not None and SPEC.loader is not None
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def _synthetic_report():
    return {
        "schema": G.SCHEMA,
        "status": G.STATUS,
        "claims": dict(G.CLAIMS),
        "pointwise_original_sigma_crit_source_return_count": 6,
        "sigma_mathematical_width_target_met_count": 6,
        "lenses": [{"lens_id": "J0822+1828", "source_sigma": 1.25}],
    }


def _mutate_and_rehash(folder, editor):
    from native_eset.evidence.receipts import canonical_json

    report = json.loads((folder / "report.json").read_bytes())
    editor(report)
    payload = canonical_json(report)
    (folder / "report.json").write_bytes(payload)
    receipt = json.loads((folder / "receipt.json").read_bytes())
    receipt["report_sha256"] = hashlib.sha256(payload).hexdigest()
    raw = canonical_json(receipt)
    (folder / "receipt.json").write_bytes(raw)
    (folder / "receipt.sha256").write_text(hashlib.sha256(raw).hexdigest() + "\n")


def test_sha_pinned_original_march_predecessor_and_scientific_firewall():
    from native_eset.historical.hist001_source import verify_hist001_source

    report = verify_hist001_source(SOURCE)
    assert report["source_lock_sha256"] == G.SOURCE_SHA256
    assert report["frozen_files"] == 46
    assert report["archived_negative_records"] == 3
    assert G.G3B_SOURCE_SHA256 == "353694da6a85c8ce0194cb60c5ab0526961b60c332d1b2931d0d186b81b495c7"
    assert G._pinned_g3b().SOURCE_SHA256 == G.SOURCE_SHA256
    G._assert_original_cosmology_files(SOURCE / "swells_pack_v2")
    assert G.CLAIMS["frozen_binary64_flatlcdm_math_sigma_crit_enclosed"] is True
    assert G.CLAIMS["six_historical_source_sigma_outputs_discrepancy_bounded_pointwise"] is True
    for flag in (
        "source_sigma_crit_errors_all_redshifts_certified",
        "source_cosmological_parameter_physical_error_bounded",
        "original_March_all_radius_baryonic_source_error_bounded",
        "all_R_model_root_existence_or_uniqueness_proved",
        "original_source_density_continuum_certified",
        "shadow_mass_outside_finite_domain_bounded",
        "independent_blinded_holdout_scored",
        "physical_weyl_lensing_derived",
        "physical_provider_admitted",
        "current_native_v172_equivalence_proved",
        "canonical_theory_state_mutated",
        "original_source_modified",
    ):
        assert G.CLAIMS[flag] is False
    assert G.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


def test_single_lens_sigma_proof_keeps_source_boundary():
    class Source:
        Om0 = 0.3
        Ode0 = 1.0 - 0.3
        H0 = 70.0

        @staticmethod
        def sigma_crit_msun_per_kpc2(zl, zs):
            from scipy.integrate import quad
            import math

            c, grav, four_pi, mpc = 299792.458, 4.30091e-6, 4.0 * math.pi, 1000.0
            def il(a, b):
                return quad(lambda z: 1.0 / math.sqrt(
                    .3*(1+z)**3 + (.7)), a, b)[0]
            # Deliberately separate source implementation as numerical test only.
            left, right = il(0, zl), il(zl, zs)
            return (c*70/(four_pi*grav*mpc))*(1+zl)*(1/left + 1/right)

    class Constants:
        C_KMS = 299792.458
        G_KPC_KMS2_MSUN = 4.30091e-6
        FOUR_PI = 4.0 * __import__("math").pi
        MPC_IN_KPC = 1000.0

    item = G._single_lens(
        {"lens_id": "J0822+1828", "z_deflector": .1153, "z_source": .871},
        Source(), Constants,
    )
    box = item["math_exact_binary64_scalar_sigma_crit_enclosure"]
    assert box["target_met"]
    assert item["source_sigma_crit_pointwise_discrepancy"][
        "source_returned_inside_target_enclosure"] is True
    assert item["value_actually_returned_by_sha_locked_original_source"] is True
    assert box["frozen_source_bytes_verified"] is False  # proof helper alone
    assert item["cosmological_observational_likelihood_certified"] is False
    assert item["other_redshifts_or_root_map_error_certified"] is False


def test_self_rehashed_numerical_source_discrepancy_forgery_rejected(tmp_path, monkeypatch):
    baseline = _synthetic_report()
    monkeypatch.setattr(G, "execute", lambda _: baseline)
    path = tmp_path / "baseline"
    result = G.run(SOURCE, path)
    assert G.verify(path / "receipt.json", SOURCE, result["receipt_sha256"])[
        "pointwise_source_outputs"] == 6
    forged = tmp_path / "forged"
    shutil.copytree(path, forged)
    _mutate_and_rehash(forged, lambda report: report["lenses"][0].__setitem__(
        "source_sigma", 9.9e99,
    ))
    with pytest.raises(G.G4aError, match="fresh original FlatLCDM"):
        G.verify(forged / "receipt.json", SOURCE)


def test_provider_promotion_and_unauthorized_member_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "execute", lambda _: _synthetic_report())
    baseline = tmp_path / "baseline"
    G.run(SOURCE, baseline)
    forged = tmp_path / "provider"
    shutil.copytree(baseline, forged)
    _mutate_and_rehash(forged, lambda r: r["claims"].update(
        {"physical_provider_admitted": True},
    ))
    with pytest.raises(G.G4aError, match="forged"):
        G.verify(forged / "receipt.json", SOURCE)
    unexpected = tmp_path / "unexpected"
    shutil.copytree(baseline, unexpected)
    (unexpected / "blind_holdout.json").write_text("{}")
    with pytest.raises(G.G4aError, match="inventory"):
        G.verify(unexpected / "receipt.json", SOURCE)
    with pytest.raises(G.G4aError, match="external expected receipt SHA"):
        G.verify(baseline / "receipt.json", SOURCE, "0" * 64)


def test_frozen_source_cosmology_file_tamper_and_output_path_fail_closed(tmp_path, monkeypatch):
    dummy = tmp_path / "swells_pack_v2" / "solv"
    dummy.mkdir(parents=True)
    (dummy / "cosmology.py").write_text("# forged")
    (dummy / "constants.py").write_text("# forged")
    with pytest.raises(G.G4aError, match="original cosmology"):
        G._assert_original_cosmology_files(dummy.parent)
    monkeypatch.setattr(G, "execute", lambda _: _synthetic_report())
    target = tmp_path / "existing"
    target.mkdir()
    with pytest.raises(G.G4aError, match="existing immutable"):
        G.run(SOURCE, target)
