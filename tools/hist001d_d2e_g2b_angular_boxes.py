"""D2e-G2b: source-locked rigorous full-azimuth analytic disk interval report.

Six previously fitted SWELLS Set A development lenses, fixed historical
D2d +-2% root guards. A certified analytic-continuum disk band is intersected
with G2's independently rigorous coarse angular band, combined with G1's
certified finite Hernquist bulge interval, then carried into an exact-rational
analytic-continuum q_eff/aperture band.

This does NOT certify the frozen SciPy Hernquist or 1024-periodic numerical
implementation, all-R ROOT topology, Weyl lensing or any new observation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from native_eset.numerics.certified_disk_angular import (
    MESH_MIDPOINTS, TARGET_RELATIVE_WIDTH,
    certified_periodic_exponential_disk_radius_band,
)
from native_eset.numerics.shadow_aperture_intervals import (
    conditional_aperture_band,
    frozen_baryonic_q_corners,
)

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
G1G2_SHA256 = "11e3dad8dd3723efc36f330720f7dda3acfa14dd1cff5b71fd91da00b97497a7"
LENS_IDS = ("J0822+1828","J0915+4211","J0930+2855",
            "J1021+2028","J1111+2234","J1135+3720")
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
SCHEMA = "NATIVE_ESET_HIST001D_D2E_G2B_CERTIFIED_FULL_AZIMUTH_ANALYTIC_DISK_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_G2B_RECEIPT_V1"
STATUS = "HIST001D_G2B_ANALYTIC_DISK_CERTIFIED_NOT_SOURCE_NUMERIC_ROOT_PROOF"
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "analytic_full_azimuth_continuum_disk_enclosed": True,
    "analytic_continuum_bulge_disk_qeff_guard_enclosed": True,
    "frozen_source_numeric_periodic1024_error_bounded": False,
    "frozen_source_numeric_Hernquist_error_bounded": False,
    "frozen_source_numeric_qeff_root_map_certified": False,
    "global_root_topology_certified": False,
    "physical_provider_admitted": False,
    "physical_weyl_lensing_derived": False,
    "source_density_continuum_error_bounded": False,
    "missing_inner_outer_shadow_mass_bounded": False,
    "current_native_v172_equivalence_proved": False,
    "new_independent_holdout_scored": False,
    "original_source_mutated": False,
    "canonical_theory_state_mutated": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class G2bError(ValueError):
    """Reject source mutation, unsupported inference or forged numerical receipts."""


def _sha(raw: bytes):
    return hashlib.sha256(raw).hexdigest()


def _load_g():
    path = Path(__file__).resolve().with_name("hist001d_d2e_g_baryon_boxes.py")
    if path.is_symlink() or not path.is_file() or _sha(path.read_bytes()) != G1G2_SHA256:
        raise G2bError("source-pinned G1/G2 prerequisite changed")
    spec = importlib.util.spec_from_file_location("d2e_g2b_frozen_g", path)
    if spec is None or spec.loader is None:
        raise G2bError("cannot import frozen analytic baryon source")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    if g.SOURCE_SHA256 != SOURCE_SHA256 or g.CLAIMS["physical_provider_admitted"] is not False:
        raise G2bError("frozen source or physical permission changed")
    return g


def one_lens(row, g, f, d2c):
    lens = str(row["lens_id"])
    if lens not in LENS_IDS:
        raise G2bError("unregistered fitted Set A lens")
    baseline = g.one_lens(row, f, d2c)
    if baseline["lens_id"] != lens or not baseline["historical_fitted_development_only"]:
        raise G2bError("analytic G1/G2 lens identity mismatch")
    rlo, rhi = baseline["guard_radius_kpc"]
    params = baseline["frozen_binary64_analytic_params"]
    mass, scale, q = (
        params["disc_mass_msun"], params["disc_exponential_scale_kpc"],
        params["disc_q"],
    )
    improved = certified_periodic_exponential_disk_radius_band(
        rlo, rhi, mass, scale, q, midpoints=MESH_MIDPOINTS,
        target_relative_width=TARGET_RELATIVE_WIDTH,
    )
    coarse = baseline["certified_coarse_continuum_elliptical_disk_radius_band"]
    # Both independent analytic-continuum proofs apply to the same frozen
    # dyadic model. Their intersection is mathematically valid, regardless
    # of interval nesting or the chosen target's success.
    lo = max(Decimal(improved["lower_msun"]), Decimal(coarse["lower_msun"]))
    hi = min(Decimal(improved["upper_msun"]), Decimal(coarse["upper_msun"]))
    if not 0 < lo <= hi:
        raise G2bError("independent analytic disk proofs disjoint")
    disc_pair = [g._outward_mass(format(lo,"f"), upper=False),
                 g._outward_mass(format(hi,"f"), upper=True)]
    bulge_pair = baseline["outward_binary64_analytic_mass_envelopes"]["bulge"]
    qb = params["bulge_q"]
    corners = frozen_baryonic_q_corners(
        bulge_pair[0],bulge_pair[1],disc_pair[0],disc_pair[1],qb,q,
    )
    aperture = conditional_aperture_band(rlo,rhi,corners)
    comparisons = baseline["uncertified_historical_numerical_comparisons"]
    for item in comparisons:
        v = item["periodic1024_disc_projection_msun_UNCERTIFIED"]
        item["historical_1024_in_refined_analytic_interval_EMPIRICAL_ONLY"] = (
            disc_pair[0] <= v <= disc_pair[1]
        )
    return {
        "lens_id":lens,
        "fitted_development_only": True,
        "radius_guard_kpc":[rlo,rhi],
        "pinned_historical_D2d_root_kpc": baseline["d2d_pinned_finite_root_kpc"],
        "G1_finite_analytic_bulge_band":baseline["certified_finite_hernquist_continuum_radius_band"],
        "G2_prior_coarse_analytic_disk_band":coarse,
        "G2b_full_azimuth_midpoint_analytic_disk_band":improved,
        "rigorous_intersection_analytic_disk_band":{
            "lower_msun":format(lo,"f"),
            "upper_msun":format(hi,"f"),
            "all_radius_values_enclosed":True,
            "underlying_floating_1024_algorithm_certified":False,
        },
        "analytic_continuum_baryonic_mass_boxes":{
            "bulge":bulge_pair,"disk":disc_pair,
        },
        "analytic_continuum_exact_qeff_corners":corners,
        "analytic_continuum_conditional_aperture_band":{
            **aperture,
            "mass_box_assumption_resolved_for_mathematical_analytic_functions":True,
            "source_SciPy_1024_numeric_equivalence_NOT_ESTABLISHED":True,
        },
        "source_numerical_quadrature_comparisons":comparisons,
        "root_uniqueness_certified":False,
    }


def execute(source_root):
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    source=Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise G2bError("original March source missing or symlinked")
    if verify_hist001_source(source)["source_lock_sha256"] != SOURCE_SHA256:
        raise G2bError("original March source lock changed")
    g = _load_g()
    f = g._load_pinned_f()
    a = f._load_e()._load_d2e_d()._load_d2e_a()
    d2c = a._load_pinned("hist001d_d2c.py", a.D2C_SHA256)
    with TemporaryDirectory(prefix="hist001d_g2b_source_locked_") as temp:
        copy=Path(temp)/"hist001"
        shutil.copytree(source,copy)
        verify_hist001_source(copy)
        pack=copy/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            data=original._load_tables(pack)
            if tuple(data.lens_id)!=LENS_IDS:
                raise G2bError("fitted Set A lens member/order changed")
            anchor,_=original._build_anchor(pack)
            gate=original._candidate_gate_config(anchor,candidate_name=CANDIDATE)
            historical=original.evaluate_portability_dataframe(
                pack,gate,gate_label=CANDIDATE,
            )
            if sum(bool(x) for x in historical.both_pass)!=6:
                raise G2bError("original historical fitted 6/6 changed")
            lenses=[one_lens(row,g,f,d2c) for row in data.to_dict("records")]
        verify_hist001_source(copy)
    verify_hist001_source(source)
    samples=[s for item in lenses for s in
             item["G2b_full_azimuth_midpoint_analytic_disk_band"]["endpoints"]]
    return {
        "schema":SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "pinned_G1G2_source_sha256":G1G2_SHA256,
        "historical_fitted_SetA_6of6":6,
        "distinct_independent_finite_D2d_3of6":3,
        "historical_development_lenses":list(LENS_IDS),
        "analytic_full_azimuth_certified_guards":len(lenses),
        "fixed_angular_midpoints":MESH_MIDPOINTS,
        "predeclared_relative_interval_target":TARGET_RELATIVE_WIDTH,
        "endpoint_target_met_count":sum(bool(s["target_met"]) for s in samples),
        "total_analytic_disk_endpoints":len(samples),
        "max_endpoint_relative_interval_width":str(max(
            Decimal(s["relative_interval_width_upper"])
            for s in samples if s["relative_interval_width_upper"] is not None
        )),
        "lenses":lenses,
        "claims":dict(CLAIMS),
        "environment":{"python":sys.version.split()[0],"numpy":np.__version__,
                       "pandas":pd.__version__,"scipy":scipy.__version__},
        "limitations":"Certifies frozen exact-binary64-param analytic CONTINUUM periodic disk, not the original 1024-angle numeric output error, full source shadow continuum, source critical density, all-radius Einstein-root uniqueness, Weyl physics or independent observations.",
    }


def run(source_root,out):
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.certified_disk_angular as proof

    source,target=Path(source_root),Path(out)
    if source.is_symlink() or target.is_symlink() or target.exists():
        raise G2bError("unsafe source symlink or existing receipt target")
    if target.resolve()==source.resolve() or target.resolve().is_relative_to(source.resolve()):
        raise G2bError("cannot write into frozen historical source")
    report=execute(source)
    payload=canonical_json(report)
    receipt={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "pinned_G1G2_source_sha256":G1G2_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "angular_kernel_sha256":_sha(Path(proof.__file__).read_bytes()),
        "report_sha256":_sha(payload),"claims":dict(CLAIMS),
    }
    raw=canonical_json(receipt)
    target.mkdir(parents=True)
    (target/"report.json").write_bytes(payload)
    (target/"receipt.json").write_bytes(raw)
    (target/"receipt.sha256").write_text(_sha(raw)+"\n",encoding="ascii")
    return {"status":STATUS,"receipt_sha256":_sha(raw),
            "analytic_full_azimuth_guards":len(report["lenses"]),
            "endpoint_target_met_count":report["endpoint_target_met_count"],
            "claims":dict(CLAIMS)}


def verify(receipt_path,source_root,expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.certified_disk_angular as proof

    path=Path(receipt_path)
    if path.name!="receipt.json" or path.is_symlink() or path.parent.is_symlink():
        raise G2bError("unsafe receipt path")
    files=list(path.parent.iterdir())
    if ({f.name for f in files}!={"report.json","receipt.json","receipt.sha256"}
            or any(not f.is_file() or f.is_symlink() for f in files)):
        raise G2bError("receipt member inventory changed")
    raw=path.read_bytes()
    actual_sha=_sha(raw)
    if expected_sha256 is not None and actual_sha!=expected_sha256:
        raise G2bError("externally provided receipt SHA mismatch")
    if (path.parent/"receipt.sha256").read_text(encoding="ascii")!=actual_sha+"\n":
        raise G2bError("receipt SHA sidecar mismatch")
    report_raw=(path.parent/"report.json").read_bytes()
    receipt,report=strict_loads(raw),strict_loads(report_raw)
    if canonical_json(receipt)!=raw or canonical_json(report)!=report_raw:
        raise G2bError("noncanonical numerical evidence")
    expected={
        "schema":RECEIPT_SCHEMA,"status":STATUS,"source_lock_sha256":SOURCE_SHA256,
        "pinned_G1G2_source_sha256":G1G2_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "angular_kernel_sha256":_sha(Path(proof.__file__).read_bytes()),
        "report_sha256":_sha(report_raw),"claims":dict(CLAIMS),
    }
    if receipt!=expected or report.get("schema")!=SCHEMA or report.get("claims")!=CLAIMS:
        raise G2bError("receipt integrity or scientific-authority forgery")
    source_report=execute(source_root)
    try:
        _load_g()._load_pinned_f()._load_e()._load_d2e_d()._load_d2e_a()._compare(
            report,source_report,
        )
    except ValueError as exc:
        raise G2bError("source-reexecuted analytic interval evidence differs") from exc
    return {
        "status":"D2E_G2B_ORIGINAL_SOURCE_REEXECUTION_ANALYTIC_DISK_MIDPOINT_PASS",
        "receipt_sha256":actual_sha,
        "lenses":len(source_report["lenses"]),
        "endpoint_target_met_count":source_report["endpoint_target_met_count"],
        "claims":dict(CLAIMS),
    }


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
    except (OSError,ValueError,TypeError,KeyError,ImportError,AssertionError) as exc:
        print(json.dumps({"status":"D2E_G2B_FAIL_CLOSED","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
