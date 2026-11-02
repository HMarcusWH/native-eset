"""Source-free synthetic mathematical controls; NOT original March source-data replay."""
from __future__ import annotations

import ast
import importlib.util
from fractions import Fraction as Q
from pathlib import Path

import pytest


REF = Path(__file__).resolve().parents[2] / "reference" / "hist001d_crossing_12node_rational_candidate"


def load_math_module(name):
    spec = importlib.util.spec_from_file_location(name, REF / (name + ".py"))
    if spec is None or spec.loader is None:
        raise RuntimeError("missing mathematical source module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


a = load_math_module("first_node_certificate")
b = load_math_module("independent_first_node")


def secant(hm, hp, fm, f0, fp):
    return (hp * (f0 - fm) / hm + hm * (fp - f0) / hp) / (hm + hp)


def lagrange(hm, hp, fm, f0, fp):
    return -hp / (hm * (hm + hp)) * fm + (hp - hm) / (hm * hp) * f0 + hm / (hp * (hm + hp)) * fp


@pytest.mark.parametrize("hm,hp", [(Q(1, 5), Q(3, 4)), (Q(3, 10), Q(3, 10)), (Q(2, 11), Q(5, 8))])
def test_lagrange_matches_secant(hm, hp):
    for degree in (0, 1, 2, 3, 4):
        f = lambda x: x**degree
        assert secant(hm, hp, f(-hm), f(0), f(hp)) == lagrange(hm, hp, f(-hm), f(0), f(hp))


@pytest.mark.parametrize("hm,hp", [(Q(1, 5), Q(3, 4)), (Q(2, 3), Q(2, 3)), (Q(5, 7), Q(7, 11))])
def test_quadratic_exact(hm, hp):
    f = lambda x: Q(3) + Q(7) * x + Q(2) * x*x
    assert secant(hm, hp, f(-hm), f(0), f(hp)) == Q(7)


@pytest.mark.parametrize("hm,hp", [(Q(1, 6), Q(2, 7)), (Q(4, 9), Q(1, 3))])
def test_cubic_error_exact(hm, hp):
    f = lambda x: x**3
    assert secant(hm, hp, f(-hm), f(0), f(hp)) == hm * hp


def test_positive_i0():
    i0 = a.positive_series(Q(1, 2), N=32)[0]
    assert i0.l > 1 and i0.u < 2


def test_independent_bessel_overlapping_ranges():
    F1, fp1, _ = a.bessel_values(Q(2, 5))
    F2, fp2 = b.bessels(Q(2, 5), b.euler_range())
    assert not (F1.u < F2.l or F2.h < F1.l)
    assert not (fp1.u < fp2.l or fp2.h < fp1.l)


def test_zero_denominator_rejection():
    with pytest.raises(ValueError):
        a.Iv(-1, 1).inv()
    with pytest.raises(ValueError):
        b.B(-1, 1).inverse()


def test_bessel_domain_rejection():
    with pytest.raises(ValueError):
        a.positive_series(Q(7, 4))
    with pytest.raises(ValueError):
        b.bessels(Q(2), b.euler_range())


def test_claim_limits_present_in_review_source():
    source = (REF / "crossing_node_producer.py").read_text()
    assert "original_full_H_root_error_certified" in source
    assert "source_11520_shadow_substituted" in source
    assert "original_general_float_operation_error_certified" in source
    assert isinstance(ast.parse(source), ast.Module)


def test_original_binary64_radius_is_not_decimal():
    assert Q.from_float(0.02) != Q(1, 50)
    assert Q.from_float(0.6902793296089386) != Q(6902793296089386, 10**16)
