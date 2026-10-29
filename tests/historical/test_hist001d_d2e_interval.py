"""D2e-B: conditional interval exclusions; no mathematical uniqueness or physics claims."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/hist001d_d2e_interval.py"
SPEC = importlib.util.spec_from_file_location("hist001d_d2e_b_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)
SOURCE = ROOT / "research/legacy/hist001"


def test_frozen_source_and_nonpromotion_contract():
    assert D.SOURCE_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert D.ROOT_GUARD_FRACTION == .02
    assert D.ASSUMED_RELATIVE_MASS_ENVELOPE == 1e-6
    assert D.FINITE_DOMAIN == (.02, 120.)
    assert D.MAX_BISECTION_DEPTH == 18
    assert D.CLAIMS["conditional_interval_root_exclusion"] is True
    for field in ("uniform_quadrature_error_budget_proved",
                  "root_uniqueness_mathematically_certified",
                  "global_error_bound_established", "mass_outside_finite_domain_bounded",
                  "physical_provider_admitted", "physical_weyl_lensing_derived",
                  "new_holdout_scored", "native_v172_equivalence_proved"):
        assert D.CLAIMS[field] is False
    assert D.CLAIMS["empirical_validation"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("qb,qd", [(0.7, 0.2), (0.2, 0.7), (1., 1.)])
def test_four_corner_q_bounds_include_every_intermediate_positive_mass(qb, qd):
    lo, hi = D.q_corner_bounds(3., 9., 2., 17., qb, qd)
    assert .001 <= lo <= hi <= 1.
    for b in (3., 3.1, 5., 9.):
        for d in (2., 2.1, 4., 17.):
            q = (qb*b + qd*d)/(b+d)
            assert lo-1e-15 <= q <= hi+1e-15


def test_interval_mass_bound_includes_all_synthetic_interior_evaluations():
    # Explicitly nonnegative, increasing projected masses and shadow profile.
    qb, qd, sig, lo, hi = .8, .3, 2., .2, 2.
    b = lambda R: R+3
    d = lambda R: 2*R+1
    sh = lambda R: 3*R/(1+R)
    qmin, qmax = D.q_corner_bounds(b(lo), b(hi), d(lo), d(hi), qb, qd)
    slo = sh(min(120., lo/math.sqrt(qmax)))
    shi = sh(min(120., hi/math.sqrt(qmin)))
    lower, upper = D.normalized_interval_enclosure(
        lo, hi, b(lo), b(hi), d(lo), d(hi), slo, shi, sig, 0.,
    )
    for i in range(101):
        R = lo+(hi-lo)*i/100
        q = (qb*b(R)+qd*d(R))/(b(R)+d(R))
        f = (b(R)+d(R)+sh(R/math.sqrt(q)))/(math.pi*sig*R**2)-1
        assert lower-1e-12 <= f <= upper+1e-12


def test_explicit_assumed_mass_envelope_widens_bounds():
    args = (.2, 2., 3., 5., 2., 4., 1., 2., 2.)
    x1, x2 = D.normalized_interval_enclosure(*args, 0.)
    y1, y2 = D.normalized_interval_enclosure(*args, .01)
    assert y1 < x1 <= x2 < y2


def polynomial_interval(a, b, x0, x1):
    p = (a-x0, b-x0)
    q = (a-x1, b-x1)
    products = [p0*q0 for p0 in p for q0 in q]
    return min(products), max(products)


def test_same_sign_endpoints_do_not_hide_two_interior_roots():
    # Both endpoints positive. An endpoint-only sign scanner would miss roots.
    result = D.exclude_intervals(
        lambda lo, hi: polynomial_interval(lo, hi, .30, .31),
        [(.1, 1.)], max_depth=8,
    )
    assert result["visited"] > 1
    assert result["all_tested_outside_guard_excluded_under_assumed_budget"] is False
    assert result["unresolved_intervals"]
    assert any(x["lo"] <= .3 <= x["hi"] or x["lo"] <= .31 <= x["hi"]
               for x in result["unresolved_intervals"])


def test_tangent_root_not_promoted_to_root_free():
    # (x-.5)^2 touches zero without a sign change.
    result = D.exclude_intervals(
        lambda lo, hi: polynomial_interval(lo, hi, .5, .5),
        [(.2, .9)], max_depth=9,
    )
    assert result["unresolved_intervals"]
    assert result["all_tested_outside_guard_excluded_under_assumed_budget"] is False


def test_strictly_positive_interval_is_excluded():
    result = D.exclude_intervals(lambda lo, hi: (lo+1, hi+1), [(.2, 1.)])
    assert result["excluded_count"] == 1
    assert result["excluded_signs"] == {"POSITIVE": 1, "NEGATIVE": 0}
    assert result["all_tested_outside_guard_excluded_under_assumed_budget"] is True


def test_insufficient_work_budget_must_be_reported():
    result = D.exclude_intervals(
        lambda lo, hi: (-1., 1.), [(.2, 1.)],
        max_depth=20, max_visits=1,
    )
    assert result["all_tested_outside_guard_excluded_under_assumed_budget"] is False
    assert any(x["reason"] == "VISIT_BUDGET" for x in result["unresolved_intervals"])


@pytest.mark.parametrize("params", [
    (2., 1., 1., 2., .5, .6),
    (0., 1., 1., 2., .5, .6),
    (1., 2., 1., 2., -.5, .6),
])
def test_bad_q_enclosures_fail_closed(params):
    with pytest.raises(D.IntervalDiagnosticError):
        D.q_corner_bounds(*params)


@pytest.mark.parametrize("parameters", [
    (.2, 2., 3., 5., 2., 4., 3., 2., 2., .01),
    (.2, 2., 3., 5., 2., 4., 1., 2., 0., .01),
    (.2, 2., 3., 5., 2., 4., 1., 2., 2., 1.1),
])
def test_bad_mass_enclosures_fail_closed(parameters):
    with pytest.raises(D.IntervalDiagnosticError):
        D.normalized_interval_enclosure(*parameters)


def test_source_and_dependent_numerical_file_hashes():
    from native_eset.historical.hist001_source import verify_hist001_source
    state = verify_hist001_source(SOURCE)
    assert state["source_lock_sha256"] == D.SOURCE_SHA256
    assert state["frozen_files"] == 46
    assert state["archived_negative_records"] == 3
    a = D.load_pinned_a()
    assert a.SOURCE_SHA256 == D.SOURCE_SHA256
    assert a.CLAIMS["root_uniqueness_mathematically_certified"] is False
