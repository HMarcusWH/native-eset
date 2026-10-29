"""HIST-001D/D2e-B: conservative interval root-exclusion diagnostic.

Source-locked finite-domain fitted *proxy*, NOT interval-verified arithmetic.
Bounds use positivity of baryon/shadow densities and explicit unproven
relative quadrature/error allowance. A conditional exclusion is not a
mathematical root-uniqueness theorem, physical Weyl-lensing solution, or
independent validation. The residual root window is deliberately unresolved.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
D2E_A_SHA256 = "ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2"
LENS_IDS = ("J0822+1828", "J0915+4211", "J0930+2855",
            "J1021+2028", "J1111+2234", "J1135+3720")
FINITE_DOMAIN = (0.02, 120.0)
ROOT_GUARD_FRACTION = 0.02
ASSUMED_RELATIVE_MASS_ENVELOPE = 1e-6
MAX_BISECTION_DEPTH = 18
MAX_INTERVAL_VISITS = 2048
GAUSS_ORDER = 24
SCHEMA = "NATIVE_ESET_HIST001D_D2E_B_CONDITIONAL_INTERVAL_REPORT_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_B_CONDITIONAL_INTERVAL_RECEIPT_V1"
STATUS = "D2E_B_CONDITIONAL_ROOT_EXCLUSION_UNCERTIFIED_NO_PHYSICAL_ADMISSION"
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "conditional_interval_root_exclusion": True,
    "uniform_quadrature_error_budget_proved": False,
    "root_uniqueness_mathematically_certified": False,
    "global_error_bound_established": False,
    "mass_outside_finite_domain_bounded": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "new_holdout_scored": False,
    "native_v172_equivalence_proved": False,
    "empirical_validation": "NOT_ESTABLISHED",
    "original_source_modified": False,
    "canonical_theory_state_mutated": False,
}


class IntervalDiagnosticError(ValueError):
    """Fail closed on missing source, invalid enclosure, or forged scientific claims."""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_pinned_a():
    path = Path(__file__).resolve().with_name("hist001d_d2e.py")
    if path.is_symlink() or not path.is_file() or sha(path.read_bytes()) != D2E_A_SHA256:
        raise IntervalDiagnosticError("pinned D2e-A numerical reference changed")
    spec = importlib.util.spec_from_file_location("hist001d_d2e_a_for_b", path)
    if spec is None or spec.loader is None:
        raise IntervalDiagnosticError("cannot import pinned D2e-A")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SOURCE_SHA256 != SOURCE_SHA256 or module.CLAIMS["physical_provider_admitted"]:
        raise IntervalDiagnosticError("D2e-A source or physics claim changed")
    return module


def q_corner_bounds(bulge_lo, bulge_hi, disk_lo, disk_hi, qb, qd):
    """Bound baryon-mass-weighted q over a radius interval by four corners.

    Since each projected baryon mass is nondecreasing in radius, the two
    positive masses each lie in their endpoint range. The ratio is
    fractional-linear in each argument; extrema lie at the four corners.
    """
    values = (bulge_lo, bulge_hi, disk_lo, disk_hi, qb, qd)
    if any(not math.isfinite(v) for v in values):
        raise IntervalDiagnosticError("nonfinite effective-axis enclosure input")
    if not (0 < bulge_lo <= bulge_hi and 0 < disk_lo <= disk_hi
            and 0 < qb <= 1 and 0 < qd <= 1):
        raise IntervalDiagnosticError("nonpositive or unordered axis enclosure input")
    corners = [(qb * b + qd * d) / (b + d)
               for b in (bulge_lo, bulge_hi)
               for d in (disk_lo, disk_hi)]
    return max(0.001, min(corners)), min(1.0, max(corners))


def normalized_interval_enclosure(
    lo, hi, bulge_lo, bulge_hi, disk_lo, disk_hi,
    shadow_at_lo, shadow_at_hi, sigma_crit, mass_error_fraction,
):
    """Conservative mass/critical-target bounds, *conditional* on pointwise error.

    mass_error_fraction is an explicit ASSUMPTION, not derived from two
    successive meshes or a quadrature difference. Monotonicity of each
    finite-domain positive-density mass is the mathematical part; the
    floating-point mass enclosure is not rigorously certified.
    """
    values = (lo, hi, bulge_lo, bulge_hi, disk_lo, disk_hi,
              shadow_at_lo, shadow_at_hi, sigma_crit, mass_error_fraction)
    if any(not math.isfinite(v) for v in values):
        raise IntervalDiagnosticError("nonfinite interval enclosure")
    if not (0 < lo < hi <= 120 and sigma_crit > 0
            and 0 <= mass_error_fraction < 1
            and 0 <= shadow_at_lo <= shadow_at_hi):
        raise IntervalDiagnosticError("invalid assumed interval envelope")
    lower_mass = (bulge_lo + disk_lo + shadow_at_lo) * (1 - mass_error_fraction)
    upper_mass = (bulge_hi + disk_hi + shadow_at_hi) * (1 + mass_error_fraction)
    if not (0 <= lower_mass <= upper_mass):
        raise IntervalDiagnosticError("inverted numerical mass bounds")
    factor = math.pi * sigma_crit
    lower = lower_mass / (factor * hi**2) - 1
    upper = upper_mass / (factor * lo**2) - 1
    if not (math.isfinite(lower) and math.isfinite(upper) and lower <= upper):
        raise IntervalDiagnosticError("invalid normalized critical-mass enclosure")
    return lower, upper


def exclude_intervals(enclose, ranges, *, max_depth=MAX_BISECTION_DEPTH,
                      max_visits=MAX_INTERVAL_VISITS):
    """Adaptive interval sign exclusion; report every unresolved interval.

    A root-free determination is only as strong as the pointwise mass
    enclosures provided by enclose(). No interval gets an unrecorded pass.
    """
    if type(max_depth) is not int or not 0 <= max_depth <= 24:
        raise IntervalDiagnosticError("unsupported bisection depth")
    if type(max_visits) is not int or not 1 <= max_visits <= 100000:
        raise IntervalDiagnosticError("unsupported visit budget")
    stack = [(float(lo), float(hi), 0) for lo, hi in reversed(ranges)]
    records, unresolved = [], []
    visits = 0
    while stack:
        if visits >= max_visits:
            unresolved.extend({"lo": a, "hi": b, "depth": d,
                               "reason": "VISIT_BUDGET"} for a, b, d in stack)
            break
        lo, hi, depth = stack.pop()
        if not (math.isfinite(lo) and math.isfinite(hi) and 0 < lo < hi <= 120):
            raise IntervalDiagnosticError("invalid interval in root isolation")
        lower, upper = enclose(lo, hi)
        visits += 1
        if not (math.isfinite(lower) and math.isfinite(upper) and lower <= upper):
            raise IntervalDiagnosticError("invalid enclosure oracle")
        if lower > 0 or upper < 0:
            records.append({"lo": lo, "hi": hi, "depth": depth,
                            "sign": "POSITIVE" if lower > 0 else "NEGATIVE",
                            "lower": lower, "upper": upper})
        elif depth >= max_depth or math.nextafter(lo, math.inf) >= hi:
            unresolved.append({"lo": lo, "hi": hi, "depth": depth,
                               "reason": "INTERVAL_INCLUDES_ZERO"})
        else:
            mid = lo + (hi - lo) / 2
            if not lo < mid < hi:
                unresolved.append({"lo": lo, "hi": hi, "depth": depth,
                                   "reason": "FLOAT_RESOLUTION"})
            else:
                stack.append((mid, hi, depth+1))
                stack.append((lo, mid, depth+1))
    return {"visited": visits, "excluded_count": len(records),
            "excluded_signs": {
                "POSITIVE": sum(x["sign"] == "POSITIVE" for x in records),
                "NEGATIVE": sum(x["sign"] == "NEGATIVE" for x in records),
            },
            "excluded_intervals": records,
            "unresolved_intervals": unresolved,
            "all_tested_outside_guard_excluded_under_assumed_budget":
                len(unresolved) == 0}


def one_lens(row: dict, anchor: dict, gate: dict, a, d2c):
    import numpy as np
    from scipy.optimize import brentq
    from solv.baryons import J2141BaryonicModel
    from solv.cosmology import FlatLCDM
    from solv.dmalane import epsilon_from_config
    from solv.gate_struct import A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values
    from solv.shadow_density import compute_shadow_density

    lid = str(row["lens_id"])
    if lid not in LENS_IDS:
        raise IntervalDiagnosticError("unknown fitted development lens")
    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10 ** float(row["logM_bulge_chabrier_central"])
    dm = 10 ** float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"]) * scale
    dre = float(row["Re_disc_arcsec"]) * scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    sig_obs = float(row["einstein_radius_arcsec_err_plus"]) * scale
    if min(scale, bm, dm, bre, dre, qb, qd, sig_obs) <= 0:
        raise IntervalDiagnosticError("invalid frozen model input")
    sigma_crit = FlatLCDM(70, 0.3).sigma_crit_msun_per_kpc2(
        float(row["z_deflector"]), float(row["z_source"]),
    )
    model = J2141BaryonicModel(bm, bre, dm, dre)
    features = extract_gate_features_from_values(
        bm, bre, dm, dre, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    radial = np.linspace(*FINITE_DOMAIN, 11520)
    gbar = model.total_vbar(radial)**2 / radial
    eps = epsilon_from_config(radial, gbar, gate, features=features, anchor=anchor)
    rho = compute_shadow_density(radial, gbar, gbar/eps, epsilon=eps)
    if not np.all(np.isfinite(rho)) or np.any(rho < 0):
        raise IntervalDiagnosticError("invalid full source shadow density")

    @lru_cache(maxsize=2048)
    def baryonic(R):
        b = d2c.reference_bulge_finite(float(R), bm, bre)
        d = d2c.reference_periodic_disk(float(R), dm, dre, qd, ntheta=1024)
        if min(b, d) <= 0 or not math.isfinite(b+d):
            raise IntervalDiagnosticError("invalid baryonic projection")
        return float(b), float(d)

    @lru_cache(maxsize=4096)
    def shadow(A):
        return d2c.integrated_shadow_piecewise_linear(
            min(float(A), FINITE_DOMAIN[1]), radial, rho, order=GAUSS_ORDER,
        )

    def total(R):
        b, d = baryonic(R)
        q = max(.001, min(1., (qb*b + qd*d)/(b+d)))
        return b+d+shadow(R/math.sqrt(q))

    def normalized(R):
        return total(float(R)) / (math.pi*sigma_crit*R*R) - 1

    ref = a.D2D_REFERENCE_ROOT_KPC[lid]
    gl = max(FINITE_DOMAIN[0], ref*(1-ROOT_GUARD_FRACTION))
    gh = min(FINITE_DOMAIN[1], ref*(1+ROOT_GUARD_FRACTION))
    left_sign, right_sign = normalized(gl), normalized(gh)
    if not (left_sign > 0 and right_sign < 0 and gl < ref < gh):
        raise IntervalDiagnosticError("root-guard does not bracket the D2d solution")
    reroot = float(brentq(normalized, gl, gh, xtol=1e-11))
    delta_sigma = (reroot-ref)/sig_obs
    if abs(delta_sigma) > 1e-7:
        raise IntervalDiagnosticError("source-recomputed D2d root mismatch")

    @lru_cache(maxsize=8192)
    def interval_enclosure(lo, hi):
        blo, dlo = baryonic(lo)
        bhi, dhi = baryonic(hi)
        if blo > bhi or dlo > dhi:
            raise IntervalDiagnosticError("positive baryonic mass monotonicity violated")
        qmin, qmax = q_corner_bounds(blo, bhi, dlo, dhi, qb, qd)
        a_min = min(FINITE_DOMAIN[1], lo/math.sqrt(qmax))
        a_max = min(FINITE_DOMAIN[1], hi/math.sqrt(qmin))
        smin, smax = shadow(a_min), shadow(a_max)
        if smin > smax:
            raise IntervalDiagnosticError("positive shadow mass monotonicity violated")
        return normalized_interval_enclosure(
            lo, hi, blo, bhi, dlo, dhi, smin, smax,
            sigma_crit, ASSUMED_RELATIVE_MASS_ENVELOPE,
        )

    result = exclude_intervals(interval_enclosure, [
        (FINITE_DOMAIN[0], gl), (gh, FINITE_DOMAIN[1]),
    ])
    return {
        "lens_id": lid,
        "d2d_reference_root_kpc": ref,
        "independent_root_kpc": reroot,
        "independent_root_delta_observational_sigma": delta_sigma,
        "guard_interval_kpc": [gl, gh],
        "guard_signs": [left_sign, right_sign],
        "outside_guard_isolation": result,
        "root_count_within_guard": "NOT_CERTIFIED",
        "global_root_uniqueness": "NOT_CERTIFIED",
        "enclosure_is_conditional_on_assumed_mass_error": True,
    }


def execute(source_root: str | Path):
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    a = load_pinned_a()
    d2c = a._load_pinned("hist001d_d2c.py", a.D2C_SHA256)
    source = Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise IntervalDiagnosticError("source root missing or symlinked")
    if verify_hist001_source(source)["source_lock_sha256"] != SOURCE_SHA256:
        raise IntervalDiagnosticError("source SHA differs")
    with TemporaryDirectory(prefix="d2e_b_frozen_") as tmp:
        working = Path(tmp) / "hist001"
        shutil.copytree(source, working)
        verify_hist001_source(working)
        with d2c.source_modules(working/"swells_pack_v2"):
            import solv.run_setA_port_cand as original
            source_rows = original._load_tables(working/"swells_pack_v2")
            if tuple(source_rows.lens_id) != LENS_IDS:
                raise IntervalDiagnosticError("fitted lens identity changed")
            anchor, _ = original._build_anchor(working/"swells_pack_v2")
            gate = original._candidate_gate_config(
                anchor, candidate_name=a.CANDIDATE,
            )
            historical = original.evaluate_portability_dataframe(
                working/"swells_pack_v2", gate, gate_label=a.CANDIDATE,
            )
            if sum(bool(x) for x in historical.both_pass) != 6:
                raise IntervalDiagnosticError("historical original 6/6 mismatch")
            lenses = [one_lens(row, anchor, gate, a, d2c)
                      for row in source_rows.to_dict("records")]
        verify_hist001_source(working)
    verify_hist001_source(source)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2e_a_sha256": D2E_A_SHA256,
        "finite_domain_kpc": list(FINITE_DOMAIN),
        "density_grid_points": 11520,
        "assumed_mass_relative_error_fraction": ASSUMED_RELATIVE_MASS_ENVELOPE,
        "assumption_proved": False,
        "root_guard_fraction": ROOT_GUARD_FRACTION,
        "max_bisection_depth": MAX_BISECTION_DEPTH,
        "max_interval_visits": MAX_INTERVAL_VISITS,
        "original_historical_fitted_joint_pass_count": 6,
        "previous_distinct_d2d_joint_pass_count": 3,
        "interval_method": "POSITIVE_COMPONENT_MONOTONICITY_QEFF_FOUR_CORNERS_CONDITIONAL_FLOAT_MASS_ENVELOPE",
        "verdict": "CONDITIONAL_ROOT_EXCLUSION_OUTSIDE_UNRESOLVED_GUARD_NOT_GLOBAL_ROOT_CERTIFICATE",
        "lenses": lenses,
        "claims": dict(CLAIMS),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "scipy": scipy.__version__},
    }


def run(source_root: str | Path, out: str | Path):
    from native_eset.evidence.receipts import canonical_json
    source, output = Path(source_root), Path(out)
    if source.is_symlink() or output.is_symlink() or output.exists():
        raise IntervalDiagnosticError("unsafe or existing output root")
    if output.resolve() == source.resolve() or output.resolve().is_relative_to(source.resolve()):
        raise IntervalDiagnosticError("cannot write into original source")
    report_raw = canonical_json(execute(source))
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2e_a_sha256": D2E_A_SHA256,
        "module_sha256": sha(Path(__file__).read_bytes()),
        "report_sha256": sha(report_raw),
        "claims": dict(CLAIMS),
    }
    receipt_raw = canonical_json(receipt)
    output.mkdir(parents=True)
    (output/"report.json").write_bytes(report_raw)
    (output/"receipt.json").write_bytes(receipt_raw)
    (output/"receipt.sha256").write_text(sha(receipt_raw)+"\n", encoding="ascii")
    return {"status": STATUS, "receipt_sha256": sha(receipt_raw), "claims": dict(CLAIMS)}


def verify(receipt_path: str | Path, source_root: str | Path, expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    p = Path(receipt_path)
    if p.name != "receipt.json" or p.is_symlink() or p.parent.is_symlink():
        raise IntervalDiagnosticError("unsafe receipt path")
    files = list(p.parent.iterdir())
    if {x.name for x in files} != {"report.json", "receipt.json", "receipt.sha256"} or any(
        not x.is_file() or x.is_symlink() for x in files
    ):
        raise IntervalDiagnosticError("receipt inventory changed")
    raw = p.read_bytes()
    digest = sha(raw)
    if expected_sha256 is not None and digest != expected_sha256:
        raise IntervalDiagnosticError("externally pinned receipt mismatch")
    if (p.parent/"receipt.sha256").read_text(encoding="ascii") != digest+"\n":
        raise IntervalDiagnosticError("receipt SHA sidecar differs")
    receipt = strict_loads(raw)
    report_raw = (p.parent/"report.json").read_bytes()
    report = strict_loads(report_raw)
    if canonical_json(receipt) != raw or canonical_json(report) != report_raw:
        raise IntervalDiagnosticError("noncanonical receipt/report JSON")
    expected = {
        "schema": RECEIPT_SCHEMA, "status": STATUS, "source_lock_sha256": SOURCE_SHA256,
        "d2e_a_sha256": D2E_A_SHA256, "module_sha256": sha(Path(__file__).read_bytes()),
        "report_sha256": sha(report_raw), "claims": dict(CLAIMS),
    }
    if receipt != expected or report.get("claims") != CLAIMS or report.get("schema") != SCHEMA:
        raise IntervalDiagnosticError("receipt or scientific claim forgery")
    original = execute(source_root)
    try:
        load_pinned_a()._compare(report, original)
    except ValueError as e:
        raise IntervalDiagnosticError("source-reexecution value mismatch") from e
    return {"status": "D2E_B_SOURCE_REEXECUTION_PASS_CONDITIONAL_NO_ADMISSION",
            "receipt_sha256": digest, "lenses": len(original["lenses"]),
            "global_root_uniqueness_certified": False, "claims": dict(CLAIMS)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out", type=Path)
    action.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        reply = verify(args.verify, args.source_root, args.expected_sha256) if args.verify else run(
            args.source_root, args.out,
        )
    except (OSError, ValueError, KeyError, ImportError, AssertionError, TypeError) as e:
        print(json.dumps({"status": "D2E_B_FAIL_CLOSED", "error": str(e)}, sort_keys=True))
        return 2
    print(json.dumps(reply, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
