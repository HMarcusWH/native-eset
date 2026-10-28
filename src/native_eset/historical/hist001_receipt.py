"""HIST-001A/2 verified historical regression receipts. NOT a physical admission.

Integrity and independent frozen-numeric checks are separate from scientific
validation. A receipt with a recomputed self-hash cannot forge model status,
selected lenses, or expected per-row numerical results.
"""
from __future__ import annotations

import csv
from importlib import resources
import json
import math
from pathlib import Path
from typing import Any

from native_eset.evidence.receipts import canonical_json, digest_bytes
from native_eset.historical.hist001_approved import approved_hist001, SOURCE_LOCK_DIGEST
from native_eset.historical.hist001_spec import (
    CENTRAL, CENTRAL_SPHERE, HistoricalRunSpec,
)
from native_eset.historical.hist001_source import verify_hist001_source
from native_eset.serialization import read_json, require_sha256, resolve_regular_file

RECEIPT_SCHEMA = "NATIVE_ESET_HIST001_RUN_RECEIPT_V1"
RUNTIME_CONTRACT = "HIST001_ISOLATED_RUNNER_V1"
CLAIM_CAP = "FITTED_HISTORICAL_REGRESSION_NOT_VALIDATION_OR_NATIVE_V172"
GOLDEN_SHA256 = "c7f53f3c419dd1ab1d7a09a68a5d8a4ea5499b440ce01673f1fe7a08408f1f9f"
ARCHIVED_COUNTS = {"0.01": 323, "0.02": 140, "0.05": 23, "0.1": 3}
J_METRICS = {
    "velocity_reduced_chi2": 1.1087208637638946,
    "einstein_radius_pull_sigma": 1.2456888888888888,
    "lensing_mass_pull_sigma": 0.20461194029850702,
    "abs_eta_minus_1": 0.0,
}
SET_A_EXPECTED = {
    "center": (6, 0.975973270592819, 0.5980326367412955),
    "sphere": (2, 8.168644014357623, 3.234216692852517),
}
J_ARTIFACTS = (
    "j2141/j2141_solver_output_filled.csv",
    "j2141/j2141_lensing_output_filled.csv",
    "j2141/j2141_acceptance_scoreboard_filled.csv",
    "j2141/j2141_run_summary.json",
    "j2141/run_manifest.json",
)
CENTRAL_ARTIFACTS = ("setA_center.csv", "setA_center.json")
SPHERE_ARTIFACTS = ("setA_spherical.csv", "setA_spherical.json")
ADDITIONAL = ("run_spec.json", "execution_steps.json")
GATES = {
    "source_exact": "PASS", "historical_regression": "PASS",
    "spherical_negative": "PASS_REEXECUTED", "archived_four_widths": "ARCHIVED_NOT_REEXECUTED",
    "physical_provider": "NOT_ADMITTED", "independent_validation": "NOT_ESTABLISHED",
    "native_v172_equivalence": "NOT_ESTABLISHED",
}


class HistoricalReceiptIntegrityError(ValueError):
    """A recorded historical run is incomplete, forged, or numerically wrong."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise HistoricalReceiptIntegrityError(message)


def expected_artifacts(mode: str) -> set[str]:
    _require(mode in {CENTRAL, CENTRAL_SPHERE}, "unregistered historical execution mode")
    return set(J_ARTIFACTS + CENTRAL_ARTIFACTS + ADDITIONAL +
               (SPHERE_ARTIFACTS if mode == CENTRAL_SPHERE else ()))


def _golden_rows() -> dict[str, list[dict[str, str]]]:
    raw = resources.files("native_eset.historical").joinpath("hist001_golden_rows.json").read_bytes()
    _require(digest_bytes(raw) == GOLDEN_SHA256, "independently pinned numerical fixture changed")
    obj = json.loads(raw)
    _require(obj.get("schema") == "HIST001_FROZEN_NUMERIC_ROWS_V1" and
             obj.get("reference_role") == "REPLAY_FROZEN_REGRESSION_NOT_HOLDOUT", "invalid golden scope")
    return obj["tables"]


def _numeric(text: object) -> float:
    _require(isinstance(text, (str, float, int)) and type(text) is not bool, "non-numeric table cell")
    try:
        v = float(text)
    except (ValueError, TypeError, OverflowError) as exc:
        raise HistoricalReceiptIntegrityError("non-numeric table cell") from exc
    _require(math.isfinite(v), "non-finite historical table cell")
    return v


def _close(actual: float, expected: float, label: str, *, atol: float = 1e-8, rtol: float = 1e-11) -> None:
    _require(math.isclose(actual, expected, abs_tol=atol, rel_tol=rtol), f"historical numeric mismatch: {label}")


def _read_csv(root: Path, name: str) -> list[dict[str, str]]:
    p = resolve_regular_file(root, name)
    _require(p.stat().st_size <= 100_000, "historical CSV exceeds output budget")
    with p.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _require(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)) and
                 all(reader.fieldnames), "historical CSV ambiguous column names")
        records = list(reader)
    _require(not any(None in row for row in records), "CSV has extra columns")
    return records


def _numeric_reference(root: Path, name: str, golden: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows = _read_csv(root, name)
    expected = golden[name]
    _require(len(rows) == len(expected), f"different historical row count: {name}")
    for idx, (a, b) in enumerate(zip(rows, expected)):
        _require(set(a) == set(b), f"historical column identity changed: {name}")
        for key, ref in b.items():
            val = a[key]
            if ref in {"", "True", "False"} or key in {"lens_id", "metric", "status", "gate_label"}:
                _require(val == ref, f"historical immutable literal changed: {name}:{idx}:{key}")
            else:
                _close(_numeric(val), _numeric(ref), f"{name}:{idx}:{key}")
    return rows


def _seta_from_rows(rows: list[dict[str, str]], summary: dict[str, Any], *, label: str) -> None:
    anchor = approved_hist001()
    _require([row["lens_id"] for row in rows] == anchor["expected_lens_ids"], "wrong Set A lens identities")
    _require(len(rows) == len(set(row["lens_id"] for row in rows)), "repeated Set A lens IDs")
    _require(all(row["gate_label"] == anchor["frozen_candidate"] for row in rows), "changed fitted candidate")
    rs, ms, both = [], [], []
    for row in rows:
        r = _numeric(row["einstein_radius_pull_sigma"])
        m = _numeric(row["mass_pull_sigma"])
        flags = (abs(r) <= 2.0, abs(m) <= 2.0)
        _require(row["radius_pass_abs_le_2sigma"] == str(flags[0]) and
                 row["mass_pass_abs_le_2sigma"] == str(flags[1]) and
                 row["both_pass"] == str(all(flags)), "per-lens gate does not match numeric pull")
        rs.append(r)
        ms.append(m)
        both.append(all(flags))
    expected_count, rmean, mmean = SET_A_EXPECTED[label]
    counts = {"n_lenses_tested": len(rows), "n_radius_pass": sum(abs(x) <= 2 for x in rs),
              "n_mass_pass": sum(abs(x) <= 2 for x in ms), "n_both_pass": sum(both)}
    _require(set(summary) == set(counts) | {"mean_abs_radius_pull_sigma", "mean_abs_mass_pull_sigma", "failed_lenses"},
             "unexpected Set A summary keys")
    for k, value in counts.items():
        _require(type(summary[k]) is int and summary[k] == value, "Set A count not independently supported: "+k)
    _require(counts["n_both_pass"] == expected_count, "historical frozen pass count mismatch")
    failed = [row["lens_id"] for row, passed in zip(rows, both) if not passed]
    _require(summary["failed_lenses"] == failed, "failed lens list mismatch")
    avg_r = sum(abs(x) for x in rs) / 6
    avg_m = sum(abs(x) for x in ms) / 6
    _close(avg_r, rmean, f"{label} per-lens radius mean")
    _close(avg_m, mmean, f"{label} per-lens mass mean")
    _close(_numeric(summary["mean_abs_radius_pull_sigma"]), avg_r, "summary radius from rows")
    _close(_numeric(summary["mean_abs_mass_pull_sigma"]), avg_m, "summary mass from rows")


def _j2141_checks(root: Path, golden: dict[str, list[dict[str, str]]], receipt: dict) -> None:
    for name in J_ARTIFACTS:
        if name.endswith(".csv"):
            _numeric_reference(root, name, golden)
    summary = read_json(resolve_regular_file(root, "j2141/j2141_run_summary.json"))
    manifest = read_json(resolve_regular_file(root, "j2141/run_manifest.json"))
    _require(summary.get("branch_id") == approved_hist001()["original_branch"], "wrong J2141 branch")
    _require(manifest.get("runner") == "solver.run_j2141_axisym_lens", "unexpected historical runner")
    _require(manifest.get("config") == approved_hist001()["config_path"], "unexpected historical configuration")
    metrics = summary.get("metrics")
    _require(type(metrics) is dict and set(metrics) == set(J_METRICS), "J2141 metric inventory changed")
    _require(receipt["j2141_metrics"] == metrics, "J2141 receipt not derived from source summary")
    for metric, expected in J_METRICS.items():
        _close(_numeric(metrics[metric]), expected, metric, atol=1e-12 if metric == "abs_eta_minus_1" else 1e-9,
               rtol=0)


def validate_outputs(root: Path, mode: str, receipt: dict) -> None:
    golden = _golden_rows()
    _j2141_checks(root, golden, receipt)
    source = approved_hist001()
    for label, prefix in (("center", "setA_center"), ("sphere", "setA_spherical")):
        if label == "sphere" and mode == CENTRAL:
            continue
        rows = _numeric_reference(root, prefix + ".csv", golden)
        obj = read_json(resolve_regular_file(root, prefix + ".json"), max_bytes=100_000)
        _require(obj.get("candidate_name") == source["frozen_candidate"], "Set A candidate not frozen")
        stats = obj.get("results")
        _require(type(stats) is dict, "missing Set A numerical summary")
        _seta_from_rows(rows, stats, label=label)
        _require(receipt["setA_metrics"] == stats if label == "center" else
                 receipt["spherical_metrics"] == stats, "historical receipt != row summary")
    _require(receipt["spherical_metrics"] is None if mode == CENTRAL else
             type(receipt["spherical_metrics"]) is dict, "negative control mode mismatch")


def _validate_archive_status(receipt: dict) -> None:
    x = receipt.get("archived_robustness")
    _require(type(x) is dict and x.get("status") == "ARCHIVED_EXECUTION_NOT_REEXECUTED_THIS_RUN",
             "archived RangeFinder outcomes cannot claim new execution")
    data = x.get("survival")
    _require(type(data) is list and len(data) == 4, "original robustness archive inventory missing")
    seen = {}
    for row in data:
        _require(type(row) is dict and set(row) == {"relative_width", "six_of_six", "survival_fraction"},
                 "invalid archive row")
        key = str(_numeric(row["relative_width"]))
        seen[key] = row
    _require(set(seen) == set(ARCHIVED_COUNTS), "geometry widths mismatch")
    for width, count in ARCHIVED_COUNTS.items():
        _require(type(seen[width]["six_of_six"]) is int and seen[width]["six_of_six"] == count,
                 "archived 1000-trial counts changed")
        _close(_numeric(seen[width]["survival_fraction"]), count/1000, "robustness archived fraction")


def historical_run_id(spec_sha: str, code_sha: str, environment: dict[str, str]) -> str:
    for s in (spec_sha, code_sha):
        require_sha256(s)
    return "hist001-" + digest_bytes(canonical_json({
        "spec_sha256": spec_sha, "code_sha256": code_sha,
        "environment": environment, "runtime_contract": RUNTIME_CONTRACT,
    }))


def verify_hist001_receipt(receipt_path: str | Path, *, source_root: str | Path,
                           expected_sha256: str | None = None) -> dict[str, Any]:
    """Validate complete hashes and independently frozen data; no new physics authorization."""
    try:
        return _verify(Path(receipt_path), Path(source_root), expected_sha256)
    except HistoricalReceiptIntegrityError:
        raise
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        raise HistoricalReceiptIntegrityError("invalid historical receipt or source: " + str(exc)) from exc


def _verify(path: Path, source_root: Path, expected_sha256: str | None) -> dict[str, Any]:
    _require(path.name == "receipt.json" and not path.is_symlink() and not path.parent.is_symlink(),
             "receipt must be a regular finalized file")
    folder = path.parent
    raw = resolve_regular_file(folder, "receipt.json").read_bytes()
    _require(len(raw) <= 150_000, "oversize historical receipt")
    sha = digest_bytes(raw)
    if expected_sha256 is not None:
        _require(require_sha256(expected_sha256) == sha, "independent expected receipt digest mismatch")
    _require(resolve_regular_file(folder, "receipt.sha256").read_bytes() == (sha+"\n").encode("ascii"),
             "historical self-hash does not match receipt bytes")
    receipt = read_json(folder / "receipt.json", max_bytes=150_000)
    required = {"schema", "runtime_contract", "run_id", "backend_id", "theory_id", "finite_model_id",
                "spec_sha256", "source_lock_sha256", "original_archive_sha256", "source_code_sha256",
                "environment", "execution_mode", "steps_sha256", "output_files", "j2141_metrics", "setA_metrics",
                "spherical_metrics", "archived_robustness", "data_use", "claim_intent", "claim_boundary",
                "physical_provider_admitted", "native_v172_equivalence_proved", "empirical_validation", "gate_ledger"}
    _require(type(receipt) is dict and set(receipt) == required and
             receipt["schema"] == RECEIPT_SCHEMA and receipt["runtime_contract"] == RUNTIME_CONTRACT,
             "historical receipt schema changed")
    _require(raw == canonical_json(receipt), "historical receipt is not canonical")
    spec = HistoricalRunSpec.read(resolve_regular_file(folder, "run_spec.json"))
    _require(spec.canonical_bytes == resolve_regular_file(folder, "run_spec.json").read_bytes(),
             "run spec bytes not canonical")
    anchor = approved_hist001()
    for k in ("backend_id", "theory_id", "finite_model_id"):
        _require(receipt[k] == spec.raw[k], "historical receipt/spec identity conflict: "+k)
    _require(receipt["source_lock_sha256"] == SOURCE_LOCK_DIGEST and
             receipt["source_lock_sha256"] == spec.raw["source_lock_sha256"] and
             receipt["original_archive_sha256"] == anchor["original_archive_sha256"] and
             receipt["spec_sha256"] == spec.spec_sha256 and
             receipt["execution_mode"] == spec.raw["execution_mode"] and
             receipt["data_use"] == anchor["data_use"] and
             receipt["claim_intent"] == "REGRESSION_ONLY", "historical identity/role mismatch")
    _require(receipt["claim_boundary"] == CLAIM_CAP and
             receipt["physical_provider_admitted"] is False and
             receipt["native_v172_equivalence_proved"] is False and
             receipt["empirical_validation"] == "NOT_ESTABLISHED", "illegal physical/holdout claim promotion")
    mode = receipt["execution_mode"]
    expected_gates = dict(GATES)
    if mode == CENTRAL:
        expected_gates["spherical_negative"] = "NOT_REQUESTED"
    _require(receipt["gate_ledger"] == expected_gates, "historical gate ledger changed")
    env = receipt["environment"]
    _require(type(env) is dict and set(env) == {"python", "platform", "machine", "numpy", "pandas", "scipy"} and
             all(type(v) is str and v and len(v) <= 160 for v in env.values()), "historical numerical environment invalid")
    code_sha = require_sha256(receipt["source_code_sha256"])
    expected_id = historical_run_id(spec.spec_sha256, code_sha, env)
    _require(receipt["run_id"] == expected_id and folder.name == expected_id,
             "historical source-bound run ID inconsistent")
    expected_inventory = expected_artifacts(mode)
    output_hashes = receipt["output_files"]
    _require(type(output_hashes) is dict and set(output_hashes) == expected_inventory,
             "historical output inventory changed")
    actual_files = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}
    _require(actual_files == expected_inventory | {"receipt.sha256", "receipt.json"},
             "historical receipt directory contains unexpected/missing files")
    for name, expected in output_hashes.items():
        fp = resolve_regular_file(folder, name)
        _require(fp.stat().st_size <= 200_000 and digest_bytes(fp.read_bytes()) == require_sha256(expected),
                 "historical output checksum mismatch: " + name)
    steps = read_json(resolve_regular_file(folder, "execution_steps.json"), max_bytes=100_000)
    _require(resolve_regular_file(folder, "execution_steps.json").read_bytes() == canonical_json(steps) and
             digest_bytes(canonical_json(steps)) == require_sha256(receipt["steps_sha256"]),
             "historical execution step hash or canonical bytes mismatch")
    _require(type(steps) is list and len(steps) == (3 if mode == CENTRAL_SPHERE else 2),
             "historical process inventory changed")
    anchor = approved_hist001()
    expected_commands = [
        ["-m", "solv.run_j2141_axisym_lens", "--config", anchor["config_path"],
         "--pack-root", ".", "--strict-regression"],
        ["-m", "solv.run_setA_port_cand", "--pack-root", ".",
         "--candidate-name", anchor["frozen_candidate"],
         "--out-csv", "<OUTPUT>/setA_center.csv", "--out-json", "<OUTPUT>/setA_center.json"],
        ["<verified_adapter>/hist001_ablation.py", "--pack-root", ".",
         "--out-csv", "<OUTPUT>/setA_spherical.csv", "--out-json", "<OUTPUT>/setA_spherical.json"],
    ]
    for i, step in enumerate(steps):
        _require(type(step) is dict and set(step) == {"label", "command", "exit_code", "stdout_sha256", "stderr_sha256"},
                 "historical process record malformed")
        _require(step["label"] == ("j2141", "setA_center", "setA_spherical")[i] and
                 type(step["exit_code"]) is int and step["exit_code"] == 0 and
                 step["command"] == expected_commands[i],
                 "unexpected/failed historical command")
        require_sha256(step["stdout_sha256"])
        require_sha256(step["stderr_sha256"])
    _validate_archive_status(receipt)
    validate_outputs(folder, mode, receipt)
    source_status = verify_hist001_source(source_root)
    _require(source_status["source_lock_sha256"] == receipt["source_lock_sha256"], "source lock missing")
    return {"status": "VERIFIED_HISTORICAL_REGRESSION_BYTES_AND_NUMERICAL_GATES_ONLY",
            "run_id": expected_id, "receipt_sha256": sha,
            "source_verified": True, "archived_survival_rerun": False,
            "physical_provider_admitted": False, "empirical_validation": "NOT_ESTABLISHED",
            "integrity_anchor": "EXTERNAL_EXPECTED_DIGEST_MATCHED" if expected_sha256 else "SELF_CONTAINED_ONLY",
            "note": "SHA hashes are not signatures or proof of actual computation"}
