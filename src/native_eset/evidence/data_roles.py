"""Role-preserving use checks. These checks cannot certify unknown data history."""
from __future__ import annotations
DATA_ROLES = frozenset({"CALIBRATION", "REGRESSION", "INTERNAL_TEST", "EXTERNAL_CONSTRAINT",
                        "FALSIFIER", "HELD_OUT_VALIDATION", "PROVIDER_CONSTRUCTION", "DIAGNOSTIC"})


class DataContaminationError(ValueError):
    pass


def check_data_role(role: str, claim_intent: str) -> None:
    if role not in DATA_ROLES:
        raise DataContaminationError(f"unknown dataset role: {role}")
    if claim_intent not in {"CONTROL_ONLY", "REGRESSION_ONLY", "EXPLORATORY_ONLY"}:
        raise DataContaminationError("bootstrap forbids physical/holdout validation promotion")
    if role == "HELD_OUT_VALIDATION":
        raise DataContaminationError("bootstrap execution must not open sealed holdout data")
    # Historical calibration data may be replayed, retaining CALIBRATION role.
    # REGRESSION_ONLY is not a claim of pristine independent validation.
