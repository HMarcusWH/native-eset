"""Independent HIST-001B receipts; no GR or HIST-001A verifier dispatch changes.

An authenticated archived CSV still cannot establish the missing original
accelerated producer. All accepted receipts are diagnostic or fail-closed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from native_eset.evidence.receipts import canonical_json
from native_eset.historical.hist001b_compare import inspect_output, WIDTHS
from native_eset.historical.hist001b_source import (
    HIST001A_SOURCE_LOCK_SHA256, HISTORICAL_PRODUCER_STATUS,
    PRECHECK_STATUS, require_no_symlink_components, verify_b_oracle,
)
from native_eset.historical.hist001b_spec import (
    HistoricalRobustnessRunSpec, SMOKE,
)
from native_eset.historical.hist001_source import verify_hist001_source
from native_eset.serialization import strict_loads

RECEIPT_SCHEMA = "NATIVE_ESET_HIST001B_ROBUSTNESS_RECEIPT_V1"
CLAIMS = {
    "physical_provider_admitted": False,
    "native_v172_equivalence_proved": False,
    "empirical_validation": "NOT_ESTABLISHED",
    "production_scoring_authorized": False,
    "source_exact_replay_authorized": False,
}
ALLOWED_STATUSES = {
    "HIST001B_SMOKE_ONLY_NOT_REEXECUTED",
    "HIST001B_ARCHIVED_REPLAY_MISMATCH_FAIL_CLOSED",
    "HIST001B_COUNTS_MATCH_SOURCE_EXACT_NOT_ESTABLISHED",
    "HIST001B_SOURCE_NOT_RECOVERED_NO_ORACLE",
}
EXPECTED_FIELDS = frozenset({
    "schema", "status", "run_id", "run_spec_sha256",
    "source_lock_sha256", "oracle_verified", "original_producer_status",
    "original_precheck_status", "output_files", "environment",
    "execution", "claim_boundary",
})


class Hist001BReceiptError(ValueError):
    pass


def _load(path: Path) -> dict:
    path = require_no_symlink_components(path)
    if not path.is_file() or path.stat().st_size > 160_000:
        raise Hist001BReceiptError("missing/oversized B receipt JSON")
    result = strict_loads(path.read_bytes())
    if not isinstance(result, dict):
        raise Hist001BReceiptError("B receipt is not a JSON object")
    return result


def _sha(path: Path, *, max_bytes: int = 300_000) -> str:
    p = require_no_symlink_components(path)
    if not p.is_file() or p.stat().st_size > max_bytes:
        raise Hist001BReceiptError("missing/oversized B output: " + str(path))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def expected_files(spec: HistoricalRobustnessRunSpec) -> set[str]:
    base = {"audit.json", "independent_inspection.json",
            "run_spec.json", "execution.json"}
    return base | {
        f"width_{round(w * 100):02d}pct.csv" for w in spec.raw["widths"]
    }


def _derived_status(spec: HistoricalRobustnessRunSpec, inspection: dict) -> str:
    if spec.raw["mode"] == SMOKE:
        return "HIST001B_SMOKE_ONLY_NOT_REEXECUTED"
    if not inspection["oracle_verified"]:
        return "HIST001B_SOURCE_NOT_RECOVERED_NO_ORACLE"
    if not inspection["complete_archival_row_match"]:
        return "HIST001B_ARCHIVED_REPLAY_MISMATCH_FAIL_CLOSED"
    return "HIST001B_COUNTS_MATCH_SOURCE_EXACT_NOT_ESTABLISHED"


def verify_hist001b_receipt(receipt_path: str | Path, *,
                            source_root: str | Path,
                            oracle_root: str | Path | None = None,
                            expected_sha256: str | None = None) -> dict[str, Any]:
    receipt_file = require_no_symlink_components(receipt_path)
    root = require_no_symlink_components(receipt_file.parent)
    actual_digest = _sha(receipt_file, max_bytes=160_000)
    if expected_sha256 is not None and (
        len(expected_sha256) != 64 or actual_digest != expected_sha256
    ):
        raise Hist001BReceiptError("independent B receipt digest mismatch")
    declared_digest = require_no_symlink_components(root / "receipt.sha256").read_text(encoding="ascii")
    if declared_digest != actual_digest + "\n":
        raise Hist001BReceiptError("B receipt marker mismatch")
    receipt = _load(receipt_file)
    if set(receipt) != EXPECTED_FIELDS or receipt.get("schema") != RECEIPT_SCHEMA:
        raise Hist001BReceiptError("unknown or forged B receipt fields/schema")
    if receipt.get("claim_boundary") != CLAIMS:
        raise Hist001BReceiptError("B receipt attempts unauthorized promotion")
    if receipt.get("original_producer_status") != HISTORICAL_PRODUCER_STATUS or (
        receipt.get("original_precheck_status") != PRECHECK_STATUS
    ):
        raise Hist001BReceiptError("B receipt attempts false producer/600-proof")
    if receipt.get("source_lock_sha256") != HIST001A_SOURCE_LOCK_SHA256:
        raise Hist001BReceiptError("B original source SHA identity changed")
    verified_a = verify_hist001_source(
        require_no_symlink_components(source_root)
    )
    if verified_a["source_lock_sha256"] != HIST001A_SOURCE_LOCK_SHA256:
        raise Hist001BReceiptError("frozen original A-source identity changed")
    if (oracle_root is not None) != (receipt.get("oracle_verified") is True):
        raise Hist001BReceiptError("B oracle identity omitted or forged")
    if oracle_root is not None:
        verify_b_oracle(oracle_root)
    spec_data = _load(root / "run_spec.json")
    spec = HistoricalRobustnessRunSpec.parse(spec_data)
    if receipt.get("run_spec_sha256") != spec.sha256:
        raise Hist001BReceiptError("B RunSpec digest changed")
    file_set = expected_files(spec)
    if set(receipt["output_files"]) != file_set:
        raise Hist001BReceiptError("B output-file inventory differs from spec")
    actual_files = {p.name for p in root.iterdir()}
    if actual_files != file_set | {"receipt.json", "receipt.sha256"}:
        raise Hist001BReceiptError("B output contains missing/extra files")
    for name in file_set:
        if _sha(root / name) != receipt["output_files"][name]:
            raise Hist001BReceiptError("B recorded file digest mismatch: " + name)
    inspection = inspect_output(
        root, n_trials=spec.raw["trials_per_width"],
        smoke=spec.raw["mode"] == SMOKE,
        oracle_root=Path(oracle_root) if oracle_root is not None else None,
    )
    recorded = _load(root / "independent_inspection.json")
    if canonical_json(recorded) != canonical_json(inspection):
        raise Hist001BReceiptError("B independent inspection was tampered")
    worker_audit = _load(root / "audit.json")
    if worker_audit.get("physical_provider_admitted") is not False or (
        worker_audit.get("source_exact_replay_authorized") is not False
    ):
        raise Hist001BReceiptError("B worker audit asserts scientific promotion")
    if worker_audit.get("seed_scheme") != "SeedSequence([2141, trial])":
        raise Hist001BReceiptError("B worker seed identity forged")
    if worker_audit.get("archived_reference_is_new_output") is not False:
        raise Hist001BReceiptError("B archived rows reported as new")
    for idx, derived in enumerate(inspection["widths"]):
        declared = worker_audit["results"][idx]
        if (declared["width"] != derived["width"] or
                declared["n_trials"] != derived["n_trials"] or
                declared["six_of_six"] != derived["n_at_6_of_6"] or
                declared["five_or_more"] != derived["n_at_5_or_more"]):
            raise Hist001BReceiptError("B worker summary differs from recalculated CSV")
    if receipt.get("status") != _derived_status(spec, inspection) or (
        receipt["status"] not in ALLOWED_STATUSES
    ):
        raise Hist001BReceiptError("B false success status")
    if not isinstance(receipt.get("environment"), dict) or not isinstance(
        receipt.get("execution"), dict
    ):
        raise Hist001BReceiptError("missing B numerical environment/execution")
    if receipt["execution"] != _load(root / "execution.json"):
        raise Hist001BReceiptError("B execution ledger differs from receipt")
    execution = receipt["execution"]
    if execution.get("exit_code") != (0 if spec.raw["mode"] == SMOKE else 4):
        raise Hist001BReceiptError("B worker returned wrong scoped exit code")
    if execution.get("source_immutable_after_execution") is not True:
        raise Hist001BReceiptError("B original-source post-execution check missing")
    for key in ("stdout_sha256", "stderr_sha256",
                "worker_implementation_sha256", "driver_implementation_sha256"):
        raw = execution.get(key)
        if not isinstance(raw, str) or len(raw) != 64 or any(
            c not in "0123456789abcdef" for c in raw
        ):
            raise Hist001BReceiptError("invalid B execution digest: " + key)
    # The run identity must bind the fixed RunSpec, source, driver code,
    # platform/dependencies and oracle-admission state. Not a signature.
    run_identity = {
        "spec_sha256": spec.sha256,
        "original_source_sha256": HIST001A_SOURCE_LOCK_SHA256,
        "implementation_sha256": execution["driver_implementation_sha256"],
        "environment": receipt["environment"],
        "oracle_verified": receipt["oracle_verified"],
    }
    computed_id = "hist001b-" + hashlib.sha256(
        canonical_json(run_identity)
    ).hexdigest()[:24]
    if receipt["run_id"] != computed_id or root.name != computed_id:
        raise Hist001BReceiptError("B run identity is not reproducible")
    if not isinstance(receipt["oracle_verified"], bool):
        raise Hist001BReceiptError("B oracle status must be boolean")
    return {
        "status": "VERIFIED_HIST001B_DIAGNOSTIC_OR_FAILURE_BYTES_ONLY",
        "scientific_disposition": receipt["status"],
        "receipt_sha256": actual_digest,
        "original_producer_verified": False,
        "original_600_prechecks_verified": False,
        "source_exact_replay_authorized": False,
        "physical_provider_admitted": False,
        "empirical_validation": "NOT_ESTABLISHED",
        "full_archive_rows_match": inspection["complete_archival_row_match"],
    }
