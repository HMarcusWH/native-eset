"""HIST-001A/3 installed historical CLI and strict receipt-schema routing."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from native_eset.capabilities import CAPABILITIES

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"


def cmd(*args: str, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "native_eset", *args],
                          cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def parsed(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr + "\n" + result.stdout[-1500:]
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def historical_cli_run(tmp_path_factory: pytest.TempPathFactory) -> dict:
    out = tmp_path_factory.mktemp("hist001_a3_command") / "runs"
    result = parsed(cmd("historical", "j2141", "--source-root", str(SOURCE),
                        "--out", str(out), "--strict", "--ablation", "spherical"))
    return result


def test_command_reproduces_narrow_historical_regression(historical_cli_run: dict) -> None:
    result = historical_cli_run
    assert result["status"] == "HIST001_HISTORICAL_REGRESSION_REPRODUCED_NOT_VALIDATED"
    assert result["physical_provider_admitted"] is False
    assert result["archived_robustness_reexecuted"] is False
    folder = Path(result["output_dir"])
    rec = json.loads((folder / "receipt.json").read_text(encoding="utf-8"))
    assert rec["j2141_metrics"]["velocity_reduced_chi2"] == pytest.approx(1.1087208637638946)
    assert rec["setA_metrics"]["n_both_pass"] == 6
    assert rec["spherical_metrics"]["n_both_pass"] == 2
    assert rec["archived_robustness"]["status"] == "ARCHIVED_EXECUTION_NOT_REEXECUTED_THIS_RUN"
    assert rec["physical_provider_admitted"] is False
    assert rec["native_v172_equivalence_proved"] is False
    assert rec["empirical_validation"] == "NOT_ESTABLISHED"


def test_cli_dispatches_historical_receipt_without_weakening_gr(historical_cli_run: dict) -> None:
    receipt = str(Path(historical_cli_run["output_dir"]) / "receipt.json")
    result = parsed(cmd("verify", "--receipt", receipt, "--source-root", str(SOURCE),
                        "--expected-sha256", historical_cli_run["receipt_sha256"]))
    assert result["status"] == "VERIFIED_HISTORICAL_REGRESSION_BYTES_AND_NUMERICAL_GATES_ONLY"
    assert result["integrity_anchor"] == "EXTERNAL_EXPECTED_DIGEST_MATCHED"
    assert result["physical_provider_admitted"] is False
    assert result["archived_survival_rerun"] is False


@pytest.mark.parametrize("args", [
    ("historical", "j2141", "--strict"),
    ("historical", "j2141", "--source-root", "not_present", "--strict"),
    ("historical", "j2141", "--ablation", "spherical"),
    ("historical", "j2141", "--strict", "--ablation", "refitted"),
    ("historical", "j2141", "--strict", "--physical-provider"),
])
def test_historical_cli_rejects_missing_source_strict_or_parameter_overrides(args: tuple[str, ...]) -> None:
    result = cmd(*args)
    assert result.returncode != 0
    assert "HIST001_HISTORICAL_REGRESSION_REPRODUCED_NOT_VALIDATED" not in result.stdout


def test_historical_receipt_requires_source_and_external_digest_is_enforced(historical_cli_run: dict) -> None:
    receipt = str(Path(historical_cli_run["output_dir"]) / "receipt.json")
    missing = cmd("verify", "--receipt", receipt)
    assert missing.returncode == 2
    assert json.loads(missing.stdout)["status"] == "FAIL_CLOSED"
    forged = cmd("verify", "--receipt", receipt, "--source-root", str(SOURCE),
                 "--expected-sha256", "0" * 64)
    assert forged.returncode == 2
    assert json.loads(forged.stdout)["failure_category"] == "INTEGRITY_FAILURE"
    wrong = cmd("verify", "--receipt", receipt, "--source-root", str(SOURCE / "other"))
    assert wrong.returncode == 2
    assert json.loads(wrong.stdout)["status"] == "FAIL_CLOSED"


def test_historical_receipt_does_not_fall_back_to_control_verifier(tmp_path: Path) -> None:
    path = tmp_path / "receipt.json"
    path.write_text('{"schema":"UNRECOGNIZED_FICTITIOUS_SCIENCE_V100"}\n', encoding="utf-8")
    res = cmd("verify", "--receipt", str(path), "--source-root", str(SOURCE))
    assert res.returncode == 2
    assert "unknown receipt schema" in res.stdout
    assert json.loads(res.stdout)["status"] == "FAIL_CLOSED"


def test_original_gr_control_run_and_verify_dispatch_unchanged(tmp_path: Path) -> None:
    fixture = ROOT / "tests/fixtures/E_of_z.json"
    run = parsed(cmd("run", "--spec", str(fixture), "--out", str(tmp_path / "runs")))
    receipt = str(Path(run["output_dir"]) / "receipt.json")
    correct = parsed(cmd("verify", "--receipt", receipt, "--expected-sha256", run["receipt_sha256"]))
    assert correct["status"] == "VERIFIED_OUTPUT_AND_RECEIPT_BYTES_ONLY"
    assert correct["claimed_role"] == "GR_REFERENCE_CONTROL_ONLY_NO_ESET_PHYSICAL_OUTPUT"
    extra = cmd("verify", "--receipt", receipt, "--source-root", str(SOURCE))
    assert extra.returncode == 2
    assert json.loads(extra.stdout)["status"] == "FAIL_CLOSED"


def test_historical_status_and_doctor_do_not_claim_modern_physics() -> None:
    status = parsed(cmd("status"))
    hist = status["backend_capabilities"]["legacy-hist001-j2141-seta"]
    assert hist["executable"] is True
    assert set(hist["observables"]) == {
        "historical_rotation_lensing_regression", "historical_setA_portability",
    }
    assert "CURRENT_NATIVE_ESET_PHYSICS_NOT_IMPLEMENTED" in status["science_status"]
    assert status["physical_outputs_authorized"] == []
    doctor = parsed(cmd("doctor"))
    assert doctor["hist001_executable_registered"] is True
    assert doctor["hist001_external_source"] == "NOT_CHECKED_SOURCE_ROOT_NOT_SUPPLIED"
    verified = parsed(cmd("doctor", "--historical-source-root", str(SOURCE)))
    assert verified["hist001_external_source"]["frozen_files"] == 46
    assert verified["hist001_external_source"]["source_preflight_is_execution"] is False
    assert verified["native_ESET_physics"] == "NOT_IMPLEMENTED"
    assert CAPABILITIES["native-v1.7.2-one-map"].executable is False
