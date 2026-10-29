"""Fixed predeclared RNG hypotheses must not be seed-fitted or promoted."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "tools/hist001b_seed_probe.py"
SPEC = importlib.util.spec_from_file_location("hist001b_seed_probe", FILE)
assert SPEC is not None and SPEC.loader is not None
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_all_hypotheses_are_explicitly_enumerated() -> None:
    assert len(PROBE.HYPOTHESES) == 7
    assert PROBE.WIDTHS == (0.01, 0.02, 0.05, 0.10)
    for name in PROBE.HYPOTHESES:
        for index, width in enumerate(PROBE.WIDTHS):
            rng = PROBE.proposed_rng(name, index, width)
            values = rng.uniform(0.8, 1.2, size=6)
            assert np.isfinite(values).all()


def test_parallel_and_serial_have_same_trial_zero_by_construction() -> None:
    parallel = PROBE.proposed_rng("parallel_trial_only", 0, 0.01).random(12)
    serial = PROBE.proposed_rng("serial_reset_each_width", 0, 0.01).random(12)
    assert np.array_equal(parallel, serial)


def test_probe_rejects_unregistered_seed_schedules() -> None:
    with pytest.raises(ValueError):
        PROBE.proposed_rng("SEARCH_10M_SEEDS_FOR_MATCH", 0, 0.01)
    with pytest.raises(ValueError):
        PROBE.proposed_rng("parallel_trial_only", 0, 0.05)
    with pytest.raises(ValueError):
        PROBE.proposed_rng("parallel_trial_only", 4, 0.01)
