"""HIST001B independent width-pair math, source and nonpromotion tests."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from native_eset.historical.hist001b_rng_forensics import (
    fisher_95_interval, inspect_width_streams, pearson,
)
from native_eset.historical.hist001b_source import Hist001BSourceError


def test_width_pair_correlation_preserves_order() -> None:
    a = [float(x) for x in range(100)]
    assert pearson(a, a) == pytest.approx(1.0, abs=1e-12)
    assert pearson(a, list(reversed(a))) == pytest.approx(-1.0, abs=1e-12)
    shuffled = [a[(i * 37) % 100] for i in range(100)]
    assert abs(pearson(a, shuffled)) < 0.1


def test_width_pair_invalid_values_fail_closed() -> None:
    with pytest.raises(ValueError):
        pearson([1, 2, 3, 4], [1, 2, 3])
    with pytest.raises(ValueError):
        pearson([1, 2, math.nan, 4], [1, 2, 3, 4])
    with pytest.raises(ValueError):
        pearson([1, 1, 1, 1], [1, 2, 3, 4])


def test_fisher_interval_not_scientific_admission() -> None:
    a, b = fisher_95_interval(0.1, n=1000)
    assert a < 0.1 < b
    assert fisher_95_interval(1.0) == [1.0, 1.0]
    with pytest.raises(ValueError):
        fisher_95_interval(1.1)
    with pytest.raises(ValueError):
        fisher_95_interval(0.5, n=3)


def test_forensics_requires_separately_pinned_archive(tmp_path: Path) -> None:
    with pytest.raises(Hist001BSourceError):
        inspect_width_streams(oracle_root=tmp_path)
