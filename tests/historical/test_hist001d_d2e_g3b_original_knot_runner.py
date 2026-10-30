"""G3b original March 180x120 knot proof contracts and receipt adversaries."""
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
RUNNER = ROOT / "tools/hist001d_d2e_g3b_original_knot_errors.py"
SPEC = importlib.util.spec_from_file_location("hist001d_g3b_runner_test", RUNNER)
assert SPEC is not None and SPEC.loader is not None
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def test_original_March_G3b_depends_on_exact_input_only_preregistration():
    from native_eset.historical.hist001_source import verify_hist001_source

    assert verify_hist001_source(SOURCE)["source_lock_sha256"] == G.SOURCE_SHA256
    assert G.G3A_SHA256 == "28156b62ccd888fbc26d08922d12f075a47eb1e8d2f4a058ee624ee357ec7836"
    assert G._load_g3a().SOURCE_SHA256 == G.SOURCE_SHA256
    r = G._load_preregistration()
    assert len(r["preregistrations"]) == 6
    assert tuple(row["lens_id"] for row in r["preregistrations"]) == G.LENS_IDS
    assert G.ROLES == ("observed_role", "d2d_role")
    assert r["preregistrations"][2]["collision_shift"] is True
    for key in (
        "original_march_all_180_grid_outputs_certified",
        "original_march_arbitrary_radius_numeric_error_certified",
        "interpolated_observed_or_d2d_radius_outputs_certified",
        "original_density_continuum_error_bounded",
        "critical_surface_density_error_bounded",
        "total_numerical_root_error_certified",
        "global_root_uniqueness_certified",
        "mass_outside_finite_domain_bounded",
        "current_native_v172_equivalence_proved",
        "physical_weyl_lensing_derived", "physical_provider_admitted",
        "new_independent_holdout_scored", "original_source_modified",
        "canonical_theory_state_mutated",
    ):
        assert G.CLAIMS[key] is False
    assert G.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"
    assert G.CLAIMS["original_march_120_angle_disk_return_discrepancy_at_12_knots"]
    assert G.CLAIMS["derived_original_march_qeff_discrepancy_at_12_knots"]


def test_original_source_arrays_use_frozen_120_angle_not_D2c(tmp_path):
    """Actual frozen functions on disposable original source, no fit/release."""
    from native_eset.historical.hist001_source import verify_hist001_source
    from native_eset.historical.hist001d_g3b_knot_preregistration import (
        original_source_grid,
    )

    frozen_g3a = G._load_g3a()
    a = (frozen_g3a._load_g2b()._load_g()._load_pinned_f()
         ._load_e()._load_d2e_d()._load_d2e_a())
    d2c = a._load_pinned("hist001d_d2c.py", a.D2C_SHA256)
    copy = tmp_path / "source"
    shutil.copytree(SOURCE, copy)
    verify_hist001_source(copy)
    pack = copy / "swells_pack_v2"
    with d2c.source_modules(pack):
        import solv.run_setA_port_cand as original
        row = next(original._load_tables(pack).iterrows())[1]
        grid = original_source_grid()
        actual = G._source_original_arrays(row, original, grid)
        params = (actual["M_d"], actual["s"], actual["q_d"])
        for index in (2, 3):
            assert actual["disk"][index] == original.projected_disk_mass_exponential(
                float(grid[index]), *params, ntheta=120,
            )
        assert actual["bulge"].shape == (180,)
        assert actual["disk"].shape == (180,)
        assert actual["qeff"].shape == (180,)
        assert np.all(actual["qeff"] > 0)
        assert not np.any(np.isnan(actual["qeff"]))
    verify_hist001_source(copy)


def _test_report():
    return {
        "schema": G.SCHEMA, "status": G.STATUS,
        "claims": dict(G.CLAIMS),
        "registered_knot_evaluation_count": 12,
        "lenses": [{"lens_id": "J0822+1828",
                    "source_bulge_k_matrix_msun_binary64": 1.5}],
    }


def _rebuild_receipt(directory, alter):
    from native_eset.evidence.receipts import canonical_json

    payload = json.loads((directory / "report.json").read_bytes())
    alter(payload)
    raw = canonical_json(payload)
    (directory / "report.json").write_bytes(raw)
    receipt = json.loads((directory / "receipt.json").read_bytes())
    receipt["report_sha256"] = hashlib.sha256(raw).hexdigest()
    encoded = canonical_json(receipt)
    (directory / "receipt.json").write_bytes(encoded)
    (directory / "receipt.sha256").write_text(
        hashlib.sha256(encoded).hexdigest() + "\n", encoding="ascii",
    )


def test_fresh_source_reexecution_rejects_self_rehashed_error_forgery(tmp_path, monkeypatch):
    """A valid self-rehashed receipt remains insufficient as proof."""
    baseline = _test_report()
    monkeypatch.setattr(G, "execute", lambda _: baseline)
    root = tmp_path / "original"
    receipt = G.run(SOURCE, root)
    assert G.verify(root / "receipt.json", SOURCE, receipt["receipt_sha256"])[
        "registered_knot_outputs"] == 12
    forged = tmp_path / "forged"
    shutil.copytree(root, forged)
    _rebuild_receipt(forged, lambda r: r["lenses"][0].__setitem__(
        "source_bulge_k_matrix_msun_binary64", 1.0e99,
    ))
    with pytest.raises(G.G3bError, match="fresh original source"):
        G.verify(forged / "receipt.json", SOURCE)


def test_forged_provider_and_receipt_inventory_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "execute", lambda _: _test_report())
    base = tmp_path / "baseline"
    G.run(SOURCE, base)
    changed = tmp_path / "changed"
    shutil.copytree(base, changed)
    _rebuild_receipt(changed, lambda r: r["claims"].update(
        {"physical_provider_admitted": True},
    ))
    with pytest.raises(G.G3bError, match="forged"):
        G.verify(changed / "receipt.json", SOURCE)
    extra = tmp_path / "extra"
    shutil.copytree(base, extra)
    (extra / "blind_holdout.json").write_text("{}")
    with pytest.raises(G.G3bError, match="inventory"):
        G.verify(extra / "receipt.json", SOURCE)
    with pytest.raises(G.G3bError, match="external expected SHA"):
        G.verify(base / "receipt.json", SOURCE, "0" * 64)


def test_untrusted_registry_and_path_denied(tmp_path, monkeypatch):
    altered = tmp_path / "altered.json"
    altered.write_bytes(G.REGISTRY_PATH.read_bytes() + b"\n")
    monkeypatch.setattr(G, "REGISTRY_PATH", altered)
    with pytest.raises(G.G3bError, match="preregistration bytes"):
        G._load_preregistration()
    monkeypatch.setattr(G, "execute", lambda _: _test_report())
    existing = tmp_path / "already-created"
    existing.mkdir()
    with pytest.raises(G.G3bError, match="existing output"):
        G.run(SOURCE, existing)
