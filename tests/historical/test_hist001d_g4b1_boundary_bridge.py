"""G4b.1 exact-rational boundary lemmas; no real source residual/root test."""
from __future__ import annotations

from fractions import Fraction

import pytest

from native_eset.numerics.hist001d_g4b1_boundary_bridge import (
    G4b1BridgeError,
    PHYSICAL_PROVIDER_ADMITTED,
    ROOT_EXISTENCE_OR_UNIQUENESS_CERTIFIED,
    SCHEMA,
    SOURCE_LOCK_SHA256,
    SOURCE_QFLOOR,
    SOURCE_RMAX,
    SOURCE_RMIN,
    exact_interval,
    exact_number,
    outward_radius_for_legacy_points,
    positive_baryon_q_box,
    proven_positive_hernquist_mass_at_left_source_boundary,
    source_aperture_outward_band,
)


def test_exact_decimal_straddles_binary64_not_collapsed():
    a, b = exact_interval(
        "0.999999999999999999999", "1.000000000000000000001", positive=True,
    )
    assert a < Fraction(1) < b
    assert float(a) == float(b) == 1.0  # unsafe legacy float() path


def test_exact_large_integer_not_binary64():
    assert exact_number(2**53 + 1) == Fraction(2**53 + 1)
    assert exact_number(2**53 + 1) != Fraction.from_float(float(2**53 + 1))


def test_outward_binary64_from_exact_source_cell():
    lo = SOURCE_RMIN + (SOURCE_RMAX-SOURCE_RMIN)/64
    hi = SOURCE_RMIN + 2*(SOURCE_RMAX-SOURCE_RMIN)/64
    a, b = outward_radius_for_legacy_points(lo, hi)
    assert SOURCE_RMIN <= Fraction.from_float(a) <= lo <= hi <= Fraction.from_float(b) <= SOURCE_RMAX
    first = outward_radius_for_legacy_points(SOURCE_RMIN, lo)
    assert Fraction.from_float(first[0]) == SOURCE_RMIN
    last = outward_radius_for_legacy_points(hi, SOURCE_RMAX)
    assert Fraction.from_float(last[1]) == SOURCE_RMAX


def test_left_boundary_finite_hernquist_is_strict_positive():
    value = proven_positive_hernquist_mass_at_left_source_boundary(1.0e10, 1.0)
    r = SOURCE_RMIN
    assert value == Fraction.from_float(1e10)*r*r/(2*(2*r+1)**3)
    assert value > 0
    assert SOURCE_RMIN != Fraction(1, 50)


def test_positive_exact_baryonic_corners_and_aperture():
    lo, hi = positive_baryon_q_box(
        ("2.000000000000000000001", "5.000000000000000000001"),
        ("1.000000000000000000001", "3.000000000000000000001"),
        0.6, 0.8,
    )
    assert SOURCE_QFLOOR <= lo <= hi <= 1
    rl = SOURCE_RMIN + (SOURCE_RMAX-SOURCE_RMIN)/64
    rh = SOURCE_RMIN + 2*(SOURCE_RMAX-SOURCE_RMIN)/64
    amin, amax = source_aperture_outward_band(rl, rh, lo, hi)
    assert 0 <= amin <= amax <= 120
    assert Fraction.from_float(amin) >= rl
    assert Fraction.from_float(amax) >= rh


def test_q_floor_and_saturation_are_exact_source_binary64():
    ql, qh = positive_baryon_q_box((1, 1), (1, 1), 0.0001, 0.0001)
    assert ql == qh == SOURCE_QFLOOR
    a, b = source_aperture_outward_band(
        SOURCE_RMAX, Fraction(120), SOURCE_QFLOOR, SOURCE_QFLOOR,
    )
    assert a == b == 120.0


def test_rejects_malformed_inputs_and_out_of_domain():
    for value in (float("nan"), float("inf"), True, "NaN", "1e2000", 2**4000):
        with pytest.raises(G4b1BridgeError):
            exact_number(value)
    with pytest.raises(G4b1BridgeError):
        outward_radius_for_legacy_points(
            SOURCE_RMIN-Fraction(1, 1000), SOURCE_RMAX,
        )
    with pytest.raises(G4b1BridgeError):
        positive_baryon_q_box((0, 1), (1, 2), 0.5, 0.8)
    with pytest.raises(G4b1BridgeError):
        source_aperture_outward_band(
            SOURCE_RMIN, SOURCE_RMAX, Fraction(0), Fraction(1),
        )


def test_scientific_firewall_and_source_identity():
    assert SCHEMA.endswith("BOUNDARY_BRIDGE_V1")
    assert SOURCE_LOCK_SHA256 == (
        "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    )
    assert PHYSICAL_PROVIDER_ADMITTED is False
    assert ROOT_EXISTENCE_OR_UNIQUENESS_CERTIFIED is False


def test_large_mass_decimal_box_does_not_round_inward_for_q():
    a, b = exact_interval(
        "9999999999999999.999999999999999999999999",
        "10000000000000000.000000000000000000000001", positive=True,
    )
    assert a < Fraction(10**16) < b and float(a) == float(b)
    qlo, qhi = positive_baryon_q_box(
        (a, b), ("0.5", "0.500000000000000000000001"), 0.4, 0.9,
    )
    assert SOURCE_QFLOOR <= qlo <= qhi <= 1
