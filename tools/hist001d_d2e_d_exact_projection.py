"""D2e-D: source-locked EXACT-RATIONAL finite shadow projection enclosures.

Narrow result: exact dyadic-nodal piecewise-linear shadow cylinder integral at
five fixed effective apertures for six previously FITTED development lenses.
The enclosing interval is not a physical error bar, an all-R/root uniqueness
result, or a bound on upstream epsilon, baryonic q, or radial continuation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from native_eset.numerics.exact_shadow_bounds import (
    enclose_finite_cylinder_mass, guaranteed_pointwise_error,
)

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
D2E_A_SHA256 = "ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
RADIAL_POINTS = 11520
DOMAIN = (0.02, 120.0)
DECIMAL_PRECISION = 70
SQRT_INTEGER_BITS = 88
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
RADIUS_LABELS = ("source_observed_radius", "d2d_11520_root", "d2d_root_minus_2pct",
                 "d2d_root_plus_2pct", "inner_0p1kpc")
SCHEMA = "NATIVE_ESET_HIST001D_D2E_D_EXACT_SHADOW_POINTWISE_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_D_EXACT_SHADOW_RECEIPT_V1"
STATUS = "D2E_D_SOURCE_DISCRETE_SHADOW_POINTWISE_ENCLOSURE_NOT_ROOT_CERTIFICATION"
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "frozen_source_density_grid_points": RADIAL_POINTS,
    "shadow_piecewise_linear_pointwise_enclosed": True,
    "input_nodal_and_aperture_values_exact_binary64": True,
    "shadow_3d_density_continuum_error_bounded": False,
    "baryonic_or_qeff_numerical_error_bounded": False,
    "root_uniqueness_mathematically_certified": False,
    "global_error_bound_established": False,
    "old_d2e_b_mass_assumption_proved": False,
    "mass_outside_finite_domain_bounded": False,
    "physical_provider_admitted": False,
    "physical_weyl_lensing_derived": False,
    "native_v172_equivalence_proved": False,
    "new_holdout_scored": False,
    "canonical_theory_state_mutated": False,
    "original_source_modified": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class D2eDIntegrityError(ValueError):
    """Reject source mutations, forged reports or unsupported numerical scope."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_d2e_a():
    path = Path(__file__).resolve().with_name("hist001d_d2e.py")
    if (not path.is_file() or path.is_symlink() or
            _sha(path.read_bytes()) != D2E_A_SHA256):
        raise D2eDIntegrityError("required D2e-A numerical source SHA mismatch")
    spec = importlib.util.spec_from_file_location("d2e_d_pinned_a", path)
    if spec is None or spec.loader is None:
        raise D2eDIntegrityError("unable to import pinned D2e-A")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SOURCE_SHA256 != SOURCE_SHA256 or module.CLAIMS["physical_provider_admitted"] is not False:
        raise D2eDIntegrityError("D2e-A historical source or admission scope changed")
    return module


def _points(row, root_kpc):
    scale = float(row["scale_kpc_per_arcsec"])
    observed = float(row["einstein_radius_arcsec_central"])*scale
    values = (observed, float(root_kpc), float(root_kpc)*.98, float(root_kpc)*1.02, .1)
    if any(not math.isfinite(x) or not DOMAIN[0] < x < DOMAIN[1] for x in values):
        raise D2eDIntegrityError("unregistered source/root aperture outside finite domain")
    return dict(zip(RADIUS_LABELS, values))


def one_lens(row, anchor, gate, a, d2c):
    import numpy as np
    from solv.baryons import J2141BaryonicModel
    from solv.dmalane import epsilon_from_config, build_gate_components
    from solv.gate_struct import A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values
    from solv.shadow_density import compute_shadow_density

    lid = str(row["lens_id"])
    if lid not in LENS_IDS:
        raise D2eDIntegrityError("unexpected historical fitted lens")
    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10**float(row["logM_bulge_chabrier_central"])
    dm = 10**float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"])*scale
    dre = float(row["Re_disc_arcsec"])*scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    model = J2141BaryonicModel(bm, bre, dm, dre)
    features = extract_gate_features_from_values(
        bm, bre, dm, dre, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    components = build_gate_components(gate, features=features, anchor=anchor)
    method = components.get("shadow_density_method", "mass_difference_gradient")
    if method != "mass_difference_gradient":
        raise D2eDIntegrityError("unregistered shadow density derivative")
    r = np.linspace(*DOMAIN, RADIAL_POINTS)
    gbar = model.total_vbar(r)**2/r
    eps = epsilon_from_config(r, gbar, gate, features=features, anchor=anchor)
    if not np.isfinite(eps).all() or np.min(eps) <= 0:
        raise D2eDIntegrityError("nonfinite or nonpositive historical epsilon")
    rho = compute_shadow_density(r, gbar, gbar/eps, epsilon=eps, method=method)
    if not np.isfinite(rho).all() or np.min(rho) < 0:
        raise D2eDIntegrityError("invalid original sampled shadow-density array")
    records = []
    for label, R in _points(row, a.D2D_REFERENCE_ROOT_KPC[lid]).items():
        bul = d2c.reference_bulge_finite(R, bm, bre)
        disc = d2c.reference_periodic_disk(R, dm, dre, qd, ntheta=1024)
        if min(bul, disc) <= 0 or not math.isfinite(bul+disc):
            raise D2eDIntegrityError("invalid reference baryon aperture masses")
        qeff = float(np.clip((qb*bul+qd*disc)/(bul+disc), 1e-3, 1.))
        A = min(DOMAIN[1], R/math.sqrt(qeff))
        bounds = enclose_finite_cylinder_mass(
            r, rho, A, decimal_precision=DECIMAL_PRECISION,
            sqrt_bits=SQRT_INTEGER_BITS,
        )
        g24 = d2c.integrated_shadow_piecewise_linear(A, r, rho, order=24)
        g48 = d2c.integrated_shadow_piecewise_linear(A, r, rho, order=48)
        a24 = guaranteed_pointwise_error(g24, bounds)
        a48 = guaranteed_pointwise_error(g48, bounds)
        records.append({
            "radius_role": label,
            "source_trial_radius_kpc": float(R),
            "baryonic_qeff_float_source": qeff,
            "effective_shadow_aperture_kpc": float(A),
            "finite_shadow_mass_enclosure": bounds,
            "d2c_gauss24_projected_shadow_msun": g24,
            "d2c_gauss48_projected_shadow_msun": g48,
            "gauss24_pointwise_error_upper": a24,
            "gauss48_pointwise_error_upper": a48,
            "critical_scope":"EXACT_FINITE_NODAL_PIECEWISE_LINEAR_SHADOW_AT_FIXED_BINARY64_APERTURE",
        })
    return {"lens_id":lid,"historical_development_lens":True,"samples":records}


def execute(source_root: str | Path) -> dict:
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    source = Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise D2eDIntegrityError("frozen March source missing or symlinked")
    trust = verify_hist001_source(source)
    if trust["source_lock_sha256"] != SOURCE_SHA256:
        raise D2eDIntegrityError("unexpected original March source SHA")
    a = _load_d2e_a()
    d2c = a._load_pinned("hist001d_d2c.py", a.D2C_SHA256)
    with TemporaryDirectory(prefix="d2e_d_exact_shadow_") as tmp:
        copy = Path(tmp)/"hist001"
        shutil.copytree(source, copy)
        verify_hist001_source(copy)
        pack = copy/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            sample = original._load_tables(pack)
            if tuple(sample.lens_id) != LENS_IDS:
                raise D2eDIntegrityError("source-development lens row/order changed")
            anchor, _ = original._build_anchor(pack)
            gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
            historical = original.evaluate_portability_dataframe(pack, gate, gate_label=CANDIDATE)
            if sum(bool(x) for x in historical.both_pass) != 6:
                raise D2eDIntegrityError("frozen original 180/120 fitted 6/6 changed")
            lenses = [one_lens(row, anchor, gate, a, d2c)
                      for row in sample.to_dict("records")]
        verify_hist001_source(copy)
    verify_hist001_source(source)
    widths = [Decimal(s["finite_shadow_mass_enclosure"]["relative_interval_width_upper"])
              for item in lenses for s in item["samples"]]
    gauss24_errors = [Decimal(s["gauss24_pointwise_error_upper"]["relative_error_upper"])
                      for item in lenses for s in item["samples"]]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "d2e_a_source_sha256": D2E_A_SHA256,
        "d2c_integrator_sha256": a.D2C_SHA256,
        "original_fitted_setA_passes": 6,
        "separately_preserved_d2d_11520_joint_passes": 3,
        "development_lens_ids": list(LENS_IDS),
        "radial_density_points": RADIAL_POINTS,
        "finite_domain_kpc": list(DOMAIN),
        "fixed_radius_roles": list(RADIUS_LABELS),
        "pointwise_shell_enclosure_method":"EXACT_RATIONAL_POSITIVE_DENSITY_MONOTONE_KERNEL_INTEGER_ISQRT_DECIMAL_DIRECTED_PI_MACHIN",
        "gauss24_error_is_global_root_bound": False,
        "pointwise_sample_count": len(widths),
        "max_sampled_shadow_enclosure_relative_width": str(max(widths)),
        "max_sampled_gauss24_shadow_relative_error_upper": str(max(gauss24_errors)),
        "lenses": lenses,
        "claims":dict(CLAIMS),
        "environment":{"python":sys.version.split()[0],"numpy":np.__version__,
                       "pandas":pd.__version__,"scipy":scipy.__version__},
        "limitations":"Exact binary64 nodal source and fixed-aperture proof only. No bound for continuum density production, baryonic q_eff, numerical root movement, nonselected R, radial continuation, metric Weyl lensing or empirical validation.",
    }


def run(source_root: str | Path, out: str | Path) -> dict:
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.exact_shadow_bounds as proof

    source, path = Path(source_root),Path(out)
    if source.is_symlink() or path.is_symlink() or path.exists():
        raise D2eDIntegrityError("unsafe source or preexisting output destination")
    if path.resolve() == source.resolve() or path.resolve().is_relative_to(source.resolve()):
        raise D2eDIntegrityError("cannot write inside frozen original source")
    raw_report = canonical_json(execute(source))
    receipt = {
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_a_source_sha256":D2E_A_SHA256,
        "source_module_sha256":_sha(Path(__file__).read_bytes()),
        "proof_kernel_sha256":_sha(Path(proof.__file__).read_bytes()),
        "report_sha256":_sha(raw_report),"claims":dict(CLAIMS),
    }
    raw_receipt = canonical_json(receipt)
    path.mkdir(parents=True)
    (path/"report.json").write_bytes(raw_report)
    (path/"receipt.json").write_bytes(raw_receipt)
    (path/"receipt.sha256").write_text(_sha(raw_receipt)+"\n",encoding="ascii")
    return {"status":STATUS,"receipt_sha256":_sha(raw_receipt),
            "lenses":len(LENS_IDS),"apertures_per_lens":len(RADIUS_LABELS),
            "claims":dict(CLAIMS)}


def verify(receipt_path: str | Path, source_root: str | Path, expected_sha256=None) -> dict:
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.exact_shadow_bounds as proof

    path = Path(receipt_path)
    if path.is_symlink() or path.name != "receipt.json" or path.parent.is_symlink():
        raise D2eDIntegrityError("unsafe receipt root")
    members = list(path.parent.iterdir())
    if {x.name for x in members}!={"report.json","receipt.json","receipt.sha256"} or any(
        x.is_symlink() or not x.is_file() for x in members
    ):
        raise D2eDIntegrityError("receipt inventory mismatch")
    raw = path.read_bytes()
    actual_sha = _sha(raw)
    if expected_sha256 is not None and expected_sha256 != actual_sha:
        raise D2eDIntegrityError("externally supplied receipt SHA mismatch")
    if (path.parent/"receipt.sha256").read_text(encoding="ascii") != actual_sha+"\n":
        raise D2eDIntegrityError("receipt SHA sidecar differs")
    payload = (path.parent/"report.json").read_bytes()
    receipt, report = strict_loads(raw),strict_loads(payload)
    if canonical_json(receipt) != raw or canonical_json(report) != payload:
        raise D2eDIntegrityError("noncanonical numerical receipt JSON")
    required={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_a_source_sha256":D2E_A_SHA256,
        "source_module_sha256":_sha(Path(__file__).read_bytes()),
        "proof_kernel_sha256":_sha(Path(proof.__file__).read_bytes()),
        "report_sha256":_sha(payload),"claims":dict(CLAIMS),
    }
    if receipt != required or report.get("schema")!=SCHEMA or report.get("claims")!=CLAIMS:
        raise D2eDIntegrityError("receipt claim, provenance or hash forgery")
    expected_report=execute(source_root)
    try:
        _load_d2e_a()._compare(report,expected_report)
    except ValueError as exc:
        raise D2eDIntegrityError("independent source numerical reexecution differs") from exc
    return {"status":"D2E_D_EXACT_NODAL_SHADOW_SOURCE_REEXECUTION_PASS_NO_PHYSICAL_ADMISSION",
            "receipt_sha256":actual_sha,"samples":expected_report["pointwise_sample_count"],
            "claims":dict(CLAIMS)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",type=Path,required=True)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out",type=Path)
    action.add_argument("--verify",type=Path)
    parser.add_argument("--expected-sha256")
    args=parser.parse_args()
    try:
        result=verify(args.verify,args.source_root,args.expected_sha256) if args.verify else run(
            args.source_root,args.out,
        )
    except (OSError,ValueError,KeyError,TypeError,ImportError,AssertionError) as exc:
        print(json.dumps({"status":"D2E_D_FAIL_CLOSED","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
