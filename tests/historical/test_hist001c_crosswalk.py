"""HIST-001C source SHA, noncanonical crosswalk and private-graph guard."""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import pytest

from native_eset.capabilities import CAPABILITIES
from native_eset.graph.snapshot import GraphIntegrityError
from native_eset.historical.hist001c_crosswalk import (
    NO_GRANT, OVERLAY_SHA256, HistoricalCrosswalkIntegrityError,
    inspect_noncanonical_crosswalk, load_pinned_crosswalk,
    validate_crosswalk,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"


def test_pinned_overlay_and_plan_source_identity() -> None:
    descriptor = load_pinned_crosswalk()
    assert len(descriptor["source_evidence"]) == 9
    assert len(descriptor["compatibility_obligations"]) == 8
    assert descriptor["claim_ceiling"] == NO_GRANT
    assert descriptor["declared_interpretation"]["role"].endswith("NOT_PDE_SOLVER")
    assert descriptor["declared_interpretation"]["source_sha256"] == hashlib.sha256(
        (ROOT / "docs/HIST001_INTEGRATION_PLAN.md").read_bytes()
    ).hexdigest()
    assert len(OVERLAY_SHA256) == 64


def test_frozen_source_inspection_and_nonpromotion() -> None:
    result = inspect_noncanonical_crosswalk(SOURCE)
    assert result["status"] == "HIST001C_NONCANONICAL_HISTORICAL_CROSSWALK_VERIFIED_NO_ADMISSION"
    assert result["source_verification"]["frozen_files"] == 46
    assert result["source_verification"]["archived_negative_records"] == 3
    assert result["source_verification"]["source_statement_refs_checked"] == 9
    assert result["graph_binding"]["reference_release"] == "0.16.39"
    assert result["graph_binding"]["sealed_private_graph_replayed"] is False
    assert result["graph_binding"]["canonical_edges_written"] == 0
    assert result["theory_state_mutated"] is False
    assert result["claim_ceiling"] == NO_GRANT
    assert CAPABILITIES["native-v1.7.2-one-map"].executable is False
    assert set(CAPABILITIES["legacy-hist001-j2141-seta"].observables) == {
        "historical_rotation_lensing_regression", "historical_setA_portability",
    }


def test_returned_metadata_is_defensively_reloadable() -> None:
    first = load_pinned_crosswalk()
    first["source_evidence"][0]["id"] = "user-promotes-theory"
    assert load_pinned_crosswalk()["source_evidence"][0]["id"] != "user-promotes-theory"


@pytest.mark.parametrize("mutation", [
    lambda d: d["claim_ceiling"].update({"physical_provider_admitted": True}),
    lambda d: d["historical"].update({"theory_id": "NATIVE_ESET_V172"}),
    lambda d: d["graph_reference"].update({"canonical_records_written": 1}),
    lambda d: d["candidate_links"][0].update({"graph_record_id": "eset:invented"}),
    lambda d: d["compatibility_obligations"][0].update({"state": "PROVED"}),
    lambda d: d["declared_interpretation"].update({"covariant_equivalence_proved": True}),
])
def test_descriptors_cannot_promote(mutation) -> None:
    altered = copy.deepcopy(load_pinned_crosswalk())
    mutation(altered)
    with pytest.raises(HistoricalCrosswalkIntegrityError):
        validate_crosswalk(altered)


def test_no_untrusted_graph_directory_can_be_admitted(tmp_path: Path) -> None:
    with pytest.raises((GraphIntegrityError, OSError, ValueError)):
        inspect_noncanonical_crosswalk(SOURCE, graph_dir=tmp_path / "untrusted")


def test_source_preflight_rejects_missing_original(tmp_path: Path) -> None:
    with pytest.raises((ValueError, OSError)):
        inspect_noncanonical_crosswalk(tmp_path)


def test_original_source_did_not_mutate() -> None:
    from native_eset.historical.hist001_source import verify_hist001_source
    assert verify_hist001_source(SOURCE)["frozen_files"] == 46
