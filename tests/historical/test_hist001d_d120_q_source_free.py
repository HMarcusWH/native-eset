"""Source-free exact arithmetic controls, NOT six original lens source replay or physical validation."""
from __future__ import annotations

import math
import runpy
import struct
from fractions import Fraction
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / 'reference/hist001d_d120_q_candidate'
PROD_DISK = runpy.run_path(str(SOURCE / 'disk120_math.py'))
PROD_Q = runpy.run_path(str(SOURCE / 'q_producer.py'))
INDEPENDENT = runpy.run_path(str(SOURCE / 'independent_verify.py'))
F = Fraction


def test_source_free_exponential_zero():
    assert PROD_DISK['exp_negative_interval'](F(0)) == (1, 1)
    assert INDEPENDENT['exp_alt_bounds'](F(0)) == (1, 1)


@pytest.mark.parametrize('x', [F(1, 200), F(1, 2), F(1), F(3), F(70)])
def test_two_independent_exponential_enclosures_intersect(x):
    a, b = PROD_DISK['exp_negative_interval'](x)
    c, d = INDEPENDENT['exp_alt_bounds'](x)
    assert 0 <= a <= b <= 1
    assert 0 <= c <= d <= 1
    assert max(a, c) <= min(b, d)


def test_nonzero_exp_rational_guard():
    a, b = PROD_DISK['exp_negative_interval'](F(1, 2))
    assert F(3, 5) < a < b < F(5, 8)


@pytest.mark.parametrize('q', [F(1, 4), F(2), F(7, 9), F(19, 101), F(1, 10**18)])
def test_two_independent_sqrt_enclosures(q):
    lo, hi = PROD_Q['sqrtbounds'](q)
    il, ih = INDEPENDENT['root_bracket'](q)
    assert lo * lo <= q <= hi * hi
    assert il * il <= q <= ih * ih
    assert max(lo, il) <= min(hi, ih)


def test_ieee754_exact_decode_and_nonfinite_rejection():
    decode = INDEPENDENT['decode']
    raw = struct.pack('>ddd', 0.5, -2.25, math.ldexp(1.0, -1074))
    assert list(decode(raw)) == [F(1, 2), F(-9, 4), F(1, 2**1074)]
    with pytest.raises(ValueError):
        list(decode(struct.pack('>d', float('inf'))))


def test_piecewise_linear_shadow_monotone():
    rs = list(map(F, (1, 2, 3)))
    masses = list(map(F, (0, 5, 9)))
    assert PROD_Q['pl'](F(1, 2), rs, masses) == 0
    assert PROD_Q['pl'](F(3, 2), rs, masses) == F(5, 2)
    assert PROD_Q['pl'](F(5, 2), rs, masses) == 7
    assert PROD_Q['pl'](F(4), rs, masses) == 9


def test_disk_exact_angular_quadrature_nonnegative():
    angular = [(F(1, 2), F(1)), (F(1, 2), F(1))]
    lo, hi = PROD_DISK['ideal_disk_at_r'](F(1), F(2), F(3), angular)
    assert lo > 0
    assert lo <= hi
    # 1-(1+x)e^-x <= x²/2 for x>=0; source-frozen coefficient sum.
    assert hi <= F(2) * F(1) ** 2 / 2


def test_quadratic_Bernstein_aperture_derivative_algebra():
    # Source-free synthetic positive B,D: q=N(t)/P(t), exact t=0,1/2,1.
    qb, qd = F(3, 4), F(1, 4)
    b0, b1, d0, d1 = F(4), F(5), F(2), F(6)
    n0 = qb * b0 + qd * d0
    n1 = qb * b1 + qd * d1
    p0, p1 = b0 + d0, b1 + d1
    C = n1 * p0 - n0 * p1
    dn, dp = n1 - n0, p1 - p0
    r0, h = F(1), F(2)
    g0 = 2 * n0 * p0 - r0 * C / h
    g1 = 2 * (n0 * dp + dn * p0) - C
    g2 = 2 * dn * dp
    coeff = (g0, g0 + g1 / 2, g0 + g1 + g2)
    for t in [F(0), F(1, 2), F(1)]:
        n, p = n0 + dn * t, p0 + dp * t
        r = r0 + h * t
        lhs = 2 * n * p - r * C / h
        rhs = coeff[0] * (1 - t) ** 2 + 2 * coeff[1] * t * (1 - t) + coeff[2] * t**2
        assert lhs == rhs
