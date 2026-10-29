"""HIST-001D/D2d: independently integrated structured-shadow Einstein roots.

STRICTLY historical fitted-development-lens numerical diagnostic. No new
holdout, no source/refit mutation, no modern Native ESET physical/Weyl provider.

The fitted gate is from the original SHA-pinned March SWELLS source. Rebuilding
finite-domain baryonic and spherical-shadow mass at *each* R and recomputing
q_eff(R) creates a NEW numerical execution identity, not a reproduction of the
archived 180x120, K-matrix + first-linear-crossing historical estimator.
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
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
SOURCE_GRID_POINTS = (180, 360, 720, 1440, 2880, 5760, 11520)
FINITE_DOMAIN_KPC = (0.02, 120.0)
ROOT_SCAN_POINTS = 45
ROOT_EPS_ABSOLUTE = 1e-11  # M(R)-pi*Sigma*R**2 relative to critical target.
GAUSS_ORDER = 24
GAUSS_CROSS_ORDER = 48
ANGULAR_POINTS = 1024  # new complete periodic angle integral, NOT old 120-trapz.
# Predeclared numerical engineering screens, NOT scientific/rigorous error bounds.
MASS_RELATIVE_SCREEN = 0.0005
ROOT_SIGMA_SCREEN = 0.05
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "new_holdout_scored": False,
    "native_v172_equivalence_proved": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "empirical_validation": "NOT_ESTABLISHED",
    "canonical_theory_state_mutated": False,
    "original_source_modified": False,
    "new_numerical_execution_identity": True,
}
REPORT_SCHEMA = "NATIVE_ESET_HIST001D_D2D_STRUCTURED_ROOT_DIAGNOSTIC_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2D_STRUCTURED_ROOT_RECEIPT_V1"
STATUS = "HIST001D_D2D_FINITE_STRUCTURED_ROOT_DIAGNOSTIC_NO_ADMISSION"


class D2dError(ValueError):
    """Refuse unexpected numerical execution identities, model claims and receipts."""


def _load_d2c():
    """Use already audited independent finite-domain integrator, not old K."""
    sibling = Path(__file__).resolve().with_name("hist001d_d2c.py")
    if not sibling.is_file():
        raise D2dError("verified D2c numerical integrator missing")
    spec = importlib.util.spec_from_file_location("hist001d_d2c_import_for_d2d", sibling)
    if spec is None or spec.loader is None:
        raise D2dError("D2c independent integrator cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.SOURCE_SHA256 != SOURCE_SHA256:
        raise D2dError("D2c numerical reference uses other original source")
    if module.CLAIMS["physical_provider_admitted"] is not False:
        raise D2dError("D2c promotion is forbidden")
    return module


def alternate_finite_hernquist(R: float, mass: float, re: float, *, order: int = 128) -> float:
    """Independent Gauss quadrature for smooth finite-domain Hernquist cylinder.

    The reference D2c uses scipy adaptive quad; this routine uses Legendre
    quadrature and a t=sqrt(r^2-R^2) outer substitution, no K-matrix interpolation.
    """
    import numpy as np
    from scipy.special import roots_legendre

    if order not in (96, 128):
        raise D2dError("unregistered independent Hernquist quadrature order")
    a, b = FINITE_DOMAIN_KPC
    if not (a <= R <= b and mass > 0 and re > 0):
        raise D2dError("invalid independent bulge radius/mass")
    h = re / 1.8153
    roots, weights = roots_legendre(order)

    def rho(r):
        return mass * h / (2 * np.pi * r * (r + h)**3)

    inner = 0.
    if R > a:
        r = ((R - a) * roots + R + a) / 2
        inner = float((R - a) * np.sum(weights * 4 * np.pi * rho(r) * r**2) / 2)
    outer = 0.
    if R < b:
        t1 = math.sqrt(b*b - R*R)
        t = t1 * (roots + 1) / 2
        r = np.sqrt(R*R + t*t)
        outer = float(t1 * np.sum(weights * 4 * np.pi * rho(r)
                                      * t * R*R / (r+t)) / 2)
    return inner + outer


def adaptive_periodic_disc(R: float, disk_mass: float, disk_r50: float, q: float) -> float:
    """Independent direct adaptive angle quadrature of SAME analytic disc law."""
    from scipy.integrate import quad
    Rd = disk_r50 / 1.67835
    if R < 0 or Rd <= 0 or disk_mass <= 0 or not 0 < q <= 1:
        raise D2dError("invalid disc parameters")
    sigma0 = disk_mass/(2*math.pi*q*Rd**2)

    def inner(th):
        a = math.hypot(math.cos(th), math.sin(th)/q)
        x = a * R / Rd
        return Rd**2 / a**2 * (-math.expm1(-x) - x * math.exp(-x))

    # Split at all quadrants to resolve high-ellipticity angular structure.
    angles=(0.0, math.pi/2, math.pi, 3*math.pi/2, 2*math.pi)
    return sigma0 * sum(quad(inner, angles[i], angles[i+1], epsabs=0.001,
                             epsrel=1e-12, limit=200)[0] for i in range(4))


def one_lens(row: dict, anchor: dict, gate: dict, d2c) -> dict:
    import numpy as np
    from scipy.optimize import brentq
    from solv.baryons import J2141BaryonicModel
    from solv.cosmology import FlatLCDM
    from solv.dmalane import build_gate_components, epsilon_from_config
    from solv.gate_struct import A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values
    from solv.shadow_density import compute_shadow_density

    lid = str(row["lens_id"])
    if lid not in LENS_IDS:
        raise D2dError("unknown development lens")
    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10**float(row["logM_bulge_chabrier_central"])
    dm = 10**float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"]) * scale
    dr50 = float(row["Re_disc_arcsec"]) * scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    radius_obs = float(row["einstein_radius_arcsec_central"]) * scale
    radius_err = float(row["einstein_radius_arcsec_err_plus"]) * scale
    mass_obs = float(row["lensing_mass_1e10Msun_central"]) * 1e10
    mass_err = float(row["lensing_mass_1e10Msun_err_plus"]) * 1e10
    if min(scale, radius_obs, radius_err, mass_err, bm, dm, bre, dr50, qb, qd) <= 0:
        raise D2dError("invalid frozen observation/model values")
    sigma = FlatLCDM(70, .3).sigma_crit_msun_per_kpc2(
        float(row["z_deflector"]), float(row["z_source"]),
    )
    if not math.isfinite(sigma) or sigma <= 0:
        raise D2dError("bad source critical surface density")
    model = J2141BaryonicModel(bm, bre, dm, dr50)
    features = extract_gate_features_from_values(
        bm, bre, dm, dr50, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    components = build_gate_components(gate, features=features, anchor=anchor)
    method = components.get("shadow_density_method", "mass_difference_gradient")

    @lru_cache(maxsize=4096)
    def baryons(R: float) -> tuple[float, float, float]:
        if not FINITE_DOMAIN_KPC[0] <= R <= FINITE_DOMAIN_KPC[1]:
            raise D2dError("evaluation outside source finite domain")
        bulge = d2c.reference_bulge_finite(R, bm, bre)
        disc = d2c.reference_periodic_disk(R, dm, dr50, qd, ntheta=ANGULAR_POINTS)
        denom = bulge + disc
        if not all(math.isfinite(x) for x in (bulge,disc,denom)) or denom <= 0:
            raise D2dError("invalid independently evaluated baryon projected mass")
        qeff = float(np.clip((qb * bulge + qd * disc) / denom, 1e-3, 1))
        return float(bulge), float(disc), qeff

    # Verify same finite-domain baryonic formula at both source radius and
    # future predicted root, without reusing the original source K matrix.
    obs_bul, obs_disk, obs_q = baryons(radius_obs)
    obs_bul_ref = alternate_finite_hernquist(radius_obs, bm, bre)
    obs_disk_ref = adaptive_periodic_disc(radius_obs, dm, dr50, qd)
    if not math.isclose(obs_bul, obs_bul_ref, rel_tol=2e-9, abs_tol=2):
        raise D2dError("adaptive/Gauss finite bulge discrepancy")
    if not math.isclose(obs_disk, obs_disk_ref, rel_tol=1e-8, abs_tol=2):
        raise D2dError("periodic/adaptive disc discrepancy")

    grids = []
    for n in SOURCE_GRID_POINTS:
        radial = np.linspace(*FINITE_DOMAIN_KPC, n)
        gbar = model.total_vbar(radial)**2 / radial
        eps = epsilon_from_config(radial,gbar,gate,features=features,anchor=anchor)
        rho = compute_shadow_density(radial,gbar,gbar/eps,epsilon=eps,method=method)
        if not (np.isfinite(rho).all() and np.min(rho) >= 0):
            raise D2dError("finite nonnegative source shadow-density check failed")

        @lru_cache(maxsize=2048)
        def projected(R: float):
            bul, disk, q = baryons(float(R))
            eff = R / math.sqrt(q)
            if eff >= FINITE_DOMAIN_KPC[1]:
                eff = FINITE_DOMAIN_KPC[1]
            shadow24 = d2c.integrated_shadow_piecewise_linear(
                eff, radial, rho, order=GAUSS_ORDER,
            )
            total = bul + disk + shadow24
            critical = math.pi*sigma*R*R
            if not all(math.isfinite(x) for x in (eff,shadow24,total,critical)):
                raise D2dError("nonfinite structured shadow mass or critical target")
            return total-critical, float(bul), float(disk), float(shadow24), float(q), float(eff), float(total)

        scan = np.geomspace(*FINITE_DOMAIN_KPC, ROOT_SCAN_POINTS)
        residuals = [projected(float(R))[0] for R in scan]
        if any(not math.isfinite(x) for x in residuals):
            raise D2dError("nonfinite critical root scan")
        changes = [i for i in range(len(scan)-1)
                   if (residuals[i] > 0 > residuals[i+1]) or (residuals[i] < 0 < residuals[i+1])]
        zeros = [i for i,x in enumerate(residuals) if x==0]
        if len(changes)+len(zeros)!=1:
            raise D2dError(f"unexpected root multiplicity {len(changes)} changes {len(zeros)} zeros")
        if zeros:
            root = float(scan[zeros[0]])
            bracket = [root,root]
        else:
            k=changes[0]
            bracket = [float(scan[k]), float(scan[k+1])]
            root=float(brentq(lambda R: projected(float(R))[0],*bracket,xtol=1e-11,
                              rtol=4*sys.float_info.epsilon))
        root_vals=projected(root)
        resid,bul,disc,shadow,qeff,eff,total=root_vals
        obs=projected(radius_obs)
        _,obs_b,obs_d,obs_s,obs_q,obs_eff,obs_total=obs
        radius_pull = (root-radius_obs)/radius_err
        mass_pull = (obs_total-mass_obs)/mass_err
        relative_root_residual=abs(resid)/max(math.pi*sigma*root*root,1.0)
        if relative_root_residual > ROOT_EPS_ABSOLUTE:
            raise D2dError("root did not satisfy high-accuracy mass/critical equality")
        if n in (180,360,11520):
            # Source density radial interpolant at the independent ROOT, not just obs R.
            s24 = d2c.integrated_shadow_piecewise_linear(eff, radial, rho, order=24)
            s48 = d2c.integrated_shadow_piecewise_linear(eff, radial, rho, order=48)
            if not math.isclose(s24,s48,rel_tol=5e-10,abs_tol=2):
                raise D2dError("24/48 Gauss shadow integration crosscheck failed")
            if n in (180,360):
                adaptive=d2c.adaptive_shadow_piecewise_linear(eff,radial,rho)
                if not math.isclose(adaptive,s48,rel_tol=5e-9,abs_tol=2):
                    raise D2dError("adaptive shadow integral and Gauss disagree at root")
                discrepancy=(adaptive-s48)/s48
            else:
                discrepancy=None
            rbul_alt=alternate_finite_hernquist(root,bm,bre)
            rdisk_alt=adaptive_periodic_disc(root,dm,dr50,qd)
            if not math.isclose(rbul_alt,bul,rel_tol=2e-9,abs_tol=2) or not math.isclose(rdisk_alt,disc,rel_tol=1e-8,abs_tol=2):
                raise D2dError("independent root baryon reference disagrees")
            crosscheck={"shadow_gauss24_48_relative":(s24-s48)/s48,
                        "adaptive_shadow_vs_gauss48_relative":discrepancy,
                        "adaptive_bulge_vs_gauss_relative":(bul-rbul_alt)/rbul_alt,
                        "periodic_disc_vs_adaptive_relative":(disc-rdisk_alt)/rdisk_alt}
        else:
            crosscheck=None
        grids.append({
            "radial_points":n,"bracket_kpc":bracket,"number_of_sign_crossings":len(changes)+len(zeros),
            "predicted_einstein_radius_kpc":root,
            "einstein_radius_pull_sigma":radius_pull,
            "predicted_projected_mass_at_observed_radius_msun":obs_total,
            "projected_mass_pull_sigma":mass_pull,
            "joint_pass_abs_le_2sigma":bool(abs(radius_pull)<=2 and abs(mass_pull)<=2),
            "root_critical_relative_residual":relative_root_residual,
            "root_components_msun":{"bulge":bul,"disk":disc,"structured_shadow":shadow,"total":total},
            "root_qeff":qeff,"root_effective_radius_kpc":eff,
            "observed_radius_components_msun":{"bulge":obs_b,"disk":obs_d,"structured_shadow":obs_s,"total":obs_total},
            "observed_radius_qeff":obs_q,"observed_radius_effective_shadow_radius_kpc":obs_eff,
            "independent_integration_crosscheck":crosscheck,
        })
    for i,item in enumerate(grids):
        if i==0:
            item["root_change_vs_previous_sigma"]=None
            item["observed_mass_change_vs_previous_relative"]=None
        else:
            prev=grids[i-1]
            item["root_change_vs_previous_sigma"]=(
                item["predicted_einstein_radius_kpc"]-prev["predicted_einstein_radius_kpc"]
            )/radius_err
            item["observed_mass_change_vs_previous_relative"]=(
                item["predicted_projected_mass_at_observed_radius_msun"]
                - prev["predicted_projected_mass_at_observed_radius_msun"]
            )/prev["predicted_projected_mass_at_observed_radius_msun"]
    newest_deltas=[grids[-2]["root_change_vs_previous_sigma"],grids[-1]["root_change_vs_previous_sigma"]]
    newest_mass=[grids[-2]["observed_mass_change_vs_previous_relative"],grids[-1]["observed_mass_change_vs_previous_relative"]]
    two_step_screen=all(abs(x)<=ROOT_SIGMA_SCREEN for x in newest_deltas) and all(
        abs(x)<=MASS_RELATIVE_SCREEN for x in newest_mass)
    return {"lens_id":lid,"source_development_lens":True,
            "observed_radius_kpc":radius_obs,"observed_radius_uncertainty_kpc":radius_err,
            "observed_mass_msun":mass_obs,"observed_mass_uncertainty_msun":mass_err,
            "sigma_crit_msun_per_kpc2":sigma,"observed_radius_reference_bulge_mass_msun":obs_bul,
            "observed_radius_reference_disk_mass_msun":obs_disk,"observed_radius_qeff_reference":obs_q,
            "independent_bulge_reference_relative_error":(obs_bul-obs_bul_ref)/obs_bul_ref,
            "independent_disc_reference_relative_error":(obs_disk-obs_disk_ref)/obs_disk_ref,
            "grid_results":grids,"two_step_root_and_mass_engineering_screen":bool(two_step_screen),
            "latest_two_root_delta_sigma":newest_deltas,"latest_two_observed_mass_relative":newest_mass}


def execute(source_root: str | Path) -> dict:
    """Source-lock 46 original files + 3 negatives; reexecute from disposable copy."""
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    source=Path(source_root)
    trust=verify_hist001_source(source)
    if trust["source_lock_sha256"]!=SOURCE_SHA256:
        raise D2dError("unexpected original SOURCE_LOCK identity")
    d2c=_load_d2c()
    with TemporaryDirectory(prefix="hist001d_d2d_frozen_") as temp:
        target=Path(temp)/"hist001"
        shutil.copytree(source,target)
        verify_hist001_source(target)
        pack=target/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            seta=original._load_tables(pack)
            if tuple(seta.lens_id)!=LENS_IDS:
                raise D2dError("six original development lens IDs have changed")
            anchor,_=original._build_anchor(pack)
            gate=original._candidate_gate_config(anchor,candidate_name=CANDIDATE)
            historical=original.evaluate_portability_dataframe(pack,gate,gate_label=CANDIDATE)
            if tuple(historical.lens_id)!=LENS_IDS:
                raise D2dError("source original row identity changed")
            if sum(bool(x) for x in historical.both_pass)!=6:
                raise D2dError("frozen 180/120 historical regression baseline changed")
            lenses=[]
            for row in seta.to_dict("records"):
                lenses.append(one_lens(row,anchor,gate,d2c))
            historical_rows=[{
                "lens_id":str(row["lens_id"]),
                "original_frozen_180_120_radius_pull_sigma":float(row["einstein_radius_pull_sigma"]),
                "original_frozen_180_120_mass_pull_sigma":float(row["mass_pull_sigma"]),
                "original_frozen_180_120_joint_pass":bool(row["both_pass"]),
            } for row in historical.to_dict("records")]
        verify_hist001_source(target)
    verify_hist001_source(source)
    return {
        "schema":REPORT_SCHEMA,"status":STATUS,"source_lock_sha256":SOURCE_SHA256,
        "candidate":CANDIDATE,"source_model_role":"EXISTING_SIX_FITTED_SET_A_DEVELOPMENT_LENSES",
        "finite_source_domain_kpc":list(FINITE_DOMAIN_KPC),
        "source_density_grids":list(SOURCE_GRID_POINTS),"root_scan_log_points":ROOT_SCAN_POINTS,
        "baryonic_projected_mass":"FINITE_DOMAIN_ADAPTIVE_HERNQUIST_AND_PERIODIC_1024_DISC",
        "shadow_projected_mass":"ORIGINAL_SOURCE_DENSITY_PIECEWISE_LINEAR_EXACT_INNER_GAUSS_OUTER",
        "structured_shadow":"AT_EACH_R_COMPUTE_QEFF_FROM_INDEPENDENT_BARYON_MASSES_AND_MSHADOW_AT_R_OVER_SQRT_Q",
        "root_solver":"BRENTQ_UNINTERPOLATED_QUADRATIC_CRITICAL_TARGET_WITH_BRACKET_SCAN",
        "numeric_screen":{"classification":"FIXED_BEFORE_LOCAL_RUN_NOT_EXTERNAL_PREREG_NOT_RIGOROUS_BOUND",
                          "root_delta_sigma":ROOT_SIGMA_SCREEN,
                          "observed_mass_relative":MASS_RELATIVE_SCREEN,
                          "pairs":[[2880,5760],[5760,11520]],
                          "all_six_pass":all(x["two_step_root_and_mass_engineering_screen"] for x in lenses)},
        "historical_original_reference":historical_rows,
        "new_numerical_identity_results":lenses,
        "claims":dict(CLAIMS),"environment":{"python":sys.version.split()[0],"numpy":np.__version__,
                                            "pandas":pd.__version__,"scipy":scipy.__version__},
        "limitations":"This is a new finite-domain structured-projection numerical execution identity. Root sample is fitted six-lens Set A. No uniform error certificate, full metric Weyl lensing, disjoint blinded holdout, or modern Native v1.7.2 transfer.",
    }


def _sha(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def run(source_root: str | Path, out: str | Path) -> dict:
    from native_eset.evidence.receipts import canonical_json

    original,output=Path(source_root),Path(out)
    if original.is_symlink() or output.is_symlink():
        raise D2dError("symlink source/output not allowed")
    if output.exists():
        raise FileExistsError("D2d output exists; immutable rerun required")
    if output.resolve()==original.resolve() or output.resolve().is_relative_to(original.resolve()):
        raise D2dError("cannot write into source")
    report=execute(original)
    payload=canonical_json(report)
    sibling=Path(__file__).with_name("hist001d_d2c.py")
    receipt={"schema":RECEIPT_SCHEMA,"status":STATUS,"source_lock_sha256":SOURCE_SHA256,
             "report_sha256":_sha(payload),"module_sha256":_sha(Path(__file__).read_bytes()),
             "d2c_integrator_sha256":_sha(sibling.read_bytes()),"claims":dict(CLAIMS)}
    raw=canonical_json(receipt)
    output.mkdir(parents=True)
    (output/"report.json").write_bytes(payload)
    (output/"receipt.json").write_bytes(raw)
    (output/"receipt.sha256").write_text(_sha(raw)+"\n",encoding="ascii")
    return {"status":STATUS,"receipt_sha256":_sha(raw),"output_dir":str(output),
            "lenses":len(report["new_numerical_identity_results"]),
            "grids":len(SOURCE_GRID_POINTS),"numeric_screen":report["numeric_screen"],
            "claims":dict(CLAIMS)}


def _compare(a,b,path="report"):
    """Strict key structure and numeric replay; skip only ambient environment tuple."""
    if type(a) is not type(b):
        raise D2dError("report type changed: "+path)
    if isinstance(a,dict):
        if a.keys()!=b.keys():
            raise D2dError("report keys changed: "+path)
        for key in b:
            if path=="report" and key=="environment":
                continue
            _compare(a[key],b[key],path+"."+str(key))
    elif isinstance(a,list):
        if len(a)!=len(b):
            raise D2dError("report list length changed: "+path)
        for i,(u,v) in enumerate(zip(a,b)):
            _compare(u,v,path+"."+str(i))
    elif isinstance(a,float):
        if not math.isfinite(a) or not math.isfinite(b):
            raise D2dError("nonfinite numerical report: "+path)
        if not math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-8):
            raise D2dError("source numerical reexecution differs: "+path)
    elif a!=b:
        raise D2dError("report value changed: "+path)


def verify(receipt_path: str | Path, source_root: str | Path,
           expected_sha256: str | None = None) -> dict:
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads

    path=Path(receipt_path)
    if path.is_symlink() or path.name!="receipt.json" or path.parent.is_symlink():
        raise D2dError("unsafe receipt location")
    names={x.name for x in path.parent.iterdir()}
    if names!={"report.json","receipt.json","receipt.sha256"}:
        raise D2dError("receipt file inventory mismatch")
    if any(x.is_symlink() or not x.is_file() for x in path.parent.iterdir()):
        raise D2dError("unsafe receipt member")
    raw=path.read_bytes(); digest=_sha(raw)
    if expected_sha256 is not None and digest!=expected_sha256:
        raise D2dError("externally pinned receipt hash mismatch")
    if (path.parent/"receipt.sha256").read_text(encoding="ascii")!=digest+"\n":
        raise D2dError("receipt SHA sidecar differs")
    payload=(path.parent/"report.json").read_bytes()
    receipt= strict_loads(raw); report=strict_loads(payload)
    if canonical_json(receipt)!=raw or canonical_json(report)!=payload:
        raise D2dError("noncanonical report/receipt JSON")
    sibling=Path(__file__).with_name("hist001d_d2c.py")
    expected={"schema":RECEIPT_SCHEMA,"status":STATUS,"source_lock_sha256":SOURCE_SHA256,
              "report_sha256":_sha(payload),"module_sha256":_sha(Path(__file__).read_bytes()),
              "d2c_integrator_sha256":_sha(sibling.read_bytes()),"claims":dict(CLAIMS)}
    if receipt!=expected:
        raise D2dError("receipt claims or integrity do not match approved schema")
    if report.get("claims")!=CLAIMS or report.get("schema")!=REPORT_SCHEMA or report.get("status")!=STATUS:
        raise D2dError("claim forgery or report schema mismatch")
    rerun=execute(source_root)
    _compare(report,rerun)
    return {"status":"HIST001D_D2D_SOURCE_REEXECUTION_PASS_NO_ADMISSION",
            "receipt_sha256":digest,"six_fitted_lenses":len(rerun["new_numerical_identity_results"]),
            "source_grids":len(SOURCE_GRID_POINTS),"claims":dict(CLAIMS)}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",type=Path,required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out",type=Path)
    group.add_argument("--verify",type=Path)
    parser.add_argument("--expected-sha256")
    args=parser.parse_args()
    try:
        result=(verify(args.verify,args.source_root,args.expected_sha256)
                if args.verify is not None else run(args.source_root,args.out))
    except (OSError,ValueError,TypeError,KeyError,ImportError,AssertionError) as e:
        print(json.dumps({"status":"HIST001D_D2D_FAIL_CLOSED","error":str(e)},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
