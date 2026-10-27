"""Re-execute ESET's frozen v0.2 policy instead of replacing it with a new guess.

This module is a read-only scientific status *reporter*. It does not promote facts.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Any
from native_eset.graph.snapshot import GraphSnapshot, GraphIntegrityError, sha256_file

REF_DIR = Path(__file__).resolve().parent
RESOLVER_SCRIPT = REF_DIR / "theory_state_resolver_v0_2_1.py"
RESOLVER_POLICY = REF_DIR / "resolver_policy_v0_2.json"



@dataclass(frozen=True, init=False)
class VerifiedResolver:
    """Defensive result container, not itself an authorization credential."""
    snapshot: GraphSnapshot
    _partitions_json: bytes
    _summaries_json: bytes
    _audit_json: bytes

    def __init__(self, snapshot: GraphSnapshot, partitions, summaries, audit):
        object.__setattr__(self, "snapshot", snapshot)
        for field, value in (("_partitions_json", partitions), ("_summaries_json", summaries), ("_audit_json", audit)):
            object.__setattr__(self, field, json.dumps(value, sort_keys=True,
                               ensure_ascii=False, allow_nan=False).encode("utf-8"))

    @property
    def partitions(self):
        return tuple(json.loads(self._partitions_json))

    @property
    def summaries(self):
        return tuple(json.loads(self._summaries_json))

    @property
    def audit(self):
        return json.loads(self._audit_json)

    def explain(self, subject: str, axis: str | None = None, scope: str | None = None) -> dict[str, Any]:
        if subject not in self.snapshot.nodes:
            raise KeyError(f"unknown graph subject: {subject}")
        rows = [x for x in self.partitions if x["subject"] == subject
                and (axis is None or x["axis"] == axis)
                and (scope is None or x["scope"] == scope)]
        return {"subject": subject, "axis": axis, "scope": scope, "partitions": rows,
                "graph_sha256": self.snapshot.graph_sha256,
                "interpretation": "Read-only replay of original ESET scoped authority policy"}


def approved_lock() -> dict[str, Any]:
    """Verify bundled independent trust roots before inspecting caller inputs."""
    from native_eset.graph.trust_roots import APPROVED_LOCK_BYTES_SHA256, APPROVED_VOCABULARY_BYTES_SHA256
    from native_eset.serialization import read_json
    lock_path = REF_DIR / "graph_snapshot.lock.json"
    vocab_path = REF_DIR / "vocabulary_v0_7_2.json"
    if lock_path.is_symlink() or sha256_file(lock_path) != APPROVED_LOCK_BYTES_SHA256:
        raise GraphIntegrityError("bundled approved lock bytes changed")
    if vocab_path.is_symlink() or sha256_file(vocab_path) != APPROVED_VOCABULARY_BYTES_SHA256:
        raise GraphIntegrityError("bundled approved vocabulary bytes changed")
    lock = read_json(lock_path)
    if RESOLVER_SCRIPT.is_symlink() or sha256_file(RESOLVER_SCRIPT) != lock["resolver_implementation_sha256"]:
        raise GraphIntegrityError("unapproved resolver implementation digest")
    if RESOLVER_POLICY.is_symlink() or sha256_file(RESOLVER_POLICY) != lock["resolver_policy_sha256"]:
        raise GraphIntegrityError("unapproved resolver policy bytes digest")
    semantic = hashlib.sha256(json.dumps(read_json(RESOLVER_POLICY), sort_keys=True,
                             separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    if semantic != lock["resolver_policy_semantic_sha256"]:
        raise GraphIntegrityError("unapproved policy semantic digest")
    return lock


def _lf_bytes(data: bytes) -> bytes:
    """Normalize only the platform newline emitted by pinned historical Python.

    Raw source hashes are never normalized. Raw generated output hashes and the
    declared LF-normalized output hashes are both retained in the audit.
    """
    data.decode("utf-8")
    if b"\r" in data.replace(b"\r\n", b""):
        raise GraphIntegrityError("unexpected bare CR in historical resolver output")
    return data.replace(b"\r\n", b"\n")


def run_pinned_resolver(snapshot: GraphSnapshot) -> VerifiedResolver:
    from native_eset.graph.snapshot import canonical_graph_digest
    from native_eset.graph.trust_roots import APPROVED_ESET_SNAPSHOT_SHA256
    from native_eset.serialization import strict_loads
    lock = approved_lock()
    if not isinstance(snapshot, GraphSnapshot) or snapshot.lock != lock:
        raise GraphIntegrityError("caller snapshot lock is not the approved release")
    if (snapshot.graph_sha256 != APPROVED_ESET_SNAPSHOT_SHA256 or
            canonical_graph_digest(snapshot.all_records()) != APPROVED_ESET_SNAPSHOT_SHA256):
        raise GraphIntegrityError("claimed snapshot digest does not match its actual records")
    blobs = snapshot.source_blobs()
    expected = {x["name"]: x["sha256"] for x in lock["files"]}
    if set(blobs) != set(expected) or any(hashlib.sha256(blobs[n]).hexdigest() != h for n, h in expected.items()):
        raise GraphIntegrityError("snapshot lacks verified original source bytes")
    with TemporaryDirectory(prefix="eset_resolver_readonly_") as d:
        workspace = Path(d)
        graph_dir, destination = workspace / "graph", workspace / "out"
        graph_dir.mkdir()
        for name, data in sorted(blobs.items()):
            (graph_dir / name).write_bytes(data)
        # The unchanged historical script reads only an exact, captured 31-file copy.
        cmd = [sys.executable, "-X", "utf8", "-B", str(RESOLVER_SCRIPT), "--graph-dir", str(graph_dir),
               "--policy", str(RESOLVER_POLICY), "--out-dir", str(destination)]
        completed = subprocess.run(cmd, capture_output=True, timeout=120, check=False)
        if completed.returncode:
            raise GraphIntegrityError(f"pinned resolver execution failed: {completed.stderr[:1000]!r}")
        audit = strict_loads((destination / "resolver_audit_v0_2.json").read_bytes())
        raw_output = (destination / "resolved_verdict_state_v0_2.jsonl").read_bytes()
        raw_summary = (destination / "subject_axis_summary_v0_2.json").read_bytes()
        output, summary = _lf_bytes(raw_output), _lf_bytes(raw_summary)
        raw_hash, raw_summary_hash = hashlib.sha256(raw_output).hexdigest(), hashlib.sha256(raw_summary).hexdigest()
        if audit["resolved_output_sha256"] != raw_hash or audit["summary_output_sha256"] != raw_summary_hash:
            raise GraphIntegrityError("resolver's own raw-output digests disagree")
        if (hashlib.sha256(output).hexdigest() != lock["resolved_output_sha256"] or
                hashlib.sha256(summary).hexdigest() != lock["summary_output_sha256"]):
            raise GraphIntegrityError("pinned resolver LF-normalized output differs from sealed result")
        for key, expected_key in (("resolution_partitions", "partitions"),
                                   ("subject_axis_summaries", "summaries"), ("verdicts_scanned", "verdict_count")):
            if audit[key] != lock[expected_key]:
                raise GraphIntegrityError(f"resolver output {key} count mismatch")
        if (audit["canonical_graph_sha256"] != snapshot.graph_sha256 or
                audit["resolver_implementation_sha256"] != lock["resolver_implementation_sha256"] or
                audit["policy_semantic_sha256"] != lock["resolver_policy_semantic_sha256"] or
                audit["resolver_execution_status"] != "PASS_SCOPED" or
                not all(audit["pass_conditions"].values()) or audit["authority_conflicts"] or
                audit["authority_gaps"] or audit["claim_firewall"]["resolver_inferred_promotions"]):
            raise GraphIntegrityError("sealed scientific resolver audit failed")
        audit["portable_output_identity"] = {
            "normalization": "UTF8_LF_FOR_GENERATED_OUTPUT_ONLY",
            "raw_resolved_sha256": raw_hash, "raw_summary_sha256": raw_summary_hash,
            "lf_resolved_sha256": hashlib.sha256(output).hexdigest(),
            "lf_summary_sha256": hashlib.sha256(summary).hexdigest()}
        parts = tuple(strict_loads(line) for line in output.splitlines() if line.strip())
        return VerifiedResolver(snapshot, parts, tuple(strict_loads(summary)), audit)


class UnauthorizedPhysicalOutput(PermissionError):
    pass


def _resolved_primary_partition(partition: dict[str, Any], *, subject: str,
                                axis: str, scope: str, state: str) -> bool:
    return (partition.get("subject")==subject and partition.get("axis")==axis and
            partition.get("scope")==scope and partition.get("resolved_state")==state and
            partition.get("resolution_status")=="RESOLVED" and
            partition.get("scope_quality")=="EXPLICIT_OR_GLOBAL" and
            not any(b.get("active_by_declared_state") for b in partition.get("blocked_by", [])))


def _evaluate_scoped_admission(*, provider: dict[str, Any], source_verdict: dict[str, Any],
                                partition: dict[str, Any], product_partition: dict[str, Any],
                                provider_id: str, observable: str, scope: str) -> bool:
    """Pure scoped positive/negative checker, also testable without a real source."""
    if not (provider.get("type")=="Provider" and provider.get("id")==provider_id and
            provider.get("provider_admitted") is True and
            provider.get("production_scoring_authorized") is False and
            isinstance(provider.get("physical_outputs_authorized"), list) and
            observable in provider["physical_outputs_authorized"]):
        return False
    if not (source_verdict.get("type")=="Verdict" and
            source_verdict.get("subject")==provider_id and
            source_verdict.get("axis")=="provider_state" and
            source_verdict.get("value")=="PROVIDER_ADMITTED" and
            source_verdict.get("scope")==scope and
            isinstance(source_verdict.get("authority_refs"),list) and source_verdict["authority_refs"]):
        return False
    if not _resolved_primary_partition(partition,subject=provider_id,axis="provider_state",scope=scope,state="PROVIDER_ADMITTED"):
        return False
    if source_verdict["id"] not in partition.get("active_verdicts",[]):
        return False
    if not partition.get("authority_basis",{}).get(source_verdict["id"]):
        return False
    if not _resolved_primary_partition(product_partition,subject=provider_id,
                                      axis="physical_claim_state",scope=product_partition.get("scope"),
                                      state="PHYSICAL_OUTPUTS_ADMITTED_NARROW"):
        return False
    return bool(product_partition.get("active_verdicts"))


def authorize_physical_output(resolved: VerifiedResolver, provider_id: str,
                              observable: str, scope: str, *, product_scope: str | None = None) -> dict[str, str]:
    """Narrow source-backed provider and physical-output authorization only.

    The sealed graph contains source-authorized P1R background and BG8 composition
    outputs; this API reports *only* those scoped outputs, not observation validation.
    A request with a broad scope or fabricated graph lock is rejected.
    """
    try:
        trusted = run_pinned_resolver(resolved.snapshot)
    except (GraphIntegrityError, OSError, ValueError, TypeError, AttributeError) as exc:
        raise UnauthorizedPhysicalOutput(f"unverified resolver/source identity: {exc}") from exc
    if (resolved.partitions != trusted.partitions or resolved.summaries != trusted.summaries or
            resolved.audit != trusted.audit):
        raise UnauthorizedPhysicalOutput("caller-supplied resolver results differ from fresh sealed replay")
    resolved = trusted
    from native_eset.graph.trust_roots import APPROVED_ESET_SNAPSHOT_SHA256
    if resolved.snapshot.graph_sha256 != APPROVED_ESET_SNAPSHOT_SHA256:
        raise UnauthorizedPhysicalOutput("snapshot is not a frozen approved ESET authority")
    if resolved.audit.get("resolver_execution_status")!="PASS_SCOPED":
        raise UnauthorizedPhysicalOutput("resolver not PASS_SCOPED")
    obj=resolved.snapshot.nodes.get(provider_id)
    if obj is None or obj.type!="Provider":
        raise UnauthorizedPhysicalOutput("unknown source provider")
    provider=obj.raw
    if not isinstance(provider.get("source_refs"),list) or not provider["source_refs"]:
        raise UnauthorizedPhysicalOutput("source provider has no source refs")
    vp=[p for p in resolved.partitions if _resolved_primary_partition(
        p,subject=provider_id,axis="provider_state",scope=scope,state="PROVIDER_ADMITTED")]
    products=[p for p in resolved.partitions if p.get("subject")==provider_id and
              p.get("axis")=="physical_claim_state" and
              p.get("resolved_state")=="PHYSICAL_OUTPUTS_ADMITTED_NARROW" and
              (product_scope is None or p.get("scope")==product_scope)]
    if len(vp) != 1 or len(products) != 1:
        raise UnauthorizedPhysicalOutput("zero/ambiguous source-authorized provider or physical-output scope")
    product = products[0]
    if (product.get("scope_quality") != "EXPLICIT_OR_GLOBAL" or
            product.get("scope") in {None, "__UNSCOPED__"} or
            not product.get("authority_basis")):
        raise UnauthorizedPhysicalOutput("physical-output scope lacks controlling authority")
    for vid in product.get("active_verdicts", []):
        source = resolved.snapshot.nodes.get(vid)
        if (source is None or source.type != "Verdict" or
                source.raw.get("subject") != provider_id or
                source.raw.get("axis") != "physical_claim_state" or
                source.raw.get("value") != "PHYSICAL_OUTPUTS_ADMITTED_NARROW" or
                not product["authority_basis"].get(vid)):
            raise UnauthorizedPhysicalOutput("physical-output verdict is not source-backed")
    for vp_row in vp:
        for vid in vp_row.get("active_verdicts",[]):
            node=resolved.snapshot.nodes.get(vid)
            if node and _evaluate_scoped_admission(
                    provider=provider,source_verdict=node.raw,partition=vp_row,
                    product_partition=products[0],provider_id=provider_id,
                    observable=observable,scope=scope):
                return {"provider_id":provider_id,"observable":observable,"provider_scope":scope,
                        "physical_output_scope":products[0]["scope"],"primary_provider_verdict":vid,
                        "graph_sha256":resolved.snapshot.graph_sha256,
                        "claim_boundary":"SCOPED_PROVIDED_OUTPUT_ONLY_NOT_VALIDATED_OR_PRODUCTION_SCORING"}
    raise UnauthorizedPhysicalOutput("no controlling primary verdict permits this exact output")
