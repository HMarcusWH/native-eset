"""D2e-G3a: SHA-locked a posteriori POINTWISE numerical source output bounds.

Compare the exact binary64 number RETURNED by the frozen historical D2c
bulge/disc projector at predeclared observed and D2d-root radii against
independently certified G1 Hernquist and G2b analytic exponential-disk
mass intervals. The exact-rational maximum endpoint distance is a
valid numerical discrepancy bound AT THESE SOURCE CALLS ONLY.

No global continuous-R implementation error, sigma_crit source error,
root-uniqueness theorem, original density continuum or Weyl lensing.
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
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

from native_eset.numerics.certified_baryon_mass import (
    certified_elliptical_disk_radius_band, certified_hernquist_point,
)
from native_eset.numerics.certified_disk_angular import (
    MESH_MIDPOINTS, TARGET_RELATIVE_WIDTH,
    certified_periodic_exponential_disk_point,
)
from native_eset.numerics.certified_pointwise_source_error import (
    certified_pointwise_q_error, certified_pointwise_source_error,
)
from native_eset.numerics.shadow_aperture_intervals import frozen_baryonic_q_corners

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
G2B_SHA256 = "37a502ff6e54d3ca9c2e6d49ad21338962f005f4350dfc859cc5b73ea48ec256"
LENS_IDS = ("J0822+1828", "J0915+4211", "J0930+2855",
            "J1021+2028", "J1111+2234", "J1135+3720")
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
ROLES = ("observed_fitted_einstein_radius", "independent_d2d_11520_root")
SCHEMA = "NATIVE_ESET_HIST001D_D2E_G3A_POINTWISE_SOURCE_BARYON_ERRORS_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_G3A_SOURCE_OUTPUT_RECEIPT_V1"
STATUS = "G3A_CERTIFIED_POINTWISE_SOURCE_OUTPUT_VS_ANALYTIC_MATH_NOT_ROOT"
CLAIMS = {
    "frozen_development_lenses_only": True,
    "registered_binary64_source_output_error_bounded_pointwise": True,
    "analytic_target_hernquist_finite_mass_rigorous": True,
    "analytic_target_disk_full_azimuth_rigorous": True,
    "original_source_46_plus_three_verified": True,
    "source_numerical_error_at_all_radii_certified": False,
    "original_source_continuum_shadow_error_bounded": False,
    "source_numeric_qeff_all_radii_certified": False,
    "sigma_critical_numerical_error_bounded": False,
    "root_uniqueness_certified": False,
    "total_model_error_bounded": False,
    "mass_outside_finite_domain_bounded": False,
    "new_holdout_scored": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "native_v172_equivalence_proved": False,
    "original_source_modified": False,
    "canonical_theory_state_mutated": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class G3aError(ValueError):
    """A blocked source-identity, claim-provenance or numerical-output contract."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_g2b():
    p = Path(__file__).resolve().with_name("hist001d_d2e_g2b_angular_boxes.py")
    if p.is_symlink() or not p.is_file() or _sha(p.read_bytes()) != G2B_SHA256:
        raise G3aError("source-pinned G2b mathematical prerequisite bytes changed")
    spec = importlib.util.spec_from_file_location("g3a_pinned_g2b", p)
    if spec is None or spec.loader is None:
        raise G3aError("cannot load frozen G2b mathematical source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SOURCE_SHA256 != SOURCE_SHA256 or module.CLAIMS["physical_provider_admitted"]:
        raise G3aError("G2b source or scientific permission changed")
    return module


def _analytic_disk_intersection(fine: dict, coarse: dict) -> dict:
    lo = max(Decimal(fine["lower_msun"]),Decimal(coarse["lower_msun"]))
    hi = min(Decimal(fine["upper_msun"]),Decimal(coarse["upper_msun"]))
    if not (lo.is_finite() and hi.is_finite() and 0 < lo <= hi):
        raise G3aError("two certified analytic disk mass enclosures disjoint")
    return {
        "lower_msun": format(lo,"f"),
        "upper_msun": format(hi,"f"),
        "fine_midpoint_target_met": fine["target_met"],
        "fine_midpoint_source_equivalence_proved": False,
        "analytic_continuum_target_consistent": True,
    }


def _q_fraction(pair):
    if set(pair) != {"num", "den"}:
        raise G3aError("malformed exact rational q range")
    n, d = int(pair["num"]), int(pair["den"])
    if d <= 0:
        raise G3aError("invalid exact rational denominator")
    return Fraction(n, d)


def one_lens(row, g2b, g1, d2c, d2d_roots):
    import numpy as np

    lid = str(row["lens_id"])
    if lid not in LENS_IDS:
        raise G3aError("unknown previously fitted development lens")
    scale = float(row["scale_kpc_per_arcsec"])
    mb = 10**float(row["logM_bulge_chabrier_central"])
    md = 10**float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"])*scale
    dre = float(row["Re_disc_arcsec"])*scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    if any(not math.isfinite(v) or v<=0 for v in (scale,mb,md,bre,dre,qb,qd)):
        raise G3aError("invalid original frozen source baryonic scalar")
    if not 0 < qb <= 1 or not 0 < qd <= 1:
        raise G3aError("invalid source axis-ratio convention")
    a, ds = bre/1.8153, dre/1.67835
    observed = float(row["einstein_radius_arcsec_central"])*scale
    root = float(d2d_roots[lid])
    output = []

    for role, R in zip(ROLES, (observed, root)):
        if not (.02 < R < 120.) or not math.isfinite(R):
            raise G3aError("unregistered pointwise radius outside frozen source")
        source_b = float(d2c.reference_bulge_finite(R, mb, bre))
        source_d = float(d2c.reference_periodic_disk(R, md, dre, qd, ntheta=1024))
        if min(source_b, source_d) <= 0 or not math.isfinite(source_b + source_d):
            raise G3aError("historical source returned nonpositive/nonfinite mass")

        analytic_b = certified_hernquist_point(R, mb, a)
        analytic_d_fine = certified_periodic_exponential_disk_point(
            R, md, ds, qd, midpoints=MESH_MIDPOINTS,
            target_relative_width=TARGET_RELATIVE_WIDTH,
        )
        analytic_d_coarse = certified_elliptical_disk_radius_band(R,R,md,ds,qd)
        analytic_d = _analytic_disk_intersection(analytic_d_fine,analytic_d_coarse)
        bulge_error = certified_pointwise_source_error(
            source_b,analytic_b["lower_msun"],analytic_b["upper_msun"],
        )
        disk_error = certified_pointwise_source_error(
            source_d,analytic_d["lower_msun"],analytic_d["upper_msun"],
        )
        # Outward float mass endpoints preserve the two rigorous
        # independent analytic-continuum enclosures for F's corner map.
        intervals = [
            g1._outward_mass(analytic_b["lower_msun"],upper=False),
            g1._outward_mass(analytic_b["upper_msun"],upper=True),
            g1._outward_mass(analytic_d["lower_msun"],upper=False),
            g1._outward_mass(analytic_d["upper_msun"],upper=True),
        ]
        qbox = frozen_baryonic_q_corners(*intervals,qb,qd)
        source_q = float(np.clip((qb*source_b + qd*source_d)/(source_b+source_d),.001,1.))
        q_error = certified_pointwise_q_error(
            source_q,_q_fraction(qbox["q_min"]),_q_fraction(qbox["q_max"]),
        )
        output.append({
            "radius_role":role,
            "radius_kpc_frozen_binary64":R,
            "source_returned_bulge_msun":source_b,
            "source_returned_disk_msun":source_d,
            "source_returned_qeff_binary64":source_q,
            "analytic_finite_bulge_enclosure":analytic_b,
            "analytic_full_azimuth_disk_enclosure":analytic_d_fine,
            "analytic_coarse_disk_crosscheck":analytic_d_coarse,
            "analytic_disk_intersection":analytic_d,
            "pointwise_bulge_discrepancy_proof":bulge_error,
            "pointwise_disk_discrepancy_proof":disk_error,
            "analytic_qeff_exact_corner_bounds":qbox,
            "pointwise_qeff_discrepancy_proof":q_error,
            "all_radius_source_implementation_error_bounded":False,
            "full_critical_radius_error_certified":False,
        })
    return {
        "lens_id":lid,
        "historical_fitted_development_only":True,
        "fixed_baryonic_parameters_binary64":{
            "bulge_mass_msun":mb, "finite_hernquist_a_kpc":a,
            "disc_mass_msun":md, "exponential_scale_kpc":ds,
            "bulge_q":qb,"disc_q":qd,
        },
        "points":output,
    }


def execute(source_root: str | Path):
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    root = Path(source_root)
    if root.is_symlink() or not root.is_dir():
        raise G3aError("March historical source missing or symlinked")
    if verify_hist001_source(root)["source_lock_sha256"] != SOURCE_SHA256:
        raise G3aError("March original 46+3 source SHA changed")
    g2b = _load_g2b()
    g1 = g2b._load_g()
    a = g1._load_pinned_f()._load_e()._load_d2e_d()._load_d2e_a()
    d2c = a._load_pinned("hist001d_d2c.py",a.D2C_SHA256)

    with TemporaryDirectory(prefix="hist001d_g3a_output_audit_") as temp:
        copy = Path(temp)/"hist001"
        shutil.copytree(root,copy)
        verify_hist001_source(copy)
        pack = copy/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            rows = original._load_tables(pack)
            if tuple(rows.lens_id) != LENS_IDS:
                raise G3aError("historical fitted development lens membership changed")
            anchor,_ = original._build_anchor(pack)
            gate = original._candidate_gate_config(anchor,candidate_name=CANDIDATE)
            historical = original.evaluate_portability_dataframe(
                pack,gate,gate_label=CANDIDATE,
            )
            if sum(bool(x) for x in historical.both_pass) != 6:
                raise G3aError("original 180/120 fitted historical 6/6 changed")
            lenses = [
                one_lens(row,g2b,g1,d2c,a.D2D_REFERENCE_ROOT_KPC)
                for row in rows.to_dict("records")
            ]
        verify_hist001_source(copy)
    verify_hist001_source(root)

    points = [p for l in lenses for p in l["points"]]
    return {
        "schema":SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "G2b_source_dependency_sha256":G2B_SHA256,
        "historical_original_fitted_6of6":6,
        "independent_D2d_finite_source_3of6":3,
        "six_previously_fitted_development_lens_ids":list(LENS_IDS),
        "predeclared_source_call_roles":list(ROLES),
        "registered_pointwise_bulge_disk_qeff_count":len(points),
        "G1_bulge_width_target_met_count":sum(bool(
            p["analytic_finite_bulge_enclosure"]["target_met"]
        ) for p in points),
        "G2b_disk_width_target_met_count":sum(bool(
            p["analytic_full_azimuth_disk_enclosure"]["target_met"]
        ) for p in points),
        "source_output_bulge_inside_analytic_enclosure_count":sum(bool(
            p["pointwise_bulge_discrepancy_proof"][
                "source_returned_inside_analytic_target_enclosure"
            ]
        ) for p in points),
        "source_output_disk_inside_analytic_enclosure_count":sum(bool(
            p["pointwise_disk_discrepancy_proof"][
                "source_returned_inside_analytic_target_enclosure"
            ]
        ) for p in points),
        "lenses":lenses,
        "claims":dict(CLAIMS),
        "environment":{"python":sys.version.split()[0],
                       "numpy":np.__version__,"pandas":pd.__version__,
                       "scipy":scipy.__version__},
        "limitations":"Exact dyadic a posteriori numeric-output discrepancies at 12 registered fitted development radii relative to exact-parameter analytic continuum mass models. Neither the source algorithm's general input-error theorem, future/other environment, sigma_crit, source shadow continuum nor full Einstein-root/physical Weyl is bounded.",
    }


def run(source_root: str | Path, output: str | Path):
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.certified_pointwise_source_error as helper

    source,dest=Path(source_root),Path(output)
    if source.is_symlink() or dest.is_symlink() or dest.exists():
        raise G3aError("unsafe source path or existing receipt output")
    if dest.resolve() == source.resolve() or dest.resolve().is_relative_to(source.resolve()):
        raise G3aError("cannot output to frozen original source")
    report=execute(source)
    rep_raw=canonical_json(report)
    receipt={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "G2b_source_dependency_sha256":G2B_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "pointwise_proof_helper_sha256":_sha(Path(helper.__file__).read_bytes()),
        "report_sha256":_sha(rep_raw),"claims":dict(CLAIMS),
    }
    raw=canonical_json(receipt)
    dest.mkdir(parents=True)
    (dest/"report.json").write_bytes(rep_raw)
    (dest/"receipt.json").write_bytes(raw)
    (dest/"receipt.sha256").write_text(_sha(raw)+"\n",encoding="ascii")
    return {
        "status":STATUS,
        "receipt_sha256":_sha(raw),
        "pointwise_baryon_qeff_observation_count":report["registered_pointwise_bulge_disk_qeff_count"],
        "claims":dict(CLAIMS),
    }


def verify(receipt_path: str | Path, source_root: str | Path, expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.certified_pointwise_source_error as helper

    p=Path(receipt_path)
    if p.name!="receipt.json" or p.is_symlink() or p.parent.is_symlink():
        raise G3aError("unsafe pointwise receipt path")
    files=list(p.parent.iterdir())
    if {x.name for x in files}!={"report.json","receipt.json","receipt.sha256"} or any(
        not x.is_file() or x.is_symlink() for x in files
    ):
        raise G3aError("pointwise receipt inventory not recognized")
    raw=p.read_bytes()
    digest=_sha(raw)
    if expected_sha256 is not None and digest!=expected_sha256:
        raise G3aError("externally pinned pointwise receipt SHA differs")
    if (p.parent/"receipt.sha256").read_text(encoding="ascii")!=digest+"\n":
        raise G3aError("pointwise receipt sidecar SHA differs")
    rep_raw=(p.parent/"report.json").read_bytes()
    receipt,report=strict_loads(raw),strict_loads(rep_raw)
    if canonical_json(receipt)!=raw or canonical_json(report)!=rep_raw:
        raise G3aError("noncanonical report/receipt JSON")
    required={
        "schema":RECEIPT_SCHEMA,"status":STATUS,"source_lock_sha256":SOURCE_SHA256,
        "G2b_source_dependency_sha256":G2B_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "pointwise_proof_helper_sha256":_sha(Path(helper.__file__).read_bytes()),
        "report_sha256":_sha(rep_raw),"claims":dict(CLAIMS),
    }
    if receipt != required or report.get("schema")!=SCHEMA or report.get("claims")!=CLAIMS:
        raise G3aError("forged receipt/physics/numerical provenance")
    fresh=execute(source_root)
    try:
        _load_g2b()._load_g()._load_pinned_f()._load_e()._load_d2e_d()._load_d2e_a()._compare(
            report,fresh,
        )
    except ValueError as exc:
        raise G3aError("source-reexecuted pointwise numerical discrepancy differs") from exc
    return {
        "status":"G3A_FRESH_SOURCE_REEXECUTION_POINTWISE_BARYON_DISCREPANCIES",
        "receipt_sha256":digest,
        "registered_outputs":fresh["registered_pointwise_bulge_disk_qeff_count"],
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
        result=(
            verify(args.verify,args.source_root,args.expected_sha256)
            if args.verify else run(args.source_root,args.out)
        )
    except (OSError,ValueError,KeyError,TypeError,ImportError,AssertionError) as exc:
        print(json.dumps({"status":"G3A_FAIL_CLOSED","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
