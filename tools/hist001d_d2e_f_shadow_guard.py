"""D2e-F source-locked shadow-aperture bands, conditional structured-root audit.

For six ALREADY FITTED development lenses: reconstruct the frozen March
11,520-point source shadow density, form the +-2% D2d-root guard, compute
baryonic endpoint masses, and conditionally map the radius interval through
q_eff corner bounds into a certified exact-nodal shadow aperture band.

Only the discrete finite shadow M(A) band is independently mathematically
enclosed. Baryonic endpoint functions, approximate q_eff, sigma critical,
continuum source density and physical lensing remain UNPROVED.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from native_eset.numerics.shadow_aperture_intervals import (
    certified_shadow_mass_band,
    conditional_aperture_band,
    conditional_normalized_root_residual_band,
    frozen_baryonic_q_corners,
)

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
D2E_E_SHA256 = "1b718e1b3fee24b8f0bb85da7dfe8ddf067460319f22cfc11bbf0f5961a8f1f6"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = ("J0822+1828", "J0915+4211", "J0930+2855",
            "J1021+2028", "J1111+2234", "J1135+3720")
RADIAL_POINTS = 11520
DOMAIN = (0.02, 120.)
GUARD_FRACTION = .02
STATUS = "HIST001D_D2E_F_SHADOW_APERTURE_BAND_CERTIFIED_ROOT_MAP_CONDITIONAL"
SCHEMA = "NATIVE_ESET_HIST001D_D2E_F_SHADOW_BAND_ROOT_GUARD_REPORT_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_F_SHADOW_BAND_RECEIPT_V1"
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "finite_discrete_shadow_mass_all_apertures_in_reported_band_enclosed": True,
    "input_shadow_density_exact_binary64_nodal": True,
    "continuous_baryonic_mass_box_certified": False,
    "qeff_root_map_unconditionally_certified": False,
    "d2e_b_total_mass_1e6_assumption_proved": False,
    "global_root_uniqueness_mathematically_certified": False,
    "global_model_numerical_error_bound_established": False,
    "mass_outside_finite_domain_bounded": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "native_v172_equivalence_proved": False,
    "new_holdout_scored": False,
    "canonical_theory_state_mutated": False,
    "original_source_modified": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class D2eFError(ValueError):
    """Invalid source identity, untrusted results, or unauthorized promotion."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_e():
    path = Path(__file__).resolve().with_name("hist001d_d2e_e_adaptive_projection.py")
    if path.is_symlink() or not path.is_file() or _sha(path.read_bytes()) != D2E_E_SHA256:
        raise D2eFError("pinned D2e-E source SHA mismatch")
    spec = importlib.util.spec_from_file_location("d2ef_locked_e", path)
    if spec is None or spec.loader is None:
        raise D2eFError("cannot import D2e-E source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SOURCE_SHA256 != SOURCE_SHA256 or module.CLAIMS["physical_provider_admitted"] is not False:
        raise D2eFError("D2e-E source identity or physics authority changed")
    return module


def one_lens(row, anchor, gate, e, d2c):
    import numpy as np
    from solv.baryons import J2141BaryonicModel
    from solv.cosmology import FlatLCDM
    from solv.dmalane import epsilon_from_config, build_gate_components
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.shadow_density import compute_shadow_density

    lens = str(row["lens_id"])
    if lens not in LENS_IDS:
        raise D2eFError("unregistered historical fitted development lens")
    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10 ** float(row["logM_bulge_chabrier_central"])
    dm = 10 ** float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"]) * scale
    dre = float(row["Re_disc_arcsec"]) * scale
    qb = float(row["q_bulge"])
    qd = float(row["q_disc"])
    if min(scale, bm, dm, bre, dre, qb, qd) <= 0:
        raise D2eFError("invalid frozen baryonic/gate input")
    root = float(e._load_d2e_d()._load_d2e_a().D2D_REFERENCE_ROOT_KPC[lens])
    rlo = root * (1 - GUARD_FRACTION)
    rhi = root * (1 + GUARD_FRACTION)
    if not DOMAIN[0] < rlo < root < rhi < DOMAIN[1]:
        raise D2eFError("invalid registered finite root guard")
    model = J2141BaryonicModel(bm, bre, dm, dre)
    features = extract_gate_features_from_values(
        bm, bre, dm, dre, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    components = build_gate_components(gate, features=features, anchor=anchor)
    method = components.get("shadow_density_method", "mass_difference_gradient")
    if method != "mass_difference_gradient":
        raise D2eFError("source density method unexpectedly changed")
    radii = np.linspace(*DOMAIN, RADIAL_POINTS)
    gbar = model.total_vbar(radii)**2 / radii
    epsilon = epsilon_from_config(radii, gbar, gate, features=features, anchor=anchor)
    if not np.isfinite(epsilon).all() or np.min(epsilon) <= 0:
        raise D2eFError("invalid historical source epsilon")
    rho = compute_shadow_density(
        radii, gbar, gbar/epsilon, epsilon=epsilon, method=method,
    )
    if not np.isfinite(rho).all() or np.min(rho) < 0:
        raise D2eFError("invalid exact-binary64 shadow density nodal inputs")

    bul_lo = float(d2c.reference_bulge_finite(rlo, bm, bre))
    bul_hi = float(d2c.reference_bulge_finite(rhi, bm, bre))
    dis_lo = float(d2c.reference_periodic_disk(rlo, dm, dre, qd, ntheta=1024))
    dis_hi = float(d2c.reference_periodic_disk(rhi, dm, dre, qd, ntheta=1024))
    if not (0 < bul_lo <= bul_hi and 0 < dis_lo <= dis_hi):
        raise D2eFError("baryonic floating endpoint mass monotonicity violated")
    corners = frozen_baryonic_q_corners(
        bul_lo, bul_hi, dis_lo, dis_hi, qb, qd,
    )
    aperture_range = conditional_aperture_band(rlo, rhi, corners)
    shadow = certified_shadow_mass_band(
        radii, rho, aperture_range["aperture_min_kpc"],
        aperture_range["aperture_max_kpc"],
    )
    sigma_crit = float(FlatLCDM(70, 0.3).sigma_crit_msun_per_kpc2(
        float(row["z_deflector"]), float(row["z_source"]),
    ))
    conditional_residual = conditional_normalized_root_residual_band(
        rlo, rhi, bul_lo, bul_hi, dis_lo, dis_hi,
        sigma_crit, shadow,
    )
    empirical_apertures = []
    for radius, bulge, disk in ((rlo, bul_lo, dis_lo), (rhi, bul_hi, dis_hi)):
        qfloat = min(1., max(.001, (qb*bulge+qd*disk)/(bulge+disk)))
        A = min(DOMAIN[1], radius/math.sqrt(qfloat))
        empirical_apertures.append(A)
    endpoints_seen = (
        aperture_range["aperture_min_kpc"] <= empirical_apertures[0] and
        empirical_apertures[1] <= aperture_range["aperture_max_kpc"]
    )
    return {
        "lens_id": lens,
        "fitted_development_lens_only": True,
        "d2d_pinned_root_kpc": root,
        "guard_radius_kpc": [rlo, rhi],
        "frozen_endpoint_baryonic_msun": {
            "bulge": [bul_lo, bul_hi], "disc": [dis_lo, dis_hi],
        },
        "frozen_spherical_qeff_axis_factors": [qb, qd],
        "frozen_endpoint_qeff_corners": corners,
        "conditional_effective_aperture_range": aperture_range,
        "source_float_apertures_at_guard_endpoints_kpc": empirical_apertures,
        "both_float_endpoint_apertures_within_conditional_range": endpoints_seen,
        "certified_finite_discrete_shadow_mass_aperture_band": shadow,
        "conditional_normalized_root_residual_guard": conditional_residual,
        "all_radius_baryonic_qeff_interval_certified": False,
        "global_root_uniqueness_certified": False,
    }


def execute(source_root: str | Path) -> dict:
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    original_root = Path(source_root)
    if original_root.is_symlink() or not original_root.is_dir():
        raise D2eFError("original March source absent or symlinked")
    trust = verify_hist001_source(original_root)
    if trust["source_lock_sha256"] != SOURCE_SHA256:
        raise D2eFError("original March source SHA changed")
    e = _load_e()
    d2c = e._load_d2e_d()._load_d2e_a()._load_pinned(
        "hist001d_d2c.py", e._load_d2e_d()._load_d2e_a().D2C_SHA256,
    )
    with TemporaryDirectory(prefix="hist001d_d2e_f_source_lock_") as temp:
        copy = Path(temp) / "hist001"
        shutil.copytree(original_root, copy)
        verify_hist001_source(copy)
        pack = copy / "swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original

            data = original._load_tables(pack)
            if tuple(data.lens_id) != LENS_IDS:
                raise D2eFError("historical fitted lens sample identity changed")
            anchor, _ = original._build_anchor(pack)
            gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
            regression = original.evaluate_portability_dataframe(
                pack, gate, gate_label=CANDIDATE,
            )
            if sum(bool(x) for x in regression.both_pass) != 6:
                raise D2eFError("original fitted 180/120 6/6 regression changed")
            lenses = [
                one_lens(row, anchor, gate, e, d2c)
                for row in data.to_dict("records")
            ]
        verify_hist001_source(copy)
    verify_hist001_source(original_root)
    return {
        "schema": SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2e_e_dependency_sha256": D2E_E_SHA256,
        "historical_candidate": CANDIDATE,
        "frozen_historical_fitted_pass_count": 6,
        "distinct_independent_d2d_finite_source_pass_count": 3,
        "development_lens_ids": list(LENS_IDS),
        "radial_shadow_source_points": RADIAL_POINTS,
        "source_finite_domain_kpc": list(DOMAIN),
        "root_guard_fraction": GUARD_FRACTION,
        "certified_discrete_shadow_aperture_bands": len(lenses),
        "endpoint_targets_met_bands": sum(
            x["certified_finite_discrete_shadow_mass_aperture_band"][
                "both_endpoint_precision_targets_met"
            ] for x in lenses
        ),
        "conditional_residual_guard_dispositions": {
            "POSITIVE_UNDER_INPUT_ASSUMPTION": sum(
                x["conditional_normalized_root_residual_guard"][
                    "conditional_sign"
                ] == "POSITIVE_UNDER_INPUT_ASSUMPTION" for x in lenses
            ),
            "NEGATIVE_UNDER_INPUT_ASSUMPTION": sum(
                x["conditional_normalized_root_residual_guard"][
                    "conditional_sign"
                ] == "NEGATIVE_UNDER_INPUT_ASSUMPTION" for x in lenses
            ),
            "ZERO_NOT_EXCLUDED_UNDER_INPUT_ASSUMPTION": sum(
                x["conditional_normalized_root_residual_guard"][
                    "conditional_sign"
                ] == "ZERO_NOT_EXCLUDED_UNDER_INPUT_ASSUMPTION" for x in lenses
            ),
        },
        "lenses": lenses,
        "claims": dict(CLAIMS),
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "pandas": pd.__version__, "scipy": scipy.__version__,
        },
        "limitations": (
            "Exact nonnegative binary64 nodal finite shadow integral is enclosed "
            "for every aperture in each reported A band. Conditional R/q map "
            "depends on UNPROVED continuous baryonic endpoint mass bounds; "
            "critical density is frozen binary64. No all-R model root theorem, "
            "density continuum error, physical continuation beyond 120 kpc, "
            "same-sourced Weyl metric, independent holdout or Native v1.7.2 transport."
        ),
    }


def run(source_root: str | Path, out: str | Path):
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.shadow_aperture_intervals as kernel

    source, target = Path(source_root), Path(out)
    if source.is_symlink() or target.is_symlink() or target.exists():
        raise D2eFError("unsafe source symlink or existing output")
    if target.resolve() == source.resolve() or target.resolve().is_relative_to(source.resolve()):
        raise D2eFError("cannot write report into frozen source")
    report = execute(source)
    raw_report = canonical_json(report)
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2e_e_dependency_sha256": D2E_E_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "math_module_sha256": _sha(Path(kernel.__file__).read_bytes()),
        "report_sha256": _sha(raw_report), "claims": dict(CLAIMS),
    }
    raw_receipt = canonical_json(receipt)
    target.mkdir(parents=True)
    (target/"report.json").write_bytes(raw_report)
    (target/"receipt.json").write_bytes(raw_receipt)
    (target/"receipt.sha256").write_text(_sha(raw_receipt)+"\n", encoding="ascii")
    return {
        "status": STATUS, "receipt_sha256": _sha(raw_receipt),
        "fitted_development_lenses": len(report["lenses"]),
        "certified_discrete_shadow_bands": report["certified_discrete_shadow_aperture_bands"],
        "claims": dict(CLAIMS),
    }


def verify(receipt_path: str | Path, source_root: str | Path, expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.shadow_aperture_intervals as kernel

    path = Path(receipt_path)
    if path.name != "receipt.json" or path.is_symlink() or path.parent.is_symlink():
        raise D2eFError("unsafe receipt path")
    members = list(path.parent.iterdir())
    if ({p.name for p in members} != {"report.json", "receipt.json", "receipt.sha256"}
            or any(p.is_symlink() or not p.is_file() for p in members)):
        raise D2eFError("unexpected receipt inventory")
    payload = path.read_bytes()
    digest = _sha(payload)
    if expected_sha256 is not None and expected_sha256 != digest:
        raise D2eFError("external receipt SHA mismatch")
    if (path.parent/"receipt.sha256").read_text(encoding="ascii") != digest+"\n":
        raise D2eFError("receipt SHA sidecar mismatch")
    report_raw = (path.parent/"report.json").read_bytes()
    receipt, report = strict_loads(payload), strict_loads(report_raw)
    if canonical_json(receipt) != payload or canonical_json(report) != report_raw:
        raise D2eFError("noncanonical source numerical evidence")
    expected = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2e_e_dependency_sha256": D2E_E_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "math_module_sha256": _sha(Path(kernel.__file__).read_bytes()),
        "report_sha256": _sha(report_raw), "claims": dict(CLAIMS),
    }
    if receipt != expected or report.get("schema") != SCHEMA or report.get("claims") != CLAIMS:
        raise D2eFError("source receipt provenance or scientific claim forgery")
    replay = execute(source_root)
    try:
        _load_e()._load_d2e_d()._load_d2e_a()._compare(report, replay)
    except ValueError as exc:
        raise D2eFError("independent source reexecution value mismatch") from exc
    return {
        "status": "D2E_F_SOURCE_REEXECUTION_DISCRETE_SHADOW_BAND_PASS_CONDITIONAL_ROOT",
        "receipt_sha256": digest,
        "lenses": len(replay["lenses"]),
        "certified_discrete_shadow_bands": replay["certified_discrete_shadow_aperture_bands"],
        "root_uniqueness_certified": False,
        "claims": dict(CLAIMS),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out", type=Path)
    action.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        result = (
            verify(args.verify, args.source_root, args.expected_sha256)
            if args.verify else run(args.source_root, args.out)
        )
    except (OSError, ValueError, KeyError, TypeError, ImportError, AssertionError) as exc:
        print(json.dumps({"status": "D2E_F_FAIL_CLOSED", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
