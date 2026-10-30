"""HIST-001D/D2e-G1/G2: frozen analytic baryonic interval-source audit.

Reconstruct source-locked six fitted development lens inputs; independently
bound the CONTINUUM finite Hernquist bulge projected mass and the analytic
elliptical exponential disk. Then enclose the continuum-model q_eff(R) over
each 2% fitted-D2d-root guard. Historical SciPy and angular quadratures
are only comparisons; their errors are not mathematically certified.

NO full source numerical root theorem, physical Weyl lensing, source
gradient continuum, outside-domain mass, heldout or v1.7.2 admission.
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
    RMIN, RMAX, G1_TARGET, G1_SPLIT_BUDGET,
    certified_hernquist_radius_band,
    certified_elliptical_disk_radius_band,
)
from native_eset.numerics.shadow_aperture_intervals import (
    _outward_float,
    frozen_baryonic_q_corners,
    conditional_aperture_band,
)

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
D2E_F_SHA256 = "8b54ab567cd049c5df97d5c596bc205e4768d4fbc5f8ee86e854a75681fce93b"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = ("J0822+1828", "J0915+4211", "J0930+2855",
            "J1021+2028", "J1111+2234", "J1135+3720")
GUARD_FRACTION = .02
SCHEMA = "NATIVE_ESET_HIST001D_D2E_G1G2_ANALYTIC_BARYON_INTERVALS_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_G1G2_BARYON_INTERVAL_RECEIPT_V1"
STATUS = "HIST001D_D2E_G1G2_CONTINUUM_BARYON_BOXES_NO_SOURCE_NUMERICAL_ROOT_THEOREM"
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "finite_continuum_hernquist_bulge_mass_enclosed": True,
    "analytic_continuum_exponential_disk_mass_coarsely_enclosed": True,
    "analytic_continuum_baryonic_qeff_interval_enclosed": True,
    "source_SciPy_bulge_quadrature_error_certified": False,
    "source_1024_angle_disk_quadrature_error_certified": False,
    "source_numerical_qeff_root_map_certified": False,
    "critical_surface_density_physical_error_bounded": False,
    "full_model_root_uniqueness_certified": False,
    "global_model_numerical_error_bound_established": False,
    "source_density_continuum_error_bounded": False,
    "mass_outside_finite_domain_bounded": False,
    "physical_provider_admitted": False,
    "physical_weyl_lensing_derived": False,
    "native_v172_equivalence_proved": False,
    "new_holdout_scored": False,
    "original_source_modified": False,
    "canonical_theory_state_mutated": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class G1G2Error(ValueError):
    """Fail closed on original source mutation, forged receipts or promotion."""


def _sha(b: bytes):
    return hashlib.sha256(b).hexdigest()


def _load_pinned_f():
    p = Path(__file__).resolve().with_name("hist001d_d2e_f_shadow_guard.py")
    if p.is_symlink() or not p.is_file() or _sha(p.read_bytes()) != D2E_F_SHA256:
        raise G1G2Error("D2e-F source runner bytes changed")
    spec = importlib.util.spec_from_file_location("g_baryon_frozen_F", p)
    if spec is None or spec.loader is None:
        raise G1G2Error("D2e-F dependency cannot be loaded")
    f = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(f)
    if f.SOURCE_SHA256 != SOURCE_SHA256 or f.CLAIMS["physical_provider_admitted"] is not False:
        raise G1G2Error("source/provenance or scientific scope changed")
    return f


def _outward_mass(value: str, *, upper: bool):
    f = Fraction(Decimal(value))
    return _outward_float(f, upper=upper)


def one_lens(row, f, d2c):
    lens = str(row["lens_id"])
    if lens not in LENS_IDS:
        raise G1G2Error("unregistered fitted development lens")

    mass_bulge = 10 ** float(row["logM_bulge_chabrier_central"])
    mass_disc = 10 ** float(row["logM_disc_chabrier_central"])
    scale = float(row["scale_kpc_per_arcsec"])
    bulge_re = float(row["Re_bulge_arcsec"])*scale
    disk_re = float(row["Re_disc_arcsec"])*scale
    qb,qd = float(row["q_bulge"]),float(row["q_disc"])
    if not all(math.isfinite(x) and x>0 for x in (
        mass_bulge,mass_disc,scale,bulge_re,disk_re,qb,qd
    )):
        raise G1G2Error("invalid frozen bulge/disc scalar")
    if not (qb<=1 and qd<=1):
        raise G1G2Error("registered source axis ratio must be <=1")
    a = bulge_re / 1.8153
    disk_scale = disk_re / 1.67835
    root = float(
        f._load_e()._load_d2e_d()._load_d2e_a().D2D_REFERENCE_ROOT_KPC[lens]
    )
    rlo, rhi = root*(1-GUARD_FRACTION),root*(1+GUARD_FRACTION)
    if not RMIN < rlo < root < rhi < RMAX:
        raise G1G2Error("source-root guard outside finite source interval")

    bulge = certified_hernquist_radius_band(
        rlo,rhi,mass_bulge,a,target_width=G1_TARGET,
        max_splits=G1_SPLIT_BUDGET,
    )
    disk = certified_elliptical_disk_radius_band(
        rlo,rhi,mass_disc,disk_scale,qd,
    )
    # Outward floats are explicitly rounded OUTWARD relative to every
    # directed Decimal rational endpoint before entering F's q corner map.
    # The source numeric evaluator itself is not promoted.
    limits = [
        _outward_mass(bulge["lower_msun"], upper=False),
        _outward_mass(bulge["upper_msun"], upper=True),
        _outward_mass(disk["lower_msun"], upper=False),
        _outward_mass(disk["upper_msun"], upper=True),
    ]
    if not 0 < limits[0] <= limits[1] and 0 < limits[2] <= limits[3]:
        raise G1G2Error("outward baryonic envelope invalid")
    q_box = frozen_baryonic_q_corners(*limits,qb,qd)
    aperture = conditional_aperture_band(rlo,rhi,q_box)
    comparisons = []
    for radius in (rlo,rhi):
        original_b = float(d2c.reference_bulge_finite(radius,mass_bulge,bulge_re))
        original_d = float(d2c.reference_periodic_disk(radius,mass_disc,disk_re,qd,ntheta=1024))
        comparisons.append({
            "radius_kpc":radius,
            "SciPy_finite_bulge_projection_msun_UNCERTIFIED":original_b,
            "periodic1024_disc_projection_msun_UNCERTIFIED":original_d,
            "bulge_within_analytic_band_empirical_only":
                limits[0] <= original_b <= limits[1],
            "disc_within_analytic_band_empirical_only":
                limits[2] <= original_d <= limits[3],
        })
    return {
        "lens_id":lens,
        "historical_fitted_development_only":True,
        "d2d_pinned_finite_root_kpc":root,
        "guard_radius_kpc":[rlo,rhi],
        "frozen_binary64_analytic_params":{
            "bulge_mass_msun":mass_bulge,"hernquist_a_kpc":a,
            "disc_mass_msun":mass_disc,"disc_exponential_scale_kpc":disk_scale,
            "bulge_q":qb,"disc_q":qd,
        },
        "certified_finite_hernquist_continuum_radius_band":bulge,
        "certified_coarse_continuum_elliptical_disk_radius_band":disk,
        "outward_binary64_analytic_mass_envelopes":{
            "bulge":[limits[0],limits[1]],"disc":[limits[2],limits[3]],
        },
        "exact_q_corners_for_analytic_continuum":q_box,
        "analytic_continuum_qeff_aperture_range":{
            **aperture,
            "mass_box_assumption_resolved_for_analytic_continuum":True,
            "source_numerical_qeff_implementation_certified":False,
        },
        "uncertified_historical_numerical_comparisons":comparisons,
        "global_finite_root_theorem":False,
    }


def execute(source_root):
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    source=Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise G1G2Error("unsafe/missing historical source root")
    if verify_hist001_source(source)["source_lock_sha256"]!=SOURCE_SHA256:
        raise G1G2Error("March 46+3 original source identity changed")
    f=_load_pinned_f()
    e=f._load_e()
    a=e._load_d2e_d()._load_d2e_a()
    d2c=a._load_pinned("hist001d_d2c.py",a.D2C_SHA256)
    with TemporaryDirectory(prefix="d2e_g_baryon_source_replay_") as tmp:
        copy=Path(tmp)/"hist001"
        shutil.copytree(source,copy)
        verify_hist001_source(copy)
        pack=copy/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            rows=original._load_tables(pack)
            if tuple(rows.lens_id)!=LENS_IDS:
                raise G1G2Error("source sample rows/order changed")
            anchor,_=original._build_anchor(pack)
            gate=original._candidate_gate_config(anchor,candidate_name=CANDIDATE)
            historical=original.evaluate_portability_dataframe(pack,gate,gate_label=CANDIDATE)
            if sum(bool(x) for x in historical.both_pass)!=6:
                raise G1G2Error("original historical fitted 6/6 regression changed")
            lenses=[one_lens(row,f,d2c) for row in rows.to_dict("records")]
        verify_hist001_source(copy)
    verify_hist001_source(source)
    return {
        "schema":SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "pinned_F_source_sha256":D2E_F_SHA256,
        "original_fitted_historical_180_120_joint_passes":6,
        "separate_independent_finite_D2d_joint_passes":3,
        "source_historical_fitted_development_lenses":list(LENS_IDS),
        "guard_fraction":GUARD_FRACTION,
        "hernquist_target":G1_TARGET,
        "hernquist_split_budget":G1_SPLIT_BUDGET,
        "bulge_endpoint_target_met_count":sum(
            int(endpoint["target_met"])
            for lens in lenses
            for endpoint in lens["certified_finite_hernquist_continuum_radius_band"]["endpoints"]
        ),
        "analytic_qeff_bands":len(lenses),
        "full_numerical_root_certified":False,
        "lenses":lenses,
        "claims":dict(CLAIMS),
        "environment":{
            "python":sys.version.split()[0],"numpy":np.__version__,
            "pandas":pd.__version__,"scipy":scipy.__version__,
        },
        "limitations":(
            "Rigor refers to exact frozen binary64 PARAMETER analytic continuum "
            "Hernquist/exponential disk mathematical functions. It does not "
            "certify the historical SciPy quadrature/1024 angular numeric outputs, "
            "source gradient, truncated source shadow, total root topology, "
            "critical density numerical errors or any physical Weyl lensing."
        ),
    }


def run(source_root,out):
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.certified_baryon_mass as kernel
    from native_eset.numerics.shadow_aperture_intervals import __file__ as f_math_path

    s,target=Path(source_root),Path(out)
    if s.is_symlink() or target.is_symlink() or target.exists():
        raise G1G2Error("unsafe source symlink or existing output")
    if target.resolve()==s.resolve() or target.resolve().is_relative_to(s.resolve()):
        raise G1G2Error("attempted report write within March source")
    report=execute(s)
    payload=canonical_json(report)
    receipt={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "pinned_F_source_sha256":D2E_F_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "baryonic_proof_kernel_sha256":_sha(Path(kernel.__file__).read_bytes()),
        "q_mapping_kernel_sha256":_sha(Path(f_math_path).read_bytes()),
        "report_sha256":_sha(payload),"claims":dict(CLAIMS),
    }
    raw=canonical_json(receipt)
    target.mkdir(parents=True)
    (target/"report.json").write_bytes(payload)
    (target/"receipt.json").write_bytes(raw)
    (target/"receipt.sha256").write_text(_sha(raw)+"\n",encoding="ascii")
    return {"status":STATUS,"receipt_sha256":_sha(raw),
            "analytic_qeff_bands":report["analytic_qeff_bands"],
            "bulge_endpoint_target_met_count":report["bulge_endpoint_target_met_count"],
            "claims":dict(CLAIMS)}


def verify(receipt_path,source_root,expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.certified_baryon_mass as kernel
    from native_eset.numerics.shadow_aperture_intervals import __file__ as q_math

    p=Path(receipt_path)
    if p.name!="receipt.json" or p.is_symlink() or p.parent.is_symlink():
        raise G1G2Error("unsafe receipt path")
    items=list(p.parent.iterdir())
    if {x.name for x in items}!={"report.json","receipt.json","receipt.sha256"} or any(
        not x.is_file() or x.is_symlink() for x in items
    ):
        raise G1G2Error("receipt member inventory changed")
    raw=p.read_bytes()
    digest=_sha(raw)
    if expected_sha256 is not None and digest!=expected_sha256:
        raise G1G2Error("externally fixed receipt SHA mismatch")
    if (p.parent/"receipt.sha256").read_text(encoding="ascii")!=digest+"\n":
        raise G1G2Error("SHA sidecar mismatch")
    rep_raw=(p.parent/"report.json").read_bytes()
    receipt,report=strict_loads(raw),strict_loads(rep_raw)
    if canonical_json(receipt)!=raw or canonical_json(report)!=rep_raw:
        raise G1G2Error("noncanonical numerical evidence JSON")
    expected={
        "schema":RECEIPT_SCHEMA,"status":STATUS,"source_lock_sha256":SOURCE_SHA256,
        "pinned_F_source_sha256":D2E_F_SHA256,
        "runner_sha256":_sha(Path(__file__).read_bytes()),
        "baryonic_proof_kernel_sha256":_sha(Path(kernel.__file__).read_bytes()),
        "q_mapping_kernel_sha256":_sha(Path(q_math).read_bytes()),
        "report_sha256":_sha(rep_raw),"claims":dict(CLAIMS),
    }
    if receipt!=expected or report.get("schema")!=SCHEMA or report.get("claims")!=CLAIMS:
        raise G1G2Error("receipt provenance or scientific-claim forgery")
    original=execute(source_root)
    try:
        _load_pinned_f()._load_e()._load_d2e_d()._load_d2e_a()._compare(report,original)
    except ValueError as exc:
        raise G1G2Error("source reexecution numerical value mismatch") from exc
    return {"status":"D2E_G1G2_SOURCE_REEXECUTION_ANALYTIC_BARYON_BOUNDS_ONLY",
            "receipt_sha256":digest,"six_development_lenses":len(original["lenses"]),
            "no_full_model_root_theorem":True,"claims":dict(CLAIMS)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",type=Path,required=True)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out",type=Path)
    action.add_argument("--verify",type=Path)
    parser.add_argument("--expected-sha256")
    args=parser.parse_args()
    try:
        value=verify(args.verify,args.source_root,args.expected_sha256) if args.verify else run(
            args.source_root,args.out,
        )
    except (OSError,ValueError,KeyError,TypeError,ImportError,AssertionError) as exc:
        print(json.dumps({"status":"D2E_G1G2_FAIL_CLOSED","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(value,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
