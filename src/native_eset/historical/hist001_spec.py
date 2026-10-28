"""HIST-001A/1: immutable source-bound specification, execution NOT implemented.

No numerical parameters, fitted-law overrides, survey selection, physical
observables or validation authorization are permitted by this schema.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from native_eset.evidence.data_roles import check_data_role
from native_eset.evidence.receipts import canonical_json
from native_eset.historical.hist001_approved import approved_hist001
from native_eset.serialization import read_json, require_sha256

HIST001_SCHEMA = "NATIVE_ESET_HIST001_RUN_SPEC_V1"
CENTRAL = "STRICT_CENTRAL"
CENTRAL_SPHERE = "STRICT_CENTRAL_PLUS_SPHERICAL_NEGATIVE"
MODES = frozenset({CENTRAL, CENTRAL_SPHERE})
HIST001_OUTPUTS = ("historical_rotation_lensing_regression", "historical_setA_portability")
NEGATIVE_OUTPUT = "historical_spherical_projection_negative_control"
FIELDS = frozenset({
    "schema", "backend_id", "theory_id", "finite_model_id", "source_lock_sha256",
    "original_archive_sha256", "original_branch", "frozen_config_sha256", "frozen_baseline_sha256",
    "lens_table_sha256", "candidate_name", "execution_mode", "data_use", "source_history",
    "claim_intent", "frame", "gauge", "coordinate", "unit_convention",
    "expected_lens_ids", "expected_output_classes",
})


class InvalidHistoricalRunSpec(ValueError):
    """An unsupported or altered historical run request."""


def historical_spec_for_mode(mode: str = CENTRAL_SPHERE) -> dict[str, Any]:
    """Return a fresh fixed-purpose request, not a source-editable parameter space."""
    if mode not in MODES:
        raise InvalidHistoricalRunSpec("unregistered historical execution mode")
    a = approved_hist001()
    return {
        "schema": HIST001_SCHEMA,
        "backend_id": a["backend_id"], "theory_id": a["theory_id"],
        "finite_model_id": a["finite_model_id"],
        "source_lock_sha256": a["source_lock_sha256"],
        "original_archive_sha256": a["original_archive_sha256"],
        "original_branch": a["original_branch"],
        "frozen_config_sha256": a["config_sha256"],
        "frozen_baseline_sha256": a["baseline_sha256"],
        "lens_table_sha256": a["lens_table_sha256"],
        "candidate_name": a["frozen_candidate"],
        "execution_mode": mode,
        "data_use": a["data_use"], "source_history": a["source_history"],
        "claim_intent": a["claim_intent"],
        "frame": a["frame"], "gauge": a["gauge"],
        "coordinate": a["coordinate"], "unit_convention": a["unit_convention"],
        "expected_lens_ids": list(a["expected_lens_ids"]),
        "expected_output_classes": list(HIST001_OUTPUTS) + ([NEGATIVE_OUTPUT] if mode == CENTRAL_SPHERE else []),
    }


def validate_historical_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != FIELDS:
        raise InvalidHistoricalRunSpec("HIST-001 request schema, missing/extra keys or unsupported capability")
    if not all(isinstance(k, str) for k in raw):
        raise InvalidHistoricalRunSpec("HIST-001 requires string field names")
    if raw.get("schema") != HIST001_SCHEMA:
        raise InvalidHistoricalRunSpec("wrong HIST-001 schema; control/current physics requires separate contract")
    mode = raw.get("execution_mode")
    if not isinstance(mode, str) or mode not in MODES:
        raise InvalidHistoricalRunSpec("only exact central and predeclared spherical-negative modes are supported")
    expected = historical_spec_for_mode(mode)
    for key, fixed in expected.items():
        current = raw[key]
        if type(current) is not type(fixed) or current != fixed:
            raise InvalidHistoricalRunSpec(f"source/model/role/units/selection mismatch: {key}")
    for name in ("source_lock_sha256", "original_archive_sha256", "frozen_config_sha256",
                 "frozen_baseline_sha256", "lens_table_sha256"):
        require_sha256(raw[name], name)
    try:
        check_data_role(raw["data_use"], raw["claim_intent"])
    except ValueError as exc:
        raise InvalidHistoricalRunSpec("historical data-use / nonvalidation gate rejected request") from exc
    return raw


@dataclass(frozen=True, init=False)
class HistoricalRunSpec:
    """Immutable bytes; caller mutation of its input or .raw cannot alter a run."""

    _bytes: bytes
    spec_sha256: str

    def __init__(self, raw: dict[str, Any], spec_sha256: str | None = None):
        validate_historical_spec(raw)
        frozen = canonical_json(raw)
        actual = hashlib.sha256(frozen).hexdigest()
        if spec_sha256 is not None and (type(spec_sha256) is not str or spec_sha256 != actual):
            raise InvalidHistoricalRunSpec("caller supplied stale or forged HIST-001 digest")
        object.__setattr__(self, "_bytes", frozen)
        object.__setattr__(self, "spec_sha256", actual)

    @property
    def raw(self) -> dict[str, Any]:
        return json.loads(self._bytes)

    @property
    def canonical_bytes(self) -> bytes:
        return self._bytes

    @classmethod
    def from_mode(cls, mode: str = CENTRAL_SPHERE) -> "HistoricalRunSpec":
        return cls(historical_spec_for_mode(mode))

    @classmethod
    def read(cls, path: str | Path) -> "HistoricalRunSpec":
        return cls(read_json(Path(path), max_bytes=64_000))
