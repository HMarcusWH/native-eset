"""G4b.0 original-source input-only partition runner and receipt attacks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from fractions import Fraction
from pathlib import Path

import pytest

from native_eset.numerics.hist001d_g4b_root_intervals import (
    INITIAL_CELLS, LENS_IDS, R_MAX, R_MIN, SOURCE_LOCK_SHA256,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
RUNNER = ROOT / "tools/hist001d_d2e_g4b0_root_partition.py"
SPEC = importlib.util.spec_from_file_location("hist001d_g4b0_runner_tests", RUNNER)
assert SPEC is not None and SPEC.loader is not None
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def _fake_report():
    return {
        "schema": G.SCHEMA, "status": G.STATUS,
        "claims": dict(G.CLAIMS),
        "total_initial_source_domain_cells": 384,
        "lenses": [{"lens_id": LENS_IDS[0], "source_output_data": None}],
    }


def _edit_rehash(folder, editor):
    from native_eset.evidence.receipts import canonical_json
    report = json.loads((folder / "report.json").read_bytes())
    editor(report)
    raw = canonical_json(report)
    (folder / "report.json").write_bytes(raw)
    receipt = json.loads((folder / "receipt.json").read_bytes())
    receipt["report_sha256"] = hashlib.sha256(raw).hexdigest()
    byte = canonical_json(receipt)
    (folder / "receipt.json").write_bytes(byte)
    (folder / "receipt.sha256").write_text(hashlib.sha256(byte).hexdigest() + "\n")


def test_actual_source_input_preregistration_frozen_46_plus_three():
    from native_eset.historical.hist001_source import verify_hist001_source
    before = verify_hist001_source(SOURCE)
    assert before["source_lock_sha256"] == SOURCE_LOCK_SHA256
    assert before["frozen_files"] == 46
    assert before["archived_negative_records"] == 3
    registry = G._registered()
    assert tuple(registry["lens_ids"]) == LENS_IDS
    assert registry["initial_cells"] == 64
    assert registry["max_dyadic_depth"] == 8
    assert registry["root_anchors_only_not_proof"] is True
    assert G._pinned_d2e().D2D_REFERENCE_ROOT_KPC == (
        registry["d2d_finite_root_anchors_kpc_for_provenance_only"]
    )
    after = verify_hist001_source(SOURCE)
    assert before["source_lock_sha256"] == after["source_lock_sha256"]


def test_source_only_executable_report_has_complete_real_domain_no_root_claim():
    report = G.execute(SOURCE)
    assert report["source_lock_sha256"] == SOURCE_LOCK_SHA256
    assert report["total_initial_source_domain_cells"] == 6 * INITIAL_CELLS
    assert report["root_or_residual_evaluation_performed"] is False
    assert report["full_domain_mathematical_partition_proven"] is True
    assert len(report["lenses"]) == 6
    for row, lid in zip(report["lenses"], LENS_IDS):
        assert row["lens_id"] == lid
        assert row["source_output_mass_sigma_shadow_or_root_computed"] is False
        cells = row["initial_cells"]
        assert len(cells) == INITIAL_CELLS
        assert cells[0]["path"] == "00:"
        assert cells[-1]["path"] == "63:"
        left = Fraction(int(cells[0]["lower"]["num"]), int(cells[0]["lower"]["den"]))
        right = Fraction(int(cells[-1]["upper"]["num"]), int(cells[-1]["upper"]["den"]))
        assert left == R_MIN and right == R_MAX
        assert row["full_exact_source_domain_cover"][
            "complete_contiguous_real_domain_covered"
        ] is True
    assert report["claims"]["root_existence_or_uniqueness_certified"] is False
    assert report["claims"]["empirical_validation"] == "NOT_ESTABLISHED"


def test_fresh_source_reexecution_denies_self_rehashed_report_forgery(tmp_path, monkeypatch):
    baseline = _fake_report()
    monkeypatch.setattr(G, "execute", lambda _: baseline)
    destination = tmp_path / "good"
    run = G.run(SOURCE, destination)
    assert G.verify(destination / "receipt.json", SOURCE, run["receipt_sha256"])[
        "source_only_initial_cells"
    ] == 384
    forged = tmp_path / "self-rehashed"
    shutil.copytree(destination, forged)
    _edit_rehash(forged, lambda x: x["lenses"][0].__setitem__(
        "source_output_data", 3.14,
    ))
    with pytest.raises(G.G4b0Error, match="fresh independent"):
        G.verify(forged / "receipt.json", SOURCE)


def test_modified_claims_extra_members_wrong_hash_denied(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "execute", lambda _: _fake_report())
    good = tmp_path / "good"
    G.run(SOURCE, good)
    bad = tmp_path / "promoted"
    shutil.copytree(good, bad)
    _edit_rehash(bad, lambda r: r["claims"].update(
        {"physical_provider_admitted": True},
    ))
    with pytest.raises(G.G4b0Error, match="forged"):
        G.verify(bad / "receipt.json", SOURCE)
    extra = tmp_path / "extra"
    shutil.copytree(good, extra)
    (extra / "unblinded_holdout.json").write_text("{}")
    with pytest.raises(G.G4b0Error, match="inventory"):
        G.verify(extra / "receipt.json", SOURCE)
    with pytest.raises(G.G4b0Error, match="externally pinned"):
        G.verify(good / "receipt.json", SOURCE, "0" * 64)


def test_registry_mutation_and_unsafe_write_denied(tmp_path, monkeypatch):
    forged = tmp_path / "registry.json"
    forged.write_bytes(G.REGISTRY.read_bytes() + b"\n")
    monkeypatch.setattr(G, "REGISTRY", forged)
    with pytest.raises(G.G4b0Error, match="registered exact partition bytes"):
        G._registered()
    monkeypatch.setattr(G, "execute", lambda _: _fake_report())
    exists = tmp_path / "exists"
    exists.mkdir()
    with pytest.raises(G.G4b0Error, match="existing immutable"):
        G.run(SOURCE, exists)
