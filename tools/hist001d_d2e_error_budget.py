"""D2e-C: source-gradient alternatives and finite-boundary root/mass sensitivity.

Nonpromoting, no-refit six-development-lens numerical ablation. All derivative
and boundary alternatives are NEW counterfactual identities. The extrema over
this finite menu are NOT validated mathematical error bounds, unmodeled mass
beyond the historical domain, physical lensing or observational validation.
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
D2E_B_SHA256 = "d2784a4609460cd562b479c3b442a9a34aaa12ad9d3d709bc48959978c209155"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = ("J0822+1828", "J0915+4211", "J0930+2855",
            "J1021+2028", "J1111+2234", "J1135+3720")
DENSITY_POINTS = 11520
FINITE_DOMAIN = (0.02, 120.0)
ALTERNATIVES = ("SOURCE_GRADIENT", "EDGE_ORDER_2", "PCHIP_DERIVATIVE",
                "ANALYTIC_INNER_HERNQUIST", "EXTERNAL_SHADOW_R_MINUS_4",
                "EXTERNAL_SHADOW_R_MINUS_5")
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "new_numerical_counterfactual_identities": True,
    "source_gradient_changed": False,
    "original_source_modified": False,
    "canonical_theory_state_mutated": False,
    "root_uniqueness_mathematically_certified": False,
    "global_error_bound_established": False,
    "mass_outside_finite_domain_bounded": False,
    "physical_provider_admitted": False,
    "physical_weyl_lensing_derived": False,
    "native_v172_equivalence_proved": False,
    "new_holdout_scored": False,
    "empirical_validation": "NOT_ESTABLISHED",
}
SCHEMA = "NATIVE_ESET_HIST001D_D2E_C_DERIVATIVE_BOUNDARY_SENSITIVITY_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_C_RECEIPT_V1"
STATUS = "D2E_C_EMPIRICAL_ERROR_MENU_NOT_A_GLOBAL_BOUND_NO_ADMISSION"


class D2eCError(ValueError):
    """Invalid original source, numerical ablation or attempted promotion."""


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_pinned(name: str, sha: str):
    p = Path(__file__).resolve().with_name(name)
    if p.is_symlink() or not p.is_file() or digest(p.read_bytes()) != sha:
        raise D2eCError("pinned prerequisite changed: " + name)
    spec = importlib.util.spec_from_file_location("d2ec_prerequisite_" + name[:-3], p)
    if spec is None or spec.loader is None:
        raise D2eCError("cannot import prerequisite: " + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if getattr(module, "SOURCE_SHA256", None) != SOURCE_SHA256:
        raise D2eCError("prerequisite original source identity differs")
    if module.CLAIMS.get("physical_provider_admitted") is not False:
        raise D2eCError("prerequisite attempted physical promotion")
    return module


def hernquist_inner_mass(bulge_mass: float, bulge_re: float, cutoff: float = .02) -> float:
    """Exact interior sphere mass if source Hernquist law is extended to r=0.

    For R >= cutoff, all this mass falls inside the projected cylinder.
    This is an explicitly NEW continuation assumption, not D2d's result.
    """
    if not all(math.isfinite(v) and v > 0 for v in (bulge_mass, bulge_re, cutoff)):
        raise D2eCError("invalid analytic inner Hernquist continuation")
    a = bulge_re / 1.8153
    return bulge_mass * cutoff**2 / (cutoff+a)**2


def analytic_shadow_tail_cylinder(aperture: float, density_at_cutoff: float,
                                  exponent: int, cutoff: float = 120.) -> float:
    """Counterfactual positive r^-p tail joined at the source boundary.

    Numerically stable finite-interval transform u=cutoff/r. NO source
    authorizes this continuation, even when the resulting mass is finite.
    """
    from scipy.integrate import quad
    if (exponent not in (4, 5) or not all(math.isfinite(x) for x in
                                        (aperture, density_at_cutoff, cutoff))
            or not 0 <= aperture < cutoff or density_at_cutoff < 0 or cutoff <= 0):
        raise D2eCError("unregistered shadow-tail continuation")
    if density_at_cutoff == 0 or aperture == 0:
        return 0.
    ratio = aperture / cutoff
    integrand = lambda u: u**(exponent-2) / (
        1 + math.sqrt(max(0., 1-(ratio*u)**2))
    )
    value, error = quad(integrand, 0., 1., epsabs=1e-12, epsrel=1e-11, limit=160)
    if not math.isfinite(value) or value < 0 or not math.isfinite(error):
        raise D2eCError("invalid tail sensitivity quadrature")
    return 4*math.pi*density_at_cutoff*cutoff*aperture**2*value


def alternate_densities(radii, source_mass, source_rho):
    """Reconstruct different gradients of the SAME fixed nodal shadow mass."""
    import numpy as np
    from scipy.interpolate import PchipInterpolator

    r = np.asarray(radii, dtype=float)
    m = np.asarray(source_mass, dtype=float)
    base = np.asarray(source_rho, dtype=float)
    if (r.ndim != 1 or m.shape != r.shape or base.shape != r.shape or
            r.size < 4 or np.any(np.diff(r) <= 0) or
            not all(np.isfinite(v).all() for v in (r, m, base)) or
            np.any(m < 0) or np.any(base < 0)):
        raise D2eCError("invalid fixed-source shadow derivative input")
    edge2 = np.gradient(m, r, edge_order=2)
    pchip = PchipInterpolator(r, m).derivative()(r)
    def make(d):
        return np.maximum(np.asarray(d, dtype=float)/(4*math.pi*r*r), 0.)
    outputs = {"SOURCE_GRADIENT": base,
               "EDGE_ORDER_2": make(edge2),
               "PCHIP_DERIVATIVE": make(pchip)}
    for k, v in outputs.items():
        if not np.isfinite(v).all() or np.any(v < 0):
            raise D2eCError("alternative density is nonfinite or negative: "+k)
    return outputs


def one_lens(row, anchor, gate, a, d2c):
    import numpy as np
    from scipy.integrate import simpson
    from scipy.optimize import brentq
    from solv.baryons import J2141BaryonicModel
    from solv.constants import G_KPC_KMS2_MSUN
    from solv.cosmology import FlatLCDM
    from solv.dmalane import epsilon_from_config
    from solv.gate_struct import A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values
    from solv.shadow_density import compute_shadow_density

    lid = str(row["lens_id"])
    if lid not in LENS_IDS:
        raise D2eCError("unknown historical development lens")
    scale = float(row["scale_kpc_per_arcsec"])
    bm = 10**float(row["logM_bulge_chabrier_central"])
    dm = 10**float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"])*scale
    dre = float(row["Re_disc_arcsec"])*scale
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    obs_r = float(row["einstein_radius_arcsec_central"])*scale
    sig_r = float(row["einstein_radius_arcsec_err_plus"])*scale
    sig_m = float(row["lensing_mass_1e10Msun_err_plus"])*1e10
    if min(scale,bm,dm,bre,dre,qb,qd,obs_r,sig_r,sig_m) <= 0:
        raise D2eCError("invalid frozen observed/model parameters")
    sigma = FlatLCDM(70,.3).sigma_crit_msun_per_kpc2(
        float(row["z_deflector"]), float(row["z_source"]),
    )
    model = J2141BaryonicModel(bm, bre, dm, dre)
    features = extract_gate_features_from_values(
        bm,bre,dm,dre,qb,qd,
        ra0_kpc=compute_transition_radius_kpc(model,a0_mps2=A0_MPS2),
    )
    r = np.linspace(*FINITE_DOMAIN, DENSITY_POINTS)
    gbar = model.total_vbar(r)**2/r
    eps = epsilon_from_config(r,gbar,gate,features=features,anchor=anchor)
    if not np.isfinite(eps).all() or np.min(eps) <= 0:
        raise D2eCError("invalid historical epsilon")
    gtot = gbar/eps
    m_eff = gtot*r*r/G_KPC_KMS2_MSUN
    m_bar = gbar*r*r/G_KPC_KMS2_MSUN
    m_sh = np.maximum(m_eff-m_bar,0.)
    rho_source = compute_shadow_density(r,gbar,gtot,epsilon=eps,method="mass_difference_gradient")
    densities = alternate_densities(r,m_sh,rho_source)
    inner_bulge = hernquist_inner_mass(bm,bre)

    @lru_cache(maxsize=2048)
    def baryonic(R):
        bul = d2c.reference_bulge_finite(R,bm,bre)
        disk = d2c.reference_periodic_disk(R,dm,dre,qd,ntheta=1024)
        if not math.isfinite(bul+disk) or min(bul,disk) <= 0:
            raise D2eCError("nonfinite baryonic projection")
        return float(bul), float(disk)

    @lru_cache(maxsize=8192)
    def shadow(R, variant):
        rho = densities[variant]
        return d2c.integrated_shadow_piecewise_linear(R,r,rho,order=24)

    def predicted_mass(R, variant):
        bul, disk = baryonic(float(R))
        if variant == "ANALYTIC_INNER_HERNQUIST":
            bul += inner_bulge
        q = max(1e-3,min(1.,(qb*bul+qd*disk)/(bul+disk)))
        eff = min(FINITE_DOMAIN[1],R/math.sqrt(q))
        density_variant = variant if variant in densities else "SOURCE_GRADIENT"
        total = bul+disk+shadow(eff,density_variant)
        if variant in ("EXTERNAL_SHADOW_R_MINUS_4","EXTERNAL_SHADOW_R_MINUS_5"):
            if eff >= FINITE_DOMAIN[1]:
                raise D2eCError("tail scenario cannot evaluate saturated aperture")
            exponent = 4 if variant.endswith("_4") else 5
            total += analytic_shadow_tail_cylinder(eff,float(rho_source[-1]),exponent)
        return float(total)

    ref = a.D2D_REFERENCE_ROOT_KPC[lid]
    baseline_observed_mass = predicted_mass(obs_r,"SOURCE_GRADIENT")
    ref_window=(max(.02,ref*.85),min(120.,ref*1.15))
    scenarios=[]
    for variant in ALTERNATIVES:
        f=lambda R: predicted_mass(R,variant)/(math.pi*sigma*R*R)-1
        flo,fhi=f(ref_window[0]),f(ref_window[1])
        if not all(math.isfinite(v) for v in (flo,fhi)):
            raise D2eCError("nonfinite counterfactual root function")
        if flo*fhi < 0:
            root = float(brentq(f,*ref_window,xtol=1e-11))
            root_status = "BRACKETED_ROOT_FOUND_WITHIN_FIXED_15PCT_WINDOW"
            sigma_shift = (root-ref)/sig_r
        else:
            root, sigma_shift = None, None
            root_status = "UNBRACKETED_IN_FIXED_WINDOW_NOT_A_GLOBAL_NO_ROOT_CLAIM"
        mass_at_observed=predicted_mass(obs_r,variant)
        scenarios.append({
            "variant":variant,
            "new_numerical_counterfactual":variant!="SOURCE_GRADIENT",
            "root_status":root_status,
            "root_kpc":root,
            "root_shift_vs_d2d_observational_sigma":sigma_shift,
            "projected_mass_at_observed_radius_msun":mass_at_observed,
            "projected_mass_change_vs_original_source_sigma":
                (mass_at_observed-baseline_observed_mass)/sig_m,
            "root_window_kpc":list(ref_window),
        })
    if scenarios[0]["root_shift_vs_d2d_observational_sigma"] is None or abs(
        scenarios[0]["root_shift_vs_d2d_observational_sigma"]
    ) > 1e-7:
        raise D2eCError("reference D2d root changed in C baseline")
    derivative_statistics=[]
    for label in ("EDGE_ORDER_2","PCHIP_DERIVATIVE"):
        delta = densities[label]-rho_source
        w = 4*math.pi*r*r
        weighted_l1=simpson(np.abs(delta)*w,x=r)
        source_sphere=simpson(rho_source*w,x=r)
        derivative_statistics.append({
            "variant":label,
            "l1_absolute_density_mass_difference_msun":float(weighted_l1),
            "l1_fraction_of_original_finite_spherical_shadow_mass":
                float(weighted_l1/max(source_sphere,1.)),
            "negative_after_clip_density_bins":int(np.count_nonzero(densities[label]<0)),
            "zero_after_clip_density_bins":int(np.count_nonzero(densities[label]==0)),
            "max_abs_density_difference_msun_per_kpc3":float(np.max(np.abs(delta))),
        })
    radius_shifts=[abs(s["root_shift_vs_d2d_observational_sigma"])
                   for s in scenarios[1:] if s["root_shift_vs_d2d_observational_sigma"] is not None]
    mass_shifts=[abs(s["projected_mass_change_vs_original_source_sigma"])
                 for s in scenarios[1:]]
    return {
        "lens_id":lid,
        "historical_development_lens":True,
        "d2d_baseline_root_kpc":ref,
        "original_historical_fitted_pass_count":6,
        "independent_d2d_pass_count":3,
        "original_source_shadow_nodal_mass_monotone":bool(np.all(np.diff(m_sh)>=0)),
        "inner_missing_hernquist_mass_under_extension_msun":inner_bulge,
        "inner_missing_shadow_mass_bounded":False,
        "outer_missing_shadow_mass_bounded":False,
        "derivative_diagnostics":derivative_statistics,
        "counterfactual_scenarios":scenarios,
        "measured_max_abs_root_excursion_sigma_among_bracketed_scenarios":
            max(radius_shifts) if radius_shifts else None,
        "measured_max_abs_observed_mass_excursion_sigma_among_scenarios":
            max(mass_shifts) if mass_shifts else None,
        "globally_valid_error_certificate":False,
    }


def execute(source_root):
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    a=load_pinned("hist001d_d2e.py",D2E_A_SHA256)
    load_pinned("hist001d_d2e_interval.py",D2E_B_SHA256)
    d2c=a._load_pinned("hist001d_d2c.py",a.D2C_SHA256)
    source=Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise D2eCError("original March source is missing or symlinked")
    if verify_hist001_source(source)["source_lock_sha256"]!=SOURCE_SHA256:
        raise D2eCError("different March source identity")
    with TemporaryDirectory(prefix="hist001d_d2e_c_") as temp:
        target=Path(temp)/"hist001"
        shutil.copytree(source,target)
        verify_hist001_source(target)
        pack=target/"swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            data=original._load_tables(pack)
            if tuple(data.lens_id)!=LENS_IDS:
                raise D2eCError("original six development lenses changed")
            anchor,_=original._build_anchor(pack)
            gate=original._candidate_gate_config(anchor,candidate_name=CANDIDATE)
            historical=original.evaluate_portability_dataframe(pack,gate,gate_label=CANDIDATE)
            if sum(bool(v) for v in historical.both_pass)!=6:
                raise D2eCError("original historical 6/6 reference not reproduced")
            results=[one_lens(row,anchor,gate,a,d2c) for row in data.to_dict("records")]
        verify_hist001_source(target)
    verify_hist001_source(source)
    return {
        "schema":SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_a_sha256":D2E_A_SHA256,"d2e_b_sha256":D2E_B_SHA256,
        "source_density_grid_points":DENSITY_POINTS,
        "source_domain_kpc":list(FINITE_DOMAIN),
        "retained_original_historical_6of6":True,
        "retained_independent_d2d_3of6":True,
        "sampled_derivative_variants":list(ALTERNATIVES),
        "outer_power_law_scenarios_unadmitted":[4,5],
        "empirical_sensitivity_not_certified_error_bound":True,
        "lenses":results,
        "claims":dict(CLAIMS),
        "environment":{"python":sys.version.split()[0],"numpy":np.__version__,
                       "pandas":pd.__version__,"scipy":scipy.__version__},
        "limitations":"Finite-menu counterfactuals are neither a worst-case numerical bound nor physical mass continuation. No global uniqueness, absolute error certificate, valid covariance likelihood, independent holdout or current ESET physical lensing.",
    }


def run(source_root,out):
    from native_eset.evidence.receipts import canonical_json
    source,output=Path(source_root),Path(out)
    if source.is_symlink() or output.is_symlink() or output.exists():
        raise D2eCError("unsafe or preexisting output path")
    if output.resolve()==source.resolve() or output.resolve().is_relative_to(source.resolve()):
        raise D2eCError("cannot write into frozen historical source")
    raw_report=canonical_json(execute(source))
    receipt={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_a_sha256":D2E_A_SHA256,"d2e_b_sha256":D2E_B_SHA256,
        "module_sha256":digest(Path(__file__).read_bytes()),
        "report_sha256":digest(raw_report),"claims":dict(CLAIMS),
    }
    raw_receipt=canonical_json(receipt)
    output.mkdir(parents=True)
    (output/"report.json").write_bytes(raw_report)
    (output/"receipt.json").write_bytes(raw_receipt)
    (output/"receipt.sha256").write_text(digest(raw_receipt)+"\n",encoding="ascii")
    return {"status":STATUS,"receipt_sha256":digest(raw_receipt),"claims":dict(CLAIMS)}


def verify(receipt_path,source_root,expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    p=Path(receipt_path)
    if p.is_symlink() or p.name!="receipt.json" or p.parent.is_symlink():
        raise D2eCError("unsafe receipt path")
    names=list(p.parent.iterdir())
    if ({x.name for x in names}!={"report.json","receipt.json","receipt.sha256"} or
            any(x.is_symlink() or not x.is_file() for x in names)):
        raise D2eCError("unexpected receipt inventory")
    raw=p.read_bytes()
    h=digest(raw)
    if expected_sha256 is not None and h!=expected_sha256:
        raise D2eCError("externally pinned SHA mismatch")
    if (p.parent/"receipt.sha256").read_text(encoding="ascii")!=h+"\n":
        raise D2eCError("receipt checksum sidecar mismatch")
    receipt= strict_loads(raw)
    report_raw=(p.parent/"report.json").read_bytes()
    report=strict_loads(report_raw)
    if canonical_json(receipt)!=raw or canonical_json(report)!=report_raw:
        raise D2eCError("noncanonical JSON receipt/report")
    expected={
        "schema":RECEIPT_SCHEMA,"status":STATUS,
        "source_lock_sha256":SOURCE_SHA256,
        "d2e_a_sha256":D2E_A_SHA256,"d2e_b_sha256":D2E_B_SHA256,
        "module_sha256":digest(Path(__file__).read_bytes()),
        "report_sha256":digest(report_raw),"claims":dict(CLAIMS),
    }
    if receipt!=expected or report.get("claims")!=CLAIMS or report.get("schema")!=SCHEMA:
        raise D2eCError("receipt integrity or scientific claim forgery")
    source_report=execute(source_root)
    try:
        load_pinned("hist001d_d2e.py",D2E_A_SHA256)._compare(report,source_report)
    except ValueError as e:
        raise D2eCError("source numerical reexecution differs") from e
    return {"status":"D2E_C_ORIGINAL_SOURCE_REEXECUTION_PASS_NO_ADMISSION",
            "receipt_sha256":h,"six_lenses":len(source_report["lenses"]),"claims":dict(CLAIMS)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root",type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--out",type=Path)
    group.add_argument("--verify",type=Path)
    p.add_argument("--expected-sha256")
    args=p.parse_args()
    try:
        value=verify(args.verify,args.source_root,args.expected_sha256) if args.verify else run(
            args.source_root,args.out,
        )
    except (OSError,ValueError,KeyError,TypeError,ImportError,AssertionError) as e:
        print(json.dumps({"status":"D2E_C_FAIL_CLOSED","error":str(e)},sort_keys=True))
        return 2
    print(json.dumps(value,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
