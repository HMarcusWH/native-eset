#!/usr/bin/env python3
"""HIST-001B source-isolated runner and immutable diagnostic/failure receipt.

Full source-exact admission is impossible without the original accelerated
producer and its 600-case precheck specification. A complete 4,000-trial
diagnostic still executes, records all rows and exits 4 (fail closed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from native_eset.evidence.receipts import canonical_json
from native_eset.historical.hist001b_compare import inspect_output
from native_eset.historical.hist001b_receipt import (
    RECEIPT_SCHEMA, CLAIMS, expected_files, _derived_status,
    verify_hist001b_receipt,
)
from native_eset.historical.hist001b_source import (
    HIST001A_SOURCE_LOCK_SHA256, HISTORICAL_PRODUCER_STATUS,
    PRECHECK_STATUS, require_no_symlink_components, verify_b_oracle,
)
from native_eset.historical.hist001b_spec import (
    HistoricalRobustnessRunSpec,
)
from native_eset.historical.hist001_source import verify_hist001_source


class Hist001BWorkerError(RuntimeError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _environment() -> dict:
    import numpy
    import pandas
    import scipy
    return {
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "pandas": pandas.__version__,
        "scipy": scipy.__version__,
        "os": platform.system(),
        "machine": platform.machine(),
        "numerical_policy": "NUMPY_SEEDSEQUENCE_TRIAL_V1_NOT_ARCHIVED_PROVED",
        "openblas_threads": "1", "omp_threads": "1", "mkl_threads": "1",
        "locale": "UTF-8",
        "r_grid": "linspace(0.02,120.0,180)",
        "theta_grid": "linspace(0,2pi,120,endpoint=False)",
    }


def _child_env() -> dict[str, str]:
    # Do not propagate credentials, PYTHONPATH, user-site imports or unbounded BLAS.
    allow = ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "TEMP", "TMP",
             "TMPDIR", "HOME")
    e = {k: os.environ[k] for k in allow if k in os.environ}
    e.update({
        "PYTHONHASHSEED": "0",
        "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1", "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
    })
    return e


def _safe_out(out: str | Path, source: Path, oracle: Path | None) -> Path:
    p = require_no_symlink_components(out)
    rp = p.resolve(strict=False)
    src = source.resolve(strict=True)
    if rp == src or rp.is_relative_to(src) or src.is_relative_to(rp):
        raise ValueError("B output cannot overlap frozen source")
    if oracle is not None:
        q = oracle.resolve(strict=True)
        if rp == q or rp.is_relative_to(q) or q.is_relative_to(rp):
            raise ValueError("B output cannot overlap archived oracle")
    if p.exists() and not p.is_dir():
        raise ValueError("B output must be a directory")
    return p


def run(*, source_root: str | Path, output_root: str | Path,
        oracle_root: str | Path | None = None, smoke: bool = False,
        trials: int = 1000) -> dict:
    # All non-executable source integrity checks precede any recovered import.
    spec = HistoricalRobustnessRunSpec.build(smoke=smoke, trials=trials)
    source = require_no_symlink_components(source_root)
    verified_source = verify_hist001_source(source)
    if (verified_source["source_lock_sha256"] != HIST001A_SOURCE_LOCK_SHA256 or
            verified_source["frozen_files"] != 46 or
            verified_source["archived_negative_records"] != 3):
        raise ValueError("HIST001B frozen source wrong identity")
    oracle = None
    if oracle_root is not None:
        oracle = require_no_symlink_components(oracle_root)
        verify_b_oracle(oracle)
    out = _safe_out(output_root, source, oracle)
    env = _environment()
    implementation = _sha(Path(__file__).read_bytes())
    run_id = "hist001b-" + _sha(canonical_json({
        "spec_sha256": spec.sha256,
        "original_source_sha256": HIST001A_SOURCE_LOCK_SHA256,
        "implementation_sha256": implementation,
        "environment": env, "oracle_verified": oracle is not None,
    }))[:24]
    final = out / run_id
    if final.exists() or final.is_symlink():
        raise FileExistsError("immutable B run exists; verify instead of overwrite")
    out.mkdir(parents=True, exist_ok=True)
    # All execution is confined to a verified disposable copy. The original 46
    # files and archived evidence are never opened with write permission.
    with tempfile.TemporaryDirectory(prefix=".hist001b-stage-", dir=out) as temp:
        scratch = Path(temp)
        copied_source = scratch / "source"
        shutil.copytree(source, copied_source)
        verify_hist001_source(copied_source)
        stage = scratch / "result"  # must NOT exist before worker's --out check.
        worker = Path(__file__).with_name("hist001b_rangefinder.py").absolute()
        args = [
            sys.executable, "-I", str(worker),
            "--source-root", str(copied_source),
            "--out", str(stage),
        ]
        if smoke:
            args += ["--smoke", "--trials", str(trials)]
        try:
            process = subprocess.run(
                args, cwd=scratch, env=_child_env(), capture_output=True,
                timeout=180 if smoke else 1500, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Hist001BWorkerError("bounded B worker failed before receipt") from exc
        if process.returncode not in (0, 4):
            raise Hist001BWorkerError(
                "B worker exit " + str(process.returncode) + ": " +
                process.stderr[-500:].decode("utf-8", "replace") + " " +
                process.stdout[-500:].decode("utf-8", "replace")
            )
        if len(process.stdout) > 1_000_000 or len(process.stderr) > 1_000_000:
            raise Hist001BWorkerError("B worker output exceeds budget")
        verify_hist001_source(copied_source)
        verify_hist001_source(source)
        independent = inspect_output(
            stage, n_trials=trials, smoke=smoke, oracle_root=oracle,
        )
        status = _derived_status(spec, independent)
        if smoke and process.returncode != 0:
            raise Hist001BWorkerError("B smoke worker did not complete")
        if not smoke and process.returncode != 4:
            raise Hist001BWorkerError("B full worker falsely reported source-exact success")
        stage.joinpath("independent_inspection.json").write_bytes(canonical_json(independent))
        stage.joinpath("run_spec.json").write_bytes(spec.canonical_bytes)
        execution = {
            "command": [
                "python", "-I", "tools/hist001b_rangefinder.py",
                "--source-root", "<verified_disposable_source>",
                "--out", "<private_stage>",
            ] + (["--smoke", "--trials", str(trials)] if smoke else []),
            "exit_code": process.returncode,
            "stdout_sha256": _sha(process.stdout),
            "stderr_sha256": _sha(process.stderr),
            "worker_implementation_sha256": _sha(worker.read_bytes()),
            "driver_implementation_sha256": implementation,
            "worker_timeout_seconds": 180 if smoke else 1500,
            "source_immutable_after_execution": True,
        }
        stage.joinpath("execution.json").write_bytes(canonical_json(execution))
        file_digests = {
            name: _sha(stage.joinpath(name).read_bytes())
            for name in sorted(expected_files(spec))
        }
        receipt = {
            "schema": RECEIPT_SCHEMA,
            "status": status,
            "run_id": run_id,
            "run_spec_sha256": spec.sha256,
            "source_lock_sha256": HIST001A_SOURCE_LOCK_SHA256,
            "oracle_verified": oracle is not None,
            "original_producer_status": HISTORICAL_PRODUCER_STATUS,
            "original_precheck_status": PRECHECK_STATUS,
            "output_files": file_digests,
            "environment": env,
            "execution": execution,
            "claim_boundary": dict(CLAIMS),
        }
        receipt_bytes = canonical_json(receipt)
        stage.joinpath("receipt.sha256").write_text(_sha(receipt_bytes) + "\n", encoding="ascii")
        stage.joinpath("receipt.json").write_bytes(receipt_bytes)  # Complete marker LAST.
        if final.exists():
            raise FileExistsError("B duplicate run, refusing overwrite")
        stage.rename(final)
    verified = verify_hist001b_receipt(
        final / "receipt.json", source_root=source,
        oracle_root=oracle, expected_sha256=_sha(receipt_bytes),
    )
    return {
        "status": status,
        "output_dir": str(final),
        "run_id": run_id,
        "receipt_sha256": verified["receipt_sha256"],
        "full_archive_rows_match": independent["complete_archival_row_match"],
        **dict(CLAIMS),
        "verification_status": verified["status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--oracle-root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--trials", type=int, default=1000)
    args = parser.parse_args()
    try:
        result = run(
            source_root=args.source_root, output_root=args.out,
            oracle_root=args.oracle_root, smoke=args.smoke, trials=args.trials,
        )
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "HIST001B_FAIL_CLOSED",
                          "error": str(exc)}, sort_keys=True))
        return 2
    except Hist001BWorkerError as exc:
        print(json.dumps({"status": "HIST001B_NUMERICAL_WORKER_FAIL_CLOSED",
                          "error": str(exc)}, sort_keys=True))
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0 if args.smoke else 4


if __name__ == "__main__":
    raise SystemExit(main())
