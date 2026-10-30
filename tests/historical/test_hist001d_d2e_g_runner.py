"""D2e-G historical original source, source-reexecution and negative authority tests."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/legacy/hist001"
RUNNER=ROOT/"tools/hist001d_d2e_g_baryon_boxes.py"
SPEC=importlib.util.spec_from_file_location("hist001d_d2eg_baryon_tests",RUNNER)
assert SPEC is not None and SPEC.loader is not None
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def test_frozen_original_46_plus_three_and_pinned_f():
    from native_eset.historical.hist001_source import verify_hist001_source

    result=verify_hist001_source(SOURCE)
    assert result["source_lock_sha256"]==G.SOURCE_SHA256
    assert result["frozen_files"]==46
    assert result["archived_negative_records"]==3
    F=G._load_pinned_f()
    assert F.CLAIMS["physical_provider_admitted"] is False
    assert F.SOURCE_SHA256==G.SOURCE_SHA256
    assert G.D2E_F_SHA256=="8b54ab567cd049c5df97d5c596bc205e4768d4fbc5f8ee86e854a75681fce93b"


def test_no_numeric_source_or_physical_promotion():
    assert G.CLAIMS["finite_continuum_hernquist_bulge_mass_enclosed"]
    assert G.CLAIMS["analytic_continuum_exponential_disk_mass_coarsely_enclosed"]
    assert G.CLAIMS["analytic_continuum_baryonic_qeff_interval_enclosed"]
    for claim in ("source_SciPy_bulge_quadrature_error_certified",
                  "source_1024_angle_disk_quadrature_error_certified",
                  "source_numerical_qeff_root_map_certified",
                  "full_model_root_uniqueness_certified",
                  "global_model_numerical_error_bound_established",
                  "mass_outside_finite_domain_bounded",
                  "physical_provider_admitted","physical_weyl_lensing_derived",
                  "native_v172_equivalence_proved","new_holdout_scored",
                  "original_source_modified","canonical_theory_state_mutated"):
        assert G.CLAIMS[claim] is False
    assert G.CLAIMS["empirical_validation"]=="NOT_ESTABLISHED"
    assert G.GUARD_FRACTION==.02
    assert len(G.LENS_IDS)==6


def _repair_self_sha(folder,edit):
    from native_eset.evidence.receipts import canonical_json
    report=json.loads((folder/"report.json").read_bytes())
    edit(report)
    new_report=canonical_json(report)
    (folder/"report.json").write_bytes(new_report)
    receipt=json.loads((folder/"receipt.json").read_bytes())
    receipt["report_sha256"]=hashlib.sha256(new_report).hexdigest()
    new_receipt=canonical_json(receipt)
    (folder/"receipt.json").write_bytes(new_receipt)
    (folder/"receipt.sha256").write_text(hashlib.sha256(new_receipt).hexdigest()+"\n")


def test_fake_rehashed_numeric_report_cannot_pass_source_replay(tmp_path,monkeypatch):
    report={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "analytic_qeff_bands":1,
        "bulge_endpoint_target_met_count":2,
        "lenses":[{"lens_id":"J0822+1828","fake_mass_msun":123.}],
    }
    monkeypatch.setattr(G,"execute",lambda source:report)
    out=tmp_path/"baseline"
    receipt=G.run(SOURCE,out)
    assert G.verify(out/"receipt.json",SOURCE,receipt["receipt_sha256"])["six_development_lenses"]==1
    forged=tmp_path/"numeric_forged"
    shutil.copytree(out,forged)
    _repair_self_sha(forged,lambda r:r["lenses"][0].__setitem__("fake_mass_msun",1e18))
    with pytest.raises(G.G1G2Error,match="source reexecution numerical value mismatch"):
        G.verify(forged/"receipt.json",SOURCE)


def test_fake_physical_admission_and_extra_file_fail_closed(tmp_path,monkeypatch):
    report={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "analytic_qeff_bands":0,
        "bulge_endpoint_target_met_count":0,
        "lenses":[],
    }
    monkeypatch.setattr(G,"execute",lambda source:report)
    baseline=tmp_path/"valid"
    G.run(SOURCE,baseline)
    forged=tmp_path/"provider"
    shutil.copytree(baseline,forged)
    _repair_self_sha(forged,lambda r:r["claims"].update({"physical_provider_admitted":True}))
    with pytest.raises(G.G1G2Error,match="forgery"):
        G.verify(forged/"receipt.json",SOURCE)
    extra=tmp_path/"extra"
    shutil.copytree(baseline,extra)
    (extra/"falsified_physics.json").write_text("{}")
    with pytest.raises(G.G1G2Error,match="inventory changed"):
        G.verify(extra/"receipt.json",SOURCE)


def test_source_symlink_and_duplicate_output_rejected(tmp_path,monkeypatch):
    report={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "analytic_qeff_bands":0,
        "bulge_endpoint_target_met_count":0,
        "lenses":[],
    }
    monkeypatch.setattr(G,"execute",lambda source:report)
    old=tmp_path/"old"
    G.run(SOURCE,old)
    with pytest.raises(G.G1G2Error,match="existing output"):
        G.run(SOURCE,old)
    link=tmp_path/"March-source-link"
    try:
        link.symlink_to(SOURCE,target_is_directory=True)
    except OSError:
        pytest.skip("Symlink permission absent")
    with pytest.raises(G.G1G2Error,match="symlink"):
        G.run(link,tmp_path/"new")
