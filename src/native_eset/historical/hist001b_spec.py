"""Immutable historical robustness RunSpec. Only diagnostic modes are admitted."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any

from native_eset.evidence.receipts import canonical_json
from native_eset.historical.hist001b_source import (
    HIST001A_SOURCE_LOCK_SHA256, HIST001B_MARCH_SHA256,
    HIST001B_MASTER_SHA256,
)

SPEC_SCHEMA = "NATIVE_ESET_HIST001B_RUN_SPEC_V1"
FULL = "DIAGNOSTIC_4X1000"
SMOKE = "DIAGNOSTIC_SMOKE"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
SEED_MODE = "NUMPY_SEEDSEQUENCE_TRIAL_V1_NOT_ORIGINAL_PROVED"
WIDTHS = [0.01, 0.02, 0.05, 0.10]


@dataclass(frozen=True)
class HistoricalRobustnessRunSpec:
    raw: dict[str, Any]
    sha256: str

    @property
    def canonical_bytes(self) -> bytes:
        return canonical_json(self.raw)

    @classmethod
    def build(cls, *, smoke: bool = False, trials: int = 1000) -> "HistoricalRobustnessRunSpec":
        if type(trials) is not int or (not smoke and trials != 1000) or (
            smoke and not (1 <= trials <= 8)
        ):
            raise ValueError("full mode requires 1000 trials; smoke permits only 1..8")
        raw = {
            "schema": SPEC_SCHEMA,
            "finite_model_id": "HIST-001-SWELLS-J2141-SETA-FROZEN",
            "backend_id": "legacy-hist001-j2141-seta",
            "candidate": CANDIDATE,
            "data_use": "HISTORICAL_FITTED_REGRESSION_NOT_HOLDOUT",
            "mode": SMOKE if smoke else FULL,
            "trials_per_width": trials,
            "widths": [0.01] if smoke else list(WIDTHS),
            "seed_root": 2141,
            "seed_mode": SEED_MODE,
            "source_lock_sha256": HIST001A_SOURCE_LOCK_SHA256,
            "march_archive_sha256": HIST001B_MARCH_SHA256,
            "june_master_sha256": HIST001B_MASTER_SHA256,
            "original_producer_authorized": False,
            "original_rng_schedule_proved": False,
            "physical_provider_admitted": False,
            "native_v172_equivalence_proved": False,
            "empirical_validation": "NOT_ESTABLISHED",
        }
        digest = hashlib.sha256(canonical_json(raw)).hexdigest()
        return cls(raw=raw, sha256=digest)

    @classmethod
    def parse(cls, raw: dict[str, Any]) -> "HistoricalRobustnessRunSpec":
        if not isinstance(raw, dict):
            raise ValueError("B RunSpec must be a dict")
        smoke = raw.get("mode") == SMOKE
        expected = cls.build(smoke=smoke, trials=raw.get("trials_per_width"))
        if raw != expected.raw or set(raw) != set(expected.raw):
            raise ValueError("unsupported HIST001B RunSpec/role/seed/tolerances")
        return expected
