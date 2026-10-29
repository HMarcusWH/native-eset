"""HIST-001C: pinned, strictly noncanonical historical equation crosswalk.

The descriptor is an evidence map, NOT a Theory-State graph partition, scientific
verdict, physical provider, equation-equivalence proof or output authorization.
The 31 sealed graph source files remain external, never written or bundled.
"""
from __future__ import annotations

import hashlib
from importlib import resources
from pathlib import Path
from typing import Any

from native_eset.graph.resolver_adapter import approved_lock, run_pinned_resolver
from native_eset.graph.snapshot import GraphIntegrityError, GraphSnapshot
from native_eset.graph.trust_roots import APPROVED_ESET_SNAPSHOT_SHA256
from native_eset.historical.hist001_approved import approved_hist001
from native_eset.historical.hist001_source import verify_hist001_source
from native_eset.serialization import read_json, strict_loads

OVERLAY_SCHEMA = "NATIVE_ESET_HIST001C_NONCANONICAL_CROSSWALK_V1"
OVERLAY_SHA256 = "546a56e363524c07c0e19cae46edca04408e041ff9cb28ba6661e103f3beface"
OVERLAY_FILENAME = "hist001c_crosswalk_v1.json"
REPORT_SCHEMA = "NATIVE_ESET_HIST001C_INSPECTION_V1"
STATUS = "HIST001C_NONCANONICAL_HISTORICAL_CROSSWALK_VERIFIED_NO_ADMISSION"
NO_GRANT = {
    "canonical_graph_mutation": False,
    "physical_provider_admitted": False,
    "native_v172_equivalence_proved": False,
    "held_out_validation": False,
    "empirical_validation": "NOT_ESTABLISHED",
    "production_scoring_authorized": False,
    "current_cmb_growth_provider_authorized": False,
    "original_rangefinder_reproduced": False,
}


class HistoricalCrosswalkIntegrityError(ValueError):
    """A historical source, crosswalk descriptor or graph trust anchor differs."""


def validate_crosswalk(data: object) -> dict[str, Any]:
    """Validate a descriptor; never treat arbitrary data as scientific authority."""
    if not isinstance(data, dict) or data.get("schema") != OVERLAY_SCHEMA:
        raise HistoricalCrosswalkIntegrityError("unrecognized historical crosswalk schema")
    if data.get("claim_ceiling") != NO_GRANT:
        raise HistoricalCrosswalkIntegrityError("historical crosswalk attempted promotion")
    hist = data.get("historical")
    approved = approved_hist001()
    required = {
        "finite_model_id": approved["finite_model_id"],
        "backend_id": approved["backend_id"],
        "theory_id": approved["theory_id"],
        "original_branch": approved["original_branch"],
        "frozen_candidate": approved["frozen_candidate"],
        "source_lock_sha256": approved["source_lock_sha256"],
        "original_archive_sha256": approved["original_archive_sha256"],
        "frozen_config_sha256": approved["config_sha256"],
        "frame": approved["frame"],
        "gauge": approved["gauge"],
        "units": approved["unit_convention"],
        "data_use": "REGRESSION_NOT_HELD_OUT",
    }
    if not isinstance(hist, dict) or hist != required:
        raise HistoricalCrosswalkIntegrityError("wrong historical theory/model/source identity")
    lock = approved_lock()
    graph = data.get("graph_reference")
    if (
        not isinstance(graph, dict)
        or graph.get("graph_sha256") != APPROVED_ESET_SNAPSHOT_SHA256
        or graph.get("release_version") != lock["release_version"]
        or graph.get("binding") != "APPROVED_SNAPSHOT_DIGEST_ONLY_UNRESOLVED_GRAPH_RECORD_IDS"
        or graph.get("requested_graph_record_ids") != []
        or graph.get("canonical_records_written") != 0
        or graph.get("automatic_relations_written") != 0
    ):
        raise HistoricalCrosswalkIntegrityError("canonical graph identity or nonmutation changed")
    if data.get("status") != "HISTORICAL_SOURCE_EQUATION_CROSSWALK_NOT_CANONICAL_ADMISSION":
        raise HistoricalCrosswalkIntegrityError("crosswalk status cannot grant authority")
    declared = data.get("declared_interpretation", {})
    if (
        declared.get("role") != "HISTORICAL_PHENOMENOLOGICAL_DECLARATION_NOT_PDE_SOLVER"
        or declared.get("covariant_equivalence_proved") is not False
        or declared.get("source_root_runtime_verification") != "NOT_PART_OF_FROZEN_46_SOURCE_FILES"
    ):
        raise HistoricalCrosswalkIntegrityError("historical PDE interpretation promoted")
    evidence = data.get("source_evidence")
    if not isinstance(evidence, list) or len(evidence) != 9:
        raise HistoricalCrosswalkIntegrityError("expected nine original-source statements")
    ids = [x.get("id") for x in evidence if isinstance(x, dict)]
    if len(ids) != len(evidence) or len(set(ids)) != len(ids):
        raise HistoricalCrosswalkIntegrityError("missing/duplicate source statement identity")
    for link in data.get("candidate_links", []):
        if (link.get("graph_record_id") is not None or
                link.get("canonical_edge_written") is not False or
                link.get("state") != "NOT_MAPPED_NO_EQUIVALENCE"):
            raise HistoricalCrosswalkIntegrityError("historical link was falsely admitted")
    obligations = data.get("compatibility_obligations")
    if (not isinstance(obligations, list) or len(obligations) != 8 or
            any(o.get("state") != "UNRESOLVED" or
                o.get("automatic_carryover") is not False for o in obligations)):
        raise HistoricalCrosswalkIntegrityError("unproved modern equivalence obligation")
    return data


def load_pinned_crosswalk() -> dict[str, Any]:
    """Read SHA-pinned package data. A self-rehashed caller JSON is not accepted."""
    raw = resources.files("native_eset.historical").joinpath(OVERLAY_FILENAME).read_bytes()
    if hashlib.sha256(raw).hexdigest() != OVERLAY_SHA256:
        raise HistoricalCrosswalkIntegrityError("independently pinned crosswalk changed")
    return validate_crosswalk(strict_loads(raw))


def inspect_noncanonical_crosswalk(source_root: str | Path, *,
                                   graph_dir: str | Path | None = None) -> dict[str, Any]:
    """Verify original 46+3 source inventory and optionally the sealed 31-file graph.

    No canonical partition mutation, new graph edge, inferred equation proof,
    physical provider admission or Theory-State verdict is ever performed.
    """
    descriptor = load_pinned_crosswalk()
    root = Path(source_root)
    verified = verify_hist001_source(root)
    if verified["source_lock_sha256"] != descriptor["historical"]["source_lock_sha256"]:
        raise HistoricalCrosswalkIntegrityError("original historical SHA differs")
    original = read_json(root / "SOURCE_LOCK.json")
    code_files = original["source_filenames_sha256"]
    negative = original["archived_negative_controls"]
    for evidence in descriptor["source_evidence"]:
        entry = evidence["source"]
        name = entry["relative_path"]
        if code_files.get(name) != entry["sha256"]:
            raise HistoricalCrosswalkIntegrityError("source statement SHA mismatch: " + name)
        start, end = entry["line_range"]
        if (type(start) is not int or type(end) is not int or start < 1
                or end < start):
            raise HistoricalCrosswalkIntegrityError("invalid historical source line range")
        # The whole file has already passed the original 46-file SHA lock.
        line_count = len((root / "swells_pack_v2" / name).read_text(
            encoding="utf-8"
        ).splitlines())
        if end > line_count:
            raise HistoricalCrosswalkIntegrityError("source-line citation out of bounds")
    for control in descriptor["negative_evidence"]:
        record = negative.get(control["source_filename"])
        if not isinstance(record, dict) or record.get("sha256") != control["sha256"]:
            raise HistoricalCrosswalkIntegrityError("archived negative evidence changed")
    graph_reference = descriptor["graph_reference"]
    graph_state = "PINNED_GRAPH_REFERENCE_ONLY_PRIVATE_SOURCE_NOT_SUPPLIED"
    private_source_replayed = False
    if graph_dir is not None:
        # No user-selected graph lock; the built-in independently pinned lock,
        # vocabulary, original resolver and policy establish exact source identity.
        graph_lock = Path(__file__).resolve().parents[1] / "graph" / "graph_snapshot.lock.json"
        snapshot = GraphSnapshot.load(graph_dir, graph_lock)
        if snapshot.graph_sha256 != graph_reference["graph_sha256"]:
            raise GraphIntegrityError("graph snapshot differs from crosswalk reference")
        resolver = run_pinned_resolver(snapshot)
        if resolver.snapshot.graph_sha256 != graph_reference["graph_sha256"]:
            raise GraphIntegrityError("verified graph resolver returned wrong snapshot")
        graph_state = "SEALED_GRAPH_RESOLVER_REPLAYED_READ_ONLY"
        private_source_replayed = True
    return {
        "schema": REPORT_SCHEMA,
        "status": STATUS,
        "overlay_sha256": OVERLAY_SHA256,
        "descriptor": descriptor,
        "source_verification": {
            "status": verified["status"],
            "frozen_files": verified["frozen_files"],
            "archived_negative_records": verified["archived_negative_records"],
            "source_lock_sha256": verified["source_lock_sha256"],
            "source_statement_refs_checked": len(descriptor["source_evidence"]),
        },
        "graph_binding": {
            "reference_sha256": graph_reference["graph_sha256"],
            "reference_release": graph_reference["release_version"],
            "status": graph_state,
            "sealed_private_graph_replayed": private_source_replayed,
            "canonical_node_adjudication": "NONE",
            "canonical_edges_written": 0,
        },
        "claim_ceiling": dict(NO_GRANT),
        "theory_state_mutated": False,
        "interpretation": "Verified historical metadata/evidence, not equation equivalence or scientific admission",
    }
