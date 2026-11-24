#!/usr/bin/env python3
"""Source-free, nonpromoting entrypoint for the immutable G4b.1c math module.

Not a substitute for protected source-bound replay. Direct imports of the
historical candidate bypass this guard and are unsupported execution paths.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "historical"
    / "g4b1c_global_math_candidate"
    / "g4b1c_global_math_lib.py"
)
EXPECTED_SOURCE_SHA256 = "7985255688073ebf63e4f723c424a05995c04e5edf3c7b095f8978b40f953b2d"
OPTIMIZED_EXECUTION_REJECTED = "HIST001D_G4B1C_GLOBAL_OPTIMIZED_EXECUTION_REJECTED"
SOURCE_HASH_MISMATCH = "HIST001D_G4B1C_GLOBAL_SOURCE_SHA256_MISMATCH"


def load_candidate(path: Path | None = None):
    """Import only verified source bytes under non-optimized Python."""
    # Must precede even the file read; no use of assert for this protection.
    if sys.flags.optimize != 0 or not __debug__:
        raise RuntimeError(OPTIMIZED_EXECUTION_REJECTED)
    candidate = SOURCE if path is None else Path(path)
    raw = candidate.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise ValueError(SOURCE_HASH_MISMATCH)
    name = "g4b1c_global_candidate_pure_math"
    spec = importlib.util.spec_from_file_location(name, candidate)
    if spec is None or spec.loader is None:
        raise RuntimeError("G4b.1c source module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    # Compile precisely the bytes authenticated above. No second disk read.
    code = compile(raw, str(candidate), "exec")
    sys.modules[name] = module
    try:
        exec(code, module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def main() -> int:
    try:
        load_candidate()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print("HIST001D_G4B1C_GLOBAL_SOURCE_GUARD_PASS", EXPECTED_SOURCE_SHA256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
