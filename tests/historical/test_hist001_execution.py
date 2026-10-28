"""HIST-001A/2: isolated executable historical regression, not native validation."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from native_eset.capabilities import CAPABILITIES, UnsupportedCapability, require_capability
from native_eset.evidence.receipts import source_tree_digest
from native_eset.historical.hist001_backend import LegacyHistJ2141Backend
from native_eset.historical.hist001_spec import CENTRAL, CENTRAL_SPHERE, HistoricalRunSpec
from native_eset.historical.hist001_receipt import verify_hist001_receipt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"


@pytest.fixture(scope="module")
def historical_run(tmp_path_factory: pytest.TempPathFactory) -> dict:
    out = tmp_path_factory.mktemp("hist001_a2_full")
    response = LegacyHistJ2141Backend().run(HistoricalRunSpec.from_mode(CENTRAL_SPHERE),
                                             source_root=SOURCE, output_root=out)
    return response


def test_frozen_source_bound_backend_outputs_and_verification(historical_run: dict) -> None:
    run = historical_run
    folder = Path(run["output_dir"])
    receipt = json.loads((folder / "receipt.json").read_text())
    assert run["status"] == "HIST001_HISTORICAL_REGRESSION_REPRODUCED_NOT_VALIDATED"
    assert receipt["physical_provider_admitted"] is False
    assert receipt["native_v172_equivalence_proved"] is False
    assert receipt["empirical_validation"] == "NOT_ESTABLISHED"
    assert receipt["claim_intent"] == "REGRESSION_ONLY"
    assert receipt["data_use"] == "REGRESSION"
    assert receipt["j2141_metrics"]["velocity_reduced_chi2"] == pytest.approx(1.1087208637638946)
    assert receipt["setA_metrics"]["n_both_pass"] == 6
    assert receipt["spherical_metrics"]["n_both_pass"] == 2
    assert [n["six_of_six"] for n in receipt["archived_robustness"]["survival"]] == [323, 140, 23, 3]
    assert receipt["archived_robustness"]["status"] == "ARCHIVED_EXECUTION_NOT_REEXECUTED_THIS_RUN"
    assert receipt["source_code_sha256"] == source_tree_digest()
    assert len(receipt["output_files"]) == 11
    verified = verify_hist001_receipt(folder / "receipt.json", source_root=SOURCE,
                                      expected_sha256=run["receipt_sha256"])
    assert verified["status"] == "VERIFIED_HISTORICAL_REGRESSION_BYTES_AND_NUMERICAL_GATES_ONLY"
    assert verified["integrity_anchor"] == "EXTERNAL_EXPECTED_DIGEST_MATCHED"
    assert verified["physical_provider_admitted"] is False
    assert verified["archived_survival_rerun"] is False


def test_original_source_unmodified_after_separate_execution(historical_run: dict) -> None:
    from native_eset.historical.hist001_source import verify_hist001_source
    status = verify_hist001_source(SOURCE)
    assert status["frozen_files"] == 46
    assert status["archived_negative_records"] == 3


def test_historical_backend_does_not_activate_public_capability() -> None:
    cap = CAPABILITIES["legacy-hist001-j2141-seta"]
    assert cap.executable is False
    assert set(cap.observables) == {"historical_rotation_lensing_regression", "historical_setA_portability"}
    with pytest.raises(UnsupportedCapability):
        require_capability(cap.backend_id, cap.theory_id, "historical_setA_portability")
    with pytest.raises(UnsupportedCapability):
        require_capability(cap.backend_id, cap.theory_id, "CMB_TT")


def test_duplicate_run_refuses_overwriting(historical_run: dict) -> None:
    out = Path(historical_run["output_dir"]).parent
    with pytest.raises(FileExistsError, match="already exists"):
        LegacyHistJ2141Backend().run(HistoricalRunSpec.from_mode(), source_root=SOURCE,
                                     output_root=out)


def test_alternate_spec_and_bad_source_fail_before_execution(tmp_path: Path) -> None:
    spec = HistoricalRunSpec.from_mode()
    source = tmp_path / "untrusted_source"
    shutil.copytree(SOURCE, source)
    program = source / "swells_pack_v2/solv/run_setA_port_cand.py"
    program.write_bytes(program.read_bytes() + b"\n# unapproved source mutation\n")
    with pytest.raises(ValueError, match="mismatch"):
        LegacyHistJ2141Backend().run(spec, source_root=source, output_root=tmp_path / "results")
    assert not (tmp_path / "results").exists()


def test_output_overlapping_frozen_source_is_rejected(tmp_path: Path) -> None:
    out = SOURCE / "runs"
    assert not out.exists()
    with pytest.raises(ValueError, match="overlaps"):
        LegacyHistJ2141Backend().run(HistoricalRunSpec.from_mode(CENTRAL),
                                     source_root=SOURCE, output_root=out)
    assert not out.exists()


def test_invalid_non_spec_object_cannot_execute(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="immutable"):
        LegacyHistJ2141Backend().run({"claim_intent": "REGRESSION_ONLY"},
                                     source_root=SOURCE, output_root=tmp_path)


def test_central_mode_produces_no_spherical_artifacts(tmp_path: Path) -> None:
    r = LegacyHistJ2141Backend().run(HistoricalRunSpec.from_mode(CENTRAL),
                                     source_root=SOURCE, output_root=tmp_path)
    folder = Path(r["output_dir"])
    receipt = json.loads((folder / "receipt.json").read_text())
    assert receipt["spherical_metrics"] is None
    assert receipt["gate_ledger"]["spherical_negative"] == "NOT_REQUESTED"
    assert not (folder / "setA_spherical.csv").exists()
    assert verify_hist001_receipt(folder / "receipt.json", source_root=SOURCE)["physical_provider_admitted"] is False
