"""HIST-001D/D2e-A: sampled root topology, gradient clipping & finite-cutoff stress.

Uses the original fitted 6-lens Set A only and D2d's NEW finite-domain
structured projected-density proxy. This is NOT a rigorous root-existence /
uniqueness certificate, unbounded-domain integral, physical Weyl field, blinded
holdout, or Native ESET v1.7.2 model/provider validation.

No historical source, fit parameters, theory authority or archived results change.
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
D2C_SHA256 = "c28910af318028f72b8710ebbe61f9f31ad3727ce3daa12750fd089620e7bfa4"
D2D_SHA256 = "6253e39aeef8e7be51369ab0b0ea75e0771ead851de6ad918140c6295aa1926f"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
# Frozen numerical reference from previously source-reexecuted D2d 11520-grid
# receipt. D2e independently solves the root again against these fixed values.
D2D_REFERENCE_ROOT_KPC = {
    "J0822+1828": 1.9335521276132295,
    "J0915+4211": 1.4631260001592172,
    "J0930+2855": 4.6762553596681755,
    "J1021+2028": 1.362052753088748,
    "J1111+2234": 4.05118631644928,
    "J1135+3720": 2.3003465922369593,
}
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
SOURCE_GRID_POINTS = (180, 360, 720, 1440, 2880, 5760, 11520)
ROOT_TOPOLOGY_SCAN_POINTS = (45, 181, 721)
SHADOW_CUTOFF_KPC = (80.0, 100.0, 120.0)
DENSITY_ANCHORS_KPC = (0.1, 0.5, 2.0, 10.0, 50.0, 100.0)
FINITE_SOURCE_KPC = (0.02, 120.0)
ANGLE_STEPS = 1024
MAX_ROOT_CUTOFF_DIAGNOSTIC_SIGMA = 0.05  # engineering report line, not physics bound
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "new_numerical_execution_identity": True,
    "root_uniqueness_mathematically_certified": False,
    "global_error_bound_established": False,
    "mass_outside_finite_domain_bounded": False,
    "shadow_gradient_clipping_absent_on_tested_grids": True,
    "new_holdout_scored": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "native_v172_equivalence_proved": False,
    "empirical_validation": "NOT_ESTABLISHED",
    "canonical_theory_state_mutated": False,
    "original_source_modified": False,
}
REPORT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_A_NUMERICAL_LIMITS_REPORT_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_A_NUMERICAL_LIMITS_RECEIPT_V1"
STATUS = "HIST001D_D2E_A_BOUNDED_NUMERICAL_DIAGNOSTIC_NO_ROOT_THEOREM_NO_ADMISSION"


class D2eError(ValueError):
    """Untrusted code, invalid domain, unexpected roots, or forged results."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_pinned(name: str, digest: str):
    path = Path(__file__).resolve().with_name(name)
    if not path.is_file() or path.is_symlink() or _sha(path.read_bytes()) != digest:
        raise D2eError(f"source-bound numerical dependency changed: {name}")
    spec = importlib.util.spec_from_file_location("hist001d_d2e_dependency_" + name[:-3], path)
    if spec is None or spec.loader is None:
        raise D2eError(f"cannot import source-bound numerical dependency: {name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if getattr(mod, "SOURCE_SHA256", None) != SOURCE_SHA256:
        raise D2eError("historical source identity changed in dependency")
    return mod


def _density_audit(row: dict, anchor: dict, gate: dict, d2c):
    """Evaluate original sampled source Mshadow, derivative and clip activation."""
    import numpy as np
    from solv.baryons import J2141BaryonicModel
    from solv.constants import G_KPC_KMS2_MSUN
    from solv.dmalane import build_gate_components, epsilon_from_config
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.shadow_density import compute_shadow_density

    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10 ** float(row["logM_bulge_chabrier_central"])
    dm = 10 ** float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"]) * scale
    dre = float(row["Re_disc_arcsec"]) * scale
    qb = float(row["q_bulge"])
    qd = float(row["q_disc"])
    model = J2141BaryonicModel(bm, bre, dm, dre)
    features = extract_gate_features_from_values(
        bm, bre, dm, dre, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    components = build_gate_components(gate, features=features, anchor=anchor)
    method = components.get("shadow_density_method", "mass_difference_gradient")
    if method != "mass_difference_gradient":
        raise D2eError("different historical shadow-density derivative definition")
    source_grids = []
    for n in SOURCE_GRID_POINTS:
        radii = np.linspace(*FINITE_SOURCE_KPC, n)
        gbar = model.total_vbar(radii) ** 2 / radii
        epsilon = epsilon_from_config(
            radii, gbar, gate, features=features, anchor=anchor,
        )
        if not np.all(np.isfinite(epsilon)) or np.min(epsilon) <= 0:
            raise D2eError("invalid source epsilon")
        m_raw = ((gbar / epsilon) - gbar) * radii**2 / G_KPC_KMS2_MSUN
        m_nonnegative = np.maximum(m_raw, 0)
        gradient = np.gradient(m_nonnegative, radii)
        rho = compute_shadow_density(
            radii, gbar, gbar / epsilon, epsilon=epsilon, method=method,
        )
        if not np.all(np.isfinite(m_raw)) or not np.all(np.isfinite(rho)):
            raise D2eError("nonfinite frozen shadow density")
        source_grids.append({
            "radial_points": n,
            "negative_preclip_mshadow_count": int(np.count_nonzero(m_raw < 0)),
            "negative_preclip_dm_dr_count": int(np.count_nonzero(gradient < 0)),
            "zero_after_clip_rho_count": int(np.count_nonzero(rho == 0)),
            "min_preclip_mshadow_msun": float(np.min(m_raw)),
            "min_preclip_dm_dr_msun_per_kpc": float(np.min(gradient)),
            "sampled_source_rho_at_anchors_msun_per_kpc3": [
                float(np.interp(r, radii, rho)) for r in DENSITY_ANCHORS_KPC
            ],
            "source_rho_values_nonnegative": bool(np.min(rho) >= 0),
        })
    reference = source_grids[-1]["sampled_source_rho_at_anchors_msun_per_kpc3"]
    for record in source_grids:
        record["max_relative_rho_anchor_drift_vs_11520"] = float(max(
            abs(a-b)/max(abs(b), 1e-300)
            for a, b in zip(record["sampled_source_rho_at_anchors_msun_per_kpc3"],
                            reference)
        ))
    # Explicitly identify whether the negative-value clamps ACTUALLY activate
    # on the fixed finite radial input series. This does NOT establish global
    # positivity off the grid or for other parameter realizations.
    if any(
        v["negative_preclip_mshadow_count"] or v["negative_preclip_dm_dr_count"]
        or v["zero_after_clip_rho_count"]
        for v in source_grids
    ):
        raise D2eError("source clip activates: revise scoped clipping verdict")
    return source_grids, radii, rho, model, features, method


def _truncated_grid(radii, rho, cutoff):
    """Drop only existing outer shadow shell; no extrapolation or baryon edits."""
    import numpy as np

    if cutoff not in SHADOW_CUTOFF_KPC or not FINITE_SOURCE_KPC[0] < cutoff <= 120:
        raise D2eError("unregistered source-shadow cutoff")
    if cutoff == 120.0:
        return radii, rho
    stop = int(np.searchsorted(radii, cutoff, side="right"))
    truncated_radii = radii[:stop].copy()
    if truncated_radii[-1] < cutoff:
        truncated_radii = np.append(truncated_radii, cutoff)
    truncated_rho = np.interp(truncated_radii, radii, rho)
    return truncated_radii, truncated_rho


def _topology_for_lens(row: dict, radii, rho, d2c):
    """Three sampled scans of D2d F(R); NOT an interval root certificate."""
    import numpy as np
    from scipy.optimize import brentq
    from solv.cosmology import FlatLCDM

    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10 ** float(row["logM_bulge_chabrier_central"])
    dm = 10 ** float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"]) * scale
    dre = float(row["Re_disc_arcsec"]) * scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    err = float(row["einstein_radius_arcsec_err_plus"]) * scale
    sigma = FlatLCDM(70, 0.3).sigma_crit_msun_per_kpc2(
        float(row["z_deflector"]), float(row["z_source"]),
    )
    root_ref = D2D_REFERENCE_ROOT_KPC[str(row["lens_id"])]
    if not (FINITE_SOURCE_KPC[0] < root_ref < FINITE_SOURCE_KPC[1]
            and sigma > 0 and err > 0):
        raise D2eError("invalid D2d root or measured uncertainty")
    truncations = {cut: _truncated_grid(radii, rho, cut)
                   for cut in SHADOW_CUTOFF_KPC}

    @lru_cache(maxsize=8192)
    def baryons(R: float):
        bul = d2c.reference_bulge_finite(R, bm, bre)
        disk = d2c.reference_periodic_disk(R, dm, dre, qd, ntheta=ANGLE_STEPS)
        if not math.isfinite(bul+disk) or bul+disk <= 0:
            raise D2eError("invalid source-bound baryon projection")
        qeff = min(1., max(1e-3, (qb*bul + qd*disk)/(bul+disk)))
        return float(bul), float(disk), float(qeff)

    @lru_cache(maxsize=16384)
    def normalized_residual(R: float, order: int = 24, top: float = 120.0):
        if not FINITE_SOURCE_KPC[0] <= R <= FINITE_SOURCE_KPC[1]:
            raise D2eError("root function outside original source radial domain")
        bul, disk, q = baryons(R)
        effective = min(R / math.sqrt(q), 120.0)
        current_radii, current_rho = truncations[top]
        eff_for_source = min(effective, top)
        shadow = d2c.integrated_shadow_piecewise_linear(
            eff_for_source, current_radii, current_rho, order=order,
        )
        return float((bul+disk+shadow) / (math.pi*sigma*R*R) - 1)

    scans = []
    for count in ROOT_TOPOLOGY_SCAN_POINTS:
        grid = np.geomspace(*FINITE_SOURCE_KPC, count)
        vals = [normalized_residual(float(R)) for R in grid]
        if not all(math.isfinite(x) for x in vals):
            raise D2eError("nonfinite full finite-domain root scan")
        signs = [i for i in range(count-1) if vals[i]*vals[i+1] < 0]
        zeros = [i for i, value in enumerate(vals) if value == 0]
        if len(signs) != 1 or zeros:
            raise D2eError("sampled first-root topology does not match D2d claim")
        k = signs[0]
        scans.append({
            "radial_sample_count": count,
            "sampled_radii_kpc": [float(x) for x in grid],
            "normalized_critical_residual": vals,
            "sampled_sign_changes": len(signs),
            "sampled_exact_zeros": len(zeros),
            "positive_slope_intervals": sum(vals[i+1] > vals[i]
                                            for i in range(count-1)),
            "negative_slope_intervals": sum(vals[i+1] < vals[i]
                                            for i in range(count-1)),
            "sign_change_bracket_kpc": [float(grid[k]), float(grid[k+1])],
            "min_abs_sample_residual": min(abs(x) for x in vals),
        })
    finest_bracket = scans[-1]["sign_change_bracket_kpc"]
    root = float(brentq(normalized_residual, *finest_bracket, xtol=1e-11))
    if abs(root-root_ref)/err > 1e-7:
        raise D2eError("independent D2e dense-scan root disagrees with D2d")
    lo, hi = max(0.02, root*.9), min(120., root*1.1)
    alternate_gauss_root = float(brentq(
        lambda R: normalized_residual(R, 48), lo, hi, xtol=1e-11,
    ))
    cutoff_roots = []
    for top in SHADOW_CUTOFF_KPC:
        if top <= hi:
            raise D2eError("shadow truncation within studied root bracket")
        cut_root = float(brentq(
            lambda R: normalized_residual(R, 24, top), lo, hi, xtol=1e-11,
        ))
        cutoff_roots.append({
            "shadow_density_max_kpc": top,
            "root_kpc": cut_root,
            "root_shift_vs_full_sigma": (cut_root-root)/err,
            "new_numerical_counterfactual": top != 120.,
        })
    h = max(1e-5, root*1e-4)
    derivative = (normalized_residual(root+h)-normalized_residual(root-h))/(2*h)
    derivative_half = (normalized_residual(root+h/2)-normalized_residual(root-h/2))/h
    if not all(math.isfinite(v) for v in (derivative, derivative_half)):
        raise D2eError("nonfinite sampled root derivative")
    return {
        "shadow_cutoff_existing_domain_empirical_screen_only": all(
            abs(item["root_shift_vs_full_sigma"]) <= MAX_ROOT_CUTOFF_DIAGNOSTIC_SIGMA
            for item in cutoff_roots
        ),
        "root_from_721_scan_kpc": root,
        "d2d_11520_reference_root_kpc": root_ref,
        "root_vs_d2d_delta_sigma": (root-root_ref)/err,
        "root_gauss48_delta_sigma": (alternate_gauss_root-root)/err,
        "normalized_root_derivative_estimate_per_kpc": derivative,
        "normalized_root_derivative_halfstep_per_kpc": derivative_half,
        "relative_local_derivative_disagreement": abs(derivative-derivative_half)
        / max(abs(derivative), 1e-100),
        "scans": scans,
        "original_shadow_upper_cutoff_counterfactuals": cutoff_roots,
        "mass_beyond_120kpc_source_constrained": False,
        "global_root_uniqueness_certified": False,
    }


def one_lens(row: dict, anchor: dict, gate: dict, d2c):
    gradient, radii, rho, _, _, _ = _density_audit(row, anchor, gate, d2c)
    root_test = _topology_for_lens(row, radii, rho, d2c)
    return {
        "lens_id": str(row["lens_id"]),
        "historical_development_lens": True,
        "d2d_source_receipt_pinned_11520_root_kpc": D2D_REFERENCE_ROOT_KPC[str(row["lens_id"])],
        "gradient_clipping_and_anchor_tests": gradient,
        "sampled_root_topology": root_test,
    }


def execute(source_root: str | Path) -> dict:
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    source = Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise D2eError("original source root missing or symlinked")
    trust = verify_hist001_source(source)
    if trust["source_lock_sha256"] != SOURCE_SHA256:
        raise D2eError("original March source anchor is different")
    d2c = _load_pinned("hist001d_d2c.py", D2C_SHA256)
    _load_pinned("hist001d_d2d.py", D2D_SHA256)  # provenance pin; numerical root independently solved below
    with TemporaryDirectory(prefix="hist001d_d2e_readonly_") as temporary:
        target = Path(temporary) / "hist001"
        shutil.copytree(source, target)
        verify_hist001_source(target)
        pack = target / "swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original

            seta = original._load_tables(pack)
            if tuple(seta.lens_id) != LENS_IDS:
                raise D2eError("original fitted Set A lens identifiers changed")
            anchor, _ = original._build_anchor(pack)
            gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
            archived = original.evaluate_portability_dataframe(
                pack, gate, gate_label=CANDIDATE,
            )
            if sum(bool(v) for v in archived.both_pass) != 6:
                raise D2eError("original 180/120 6-of-6 regression did not reproduce")
            lenses = [one_lens(row, anchor, gate, d2c)
                      for row in seta.to_dict("records")]
        verify_hist001_source(target)
    verify_hist001_source(source)
    return {
        "schema": REPORT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2c_sha256": D2C_SHA256, "d2d_sha256": D2D_SHA256,
        "original_historical_model": CANDIDATE,
        "original_historical_fitted_180_120_passes": 6,
        "source_density_grids": list(SOURCE_GRID_POINTS),
        "root_topology_scan_sizes": list(ROOT_TOPOLOGY_SCAN_POINTS),
        "finite_original_source_domain_kpc": list(FINITE_SOURCE_KPC),
        "shadow_cutoff_stress_kpc": list(SHADOW_CUTOFF_KPC),
        "density_anchor_radii_kpc": list(DENSITY_ANCHORS_KPC),
        "study_design": "D2E_A_EXPLORATORY_NUMERICAL_STRESS_NOT_EXTERNAL_PREREGISTRATION",
        "root_topology_verdict": (
            "ONE_SIGN_CHANGE_AT_TESTED_SAMPLE_DENSITIES_ONLY;"
            "NO_INTERVAL_ENCLOSURE_OR_GLOBAL_UNIQUENESS_THEOREM"
        ),
        "domain_verdict": "SOURCE_PROVIDES_NO_MASS_CONTINUATION_OUTSIDE_0.02_TO_120_KPC",
        "lenses": lenses, "claims": dict(CLAIMS),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "pandas": pd.__version__, "scipy": scipy.__version__},
        "limitations": (
            "Counterfactual outer-shadow cutoffs preserve fixed source baryons and do not "
            "bound unobserved mass beyond 120 kpc. Sampled signs and local finite "
            "differences are not mathematical interval/root/physical error certificates; "
            "no holdout, Weyl lensing or contemporary ESET theory transport is established."
        ),
    }


def run(source_root: str | Path, output_root: str | Path):
    from native_eset.evidence.receipts import canonical_json

    source, out = Path(source_root), Path(output_root)
    if source.is_symlink() or out.is_symlink() or out.exists():
        raise D2eError("source symlink or output destination exists")
    if out.resolve() == source.resolve() or out.resolve().is_relative_to(source.resolve()):
        raise D2eError("cannot write diagnostic inside frozen source")
    report = execute(source)
    report_raw = canonical_json(report)
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS, "report_sha256": _sha(report_raw),
        "source_lock_sha256": SOURCE_SHA256,
        "module_sha256": _sha(Path(__file__).read_bytes()),
        "d2c_sha256": D2C_SHA256, "d2d_sha256": D2D_SHA256,
        "claims": dict(CLAIMS),
    }
    receipt_raw = canonical_json(receipt)
    out.mkdir(parents=True)
    (out/"report.json").write_bytes(report_raw)
    (out/"receipt.json").write_bytes(receipt_raw)
    (out/"receipt.sha256").write_text(_sha(receipt_raw)+"\n", encoding="ascii")
    return {"status": STATUS, "output_root": str(out),
            "receipt_sha256": _sha(receipt_raw),
            "development_lenses": len(report["lenses"]),
            "scan_sizes": list(ROOT_TOPOLOGY_SCAN_POINTS),
            "claims": dict(CLAIMS)}


def _compare(actual, expected, path="report"):
    if type(actual) is not type(expected):
        raise D2eError("source-reexecution type mismatch: "+path)
    if isinstance(actual, dict):
        if actual.keys() != expected.keys():
            raise D2eError("source-reexecution object keys mismatch: "+path)
        for key in expected:
            if path == "report" and key == "environment":
                continue
            _compare(actual[key], expected[key], path+"."+str(key))
    elif isinstance(actual, list):
        if len(actual) != len(expected):
            raise D2eError("source-reexecution array length mismatch: "+path)
        for index, (a,b) in enumerate(zip(actual, expected)):
            _compare(a,b,path+"."+str(index))
    elif isinstance(actual, float):
        if not math.isfinite(actual) or not math.isfinite(expected):
            raise D2eError("source-reexecution nonfinite value: "+path)
        if not math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8):
            raise D2eError("source-reexecution value mismatch: "+path)
    elif actual != expected:
        raise D2eError("source-reexecution categorical mismatch: "+path)


def verify(receipt_file: str | Path, source_root: str | Path,
           expected_sha256: str | None = None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads

    path = Path(receipt_file)
    if path.is_symlink() or path.parent.is_symlink() or path.name != "receipt.json":
        raise D2eError("unexpected/symlinked receipt path")
    if not path.parent.is_dir():
        raise D2eError("missing receipt directory")
    members = list(path.parent.iterdir())
    if {item.name for item in members} != {"report.json","receipt.json","receipt.sha256"}:
        raise D2eError("unexpected receipt inventory")
    if any(item.is_symlink() or not item.is_file() for item in members):
        raise D2eError("unsafe receipt files")
    receipt_raw = path.read_bytes()
    digest = _sha(receipt_raw)
    if expected_sha256 is not None and expected_sha256 != digest:
        raise D2eError("externally pinned receipt digest mismatch")
    if (path.parent/"receipt.sha256").read_text(encoding="ascii") != digest+"\n":
        raise D2eError("receipt sidecar digest mismatch")
    payload = (path.parent/"report.json").read_bytes()
    receipt = strict_loads(receipt_raw)
    report = strict_loads(payload)
    if canonical_json(receipt)!=receipt_raw or canonical_json(report)!=payload:
        raise D2eError("noncanonical report/receipt JSON")
    expected_receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS, "report_sha256": _sha(payload),
        "source_lock_sha256": SOURCE_SHA256,
        "module_sha256": _sha(Path(__file__).read_bytes()),
        "d2c_sha256": D2C_SHA256, "d2d_sha256": D2D_SHA256,
        "claims": dict(CLAIMS),
    }
    if receipt != expected_receipt:
        raise D2eError("receipt integrity, provenance or claims changed")
    if report.get("schema")!=REPORT_SCHEMA or report.get("status")!=STATUS or report.get("claims")!=CLAIMS:
        raise D2eError("report authority/schema or claim forgery")
    if (report.get("source_lock_sha256")!=SOURCE_SHA256
            or report.get("d2c_sha256")!=D2C_SHA256
            or report.get("d2d_sha256")!=D2D_SHA256):
        raise D2eError("report provenance changed")
    # Reexecute everything from the exact original SHA-locked March source,
    # not just recomputing a hash chosen by the caller.
    again = execute(source_root)
    _compare(report, again)
    return {"status": "HIST001D_D2E_A_INDEPENDENT_FULL_SOURCE_REEXECUTION_PASS_NO_ADMISSION",
            "receipt_sha256": digest,
            "development_lenses_reexecuted": len(again["lenses"]),
            "scan_sizes": list(ROOT_TOPOLOGY_SCAN_POINTS),
            "root_uniqueness_certified": False,
            "unmeasured_outer_mass_bounded": False,
            "claims": dict(CLAIMS)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        result = (verify(args.verify, args.source_root, args.expected_sha256)
                  if args.verify is not None else run(args.source_root,args.out))
    except (OSError, ValueError, TypeError, KeyError, ImportError) as exc:
        print(json.dumps({"status": "HIST001D_D2E_A_FAIL_CLOSED", "error": str(exc)},
                         sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
