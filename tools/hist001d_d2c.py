"""HIST-001D/D2c: source-locked shadow projection and empirical Cauchy screen.

The original six fitted Set A lenses are NOT blind holdouts. This studies a
finite-domain scalar effective-density proxy, not sourced Weyl lensing or the
physical Native ESET v1.7.2 model. No historical original is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
RADIAL_GRIDS = (180, 360, 720, 1440, 2880, 5760, 11520)
GAUSS_ORDERS = (24, 48)
CAUCHY_LATEST_RELATIVE_THRESHOLD = 5e-4  # engineering screen; explicitly NOT preregistered physics
QUADRATURE_REFERENCE_RELATIVE_TOLERANCE = 1e-9
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "new_holdout_scored": False,
    "physical_weyl_lensing_derived": False,
    "native_v172_equivalence_proved": False,
    "physical_provider_admitted": False,
    "empirical_validation": "NOT_ESTABLISHED",
    "canonical_theory_state_mutated": False,
    "original_source_modified": False,
}


class D2cIntegrityError(ValueError):
    """Unsupported numerical input, changed source, or forged evidence."""


@contextmanager
def source_modules(pack: Path):
    """Load frozen original solver from disposable copy without import pollution."""
    cached = {name: value for name, value in sys.modules.items()
              if name == "solv" or name.startswith("solv.")}
    for name in cached:
        del sys.modules[name]
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(pack))
    try:
        import solv
        if Path(solv.__file__).resolve().parent != pack.resolve() / "solv":
            raise D2cIntegrityError("unexpected historical solver origin")
        yield
    finally:
        sys.path.remove(str(pack))
        for name in tuple(sys.modules):
            if name == "solv" or name.startswith("solv."):
                del sys.modules[name]
        sys.modules.update(cached)
        sys.dont_write_bytecode = old


def integrated_shadow_piecewise_linear(R: float, r, rho, *, order: int = 24) -> float:
    """Independent cylinder integral for exact *piecewise-linear* input rho.

    Integrate 4*pi*[integral_a^R rho*r^2 dr +
                     integral_R^b rho*r*(r-sqrt(r^2-R^2)) dr]
    on a finite radial domain [a,b]. On outer intervals substitute
    t=sqrt(r^2-R^2), yielding rho(r(t))*t*R^2/(r(t)+t).
    The substitution removes the square-root kink at r=R and avoids
    subtraction of nearly equal large radii.
    """
    import numpy as np
    from scipy.special import roots_legendre

    if order not in GAUSS_ORDERS:
        raise D2cIntegrityError("unregistered Gauss order")
    grid = np.asarray(r, dtype=float)
    values = np.asarray(rho, dtype=float)
    if (grid.ndim != 1 or values.ndim != 1 or grid.size != values.size
            or grid.size < 3 or not np.all(np.isfinite(grid))
            or not np.all(np.isfinite(values)) or np.any(values < 0)
            or not np.all(np.diff(grid) > 0)):
        raise D2cIntegrityError("invalid finite source density grid")
    radius = float(R)
    if not math.isfinite(radius) or not 0.0 <= radius <= grid[-1]:
        raise D2cIntegrityError("projection radius outside source radial domain")
    left, right = grid[:-1], grid[1:]
    dr = right - left
    slope = np.diff(values) / dr
    inside_extent = np.maximum(np.minimum(right, radius) - left, 0.0)
    t = inside_extent
    # rho(left+u)*(left+u)^2 is a cubic in u; integrate it exactly.
    inside = np.sum(
        values[:-1] * left**2 * t
        + (2 * values[:-1] * left + slope * left**2) * t**2 / 2
        + (values[:-1] + 2 * slope * left) * t**3 / 3
        + slope * t**4 / 4
    )
    segments = right > radius
    if not np.any(segments) or radius == 0.0:
        return float(4 * np.pi * inside)
    a, b = left[segments], right[segments]
    start = np.maximum(a, radius)
    t0 = np.sqrt(np.maximum(start**2 - radius**2, 0.0))
    t1 = np.sqrt(np.maximum(b**2 - radius**2, 0.0))
    roots, weights = roots_legendre(order)
    tt = (t1 - t0)[:, None] * roots[None, :] / 2 + (t1 + t0)[:, None] / 2
    rr = np.sqrt(radius**2 + tt**2)
    rho_interp = values[:-1][segments, None] + slope[segments, None] * (rr - a[:, None])
    # Since r*(r-sqrt(r^2-R^2)) dr = t*R^2/(r+t) dt.
    out = rho_interp * tt * radius**2 / (rr + tt)
    outside = np.sum((t1 - t0) / 2 * (out @ weights))
    mass = float(4 * np.pi * (inside + outside))
    if not math.isfinite(mass) or mass < 0:
        raise D2cIntegrityError("nonfinite or negative independent projected mass")
    return mass


def adaptive_shadow_piecewise_linear(R: float, r, rho) -> float:
    """Second, independent SciPy quad integration of the SAME interpolant.

    Integrate every original linear-density cell separately, split any cell
    crossing R; there is no Gaussian quadrature, original K matrix, or q map.
    """
    import numpy as np
    from scipy.integrate import quad

    grid = np.asarray(r, dtype=float)
    values = np.asarray(rho, dtype=float)
    R = float(R)
    if not 0 < R < grid[-1]:
        raise D2cIntegrityError("adaptive reference radius outside domain")

    def rho_at(x):
        return float(np.interp(x, grid, values))

    total = 0.0
    for lower, upper in zip(grid[:-1], grid[1:]):
        if lower < R:
            inside_right = min(float(upper), R)
            total += quad(lambda x: 4 * math.pi * rho_at(x) * x**2,
                          lower, inside_right, epsabs=1.0, epsrel=1e-11, limit=90)[0]
        if upper > R:
            outer_left = max(float(lower), R)
            t0 = math.sqrt(max(outer_left**2 - R**2, 0.0))
            t1 = math.sqrt(max(float(upper)**2 - R**2, 0.0))

            def out(t):
                x = math.sqrt(R**2 + t**2)
                return 4 * math.pi * rho_at(x) * t * R**2 / (x + t)

            total += quad(out, t0, t1, epsabs=1.0, epsrel=1e-11, limit=90)[0]
    return float(total)


def source_projection_interpolated(R: float, grid, values) -> float:
    """Original K-matrix trapezoid at two grid knots plus linear R interpolation."""
    import numpy as np

    r = np.asarray(grid, dtype=float)
    rho = np.asarray(values, dtype=float)
    if R < r[0] or R > r[-1]:
        raise D2cIntegrityError("original source reference R outside grid")
    w = np.empty_like(r)
    w[0] = (r[1] - r[0]) / 2
    w[-1] = (r[-1] - r[-2]) / 2
    w[1:-1] = (r[2:] - r[:-2]) / 2
    index = int(np.clip(np.searchsorted(r, R, side="right"), 1, len(r) - 1))
    knots = r[index - 1:index + 1]
    masses = []
    for radius in knots:
        inside = np.where(r <= radius, r**2, 0.0)
        outside = np.where(
            r > radius, r * (r - np.sqrt(np.clip(r**2 - radius**2, 0.0, None))), 0.0,
        )
        masses.append(float(np.dot(4 * np.pi * (inside + outside) * w, rho)))
    return float(np.interp(R, knots, masses))


def reference_bulge_finite(R: float, bulge_mass: float, bulge_re: float) -> float:
    """Adaptive Hernquist projected mass in the original finite radial domain."""
    from scipy.integrate import quad

    a = bulge_re / 1.8153

    def density(x):
        return bulge_mass * a / (2 * math.pi * x * (x + a)**3)

    inner = quad(lambda x: 4 * math.pi * density(x) * x**2,
                 0.02, R, epsabs=1.0, epsrel=1e-10, limit=120)[0]
    outer = quad(lambda x: 4 * math.pi * density(x) * x * R**2
                 / (x + math.sqrt(max(0, x * x - R * R))),
                 R, 120, epsabs=1.0, epsrel=1e-10, limit=120)[0]
    return float(inner + outer)


def reference_periodic_disk(R: float, disc_mass: float, disc_r50: float,
                            axis_ratio: float, ntheta: int = 512) -> float:
    """Full periodic trapezoid of source analytic disc integrand, not source's omitted arc."""
    import numpy as np

    if ntheta not in (512, 1024):
        raise D2cIntegrityError("unsupported periodic disc accuracy screen")
    scale = disc_r50 / 1.67835
    theta = np.linspace(0.0, 2 * np.pi, ntheta, endpoint=False)
    geometrical = np.sqrt(np.cos(theta)**2 + np.sin(theta)**2 / axis_ratio**2)
    x = geometrical * R / scale
    # Stable alternative to 1-exp(-x)*(1+x) at small x.
    inner = scale**2 / geometrical**2 * (-np.expm1(-x) - x * np.exp(-x))
    sigma0 = disc_mass / (2 * np.pi * axis_ratio * scale**2)
    return float(sigma0 * np.mean(inner) * 2 * np.pi)


def one_lens(row: dict, anchor: dict, gate: dict) -> dict:
    """Keep R_eff fixed with independent finite-baryon q_eff across all grids."""
    import numpy as np
    from solv.baryons import J2141BaryonicModel
    from solv.dmalane import build_gate_components, epsilon_from_config
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.shadow_density import compute_shadow_density
    from solv.run_setA_port_cand import _projection_matrix

    bm = 10**float(row["logM_bulge_chabrier_central"])
    dm = 10**float(row["logM_disc_chabrier_central"])
    scale = float(row["scale_kpc_per_arcsec"])
    radius = float(row["einstein_radius_arcsec_central"]) * scale
    bre = float(row["Re_bulge_arcsec"]) * scale
    dr50 = float(row["Re_disc_arcsec"]) * scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    if not 0.02 < radius < 120:
        raise D2cIntegrityError("observed Einstein radius outside source finite domain")
    mass_bulge = reference_bulge_finite(radius, bm, bre)
    disk512 = reference_periodic_disk(radius, dm, dr50, qd)
    disk1024 = reference_periodic_disk(radius, dm, dr50, qd, 1024)
    if not math.isclose(disk512, disk1024, rel_tol=1e-8, abs_tol=1):
        raise D2cIntegrityError("fixed baryonic reference angle quadrature unconverged")
    qref = float(np.clip((qb * mass_bulge + qd * disk1024)
                         / (mass_bulge + disk1024), 1e-3, 1.0))
    effective = float(radius / math.sqrt(qref))
    if effective >= 120:
        raise D2cIntegrityError("structured evaluation R_eff exceeds finite grid")

    model = J2141BaryonicModel(bm, bre, dm, dr50)
    features = extract_gate_features_from_values(
        bm, bre, dm, dr50, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    components = build_gate_components(gate, features=features, anchor=anchor)
    measurements = []
    for n in RADIAL_GRIDS:
        grid = np.linspace(0.02, 120, n)
        gbar = model.total_vbar(grid)**2 / grid
        eps = epsilon_from_config(grid, gbar, gate, features=features, anchor=anchor)
        rho = compute_shadow_density(
            grid, gbar, gbar / eps, epsilon=eps,
            method=components.get("shadow_density_method", "mass_difference_gradient"),
        )
        gauss24 = integrated_shadow_piecewise_linear(effective, grid, rho, order=24)
        gauss48 = integrated_shadow_piecewise_linear(effective, grid, rho, order=48)
        if not math.isclose(gauss24, gauss48,
                            rel_tol=QUADRATURE_REFERENCE_RELATIVE_TOLERANCE, abs_tol=1):
            raise D2cIntegrityError("24/48 Gaussian projection reference disagrees")
        from_source = source_projection_interpolated(effective, grid, rho)
        if n in (180, 360):
            # Independently confirm source K @rho as well as quad vs Gauss.
            fullK = _projection_matrix(grid) @ rho
            source_brute = float(np.interp(effective, grid, fullK))
            if not math.isclose(from_source, source_brute, rel_tol=1e-12, abs_tol=1):
                raise D2cIntegrityError("original K-matrix readback differs")
            adaptive = adaptive_shadow_piecewise_linear(effective, grid, rho)
            if not math.isclose(gauss48, adaptive,
                                rel_tol=QUADRATURE_REFERENCE_RELATIVE_TOLERANCE, abs_tol=1):
                raise D2cIntegrityError("independent scipy quad disagrees with transformed Gauss")
            adaptive_rel = float((adaptive - gauss48) / gauss48)
        else:
            adaptive_rel = None
        measurements.append({
            "radial_grid_points": n,
            "source_K_projected_shadow_msun": from_source,
            "independent_finite_piecewise_linear_shadow_msun": gauss48,
            "source_K_fractional_bias_vs_independent": float((from_source - gauss48) / gauss48),
            "gauss24_vs_gauss48_fractional_difference": float((gauss24 - gauss48) / gauss48),
            "adaptive_scipy_vs_gauss48_fractional_difference": adaptive_rel,
            "negative_density_bins": int(np.sum(rho < 0)),
            "zero_density_bins": int(np.sum(rho == 0)),
        })
    for index in range(1, len(measurements)):
        previous = measurements[index - 1]["independent_finite_piecewise_linear_shadow_msun"]
        current = measurements[index]["independent_finite_piecewise_linear_shadow_msun"]
        measurements[index]["fixed_R_cauchy_relative_delta"] = float((current - previous) / previous)
    measurements[0]["fixed_R_cauchy_relative_delta"] = None
    recent = [abs(measurements[-k]["fixed_R_cauchy_relative_delta"]) for k in (2, 1)]
    cauchy_pass = bool(all(value <= CAUCHY_LATEST_RELATIVE_THRESHOLD for value in recent))
    # Empirical 2nd-order tail estimate, NOT a rigorous error bound.
    deltas = [measurements[-k]["independent_finite_piecewise_linear_shadow_msun"]
              - measurements[-k - 1]["independent_finite_piecewise_linear_shadow_msun"]
              for k in (2, 1)]
    tail_est = float(abs(deltas[-1]) / 3)
    return {
        "lens_id": row["lens_id"],
        "observed_einstein_radius_kpc": radius,
        "fixed_baryon_q_eff_adaptive_and_periodic": qref,
        "fixed_effective_shadow_radius_kpc": effective,
        "reference_bulge_finite_domain_mass_msun": mass_bulge,
        "reference_full_periodic_disc_mass_msun": disk1024,
        "mass_by_source_density_grid": measurements,
        "latest_two_cauchy_relative_abs": recent,
        "latest_two_pass_0p05_percent_screen": cauchy_pass,
        "second_order_tail_heuristic_msun": tail_est,
        "second_order_tail_heuristic_is_proof": False,
    }


def execute(source_root: str | Path) -> dict:
    """Recompute without refitting; enforce March 46+3 source lock before/after."""
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    root = Path(source_root)
    verified = verify_hist001_source(root)
    if verified["source_lock_sha256"] != SOURCE_SHA256:
        raise D2cIntegrityError("wrong frozen original source identity")
    with TemporaryDirectory(prefix="hist001d_d2c_source_") as temporary:
        working = Path(temporary) / "hist001"
        shutil.copytree(root, working)
        verify_hist001_source(working)
        pack = working / "swells_pack_v2"
        with source_modules(pack):
            import solv.run_setA_port_cand as original
            sample = original._load_tables(pack)
            if tuple(sample["lens_id"]) != LENS_IDS:
                raise D2cIntegrityError("wrong development lens order")
            anchor, _ = original._build_anchor(pack)
            gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
            results = [one_lens(row, anchor, gate) for row in sample.to_dict("records")]
        verify_hist001_source(working)
    verify_hist001_source(root)
    if not all(x["latest_two_pass_0p05_percent_screen"] for x in results):
        raise D2cIntegrityError("empirical fine-grid Cauchy screen failed")
    return {
        "schema": "NATIVE_ESET_HIST001D_D2C_SHADOW_PROJECTION_DIAGNOSTIC_V1",
        "status": "HIST001D_D2C_FINITE_SOURCE_QUADRATURE_CAUCHY_DIAGNOSTIC_NO_ADMISSION",
        "source_lock_sha256": SOURCE_SHA256,
        "candidate": CANDIDATE,
        "data_role": "SIX_FITTED_DEVELOPMENT_LENSES_NO_HOLDOUT",
        "radial_grids": list(RADIAL_GRIDS),
        "gauss_orders": list(GAUSS_ORDERS),
        "finite_radial_domain_kpc": [0.02, 120],
        "effective_radius_policy": "FIXED_ACROSS_GRIDS_INDEPENDENT_FINITE_HERNQUIST_AND_PERIODIC_DISC",
        "numerical_reference": "PIECEWISE_LINEAR_FROZEN_DENSITY_EXACT_INSIDE_GAUSS_TRANSFORMED_OUTSIDE",
        "cauchy_engineering_screen": {
            "relative_limit": CAUCHY_LATEST_RELATIVE_THRESHOLD,
            "pairs": [[2880, 5760], [5760, 11520]],
            "all_six_lenses_pass": True,
            "classification": "RETROSPECTIVE_ENGINEERING_SCREEN_NOT_EXTERNAL_PREREGISTRATION",
            "not_a_rigorous_global_or_physical_error_bound": True,
        },
        "results": results,
        "claims": dict(CLAIMS),
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "pandas": pd.__version__, "scipy": scipy.__version__,
        },
        "limitations": (
            "Discrete original shadow density reconstructed piecewise linearly; reference has fixed "
            "baryon-derived effective radius at six already-fitted Einstein radii. "
            "Numerical quadrature/Cauchy tests do not establish full critical-radius "
            "root convergence, mathematical a-priori bounds, physical Weyl lensing, "
            "heldout validity or native ESET v1.7.2 theory equivalence."
        ),
    }


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def run(source_root: str | Path, output_root: str | Path) -> dict:
    from native_eset.evidence.receipts import canonical_json

    source = Path(source_root)
    out = Path(output_root)
    if source.is_symlink() or out.is_symlink():
        raise D2cIntegrityError("unsafe source/output symlink")
    if out.resolve() == source.resolve() or out.resolve().is_relative_to(source.resolve()):
        raise D2cIntegrityError("output overlaps immutable source")
    if out.exists():
        raise FileExistsError("D2c output already exists")
    report = execute(source)
    raw = canonical_json(report)
    receipt = {
        "schema": "NATIVE_ESET_HIST001D_D2C_RECEIPT_V1",
        "status": "HIST001D_D2C_FINITE_SOURCE_QUADRATURE_CAUCHY_DIAGNOSTIC_NO_ADMISSION",
        "report_sha256": _sha(raw),
        "module_sha256": _sha(Path(__file__).read_bytes()),
        "source_lock_sha256": SOURCE_SHA256,
        "claims": dict(CLAIMS),
    }
    receipt_raw = canonical_json(receipt)
    out.mkdir(parents=True)
    (out / "report.json").write_bytes(raw)
    (out / "receipt.json").write_bytes(receipt_raw)
    (out / "receipt.sha256").write_text(_sha(receipt_raw) + "\n", encoding="ascii")
    return {
        "status": receipt["status"], "receipt_sha256": _sha(receipt_raw),
        "output_dir": str(out), "cases": len(report["results"]),
        "radial_grids": len(RADIAL_GRIDS), "claims": dict(CLAIMS),
    }


def _compare(left, right, path: str = "report") -> None:
    """Reexecution check, even if attacker repairs internal hashes."""
    if type(left) is not type(right):
        raise D2cIntegrityError(f"changed field type: {path}")
    if isinstance(right, dict):
        if left.keys() != right.keys():
            raise D2cIntegrityError(f"modified report fields: {path}")
        for key in right:
            if path == "report" and key == "environment":
                continue
            _compare(left[key], right[key], path + "." + str(key))
    elif isinstance(right, list):
        if len(left) != len(right):
            raise D2cIntegrityError(f"changed row count: {path}")
        for index, (a, b) in enumerate(zip(left, right)):
            _compare(a, b, path + "[" + str(index) + "]")
    elif type(right) is float:
        if not math.isfinite(left) or abs(left - right) > 1e-9 * max(1.0, abs(right)):
            raise D2cIntegrityError(f"numerical source reexecution mismatch: {path}")
    elif left != right:
        raise D2cIntegrityError(f"changed report value: {path}")


def verify(receipt_path: str | Path, source_root: str | Path,
           expected_sha256: str | None = None) -> dict:
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads

    path = Path(receipt_path)
    if (path.name != "receipt.json" or path.is_symlink() or path.parent.is_symlink()
            or not path.is_file()):
        raise D2cIntegrityError("unsafe official receipt")
    files = list(path.parent.iterdir())
    if {x.name for x in files} != {"receipt.json", "report.json", "receipt.sha256"}:
        raise D2cIntegrityError("missing/unexpected receipt files")
    if any(x.is_symlink() or not x.is_file() for x in files):
        raise D2cIntegrityError("unsafe receipt file type")
    receipt_bytes = path.read_bytes()
    digest = _sha(receipt_bytes)
    if (path.parent / "receipt.sha256").read_text(encoding="ascii") != digest + "\n":
        raise D2cIntegrityError("receipt SHA text differs")
    if expected_sha256 is not None and digest != expected_sha256:
        raise D2cIntegrityError("external receipt SHA differs")
    report_bytes = (path.parent / "report.json").read_bytes()
    receipt, report = strict_loads(receipt_bytes), strict_loads(report_bytes)
    if canonical_json(receipt) != receipt_bytes or canonical_json(report) != report_bytes:
        raise D2cIntegrityError("receipt is not canonical JSON")
    if (
        set(receipt) != {"schema", "status", "report_sha256", "module_sha256", "source_lock_sha256", "claims"}
        or receipt.get("schema") != "NATIVE_ESET_HIST001D_D2C_RECEIPT_V1"
        or receipt.get("status") != "HIST001D_D2C_FINITE_SOURCE_QUADRATURE_CAUCHY_DIAGNOSTIC_NO_ADMISSION"
        or receipt.get("report_sha256") != _sha(report_bytes)
        or receipt.get("module_sha256") != _sha(Path(__file__).read_bytes())
        or receipt.get("source_lock_sha256") != SOURCE_SHA256
        or receipt.get("claims") != CLAIMS
        or report.get("schema") != "NATIVE_ESET_HIST001D_D2C_SHADOW_PROJECTION_DIAGNOSTIC_V1"
        or report.get("status") != "HIST001D_D2C_FINITE_SOURCE_QUADRATURE_CAUCHY_DIAGNOSTIC_NO_ADMISSION"
        or report.get("claims") != CLAIMS
    ):
        raise D2cIntegrityError("wrong source/status or attempted physical promotion")
    _compare(report, execute(source_root))
    return {
        "status": "HIST001D_D2C_INDEPENDENT_SOURCE_REEXECUTION_PASS_NO_ADMISSION",
        "receipt_sha256": digest, "six_development_lenses_recomputed": 6,
        "density_grids_each": len(RADIAL_GRIDS), "claims": dict(CLAIMS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--out", type=Path)
    modes.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        result = (verify(args.verify, args.source_root, args.expected_sha256)
                  if args.verify is not None else run(args.source_root, args.out))
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(json.dumps({"status": "HIST001D_D2C_FAIL_CLOSED", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
