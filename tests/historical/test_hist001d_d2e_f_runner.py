"""D2e-F frozen March original source and adversarial evidence controls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/"research/legacy/hist001"
SCRIPT = ROOT/"tools/hist001d_d2e_f_shadow_guard.py"
SPEC = importlib.util.spec_from_file_location("d2e_f_source_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)


def test_frozen_identity_and_unpromoted_claims():
    assert F.SOURCE_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert F.D2E_E_SHA256 == "1b718e1b3fee24b8f0bb85da7dfe8ddf067460319f22cfc11bbf0f5961a8f1f6"
    assert F.RADIAL_POINTS == 11520
    assert F.GUARD_FRACTION == .02
    assert F.CLAIMS["finite_discrete_shadow_mass_all_apertures_in_reported_band_enclosed"] is True
    assert F.CLAIMS["continuous_baryonic_mass_box_certified"] is False
    for label in (
        "qeff_root_map_unconditionally_certified",
        "d2e_b_total_mass_1e6_assumption_proved",
        "global_root_uniqueness_mathematically_certified",
        "global_model_numerical_error_bound_established",
        "mass_outside_finite_domain_bounded",
        "physical_weyl_lensing_derived",
        "physical_provider_admitted",
        "native_v172_equivalence_proved",
        "new_holdout_scored",
    ):
        assert F.CLAIMS[label] is False
    assert F.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


def test_original_46_plus_three_source_and_e_module_pin():
    from native_eset.historical.hist001_source import verify_hist001_source

    original = verify_hist001_source(SOURCE)
    assert original["source_lock_sha256"] == F.SOURCE_SHA256
    assert original["frozen_files"] == 46
    assert original["archived_negative_records"] == 3
    e = F._load_e()
    assert e.SOURCE_SHA256 == F.SOURCE_SHA256
    assert e.CLAIMS["root_uniqueness_mathematically_certified"] is False


def _rehashed_forgery(directory, modifier):
    from native_eset.evidence.receipts import canonical_json

    report = json.loads((directory/"report.json").read_bytes())
    modifier(report)
    report_raw = canonical_json(report)
    (directory/"report.json").write_bytes(report_raw)
    receipt = json.loads((directory/"receipt.json").read_bytes())
    receipt["report_sha256"] = hashlib.sha256(report_raw).hexdigest()
    raw = canonical_json(receipt)
    (directory/"receipt.json").write_bytes(raw)
    (directory/"receipt.sha256").write_text(hashlib.sha256(raw).hexdigest()+"\n")


def test_source_reexecution_rejects_self_rehashed_numeric_forgery(tmp_path, monkeypatch):
    model = {
        "schema": F.SCHEMA,
        "status": F.STATUS,
        "claims": dict(F.CLAIMS),
        "lenses": [{"lens_id":"J0822+1828","normalized_guard_test":[.1,-.1]}],
        "certified_discrete_shadow_aperture_bands": 1,
    }
    monkeypatch.setattr(F,"execute",lambda _source:model)
    destination = tmp_path/"baseline"
    result = F.run(SOURCE,destination)
    checked = F.verify(destination/"receipt.json",SOURCE,result["receipt_sha256"])
    assert checked["certified_discrete_shadow_bands"] == 1
    forged = tmp_path/"numeric"
    shutil.copytree(destination,forged)
    _rehashed_forgery(forged,lambda x:x["lenses"][0]["normalized_guard_test"].__setitem__(0,999.))
    with pytest.raises(F.D2eFError,match="source reexecution value mismatch"):
        F.verify(forged/"receipt.json",SOURCE)


def test_forged_physical_provider_and_extra_receipt_file_rejected(tmp_path,monkeypatch):
    fixture = {
        "schema":F.SCHEMA,"status":F.STATUS,"claims":dict(F.CLAIMS),
        "lenses":[],"certified_discrete_shadow_aperture_bands":0,
    }
    monkeypatch.setattr(F,"execute",lambda _source:fixture)
    output = tmp_path/"ok"
    F.run(SOURCE,output)
    changed = tmp_path/"claimed"
    shutil.copytree(output,changed)
    _rehashed_forgery(changed,lambda x:x["claims"].update({"physical_provider_admitted":True}))
    with pytest.raises(F.D2eFError,match="forgery"):
        F.verify(changed/"receipt.json",SOURCE)
    extra = tmp_path/"extra"
    shutil.copytree(output,extra)
    (extra/"fabricated_holdout.json").write_text("{}")
    with pytest.raises(F.D2eFError,match="unexpected receipt inventory"):
        F.verify(extra/"receipt.json",SOURCE)


def test_source_symlink_and_existing_destination_fail_closed(tmp_path,monkeypatch):
    fixture = {
        "schema":F.SCHEMA,"status":F.STATUS,"claims":dict(F.CLAIMS),
        "lenses":[],"certified_discrete_shadow_aperture_bands":0,
    }
    monkeypatch.setattr(F,"execute",lambda _source:fixture)
    destination = tmp_path/"used"
    F.run(SOURCE,destination)
    with pytest.raises(F.D2eFError,match="existing output"):
        F.run(SOURCE,destination)
    link = tmp_path/"source-link"
    try:
        link.symlink_to(SOURCE,target_is_directory=True)
    except OSError:
        pytest.skip("Windows symlink privileges unavailable")
    with pytest.raises(F.D2eFError,match="symlink"):
        F.run(link,tmp_path/"new")
