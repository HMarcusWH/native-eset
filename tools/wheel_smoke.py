#!/usr/bin/env python3
"""Run installed wheel from an unrelated working directory, with no PYTHONPATH."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
env = dict(os.environ)
env.pop("PYTHONPATH", None)
with tempfile.TemporaryDirectory(prefix="eset-wheel-smoke-") as d:
    for name in ("E_of_z", "chi_dimensionless_of_z"):
        command = [sys.executable, "-I", "-m", "native_eset", "run", "--spec",
                   str(root / "tests/fixtures" / f"{name}.json"), "--out", str(Path(d)/"runs")]
        completed = subprocess.run(command, cwd=d, env=env, capture_output=True, text=True,
                                   encoding="utf-8", check=True)
        run = json.loads(completed.stdout)
        verified = subprocess.run([sys.executable, "-I", "-m", "native_eset", "verify", "--receipt",
                                   str(Path(run["output_dir"])/"receipt.json"), "--expected-sha256",
                                   run["receipt_sha256"]], cwd=d, env=env, capture_output=True,
                                   text=True, encoding="utf-8", check=True)
        print(json.dumps({"fixture":name,"run":run,"verification":json.loads(verified.stdout)},sort_keys=True))
