"""G3a: SHA-locked source output discrepancy runner and adversarial receipts."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/legacy/hist001"
RUNNER=ROOT/"tools/hist001d_d2e_g3a_pointwise_baryons.py"
SPEC=importlib.util.spec_from_file_location("hist001d_g3a_source_tests",RUNNER)
assert SPEC is not None and SPEC.loader is not None
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def test_source_46_plus_three_prerequisite_and_nonpromoting_claims():
    from native_eset.historical.hist001_source import verify_hist001_source
    original=verify_hist001_source(SOURCE)
    assert original["source_lock_sha256"] == G.SOURCE_SHA256
    assert original["frozen_files"] == 46
    assert original["archived_negative_records"] == 3
    assert G.G2B_SHA256=="37a502ff6e54d3ca9c2e6d49ad21338962f005f4350dfc859cc5b73ea48ec256"
    p=G._load_g2b()
    assert p.SOURCE_SHA256==G.SOURCE_SHA256
    assert G.CLAIMS["registered_binary64_source_output_error_bounded_pointwise"]
    assert G.ROLES==(
        "observed_fitted_einstein_radius","independent_d2d_11520_root",
    )
    for key in (
        "source_numerical_error_at_all_radii_certified",
        "original_source_continuum_shadow_error_bounded",
        "source_numeric_qeff_all_radii_certified",
        "sigma_critical_numerical_error_bounded",
        "root_uniqueness_certified",
        "total_model_error_bounded",
        "mass_outside_finite_domain_bounded",
        "new_holdout_scored",
        "physical_weyl_lensing_derived",
        "physical_provider_admitted",
        "native_v172_equivalence_proved",
        "original_source_modified",
        "canonical_theory_state_mutated",
    ):
        assert G.CLAIMS[key] is False
    assert G.CLAIMS["empirical_validation"]=="NOT_ESTABLISHED"


def _refresh_receipt(folder,edit):
    from native_eset.evidence.receipts import canonical_json
    report=json.loads((folder/"report.json").read_bytes())
    edit(report)
    rep_raw=canonical_json(report)
    (folder/"report.json").write_bytes(rep_raw)
    receipt=json.loads((folder/"receipt.json").read_bytes())
    receipt["report_sha256"]=hashlib.sha256(rep_raw).hexdigest()
    raw=canonical_json(receipt)
    (folder/"receipt.json").write_bytes(raw)
    (folder/"receipt.sha256").write_text(hashlib.sha256(raw).hexdigest()+"\n")


def test_self_rehashed_source_discrepancy_forgery_rejected(tmp_path,monkeypatch):
    report={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "registered_pointwise_bulge_disk_qeff_count":1,
        "lenses":[{"lens_id":"J0822+1828","numeric_error_msun":"3.14"}],
    }
    monkeypatch.setattr(G,"execute",lambda _:report)
    base=tmp_path/"report"
    result=G.run(SOURCE,base)
    assert G.verify(base/"receipt.json",SOURCE,result["receipt_sha256"])["registered_outputs"]==1
    forgery=tmp_path/"forgery"
    shutil.copytree(base,forgery)
    _refresh_receipt(forgery,lambda r:r["lenses"][0].__setitem__(
        "numeric_error_msun","1e99",
    ))
    with pytest.raises(G.G3aError,match="source-reexecuted pointwise numerical discrepancy differs"):
        G.verify(forgery/"receipt.json",SOURCE)


def test_provider_promotion_and_receipt_inventory_forgery_rejected(tmp_path,monkeypatch):
    report={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "registered_pointwise_bulge_disk_qeff_count":0,"lenses":[],
    }
    monkeypatch.setattr(G,"execute",lambda _:report)
    base=tmp_path/"original"
    G.run(SOURCE,base)
    changed=tmp_path/"provider"
    shutil.copytree(base,changed)
    _refresh_receipt(changed,lambda r:r["claims"].update({"physical_provider_admitted":True}))
    with pytest.raises(G.G3aError,match="forged receipt"):
        G.verify(changed/"receipt.json",SOURCE)
    extra=tmp_path/"extra"
    shutil.copytree(base,extra)
    (extra/"unmasked_holdout.json").write_text("{}")
    with pytest.raises(G.G3aError,match="inventory"):
        G.verify(extra/"receipt.json",SOURCE)


def test_source_symlink_and_duplicate_result_denied(tmp_path,monkeypatch):
    fixture={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "registered_pointwise_bulge_disk_qeff_count":0,"lenses":[],
    }
    monkeypatch.setattr(G,"execute",lambda _:fixture)
    output=tmp_path/"out"
    G.run(SOURCE,output)
    with pytest.raises(G.G3aError,match="existing receipt output"):
        G.run(SOURCE,output)
    link=tmp_path/"source-link"
    try:
        link.symlink_to(SOURCE,target_is_directory=True)
    except OSError:
        pytest.skip("symlink privilege unavailable")
    with pytest.raises(G.G3aError,match="unsafe source path"):
        G.run(link,tmp_path/"new")
