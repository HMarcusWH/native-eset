"""D2e-F interval proof component: source-independent synthetic tests."""
from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pytest

from native_eset.numerics.adaptive_shadow_bounds import (
    enclose_adaptive_convex_shadow,
)
from native_eset.numerics.exact_shadow_bounds import ShadowEnclosureError
from native_eset.numerics.shadow_aperture_intervals import (
    _outward_float,
    _q_from_pair,
    certified_shadow_mass_band,
    conditional_aperture_band,
    conditional_normalized_root_residual_band,
    frozen_baryonic_q_corners,
)


def test_q_corner_interval_bounds_every_positive_mass_in_rectangle():
    for qb, qd in ((.7, .2), (.2, .7), (1., 1.), (.001, .7)):
        box = frozen_baryonic_q_corners(3., 9., 2., 17., qb, qd)
        lo, hi = _q_from_pair(box["q_min"]), _q_from_pair(box["q_max"])
        for b in (3., 3.1, 5., 9.):
            for d in (2., 2.1, 4., 17.):
                b, d = Fraction.from_float(b), Fraction.from_float(d)
                actual = (Fraction.from_float(qb)*b + Fraction.from_float(qd)*d)/(b+d)
                assert lo <= actual <= hi
        assert box["valid_given_mass_box"] is True
        assert box["assumption"].startswith("INPUT_BARYON_MASS_INTERVALS")


def test_aperture_band_outward_rounding_contains_corner_bound():
    box = frozen_baryonic_q_corners(3., 9., 2., 17., .8, .3)
    out = conditional_aperture_band(.2, 2.0, box)
    qlow = float(_q_from_pair(box["q_min"]))
    qhigh = float(_q_from_pair(box["q_max"]))
    assert out["aperture_min_kpc"] <= .2/math.sqrt(qhigh)
    assert out["aperture_max_kpc"] >= 2./math.sqrt(qlow)
    assert out["conditioning"] == "UNPROVED_ALL_RADIUS_BARYON_MASS_BOX_ASSUMPTION"
    assert out["aperture_interval_is_sufficient_if_baryonic_box_sound"]


def test_qeff_mass_box_contains_continuous_constructed_monotone_case():
    def B(r):
        return 10.+3.*r
    def D(r):
        return 3.+r
    lo, hi = .1, 1.0
    qb, qd = .7, .25
    box = frozen_baryonic_q_corners(B(lo), B(hi), D(lo), D(hi), qb, qd)
    aperture = conditional_aperture_band(lo, hi, box)
    for i in range(501):
        r = lo+(hi-lo)*i/500
        q = (qb*B(r)+qd*D(r))/(B(r)+D(r))
        A = r/math.sqrt(q)
        # Standard float evaluation agrees within a few ULPs; not the proof.
        assert aperture["aperture_min_kpc"] <= A*(1+1e-14)
        assert A <= aperture["aperture_max_kpc"]*(1+1e-14)


def test_shadow_mass_entire_real_aperture_band_from_endpoint_bounds():
    radii = np.linspace(.02, 3., 65)
    rho = np.array([100.+40.*abs(math.sin(3.*r)) for r in radii])
    result = certified_shadow_mass_band(radii, rho, .35, 1.1)
    lo, hi = Decimal(result["lower_msun"]), Decimal(result["upper_msun"])
    assert 0 <= lo < hi
    assert result["both_endpoint_precision_targets_met"]
    for aperture in (.35, .43, .75, 1.0, 1.1):
        evaluation = enclose_adaptive_convex_shadow(radii, rho, aperture)
        assert lo <= Decimal(evaluation["lower_msun"])
        assert Decimal(evaluation["upper_msun"]) <= hi
    assert result["all_real_apertures_between_binary64_endpoints_enclosed"]


def test_conditional_residual_signs_are_explicitly_nonpromoting():
    narrow = {"lower_msun":"1.0","upper_msun":"1.1"}
    positive = conditional_normalized_root_residual_band(
        1.,1.1,20.,21.,10.,11.,1.,narrow,
    )
    assert positive["conditional_sign"] == "POSITIVE_UNDER_INPUT_ASSUMPTION"
    negative = conditional_normalized_root_residual_band(
        1.,1.1,.01,.011,.01,.011,1.,
        {"lower_msun":".001","upper_msun":".002"},
    )
    assert negative["conditional_sign"] == "NEGATIVE_UNDER_INPUT_ASSUMPTION"
    broad = conditional_normalized_root_residual_band(
        1.,1.1,1.,4.,1.,4.,1.,
        {"lower_msun":"1.0","upper_msun":"2.0"},
    )
    assert broad["conditional_sign"] == "ZERO_NOT_EXCLUDED_UNDER_INPUT_ASSUMPTION"
    for result in (positive, negative, broad):
        assert not result["all_radius_root_uniqueness_certified"]
        assert not result["baryonic_continuous_mass_bounds_verified"]


@pytest.mark.parametrize("params", [
    (0., 3., 2., 4., .8, .4),
    (3., 2., 2., 4., .8, .4),
    (3., 4., -1., 4., .8, .4),
    (3., 4., 2., 4., -.8, .4),
])
def test_malformed_q_box_fail_closed(params):
    with pytest.raises(ShadowEnclosureError):
        frozen_baryonic_q_corners(*params)


def test_invalid_aperture_q_and_radius_boxes_denied():
    box = frozen_baryonic_q_corners(3.,4.,2.,4.,.7,.2)
    for lo,hi in ((0.,1.),(2.,1.),(.3,121.)):
        with pytest.raises(ShadowEnclosureError):
            conditional_aperture_band(lo,hi,box)
    with pytest.raises(ShadowEnclosureError):
        conditional_aperture_band(.2,1.,{"q_min":{"num":"0","den":"1"},
                                                 "q_max":{"num":"1","den":"1"}})
    with pytest.raises(ShadowEnclosureError):
        _outward_float(Fraction(-1),upper=False)


def test_reused_shadow_bound_rejects_invalid_source_and_inverted_interval():
    with pytest.raises(ShadowEnclosureError):
        certified_shadow_mass_band([.1,.2,.3],[1,2,3],.3,.2)
    with pytest.raises(ShadowEnclosureError):
        certified_shadow_mass_band([.1,.2,.3],[1,-2,3],.2,.2)


def test_conditional_residual_rejects_unordered_baryons_or_shadow():
    with pytest.raises(ShadowEnclosureError):
        conditional_normalized_root_residual_band(
            1.,2.,3.,2.,2.,3.,1.,{"lower_msun":"1","upper_msun":"2"},
        )
    with pytest.raises(ShadowEnclosureError):
        conditional_normalized_root_residual_band(
            1.,2.,1.,2.,1.,2.,1.,{"lower_msun":"3","upper_msun":"2"},
        )
