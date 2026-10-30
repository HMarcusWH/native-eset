"""G3a: exact rational source-output error envelope and scientific firewalls."""
from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction

import pytest

from native_eset.numerics.certified_pointwise_source_error import (
    certified_pointwise_q_error,
    certified_pointwise_source_error,
)
from native_eset.numerics.exact_shadow_bounds import ShadowEnclosureError


@pytest.mark.parametrize("output,lo,hi,expected", [
    (1.5,"1.25","1.75",Fraction(1,4)),
    (2.0,"1.25","1.75",Fraction(3,4)),
    (1.0,"1.25","1.75",Fraction(3,4)),
    (0.0,"0.0","2.0",Fraction(2)),
    (1.5,"1.5","1.5",Fraction(0)),
])
def test_pointwise_absolute_error_upper_is_rationally_certified(output,lo,hi,expected):
    box=certified_pointwise_source_error(output,lo,hi)
    upper=Fraction(Decimal(box["absolute_discrepancy_upper"]))
    assert expected<=upper
    assert upper-expected < Fraction(1,10**65)
    assert box["single_registered_output_vs_exact_binary64_parameter_analytic_model"]
    assert box["all_radius_implementation_error_certified"] is False
    assert box["physical_or_observational_error_bar"] is False


def test_pointwise_exact_fraction_bounds_source_returned_in_interval():
    b=certified_pointwise_source_error(1.5,"1.4","1.6")
    assert b["source_returned_inside_analytic_target_enclosure"]
    assert b["relative_to_source_return_upper"] is not None
    assert b["relative_to_true_lower_upper"] is not None
    n,d=map(int,(
        b["source_returned_exact_dyadic_numerator"],
        b["source_returned_exact_dyadic_denominator"],
    ))
    assert Fraction(n,d)==Fraction.from_float(1.5)


def test_decimal_output_is_not_unsafely_rounded_down():
    value=math.nextafter(1., math.inf)
    result=certified_pointwise_source_error(value,"0.999999999999","1.000000000001")
    v=Fraction.from_float(value)
    exact=max(abs(v-Fraction(Decimal("0.999999999999"))),
              abs(v-Fraction(Decimal("1.000000000001"))))
    assert Fraction(Decimal(result["absolute_discrepancy_upper"])) >= exact
    assert Fraction(Decimal(result["relative_to_true_lower_upper"])) >= exact/Fraction(
        Decimal("0.999999999999")
    )


def test_qeff_corners_pointwise_dyadic_error():
    low,high=Fraction(2,5),Fraction(3,5)
    result=certified_pointwise_q_error(.5,low,high)
    assert Fraction(Decimal(result["absolute_discrepancy_upper"])) >= Fraction(1,10)
    assert result["source_qeff_in_exact_analytic_box"]
    assert result["full_model_root_error_certified"] is False
    assert result["source_numeric_qeff_other_radii_certified"] is False


@pytest.mark.parametrize("output,lo,hi", [
    (float("nan"),"1","2"),(float("inf"),"1","2"),
    (True,"1","2"),(-1.0,"1","2"),
    (1.0,"3","2"),(1.0,"NaN","2"),
    (1.0,"1","Infinity"),(1.0,"-1","1"),
    (1.0,"broken","1"),
])
def test_invalid_source_or_certification_input_fails_closed(output,lo,hi):
    with pytest.raises(ShadowEnclosureError):
        certified_pointwise_source_error(output,lo,hi)


def test_pointwise_q_source_guard_invalid_inputs():
    with pytest.raises(ShadowEnclosureError):
        certified_pointwise_q_error(.5,Fraction(3,5),Fraction(2,5))
    with pytest.raises(ShadowEnclosureError):
        certified_pointwise_q_error(0.,Fraction(1,5),Fraction(3,5))
    with pytest.raises(ShadowEnclosureError):
        certified_pointwise_q_error(.5,Fraction(0),Fraction(3,5))
