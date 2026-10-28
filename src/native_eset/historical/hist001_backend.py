"""HIST-001A/2: package-level historical executor, deliberately not CLI-activated.

Runs the SHA-locked original J2141 and SWELLS Set A scripts in a disposable
copy, then commits a fully verified content-addressed historical receipt. It
is historical fitted regression ONLY, never a native v1.7.2 lensing provider.
"""
from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from native_eset.evidence.receipts import canonical_json, digest_bytes, source_tree_digest, write_immutable
from native_eset.historical.hist001_approved import approved_hist001, SOURCE_LOCK_DIGEST
from native_eset.historical.hist001_source import verify_hist001_source
from native_eset.historical.hist001_spec import CENTRAL_SPHERE, HistoricalRunSpec
from native_eset.historical.hist001_receipt import (
    CLAIM_CAP, GATES, RECEIPT_SCHEMA, RUNTIME_CONTRACT,
    expected_artifacts, historical_run_id, validate_outputs,
    verify_hist001_receipt,
)
from native_eset.serialization import read_json, resolve_regular_file


class HistoricalExecutionError(RuntimeError):
    """Subprocess/numeric failure of the source-exact historical implementation."""


def _environment() -> dict[str, str]:
    import numpy
    import pandas
    import scipy
    return {"python": platform.python_version(), "platform": platform.system(),
            "machine": platform.machine(), "numpy": numpy.__version__,
            "pandas": pandas.__version__, "scipy": scipy.__version__}


def _child_env() -> dict[str, str]:
    # Restrict inherited credentials, arbitrary Python paths and thread pools.
    allow = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP", "TMPDIR", "HOME")
    env = {k: os.environ[k] for k in allow if k in os.environ}
    env.update({"PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
                "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"})
    return env


def _run(args: list[str], *, cwd: Path, label: str, receipt_args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(args, cwd=cwd, env=_child_env(), capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HistoricalExecutionError(f"HIST-001 original subprocess failed: {label}: {type(exc).__name__}") from exc
    if proc.returncode:
        err = proc.stderr[-1000:].decode("utf-8", errors="replace")
        raise HistoricalExecutionError(f"HIST-001 original subprocess failed ({label}, {proc.returncode}): {err}")
    if len(proc.stdout) > 2_000_000 or len(proc.stderr) > 2_000_000:
        raise HistoricalExecutionError("HIST-001 subprocess output exceeded budget")
    return {"label": label, "command": receipt_args, "exit_code": proc.returncode,
            "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(proc.stderr).hexdigest()}


def _source_unchanged(root: Path) -> None:
    """Check original source bytes in writable copy while ignoring generated res/ files."""
    lock = read_json(root / "SOURCE_LOCK.json")
    for rel, sha in lock["source_filenames_sha256"].items():
        target = resolve_regular_file(root / "swells_pack_v2", rel)
        if digest_bytes(target.read_bytes()) != sha:
            raise HistoricalExecutionError("historical original solver/input changed in work copy: " + rel)
    for rel, meta in lock["archived_negative_controls"].items():
        target = resolve_regular_file(root / "archived_rangefinder", rel)
        if digest_bytes(target.read_bytes()) != meta["sha256"]:
            raise HistoricalExecutionError("historical negative evidence changed in work copy: " + rel)


def _archived(root: Path) -> dict[str, Any]:
    obj = read_json(root / "archived_rangefinder" /
                    "reg_v2_fixed_law_geometry_morphology_nuisance_survival_curve_summary.json")
    return {"status": "ARCHIVED_EXECUTION_NOT_REEXECUTED_THIS_RUN",
            "survival": [{"relative_width": x["rel_width"], "six_of_six": x["n_at_6_of_6"],
                          "survival_fraction": x["survival_fraction_6_of_6"]} for x in obj["summaries"]]}


def _safe_output(out: Path, source: Path) -> Path:
    """Reject symlink roots and any attempt to write into the frozen source pack."""
    out = out.absolute()
    root = source.resolve()
    if out.is_symlink() or out.resolve().is_relative_to(root) or root.is_relative_to(out.resolve()):
        raise ValueError("historical output root overlaps frozen source")
    if out.exists() and not out.is_dir():
        raise ValueError("historical output location is not a directory")
    return out


class LegacyHistJ2141Backend:
    """Separate historical numerical interface, not a background/physical provider."""

    def run(self, spec: HistoricalRunSpec, *, source_root: str | Path, output_root: str | Path) -> dict[str, Any]:
        if not isinstance(spec, HistoricalRunSpec):
            raise TypeError("only an immutable validated historical RunSpec can execute")
        checked = HistoricalRunSpec(spec.raw, spec.spec_sha256)
        info = checked.raw
        anchor = approved_hist001()
        if info["backend_id"] != anchor["backend_id"]:
            raise ValueError("wrong historical backend")
        source = Path(source_root).absolute()
        original_state = verify_hist001_source(source)
        out = _safe_output(Path(output_root), source)
        code_sha = source_tree_digest()
        environment = _environment()
        run_id = historical_run_id(checked.spec_sha256, code_sha, environment)
        final = out / run_id
        if final.exists() or final.is_symlink():
            raise FileExistsError("historical run already exists; verify rather than overwrite")
        out.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".hist001-stage-", dir=out) as tmp:
            tmpdir = Path(tmp)
            stage = tmpdir / run_id
            stage.mkdir()
            scratch = tmpdir / "original_copy"
            shutil.copytree(source, scratch)
            verify_hist001_source(scratch)  # SHA-verify *inside the disposable copy* before any original code runs.
            work = scratch / "swells_pack_v2"
            steps = []
            j_args = ["-m", "solv.run_j2141_axisym_lens", "--config", anchor["config_path"],
                      "--pack-root", ".", "--strict-regression"]
            j_cmd = [sys.executable, *j_args]
            steps.append(_run(j_cmd, cwd=work, label="j2141", receipt_args=j_args))
            sa_args = ["-m", "solv.run_setA_port_cand", "--pack-root", ".",
                       "--candidate-name", anchor["frozen_candidate"],
                       "--out-csv", "<OUTPUT>/setA_center.csv", "--out-json", "<OUTPUT>/setA_center.json"]
            sa_cmd = [sys.executable, *sa_args[:7], str(stage / "setA_center.csv"),
                      sa_args[8], str(stage / "setA_center.json")]
            steps.append(_run(sa_cmd, cwd=work, label="setA_center", receipt_args=sa_args))
            if info["execution_mode"] == CENTRAL_SPHERE:
                ablation = Path(__file__).with_name("hist001_ablation.py").resolve()
                sphere_args = ["<verified_adapter>/hist001_ablation.py", "--pack-root", ".",
                               "--out-csv", "<OUTPUT>/setA_spherical.csv",
                               "--out-json", "<OUTPUT>/setA_spherical.json"]
                sphere_cmd = [sys.executable, str(ablation), "--pack-root", str(work),
                              "--out-csv", str(stage / "setA_spherical.csv"),
                              "--out-json", str(stage / "setA_spherical.json")]
                steps.append(_run(sphere_cmd, cwd=work, label="setA_spherical", receipt_args=sphere_args))
            # Capture all genuinely calculated original J2141 output tables.
            original_outputs = work / "res" / "j2141_test1_axisym_structproj_baryonq"
            from native_eset.historical.hist001_receipt import J_ARTIFACTS
            for filename in J_ARTIFACTS:
                source_file = resolve_regular_file(original_outputs, filename.split("/")[-1])
                target = stage / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source_file, target)
            _source_unchanged(scratch)
            verify_hist001_source(source)  # Source in user's original directory was not changed.
            jsummary = read_json(stage / "j2141/j2141_run_summary.json")
            csummary = read_json(stage / "setA_center.json")
            ssummary = read_json(stage / "setA_spherical.json") if info["execution_mode"] == CENTRAL_SPHERE else None
            art = expected_artifacts(info["execution_mode"])
            data_outputs = art - {"execution_steps.json", "run_spec.json"}
            for name in data_outputs:
                if not (stage / name).is_file():
                    raise HistoricalExecutionError("missing generated historical output: " + name)
            spec_bytes = checked.canonical_bytes
            steps_bytes = canonical_json(steps)
            write_immutable(stage / "run_spec.json", spec_bytes)
            write_immutable(stage / "execution_steps.json", steps_bytes)
            files_sha = {name: digest_bytes(resolve_regular_file(stage, name).read_bytes()) for name in sorted(art)}
            gates = dict(GATES)
            if info["execution_mode"] == CENTRAL:
                gates["spherical_negative"] = "NOT_REQUESTED"
            receipt = {
                "schema": RECEIPT_SCHEMA, "runtime_contract": RUNTIME_CONTRACT, "run_id": run_id,
                "backend_id": info["backend_id"], "theory_id": info["theory_id"],
                "finite_model_id": info["finite_model_id"], "spec_sha256": checked.spec_sha256,
                "source_lock_sha256": SOURCE_LOCK_DIGEST,
                "original_archive_sha256": original_state["original_archive_sha256"],
                "source_code_sha256": code_sha,
                "environment": environment, "execution_mode": info["execution_mode"],
                "steps_sha256": digest_bytes(steps_bytes), "output_files": files_sha,
                "j2141_metrics": jsummary["metrics"], "setA_metrics": csummary["results"],
                "spherical_metrics": ssummary["results"] if ssummary is not None else None,
                "archived_robustness": _archived(scratch), "data_use": info["data_use"],
                "claim_intent": info["claim_intent"], "claim_boundary": CLAIM_CAP,
                "physical_provider_admitted": False, "native_v172_equivalence_proved": False,
                "empirical_validation": "NOT_ESTABLISHED", "gate_ledger": gates,
            }
            validate_outputs(stage, info["execution_mode"], receipt)
            rec_bytes = canonical_json(receipt)
            write_immutable(stage / "receipt.sha256", (digest_bytes(rec_bytes) + "\n").encode("ascii"))
            write_immutable(stage / "receipt.json", rec_bytes)  # Complete run marker last.
            checked_result = verify_hist001_receipt(stage / "receipt.json", source_root=source,
                                                   expected_sha256=digest_bytes(rec_bytes))
            if final.exists() or final.is_symlink():
                raise FileExistsError("historical run identity collision; refusing overwrite")
            stage.rename(final)
        return {"status": "HIST001_HISTORICAL_REGRESSION_REPRODUCED_NOT_VALIDATED",
                "run_id": run_id, "output_dir": str(final),
                "receipt_sha256": checked_result["receipt_sha256"],
                "source_lock_sha256": SOURCE_LOCK_DIGEST,
                "archived_robustness_reexecuted": False,
                "physical_provider_admitted": False}
