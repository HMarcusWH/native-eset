"""Independently pinned, packaged HIST-001 source-trust anchor.

Byte digests guard accidental or caller-driven replacement, not malicious code
editors or provenance signatures. Scientific authority stays in Theory-State.
"""
from __future__ import annotations

import hashlib
from importlib import resources
from typing import Any

from native_eset.serialization import strict_loads

APPROVED_LOCK_DIGEST = "00110301e97504a53bfa628b565bf1da643ffc0c78b74710e5b576a33d76be1f"
SOURCE_LOCK_DIGEST = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
APPROVED_SCHEMA = "NATIVE_ESET_HIST001_APPROVED_SOURCE_V1"


class HistoricalSourceIntegrityError(ValueError):
    """The historical source is missing, changed, or outside its declared scope."""


def _read_packaged_anchor() -> bytes:
    return resources.files("native_eset.historical").joinpath("hist001_approved_lock.json").read_bytes()


def approved_hist001() -> dict[str, Any]:
    """Read the independently pinned metadata, never a caller-provided lock."""
    raw = _read_packaged_anchor()
    if hashlib.sha256(raw).hexdigest() != APPROVED_LOCK_DIGEST:
        raise HistoricalSourceIntegrityError("packaged HIST-001 approved-source anchor changed")
    try:
        obj = strict_loads(raw)
    except (TypeError, ValueError, UnicodeError) as exc:
        raise HistoricalSourceIntegrityError("invalid packaged HIST-001 approved-source anchor") from exc
    if (not isinstance(obj, dict) or obj.get("schema") != APPROVED_SCHEMA or
            obj.get("source_lock_sha256") != SOURCE_LOCK_DIGEST or
            obj.get("physical_provider_admitted") is not False or
            obj.get("native_v172_equivalence_proved") is not False or
            obj.get("source_file_count") != 46 or obj.get("negative_record_count") != 3):
        raise HistoricalSourceIntegrityError("invalid HIST-001 approved-source scope")
    return obj
