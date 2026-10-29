#!/usr/bin/env python3
"""Prove historical execution and receipt checking use an installed wheel outside Git."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "legacy" / "hist001"


def isolated(cwd: Path, *args: str, expected_success: bool = True) -> dict:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    cmd = [sys.executable, "-I", "-m", "native_eset", *args]
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8", timeout=240)
    if expected_success and proc.returncode != 0:
        raise RuntimeError("isolated installed-wheel command failed: "
                           + " ".join(args) + "\n" + proc.stderr[-1000:] + proc.stdout[-2000:])
    if not expected_success and proc.returncode == 0:
        raise RuntimeError("an invalid historical request was unexpectedly accepted")
    if not proc.stdout.strip():
        if expected_success:
            raise RuntimeError("installed-wheel command emitted no JSON")
        return {"status": "REJECTED_BY_ARGUMENT_PARSER"}
    result = json.loads(proc.stdout)
    if not expected_success and result.get("status") != "FAIL_CLOSED":
        raise RuntimeError("invalid historical request did not fail closed")
    return result


def main() -> int:
    if not SOURCE.is_dir() or not (SOURCE / "SOURCE_LOCK.json").is_file():
        raise RuntimeError("external frozen HIST-001 source pack unavailable")
    with tempfile.TemporaryDirectory(prefix="hist001-installed-wheel-smoke-") as td:
        root = Path(td)
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        proc = subprocess.run([sys.executable, "-I", "-c",
                               "import native_eset; print(native_eset.__file__)"],
                              cwd=root, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=30, check=True)
        package = Path(proc.stdout.strip()).resolve()
        if package.is_relative_to(ROOT.resolve()) or "site-packages" not in package.parts:
            raise RuntimeError("historical CLI smoke did not import the installed wheel")
        args = ("historical", "j2141", "--source-root", str(SOURCE),
                "--out", str(root / "runs"), "--strict", "--ablation", "spherical")
        run = isolated(root, *args)
        if (run.get("status") != "HIST001_HISTORICAL_REGRESSION_REPRODUCED_NOT_VALIDATED" or
                run.get("physical_provider_admitted") is not False or
                run.get("archived_robustness_reexecuted") is not False):
            raise RuntimeError("historical installed-wheel scope was broadened")
        receipt = Path(run["output_dir"]) / "receipt.json"
        verified = isolated(root, "verify", "--receipt", str(receipt),
                            "--source-root", str(SOURCE), "--expected-sha256",
                            run["receipt_sha256"])
        if (verified.get("integrity_anchor") != "EXTERNAL_EXPECTED_DIGEST_MATCHED" or
                verified.get("physical_provider_admitted") is not False):
            raise RuntimeError("historical wheel receipt verification insufficient")
        isolated(root, "verify", "--receipt", str(receipt), expected_success=False)
        isolated(root, "verify", "--receipt", str(receipt), "--source-root",
                 str(SOURCE), "--expected-sha256", "0" * 64, expected_success=False)
        isolated(root, "historical", "j2141", "--source-root", str(SOURCE),
                 "--out", str(root / "runs_missing_strict"), expected_success=False)
        doctor = isolated(root, "doctor", "--historical-source-root", str(SOURCE))
        if (doctor.get("hist001_executable_registered") is not True or
                doctor.get("hist001_external_source", {}).get("frozen_files") != 46):
            raise RuntimeError("installed source verification status is wrong")
        print(json.dumps({"status": "HIST001_INSTALLED_WHEEL_STRICT_REPLAY_AND_RECEIPT_PASS",
                          "historical_run_id": run["run_id"],
                          "receipt_sha256": run["receipt_sha256"],
                          "package_path": str(package),
                          "physical_provider_admitted": False,
                          "empirical_validation": "NOT_ESTABLISHED"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
