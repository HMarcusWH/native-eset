"""Declared backend capabilities. Nothing in this file grants provider admission."""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType


class UnsupportedCapability(RuntimeError):
    pass


@dataclass(frozen=True)
class Capability:
    backend_id: str
    theory_id: str
    executable: bool
    observables: tuple[str, ...]
    model_role: str


CAPABILITIES = MappingProxyType({
    "external-gr-lcdm-control": Capability("external-gr-lcdm-control", "GR_LCDM_REFERENCE", True,
                                            ("E_of_z", "chi_dimensionless_of_z"), "EXTERNAL_REFERENCE_CONTROL_ONLY"),
    "legacy-june-eset3-4": Capability("legacy-june-eset3-4", "HISTORICAL_ESET3_4", False, (), "ARCHIVE_RECOVERY_PENDING"),
    "legacy-june-gd-variable-f": Capability("legacy-june-gd-variable-f", "HISTORICAL_VARIABLE_F", False, (), "ARCHIVED_RESULT_NOT_IMPORTED"),
    "native-v1.7.2-one-map": Capability("native-v1.7.2-one-map", "NATIVE_ESET_V172", False, (), "CURRENT_PHYSICS_NOT_IMPORTED"),
})


def require_capability(backend_id: str, theory_id: str, observable: str) -> Capability:
    if backend_id not in CAPABILITIES:
        raise UnsupportedCapability(f"unknown backend {backend_id}; no discovery-by-name fallback")
    cap = CAPABILITIES[backend_id]
    if not cap.executable:
        raise UnsupportedCapability(f"backend {backend_id} not implemented; physics import required")
    if cap.theory_id != theory_id or observable not in cap.observables:
        raise UnsupportedCapability("wrong theory/observable for this backend; no cross-model inference")
    return cap
