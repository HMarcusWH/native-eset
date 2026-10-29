"""HIST-001B transition-radius precheck admission boundary.

The June ledger claims 600 grid-cell matches, but the original accelerated
implementation and original 600 input-case inventory are absent. This module
must not substitute newly generated cases and call the archive verified.
"""
from __future__ import annotations

from native_eset.historical.hist001b_source import (
    HISTORICAL_PRODUCER_STATUS, PRECHECK_STATUS,
)


class OriginalPrechecksUnavailable(ValueError):
    pass


REQUIRED_ORIGINAL_CASES = 600


def precheck_status() -> dict:
    return {
        "status": PRECHECK_STATUS,
        "required_cases": REQUIRED_ORIGINAL_CASES,
        "executed_original_cases": 0,
        "original_case_manifest_sha256": None,
        "original_accelerated_code_sha256": None,
        "grid_cell_equivalence_proved": False,
        "original_producer_status": HISTORICAL_PRODUCER_STATUS,
        "source_exact_replay_authorized": False,
    }


def require_original_600_prechecks(*, producer_sha256: str | None = None,
                                   case_manifest_sha256: str | None = None,
                                   claimed_matches: int | None = None) -> None:
    """Fail closed until trusted, non-caller-defined original identities exist.

    Even 600/600 claimed matches are not a proof without independently
    authenticated code and the exact original 600 input cases.
    """
    del producer_sha256, case_manifest_sha256, claimed_matches
    raise OriginalPrechecksUnavailable(
        "Original accelerated producer and original 600-case manifest "
        "not recovered; independent precheck authority is blocked"
    )
