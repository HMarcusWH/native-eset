"""HIST-001A/1: history identity/role gate; execution stays disabled."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from native_eset.capabilities import CAPABILITIES, UnsupportedCapability, require_capability
from native_eset.historical import HistoricalRunSpec, InvalidHistoricalRunSpec
from native_eset.historical.hist001_spec import (
    CENTRAL, CENTRAL_SPHERE, HIST001_SCHEMA, HIST001_OUTPUTS, NEGATIVE_OUTPUT,
    historical_spec_for_mode,
)


@pytest.mark.parametrize("mode", [CENTRAL, CENTRAL_SPHERE])
def test_frozen_source_bound_spec_and_defensive_canonical_bytes(mode: str, tmp_path: Path) -> None:
    original = historical_spec_for_mode(mode)
    spec = HistoricalRunSpec(original)
    assert spec.raw["schema"] == HIST001_SCHEMA
    assert spec.raw["execution_mode"] == mode
    assert spec.spec_sha256 == HistoricalRunSpec(spec.raw).spec_sha256
    assert spec.raw["expected_output_classes"] == list(HIST001_OUTPUTS) + (
        [NEGATIVE_OUTPUT] if mode == CENTRAL_SPHERE else [])
    original["backend_id"] = "forged-from-input"
    original["expected_lens_ids"].append("new-lens")
    spec.raw["expected_output_classes"].append("physical_CMB")
    assert spec.raw["backend_id"] == "legacy-hist001-j2141-seta"
    assert len(spec.raw["expected_lens_ids"]) == 6
    assert len(spec.raw["expected_output_classes"]) == (3 if mode == CENTRAL_SPHERE else 2)
    path = tmp_path / "hist001.json"
    path.write_bytes(spec.canonical_bytes)
    assert HistoricalRunSpec.read(path).spec_sha256 == spec.spec_sha256
    assert HistoricalRunSpec(spec.raw, spec.spec_sha256).spec_sha256 == spec.spec_sha256
    with pytest.raises(InvalidHistoricalRunSpec, match="stale or forged"):
        HistoricalRunSpec(spec.raw, "0" * 64)


@pytest.mark.parametrize("field,value", [
    ("backend_id", "legacy-june-eset3-4"),
    ("backend_id", "native-v1.7.2-one-map"),
    ("theory_id", "NATIVE_ESET_V172"),
    ("theory_id", "GR_LCDM_REFERENCE"),
    ("finite_model_id", "current-physics-assumed"),
    ("source_lock_sha256", "f" * 64),
    ("original_archive_sha256", "0" * 64),
    ("original_branch", "dma_v2_revised"),
    ("frozen_config_sha256", "0" * 64),
    ("frozen_baseline_sha256", "0" * 64),
    ("lens_table_sha256", "0" * 64),
    ("candidate_name", "new_fitted_candidate"),
    ("execution_mode", "FIT_MORE_PARAMETERS"),
    ("execution_mode", "HELDOUT_LENS_SCORE"),
    ("data_use", "HELD_OUT_VALIDATION"),
    ("data_use", "CALIBRATION"),
    ("source_history", "NEW_INDEPENDENT_HOLDOUT"),
    ("claim_intent", "PHYSICAL_PROVIDER"),
    ("claim_intent", "CONTROL_ONLY"),
    ("frame", "NATIVE_V172_EINSTEIN_FIXED_MP"),
    ("gauge", "NEWTONIAN"),
    ("coordinate", "redshift"),
    ("unit_convention", "SI_AUTOMATIC"),
    ("schema", "NATIVE_ESET_RUN_SPEC_V1"),
])
def test_exact_scientific_frozen_field_contract_rejects_changes(field: str, value: str) -> None:
    a = historical_spec_for_mode()
    a[field] = value
    with pytest.raises(InvalidHistoricalRunSpec):
        HistoricalRunSpec(a)


@pytest.mark.parametrize("key", [
    "delta_epsilon", "fitted_parameters", "redshifts", "physical_provider_admitted", "provider_status",
    "validation", "allowed_holdouts", "dataset", "source_root", "frozen_tolerance_override", "parameters",
    "code_sha256", "prediction_class", "CMB", "R30_BG8", "eta_physical", "source_lock_path",
])
def test_no_refit_providers_or_external_path_in_spec(key: str) -> None:
    a = historical_spec_for_mode()
    a[key] = "trust_me"
    with pytest.raises(InvalidHistoricalRunSpec):
        HistoricalRunSpec(a)


def test_missing_or_mutated_case_membership_and_products() -> None:
    a = historical_spec_for_mode()
    for field in ("expected_lens_ids", "expected_output_classes"):
        bad = copy.deepcopy(a)
        bad[field] = bad[field][:-1]
        with pytest.raises(InvalidHistoricalRunSpec):
            HistoricalRunSpec(bad)
        bad = copy.deepcopy(a)
        bad[field][0] = bad[field][1]
        with pytest.raises(InvalidHistoricalRunSpec):
            HistoricalRunSpec(bad)
        bad = copy.deepcopy(a)
        bad[field] = tuple(bad[field])
        with pytest.raises(InvalidHistoricalRunSpec):
            HistoricalRunSpec(bad)
    del a["original_branch"]
    with pytest.raises(InvalidHistoricalRunSpec):
        HistoricalRunSpec(a)


def test_duplicate_keys_non_finite_and_oversized_input_fail_closed(tmp_path: Path) -> None:
    spec = HistoricalRunSpec.from_mode().canonical_bytes.decode("utf-8")
    cases = (
        spec.replace('"schema":', '"schema":"FAKE","schema":', 1),
        spec.replace('"source_lock_sha256":', '"junk":NaN,"source_lock_sha256":', 1),
        spec.replace('"source_lock_sha256":', '"junk":Infinity,"source_lock_sha256":', 1),
        spec + " " * 65_000,
    )
    p = tmp_path / "untrusted.json"
    for invalid in cases:
        p.write_text(invalid, encoding="utf-8")
        with pytest.raises((ValueError, InvalidHistoricalRunSpec)):
            HistoricalRunSpec.read(p)


def test_capability_exists_but_cannot_dispatch_until_a2_and_a3() -> None:
    cap = CAPABILITIES["legacy-hist001-j2141-seta"]
    assert cap.executable is False
    assert cap.observables == HIST001_OUTPUTS
    assert cap.theory_id == "LEGACY_ESET3_DM_A_FITTED_STRUCTURED_PROJECTION"
    for observable in (*HIST001_OUTPUTS, "physical_lensing", "P3_CMB", "native_growth"):
        with pytest.raises(UnsupportedCapability):
            require_capability(cap.backend_id, cap.theory_id, observable)
