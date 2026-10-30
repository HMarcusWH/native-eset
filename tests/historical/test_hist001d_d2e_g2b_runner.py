"""D2e-G2b frozen source / receipt / nonpromotion integrity checks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/legacy/hist001"
SCRIPT=ROOT/"tools/hist001d_d2e_g2b_angular_boxes.py"
SPEC=importlib.util.spec_from_file_location("hist001d_d2eg2b_tests",SCRIPT)
assert SPEC is not None and SPEC.loader is not None
G=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def test_source_lock_prerequisite_and_no_physics_permission():
    from native_eset.historical.hist001_source import verify_hist001_source

    original=verify_hist001_source(SOURCE)
    assert original["source_lock_sha256"]==G.SOURCE_SHA256
    assert original["frozen_files"]==46
    assert original["archived_negative_records"]==3
    assert G.G1G2_SHA256=="11e3dad8dd3723efc36f330720f7dda3acfa14dd1cff5b71fd91da00b97497a7"
    g=G._load_g()
    assert g.SOURCE_SHA256==G.SOURCE_SHA256
    assert g.CLAIMS["physical_provider_admitted"] is False
    assert G.CLAIMS["analytic_full_azimuth_continuum_disk_enclosed"] is True
    for key in (
        "frozen_source_numeric_periodic1024_error_bounded",
        "frozen_source_numeric_Hernquist_error_bounded",
        "frozen_source_numeric_qeff_root_map_certified",
        "global_root_topology_certified",
        "physical_provider_admitted",
        "physical_weyl_lensing_derived",
        "source_density_continuum_error_bounded",
        "missing_inner_outer_shadow_mass_bounded",
        "current_native_v172_equivalence_proved",
        "new_independent_holdout_scored",
        "original_source_mutated",
        "canonical_theory_state_mutated",
    ):
        assert G.CLAIMS[key] is False
    assert G.CLAIMS["empirical_validation"]=="NOT_ESTABLISHED"


def _rehash(folder,edit):
    from native_eset.evidence.receipts import canonical_json

    value=json.loads((folder/"report.json").read_bytes())
    edit(value)
    raw=canonical_json(value)
    (folder/"report.json").write_bytes(raw)
    receipt=json.loads((folder/"receipt.json").read_bytes())
    receipt["report_sha256"]=hashlib.sha256(raw).hexdigest()
    signed=canonical_json(receipt)
    (folder/"receipt.json").write_bytes(signed)
    (folder/"receipt.sha256").write_text(hashlib.sha256(signed).hexdigest()+"\n")


def test_source_reexecution_detects_rehashed_fabricated_mass(tmp_path,monkeypatch):
    synthetic={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "endpoint_target_met_count":1,
        "lenses":[{"lens_id":"J0822+1828","certified_test_mass":[3.,4.]}],
    }
    monkeypatch.setattr(G,"execute",lambda _source:synthetic)
    baseline=tmp_path/"baseline"
    signed=G.run(SOURCE,baseline)
    assert G.verify(baseline/"receipt.json",SOURCE,signed["receipt_sha256"])["lenses"]==1
    forged=tmp_path/"forged"
    shutil.copytree(baseline,forged)
    _rehash(forged,lambda r:r["lenses"][0]["certified_test_mass"].__setitem__(0,1e20))
    with pytest.raises(G.G2bError,match="source-reexecuted analytic interval evidence differs"):
        G.verify(forged/"receipt.json",SOURCE)


def test_fake_admission_and_added_receipt_files_are_denied(tmp_path,monkeypatch):
    report={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "endpoint_target_met_count":0,"lenses":[],
    }
    monkeypatch.setattr(G,"execute",lambda _source:report)
    output=tmp_path/"ok"
    G.run(SOURCE,output)
    altered=tmp_path/"bad_provider"
    shutil.copytree(output,altered)
    _rehash(altered,lambda r:r["claims"].update({"physical_provider_admitted":True}))
    with pytest.raises(G.G2bError,match="forgery"):
        G.verify(altered/"receipt.json",SOURCE)
    extraneous=tmp_path/"extra"
    shutil.copytree(output,extraneous)
    (extraneous/"invented_holdout.json").write_text("{}")
    with pytest.raises(G.G2bError,match="inventory changed"):
        G.verify(extraneous/"receipt.json",SOURCE)


def test_preexisting_target_and_source_symlink_denied(tmp_path,monkeypatch):
    dummy={
        "schema":G.SCHEMA,"status":G.STATUS,"claims":dict(G.CLAIMS),
        "lenses":[],"endpoint_target_met_count":0,
    }
    monkeypatch.setattr(G,"execute",lambda _source:dummy)
    target=tmp_path/"existing"
    G.run(SOURCE,target)
    with pytest.raises(G.G2bError,match="existing receipt target"):
        G.run(SOURCE,target)
    link=tmp_path/"link"
    try:
        link.symlink_to(SOURCE,target_is_directory=True)
    except OSError:
        pytest.skip("No symlink privileges on this platform")
    with pytest.raises(G.G2bError,match="source symlink"):
        G.run(link,tmp_path/"next")
