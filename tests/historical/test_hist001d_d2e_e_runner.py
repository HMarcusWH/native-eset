"""D2e-E source-locked runner and nonpromoting original-source receipt tests."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/legacy/hist001"
SCRIPT=ROOT/"tools/hist001d_d2e_e_adaptive_projection.py"
SPEC=importlib.util.spec_from_file_location("hist001d_d2e_e_test",SCRIPT)
assert SPEC is not None and SPEC.loader is not None
E=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


def test_d2e_e_frozen_source_scope_and_nonclaims():
    assert E.SOURCE_SHA256=="fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert E.D2E_D_SHA256=="bf8e7f5fca71d45224ed8f123de600a525c9360dab823b0183b9b82a460e53e5"
    assert E.RADIUS_ROLES==("fitted_observed_einstein_radius","independent_d2d_11520_root")
    assert E.RADIAL_POINTS==11520
    assert E.TARGET_RELATIVE_WIDTH=="0.00000001"
    assert E.CLAIMS["rigorous_pointwise_quadrature_bound"] is True
    for field in ("source_gradient_continuum_error_bounded",
                  "baryonic_qeff_numerical_error_bounded",
                  "d2e_b_all_radius_mass_assumption_proved",
                  "global_error_bound_established",
                  "root_uniqueness_mathematically_certified",
                  "mass_outside_finite_domain_bounded",
                  "physical_weyl_lensing_derived","physical_provider_admitted",
                  "native_v172_equivalence_proved","new_holdout_scored"):
        assert E.CLAIMS[field] is False
    assert E.CLAIMS["empirical_validation"]=="NOT_ESTABLISHED"


def test_source_46_3_and_pinned_dependency_integrity():
    from native_eset.historical.hist001_source import verify_hist001_source
    original=verify_hist001_source(SOURCE)
    assert original["source_lock_sha256"]==E.SOURCE_SHA256
    assert original["frozen_files"]==46
    assert original["archived_negative_records"]==3
    old=E._load_d2e_d()
    assert old.CLAIMS["shadow_piecewise_linear_pointwise_enclosed"] is True
    assert old.CLAIMS["root_uniqueness_mathematically_certified"] is False


def _refresh_hashes(folder,update):
    from native_eset.evidence.receipts import canonical_json
    report=json.loads((folder/"report.json").read_bytes())
    update(report)
    payload=canonical_json(report)
    (folder/"report.json").write_bytes(payload)
    receipt=json.loads((folder/"receipt.json").read_bytes())
    receipt["report_sha256"]=hashlib.sha256(payload).hexdigest()
    signed=canonical_json(receipt)
    (folder/"receipt.json").write_bytes(signed)
    (folder/"receipt.sha256").write_text(hashlib.sha256(signed).hexdigest()+"\n")


def test_source_reexecution_comparison_rejects_rehashed_numerics(tmp_path,monkeypatch):
    source_report={
        "schema":E.SCHEMA,"status":E.STATUS,"claims":dict(E.CLAIMS),
        "fixed_aperture_count":12,"fixed_aperture_target_met_count":12,
        "model_data":[42.0],
    }
    monkeypatch.setattr(E,"execute",lambda source:source_report)
    directory=tmp_path/"sample"
    result=E.run(SOURCE,directory)
    assert E.verify(directory/"receipt.json",SOURCE,result["receipt_sha256"])["fixed_aperture_count"]==12
    changed=tmp_path/"fake"
    shutil.copytree(directory,changed)
    _refresh_hashes(changed,lambda r:r["model_data"].__setitem__(0,1337.))
    with pytest.raises(E.D2eEError,match="source reexecution differs"):
        E.verify(changed/"receipt.json",SOURCE)


def test_fake_provider_claim_and_extra_receipt_file_rejected(tmp_path,monkeypatch):
    source_report={"schema":E.SCHEMA,"status":E.STATUS,"claims":dict(E.CLAIMS),"fixed_aperture_count":0,"fixed_aperture_target_met_count":0}
    monkeypatch.setattr(E,"execute",lambda source:source_report)
    source=tmp_path/"baseline"
    E.run(SOURCE,source)
    forged=tmp_path/"provider"
    shutil.copytree(source,forged)
    _refresh_hashes(forged,lambda r:r["claims"].update({"physical_provider_admitted":True}))
    with pytest.raises(E.D2eEError,match="forgery"):
        E.verify(forged/"receipt.json",SOURCE)
    extra=tmp_path/"extra"
    shutil.copytree(source,extra)
    (extra/"fabricated.json").write_text("{}")
    with pytest.raises(E.D2eEError,match="unexpected receipt members"):
        E.verify(extra/"receipt.json",SOURCE)


def test_bad_source_symlink_and_duplicate_output(tmp_path,monkeypatch):
    report={"schema":E.SCHEMA,"status":E.STATUS,"claims":dict(E.CLAIMS),"fixed_aperture_count":0,"fixed_aperture_target_met_count":0}
    monkeypatch.setattr(E,"execute",lambda source:report)
    destination=tmp_path/"out"
    E.run(SOURCE,destination)
    with pytest.raises(E.D2eEError,match="unsafe or existing"):
        E.run(SOURCE,destination)
    link=tmp_path/"original-link"
    try:
        link.symlink_to(SOURCE,target_is_directory=True)
    except OSError:
        pytest.skip("Windows may disallow symlinks")
    with pytest.raises(E.D2eEError,match="unsafe or existing"):
        E.run(link,tmp_path/"new")
