from math import sqrt
import pytest
from native_eset.controls import FlatGRLambdaCDM


def test_gr_control_today():
    assert FlatGRLambdaCDM().E(0) == pytest.approx(1.0)


def test_gr_control_matter_only():
    m = FlatGRLambdaCDM(omega_m=1.0, omega_lambda=0.0)
    assert m.E(3.0) == pytest.approx(sqrt(64.0))


def test_gr_control_radiation_only():
    m = FlatGRLambdaCDM(omega_r=1.0, omega_m=0, omega_lambda=0)
    assert m.E(3) == pytest.approx(16.0)


def test_invalid_control_rejected():
    with pytest.raises(ValueError):
        FlatGRLambdaCDM(omega_m=.31, omega_lambda=.7)
    with pytest.raises(ValueError):
        FlatGRLambdaCDM().E(-1.0)
