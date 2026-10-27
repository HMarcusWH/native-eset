"""Legacy Admission objects cannot mint scientific status.

Only source-verified Theory-State resolution can authorize narrowly scoped output.
"""
from dataclasses import dataclass
from enum import Enum


class ClaimStatus(str, Enum):
    SPECIFIED = "specified"
    INTERNAL_PASS = "internal_pass"
    OPEN_BLOCKING = "open_blocking"
    FAILED = "failed"
    PHYSICAL_PROVIDER_ADMITTED = "physical_provider_admitted"
    HOLDOUT_VALIDATED = "holdout_validated"


class AdmissionError(RuntimeError):
    pass


@dataclass(frozen=True)
class Admission:
    provider_id: str
    status: ClaimStatus = ClaimStatus.OPEN_BLOCKING
    physical_outputs: tuple[str, ...] = ()
    evidence_hash: str | None = None

    def authorize(self, observable: str) -> None:
        raise AdmissionError(
            "Caller-supplied admission is not authoritative. "
            "Use graph.resolver_adapter.authorize_physical_output against the frozen graph."
        )
