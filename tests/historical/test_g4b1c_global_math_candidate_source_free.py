"""Source-free numerical sanity and fail-closed scope tests for a reviewed MATH CANDIDATE.

No original March source data, six lens nodes, or external archive is imported.
These are guards and independent controls, not substitutes for six source-bound
rigorous certificate replays or a peer review.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "research" / "historical" / "g4b1c_global_math_candidate"
ARCHIVED = {
    "g4b1c_global_math_lib.py": "7985255688073ebf63e4f723c424a05995c04e5edf3c7b095f8978b40f953b2d",
    "g4b1c_global_rootcount_producer.py": "0520b0ddec25db68ccc29e15806d8cffe869673602145d7f43b59ee489573d6d",
    "g4b1c_global_independent_verifier.py": "8807b61ad743035a17aa74d775c95c6b55cc8c7bf2077e40b9aedd80c9bee9b5",
    "source_input_adapter.py": "38813d07b6ade04a08d5dcdb864cf1cd63a285efc535df707b1e9fcaaf089584",
    "g4b1c_global_adversarial_qa.py": "31feb52b2b2ba6251d8edb2cb3c3ee268097ca58122de24e5d931127c2089cc2",
    "reproduce_g4b1c_global_finite_proxy_v1.py": "914b5cced57c030c176c7548ae6b505e68688907b4c5f5aa3780c36cbe033c91",
    "README_GLOBAL_FINITE_PROXY_ROOT_COUNT_CANDIDATE.md": "e4cbfd323d1aea484bbddb20c0d717073ce3e0cd9dcb5c067555a220bf042b9b",
}


def m():
    # Import only the pure arithmetic module. In particular, never execute
    # the producer or source_input_adapter.py during repository-only CI.
    name = "g4b1c_global_candidate_pure_math"
    spec = importlib.util.spec_from_file_location(name, PROOF / "g4b1c_global_math_lib.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_exact_archived_source_byte_hashes():
    assert set(ARCHIVED) == {p.name for p in PROOF.iterdir() if p.is_file()}
    assert {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in PROOF.iterdir() if p.is_file()
    } == ARCHIVED


def test_pi_rational_series_strict_enclosure():
    z = m()
    assert F(314159, 100000) < z.PI_LOW < z.PI_HIGH < F(314160, 100000)
    # Independent 65-digit decimal sanity check; the rigorous source proof is the
    # alternating arctan remainder, not this decimal constant.
    with localcontext() as ctx:
        ctx.prec = 75
        pi_check = F(str(Decimal("3.141592653589793238462643383279502884197169399375105820974944592307816")))
        assert z.PI_LOW < pi_check < z.PI_HIGH


def test_directed_sqrt_on_nonperfect_and_perfect_squares():
    z = m()
    e = z.Enclosure(bits=24)
    for x in [F(0), F(1, 16), F(2), F(7, 19), F(121, 100), F(999, 7)]:
        lo, hi = e.sqrt_lo(x), e.sqrt_hi(x)
        assert lo * lo <= x <= hi * hi
        assert hi - lo <= F(1, 2**24)
        assert lo >= 0
    # Exactness occurs only if the square-root fits the dyadic output grid.
    assert e.sqrt_lo(F(25, 16)) == e.sqrt_hi(F(25, 16)) == F(5, 4)
    with pytest.raises(ValueError):
        e.sqrt_lo(F(-1))


@pytest.mark.parametrize("x", [F(0), F(1, 1000), F(1, 10), F(1), F(5), F(20), F(50)])
def test_exponential_rational_enclosure_sanity(x):
    z = m()
    lo, hi = z.Enclosure(bits=40).exp_neg(x)
    with localcontext() as ctx:
        ctx.prec = 80
        reference = F(str((-Decimal(x.numerator) / Decimal(x.denominator)).exp()))
    assert lo <= reference <= hi
    assert 0 <= lo <= hi <= 1


def test_full_azimuth_disk_spherical_special_case():
    # For q=1, the continuum elliptical exponential disk becomes the analytic
    # circular disk M * [1-(1+R/s)exp(-R/s)]. Decimal reference is NONPROOF.
    z = m()
    e = z.Enclosure(bits=45)
    M = F(10**11)
    for R, s in [(F(1), F(3, 2)), (F(5), F(2)), (F(9, 2), F(4))]:
        lo, hi = e.disk_value(R, M, s, F(1), n=90)
        with localcontext() as ctx:
            ctx.prec = 70
            x = Decimal(R.numerator) / Decimal(R.denominator) / (
                Decimal(s.numerator) / Decimal(s.denominator)
            )
            reference = F(str(Decimal(M.numerator) * (1 - (1 + x) * (-x).exp())))
        assert 0 < lo < reference < hi < M


def test_finite_uniform_density_cylinder_analytic_enclosure():
    # rho=1 on [RMIN,RMAX], aperture A>=RMIN: cylinder integral of rho*r^2,
    # divided by 4*pi, equals [RMAX^3-RMIN^3-(RMAX^2-A^2)^(3/2)]/3.
    z = m()
    e = z.Enclosure(bits=40)
    inside = lambda r: (r**3 - z.RMIN**3) / 3
    for A in [F(1), F(5), F(30)]:
        lo, hi = e.masses_on_shells(A, inside, N=70)
        delta = z.RMAX**2 - A**2
        analytic_lo = (z.RMAX**3 - z.RMIN**3 - delta * e.sqrt_hi(delta)) / 3
        analytic_hi = (z.RMAX**3 - z.RMIN**3 - delta * e.sqrt_lo(delta)) / 3
        assert 0 < lo <= analytic_lo <= analytic_hi <= hi <= inside(z.RMAX)


def test_hernquist_finite_spherical_mass_boundary():
    z = m()
    E = z.Enclosure(bits=40)
    mass = F(10**10)
    a = F(4, 3)
    primitive = lambda r: mass * ((r/(r+a))**2 - (z.RMIN/(z.RMIN+a))**2)
    low, high = E.masses_on_shells(z.RMAX, primitive, N=22)
    assert low == high == primitive(z.RMAX)
    with pytest.raises(ValueError):
        E.masses_on_shells(z.RMIN - F(1, 1000), primitive)


def test_mass_weighted_axis_ratio_and_derivative_identity():
    # Independent exact algebra check on q=(qb B+qd D)/(B+D).
    qb, qd = F(3, 5), F(9, 10)
    B, D = F(17), F(19)
    Bp, Dp = F(13), F(7)
    qprime = (qb - qd)*(Bp*D-B*Dp)/(B+D)**2
    # Direct quotient-rule expression, NOT copied from the producer's function.
    qprime_quot = ((qb*Bp+qd*Dp)*(B+D)-(qb*B+qd*D)*(Bp+Dp))/(B+D)**2
    assert qprime == qprime_quot
    # Verify the mathematical corner envelope is sound at exact interior values.
    bnds = (F(11), F(23))
    dnds = (F(15), F(35))
    corners = [(qb*b+qd*d)/(b+d) for b in bnds for d in dnds]
    for b in [F(11), F(16), F(23)]:
        for d in [F(15), F(24), F(35)]:
            assert min(corners) <= (qb*b+qd*d)/(b+d) <= max(corners)


def test_fail_closed_without_external_source_bundle():
    # A source-visible math-only PR cannot masquerade as an executed lens proof.
    assert not (PROOF / "input").exists()
    assert not (PROOF / "G4b1c_Global_Six_Lens_Exactly_One_Finite_Proxy_Real_Root_Candidate_v1.json").exists()
    assert not any(p.suffix == '.zip' for p in PROOF.iterdir())
    doc = (ROOT / "docs" / "HIST001D_D2E_G4B1C_GLOBAL_ROOT_COUNT_MATH_CANDIDATE.md").read_text()
    assert "NOT_ESTABLISHED" in doc and "NOT_PEER_REVIEWED" in doc
    assert "MARCH_180x120_NOT_PROVED" in doc
