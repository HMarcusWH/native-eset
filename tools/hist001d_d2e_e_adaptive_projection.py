"""HIST-001D/D2e-E: source-locked adaptive finite-discrete shadow mass enclosures.

Certified relative WIDTH of exact-nodal, piecewise-linear cylindrical shadow
mass at six D2d roots and six observed fitted development apertures, only.
No baryonic/q_eff, source-density discretization, all-R root uniqueness,
physical radial continuation, Weyl-lensing or empirical certification.
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

from native_eset.numerics.adaptive_shadow_bounds import (
    TARGET_RELATIVE_WIDTH,
    MAX_REFINEMENT_SPLITS,
    enclose_adaptive_convex_shadow,
)
from native_eset.numerics.exact_shadow_bounds import (
    enclose_finite_cylinder_mass,
    guaranteed_pointwise_error,
)

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
D2E_D_SHA256 = "bf8e7f5fca71d45224ed8f123de600a525c9360dab823b0183b9b82a460e53e5"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = ("J0822+1828", "J0915+4211", "J0930+2855",
            "J1021+2028", "J1111+2234", "J1135+3720")
RADIAL_POINTS = 11520
DOMAIN = (0.02,120.)
RADIUS_ROLES = ("fitted_observed_einstein_radius","independent_d2d_11520_root")
SCHEMA = "NATIVE_ESET_HIST001D_D2E_E_ADAPTIVE_CERTIFIED_NODAL_SHADOW_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_E_RECEIPT_V1"
STATUS = "HIST001D_D2E_E_NODAL_SHADOW_ADAPTIVE_POINTWISE_ONLY_NO_ROOT_THEOREM"
CLAIMS = {
    "historical_fitted_development_regression_only":True,
    "source_input_sha_verified":True,
    "source_exact_nodal_shadow_enclosure":True,
    "old_discrete_shadow_monotone_bound_retained":True,
    "rigorous_pointwise_quadrature_bound":True,
    "source_gradient_continuum_error_bounded":False,
    "baryonic_qeff_numerical_error_bounded":False,
    "d2e_b_all_radius_mass_assumption_proved":False,
    "global_error_bound_established":False,
    "root_uniqueness_mathematically_certified":False,
    "mass_outside_finite_domain_bounded":False,
    "physical_weyl_lensing_derived":False,
    "physical_provider_admitted":False,
    "native_v172_equivalence_proved":False,
    "new_holdout_scored":False,
    "canonical_theory_state_mutated":False,
    "original_source_modified":False,
    "empirical_validation":"NOT_ESTABLISHED",
}


class D2eEError(ValueError):
    """Untrusted source, malformed numerical identity, or forged receipt."""


def _sha(raw:bytes)->str:
    return hashlib.sha256(raw).hexdigest()


def _load_d2e_d():
    path=Path(__file__).resolve().with_name("hist001d_d2e_d_exact_projection.py")
    if path.is_symlink() or not path.is_file() or _sha(path.read_bytes())!=D2E_D_SHA256:
        raise D2eEError("pinned D2e-D source SHA changed")
    spec=importlib.util.spec_from_file_location("hist001d_d2e_e_locked_d",path)
    if spec is None or spec.loader is None:
        raise D2eEError("cannot load D2e-D exact-shadow reference")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SOURCE_SHA256!=SOURCE_SHA256 or module.CLAIMS["physical_provider_admitted"] is not False:
        raise D2eEError("D2e-D original source or scientific status changed")
    return module


def one_lens(row,anchor,gate,d,d2c):
    import numpy as np
    from solv.baryons import J2141BaryonicModel
    from solv.dmalane import epsilon_from_config,build_gate_components
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.shadow_density import compute_shadow_density

    lid=str(row["lens_id"])
    if lid not in LENS_IDS:
        raise D2eEError("unapproved historical development lens")
    scale=float(row["scale_kpc_per_arcsec"])
    bm=10**float(row["logM_bulge_chabrier_central"])
    dm=10**float(row["logM_disc_chabrier_central"])
    bre=float(row["Re_bulge_arcsec"])*scale
    dre=float(row["Re_disc_arcsec"])*scale
    qb,qd=float(row["q_bulge"]),float(row["q_disc"])
    if min(scale,bm,dm,bre,dre,qb,qd) <= 0:
        raise D2eEError("invalid frozen historical input")

    model=J2141BaryonicModel(bm,bre,dm,dre)
    features=extract_gate_features_from_values(
        bm,bre,dm,dre,qb,qd,
        ra0_kpc=compute_transition_radius_kpc(model,a0_mps2=A0_MPS2),
    )
    components=build_gate_components(gate,features=features,anchor=anchor)
    method=components.get("shadow_density_method","mass_difference_gradient")
    if method!="mass_difference_gradient":
        raise D2eEError("unregistered source density method")
    radii=np.linspace(*DOMAIN,RADIAL_POINTS)
    gbar=model.total_vbar(radii)**2/radii
    eps=epsilon_from_config(radii,gbar,gate,features=features,anchor=anchor)
    if not np.isfinite(eps).all() or np.min(eps) <= 0:
        raise D2eEError("invalid historical epsilon source")
    rho=compute_shadow_density(radii,gbar,gbar/eps,epsilon=eps,method=method)
    if not np.isfinite(rho).all() or np.min(rho) < 0:
        raise D2eEError("nonfinite or negative original shadow array")

    observed=float(row["einstein_radius_arcsec_central"])*scale
    root=float(d._load_d2e_a().D2D_REFERENCE_ROOT_KPC[lid])
    trial=(observed,root)
    sample=[]
    for label,R in zip(RADIUS_ROLES,trial):
        if not (DOMAIN[0] < R < DOMAIN[1]):
            raise D2eEError("trial radius outside frozen finite domain")
        bul=d2c.reference_bulge_finite(R,bm,bre)
        disk=d2c.reference_periodic_disk(R,dm,dre,qd,ntheta=1024)
        if min(bul,disk)<=0 or not math.isfinite(bul+disk):
            raise D2eEError("nonfinite baryonic aperture")
        qeff=float(np.clip((qb*bul+qd*disk)/(bul+disk),1e-3,1.))
        aperture=min(DOMAIN[1],R/math.sqrt(qeff))
        original=enclose_finite_cylinder_mass(radii,rho,aperture)
        refined=enclose_adaptive_convex_shadow(
            radii,rho,aperture,
            target_relative_width=TARGET_RELATIVE_WIDTH,
            max_refinement_splits=MAX_REFINEMENT_SPLITS,
        )
        # Both independently bounded results must be compatible: the new
        # mathematically stronger interval must stay INSIDE the old interval.
        if (Decimal(refined["lower_msun"])<Decimal(original["lower_msun"]) or
                Decimal(refined["upper_msun"])>Decimal(original["upper_msun"])):
            raise D2eEError("new convex enclosure escaped previous exact bound")
        gauss24=d2c.integrated_shadow_piecewise_linear(aperture,radii,rho,order=24)
        gauss48=d2c.integrated_shadow_piecewise_linear(aperture,radii,rho,order=48)
        sample.append({
            "radius_role":label,
            "trial_radius_kpc":R,
            "baryonic_qeff_approx_from_frozen_source":qeff,
            "effective_shadow_aperture_kpc":aperture,
            "prior_monotone_shell_bound":original,
            "new_adaptive_convex_bound":refined,
            "d2c_gauss24_msun":gauss24,
            "d2c_gauss48_msun":gauss48,
            "gauss24_pointwise_discrete_error_upper":guaranteed_pointwise_error(gauss24,refined),
            "gauss48_pointwise_discrete_error_upper":guaranteed_pointwise_error(gauss48,refined),
        })
    return {"lens_id":lid,"fitted_development_lens":True,"samples":sample,
            "both_nodal_discrete_targets_met":all(
                s["new_adaptive_convex_bound"]["target_met"] for s in sample,
            )}


def execute(source_root:str|Path)->dict:
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source
    root=Path(source_root)
    if root.is_symlink() or not root.is_dir():
        raise D2eEError("frozen original source root missing or symlinked")
    trust=verify_hist001_source(root)
    if trust["source_lock_sha256"]!=SOURCE_SHA256:
        raise D2eEError("unexpected historical SHA identity")
    d=_load_d2e_d()
    a=d._load_d2e_a()
    d2c=a._load_pinned("hist001d_d2c.py",a.D2C_SHA256)
    with TemporaryDirectory(prefix="d2e_e_source_exact_") as tmp:
        copy=Path(tmp)/"hist001"
        shutil.copytree(root,copy)
        verify_hist001_source(copy)
        pack=copy/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            source=original._load_tables(pack)
            if tuple(source.lens_id)!=LENS_IDS:
                raise D2eEError("historical Set A sample membership changed")
            anchor,_=original._build_anchor(pack)
            gate=original._candidate_gate_config(anchor,candidate_name=CANDIDATE)
            archive=original.evaluate_portability_dataframe(pack,gate,gate_label=CANDIDATE)
            if sum(bool(x) for x in archive.both_pass)!=6:
                raise D2eEError("original 180/120 historical fitted 6/6 changed")
            lenses=[one_lens(row,anchor,gate,d,d2c) for row in source.to_dict("records")]
        verify_hist001_source(copy)
    verify_hist001_source(root)
    all_samples=[s for x in lenses for s in x["samples"]]
    return {
        "schema":SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_d_dependency_sha256":D2E_D_SHA256,
        "source_lenses":list(LENS_IDS),
        "original_historical_fitted_joint_passes":6,
        "separate_independent_d2d_joint_passes":3,
        "source_density_grid_points":RADIAL_POINTS,
        "source_finite_domain_kpc":list(DOMAIN),
        "trial_radius_roles":list(RADIUS_ROLES),
        "precision_target_relative_width":TARGET_RELATIVE_WIDTH,
        "adaptive_max_refinement_splits":MAX_REFINEMENT_SPLITS,
        "original_source_fitted_development_lenses_only":True,
        "fixed_aperture_count":len(all_samples),
        "fixed_aperture_target_met_count":sum(
            s["new_adaptive_convex_bound"]["target_met"] for s in all_samples,
        ),
        "maximum_achieved_relative_interval_width_upper":str(max(
            Decimal(s["new_adaptive_convex_bound"]["relative_interval_width_upper"])
            for s in all_samples
        )),
        "maximum_gauss24_relative_error_upper":str(max(
            Decimal(s["gauss24_pointwise_discrete_error_upper"]["relative_error_upper"])
            for s in all_samples
        )),
        "lenses":lenses,
        "claims":dict(CLAIMS),
        "environment":{"python":sys.version.split()[0],"numpy":np.__version__,
                       "pandas":pd.__version__,"scipy":scipy.__version__},
        "limitations":"Nodal binary64 piecewise-linear shadow only at 12 selected apertures. No all-R source law/derivative convergence, baryon qeff error, missing exterior density, guaranteed roots, physical Weyl lensing, survey covariance or blinded validation.",
    }


def run(source_root:str|Path,out:str|Path)->dict:
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.adaptive_shadow_bounds as kernel
    source,destination=Path(source_root),Path(out)
    if source.is_symlink() or destination.is_symlink() or destination.exists():
        raise D2eEError("unsafe or existing original/result path")
    if destination.resolve()==source.resolve() or destination.resolve().is_relative_to(source.resolve()):
        raise D2eEError("cannot write into frozen original source")
    report=execute(source)
    payload=canonical_json(report)
    receipt={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_d_dependency_sha256":D2E_D_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "adaptive_kernel_sha256":_sha(Path(kernel.__file__).read_bytes()),
        "report_sha256":_sha(payload),"claims":dict(CLAIMS),
    }
    raw=canonical_json(receipt)
    destination.mkdir(parents=True)
    (destination/"report.json").write_bytes(payload)
    (destination/"receipt.json").write_bytes(raw)
    (destination/"receipt.sha256").write_text(_sha(raw)+"\n",encoding="ascii")
    return {"status":STATUS,"receipt_sha256":_sha(raw),
            "fixed_aperture_count":report["fixed_aperture_count"],
            "target_met_count":report["fixed_aperture_target_met_count"],
            "claims":dict(CLAIMS)}


def verify(receipt_path:str|Path,source_root:str|Path,expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.adaptive_shadow_bounds as kernel

    path=Path(receipt_path)
    if path.name!="receipt.json" or path.is_symlink() or path.parent.is_symlink():
        raise D2eEError("unsafe receipt path")
    items=list(path.parent.iterdir())
    if {p.name for p in items}!={"report.json","receipt.json","receipt.sha256"} or any(
        p.is_symlink() or not p.is_file() for p in items
    ):
        raise D2eEError("unexpected receipt members")
    raw=path.read_bytes()
    sha=_sha(raw)
    if expected_sha256 is not None and expected_sha256!=sha:
        raise D2eEError("independent external receipt SHA mismatch")
    if (path.parent/"receipt.sha256").read_text(encoding="ascii")!=sha+"\n":
        raise D2eEError("receipt SHA sidecar mismatch")
    payload=(path.parent/"report.json").read_bytes()
    receipt,report=strict_loads(raw),strict_loads(payload)
    if canonical_json(receipt)!=raw or canonical_json(report)!=payload:
        raise D2eEError("noncanonical JSON report/receipt")
    expected={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_d_dependency_sha256":D2E_D_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "adaptive_kernel_sha256":_sha(Path(kernel.__file__).read_bytes()),
        "report_sha256":_sha(payload),"claims":dict(CLAIMS),
    }
    if (receipt!=expected or report.get("schema")!=SCHEMA or
            report.get("status")!=STATUS or report.get("claims")!=CLAIMS):
        raise D2eEError("receipt or scientific-claim forgery")
    replay=execute(source_root)
    try:
        _load_d2e_d()._load_d2e_a()._compare(report,replay)
    except ValueError as exc:
        raise D2eEError("independent source reexecution differs") from exc
    return {"status":"D2E_E_SOURCE_REEXECUTION_POINTWISE_DISCRETE_BOUNDS_PASS",
            "receipt_sha256":sha,"fixed_aperture_count":replay["fixed_aperture_count"],
            "target_met_count":replay["fixed_aperture_target_met_count"],
            "claims":dict(CLAIMS)}


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",type=Path,required=True)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out",type=Path)
    action.add_argument("--verify",type=Path)
    parser.add_argument("--expected-sha256")
    args=parser.parse_args()
    try:
        reply=verify(args.verify,args.source_root,args.expected_sha256) if args.verify else run(
            args.source_root,args.out,
        )
    except (OSError,ValueError,TypeError,KeyError,ImportError,AssertionError) as exc:
        print(json.dumps({"status":"D2E_E_FAIL_CLOSED","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(reply,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
