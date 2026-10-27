"""Independent mathematical controls (not ESET background or empirical validation)."""
import math
import pytest
from native_eset.controls import FlatGRLambdaCDM
from native_eset.numerics.integrators import refined_simpson


def test_edS_control_closed_form():
    model=FlatGRLambdaCDM(omega_m=1.0,omega_lambda=0.0)
    for z in [0,0.25,1,3,9]:
        assert model.E(z)==pytest.approx((1+z)**1.5,rel=1e-14)
    val=refined_simpson(lambda z:1/model.E(z),0,3,n=128,absolute_tolerance=1e-7)
    assert val.value==pytest.approx(2*(1-1/math.sqrt(4.0)),abs=1e-7)


def test_deSitter_control_closed_form():
    model=FlatGRLambdaCDM(omega_m=0.0,omega_lambda=1.0)
    for z in [0,1,3,15]:
        assert model.E(z)==pytest.approx(1,rel=1e-15)
    x=refined_simpson(lambda z:1/model.E(z),0,3)
    assert x.value==pytest.approx(3,rel=1e-14)
