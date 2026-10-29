"""HIST-001D/D2b: nonpromoting, SHA-locked projection/root sensitivity.

Investigates frozen legacy ESET3 fitted J2141/Set A numerical artifacts.
Cannot validate native ESET v1.7.2, select holdouts, or change frozen source.
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
RADIAL_GRIDS = (180, 360, 720)
ANGLE_STEPS = (60, 120, 240, 480, 960)
CROSS_PAIRS = ((180, 180), (180, 360), (360, 180), (360, 360))
CLAIMS = {
    "historical_fitted_development_regression_only": True,
    "source_code_modified": False,
    "new_holdout_scored": False,
    "native_v172_equivalence_proved": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class D2bIntegrityError(ValueError):
    """Wrong original-source identity, unsupported recipe, or altered receipt."""


@contextmanager
def _verified_source_module_context(pack: Path):
    """Import SHA-checked historical solver in an isolated, disposable copy.

    Temporarily evict any cached `solv` modules from earlier historical tests,
    then restore them so neither repo source nor other pytest imports mutate.
    """
    cached = {key: value for key, value in sys.modules.items()
              if key == "solv" or key.startswith("solv.")}
    for key in cached:
        del sys.modules[key]
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(pack))
    try:
        import solv
        if Path(solv.__file__).resolve().parent != pack.resolve() / "solv":
            raise D2bIntegrityError("wrong historical solver import origin")
        yield
    finally:
        sys.path.remove(str(pack))
        for key in tuple(sys.modules):
            if key == "solv" or key.startswith("solv."):
                del sys.modules[key]
        sys.modules.update(cached)
        sys.dont_write_bytecode = old


def _linearly_interpolated_mass_root(radius, projected_mass, sigma, source_root):
    """Find M_linear(R)=pi*sigma*R^2 inside source's first sign bracket.

    Counterfactual root on the SAME projected mass sample, not a correction
    to the original frozen source or a new physical solution.
    """
    import numpy as np
    from scipy.optimize import brentq
    f = projected_mass - math.pi * sigma * radius**2
    indexes = np.flatnonzero(np.diff(np.sign(f)))
    if len(indexes) != 1:
        raise D2bIntegrityError("unexpected root multiplicity / no root")
    k = int(indexes[0])
    a, b = float(radius[k]), float(radius[k + 1])
    ma, mb = float(projected_mass[k]), float(projected_mass[k + 1])
    if b <= a:
        raise D2bIntegrityError("invalid root bracket")
    v = brentq(
        lambda x: (ma + (mb - ma) * (x - a) / (b - a))
                  - math.pi * sigma * x**2,
        a, b, xtol=1e-13,
    )
    return {
        "source_linear_f_root_kpc": float(source_root),
        "same_mass_linear_M_quadratic_target_root_kpc": float(v),
        "bracket_kpc": [a, b],
        "source_bracket_index": k,
    }


def _analytic_bulge_projected_mass(R: float, total_mass: float, bulge_re: float) -> float:
    """Independent adaptive finite-domain cylinder mass for exact Hernquist rho.

    Compares K-matrix radial integration and R interpolation to an adaptive
    quadrature of the *same* 0.02-to-120 kpc integration domain.
    """
    from scipy.integrate import quad
    a = bulge_re / 1.8153

    def density(x):
        return total_mass * a / (2 * math.pi * x * (x + a)**3)

    if not (0.02 < R < 120.):
        raise D2bIntegrityError("Einstein mass interpolation radius out of domain")
    lower = quad(lambda x: 4 * math.pi * density(x) * x**2,
                 .02, R, epsabs=1., epsrel=1e-9, limit=180)[0]
    upper = quad(lambda x: 4 * math.pi * density(x) * x
                 * (x - math.sqrt(max(0, x*x - R*R))),
                 R, 120., epsabs=1., epsrel=1e-9, limit=180)[0]
    return float(lower + upper)


def _angle_comparison(R, mass, disk_r50, q):
    import numpy as np
    from solv.run_j2141_axisym_lens import projected_disk_mass_exponential
    disk_scale = disk_r50 / 1.67835
    out = {}
    for n in ANGLE_STEPS:
        theta = np.linspace(0., 2*math.pi, n, endpoint=False)
        factor = np.sqrt(np.cos(theta)**2 + np.sin(theta)**2 / q**2)
        v = factor * R / disk_scale
        integrand = (disk_scale**2 / factor**2) * (1 - np.exp(-v) * (1+v))
        sigma = mass / (2 * math.pi * q * disk_scale**2)
        periodic = float(sigma * np.sum(integrand) * (2 * math.pi / n))
        original = projected_disk_mass_exponential(R, mass, disk_scale, q, ntheta=n)
        out[str(n)] = {
            "original_endpoint_omitting_mass_msun": original,
            "full_periodic_trapezoid_mass_msun": periodic,
            "fractional_bias_relative_to_periodic": float((original-periodic)/periodic),
        }
    return out


def _one_lens(row, original, cached_projection):
    import numpy as np
    from solv.baryons import J2141BaryonicModel
    from solv.cosmology import FlatLCDM
    from solv.dmalane import build_gate_components, epsilon_from_config
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.run_j2141_axisym_lens import (
        hernquist_density, projected_disk_mass_exponential,
        apply_shadow_projection_mode, solve_einstein_radius_projected,
    )
    from solv.shadow_density import compute_shadow_density

    bm = 10**float(row["logM_bulge_chabrier_central"])
    dm = 10**float(row["logM_disc_chabrier_central"])
    bre = float(row["Re_bulge_arcsec"])*float(row["scale_kpc_per_arcsec"])
    dr50 = float(row["Re_disc_arcsec"])*float(row["scale_kpc_per_arcsec"])
    qb, qd = float(row["q_bulge"]), float(row["q_disc"])
    model = J2141BaryonicModel(bm, bre, dm, dr50)
    anchor = cached_projection["anchor"]
    gate = cached_projection["gate"]
    features = extract_gate_features_from_values(
        bm, bre, dm, dr50, qb, qd,
        ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
    )
    comp = build_gate_components(gate, features=features, anchor=anchor)
    rho_on_grids = {}
    for n in RADIAL_GRIDS:
        r = cached_projection["grids"][n]["r"]
        gbar = model.total_vbar(r)**2/r
        eps = epsilon_from_config(r, gbar, gate, features=features, anchor=anchor)
        rho_on_grids[n] = compute_shadow_density(
            r, gbar, gbar/eps, epsilon=eps,
            method=comp.get("shadow_density_method", "mass_difference_gradient"),
        )
    obs_r = float(row["einstein_radius_arcsec_central"])*float(row["scale_kpc_per_arcsec"])
    sigma = FlatLCDM(70., .3).sigma_crit_msun_per_kpc2(
        float(row["z_deflector"]), float(row["z_source"]),
    )

    def evaluate(density_n, projection_n):
        r = cached_projection["grids"][projection_n]["r"]
        K = cached_projection["grids"][projection_n]["K"]
        density_r = cached_projection["grids"][density_n]["r"]
        rho = np.interp(r, density_r, rho_on_grids[density_n])
        bulge = K @ hernquist_density(r, bm, bre/1.8153)
        disk = np.array([
            projected_disk_mass_exponential(R, dm, dr50/1.67835, qd, ntheta=120)
            for R in r
        ])
        spherical_shadow = K @ rho
        lens_cfg = {
            "shadow_projection": "baryon_structure_circularized",
            "disk_axis_ratio_q": qd,
            "bulge_axis_ratio_q": qb,
        }
        shadow = apply_shadow_projection_mode(
            r, spherical_shadow, lens_cfg, bulge, disk, lens_cfg,
        )
        total = bulge + disk + shadow
        root = solve_einstein_radius_projected(r, total, sigma)
        radius_pull = (
            root/float(row["scale_kpc_per_arcsec"])
            - float(row["einstein_radius_arcsec_central"])
        ) / float(row["einstein_radius_arcsec_err_plus"])
        mass_pull = (
            np.interp(obs_r, r, total)/1e10
            - float(row["lensing_mass_1e10Msun_central"])
        ) / float(row["lensing_mass_1e10Msun_err_plus"])
        joint = abs(radius_pull) <= 2 and abs(mass_pull) <= 2
        bracket = _linearly_interpolated_mass_root(r, total, sigma, root)
        width = float(row["scale_kpc_per_arcsec"])*float(row["einstein_radius_arcsec_err_plus"])
        bracket["radius_pull_shift_from_original_root_sigma"] = (
            bracket["same_mass_linear_M_quadratic_target_root_kpc"] - root
        ) / width
        return {
            "density_grid": density_n, "projection_grid": projection_n,
            "radius_pull_sigma": float(radius_pull), "mass_pull_sigma": float(mass_pull),
            "joint_pass": bool(joint),
            "observed_projected_mass_msun": float(np.interp(obs_r, r, total)),
            "bulge_mass_msun_at_observed_R": float(np.interp(obs_r, r, bulge)),
            "disk_mass_msun_at_observed_R": float(np.interp(obs_r, r, disk)),
            "spherical_shadow_mass_msun_at_observed_R": float(np.interp(obs_r, r, spherical_shadow)),
            "structured_shadow_mass_msun_at_observed_R": float(np.interp(obs_r, r, shadow)),
            "root_interpolation_diagnostic": bracket,
        }

    combinations = {f"rho{n}_K{m}": evaluate(n, m) for n,m in CROSS_PAIRS}
    reference = _analytic_bulge_projected_mass(obs_r, bm, bre)
    bulge = {}
    for n in RADIAL_GRIDS:
        r = cached_projection["grids"][n]["r"]
        K = cached_projection["grids"][n]["K"]
        val = float(np.interp(obs_r, r, K @ hernquist_density(r, bm, bre/1.8153)))
        bulge[str(n)] = {
            "source_matrix_then_R_interpolation_msun": val,
            "relative_error_vs_adaptive_finite_domain": (val-reference)/reference,
        }
    # Fine original source path vs frozen counterpart, no fitting or rescaling.
    fine = evaluate(720, 720)
    original_180 = combinations["rho180_K180"]
    original_360 = combinations["rho360_K360"]
    return {
        "lens_id": str(row["lens_id"]),
        "fixed_observed_R_kpc": obs_r,
        "factorial_density_projection_grid": combinations,
        "fine720_self_consistent_source_proxy": fine,
        "bulge_projected_mass_adaptive_finite_domain_msun": reference,
        "bulge_projection_grid_reference": bulge,
        "source_disk_vs_periodic_angle": _angle_comparison(obs_r, dm, dr50, qd),
        "full_180_to_360_radius_pull_shift_sigma": (
            original_360["radius_pull_sigma"] - original_180["radius_pull_sigma"]
        ),
        "density_only_shift_at_K180_sigma": (
            combinations["rho360_K180"]["radius_pull_sigma"] - original_180["radius_pull_sigma"]
        ),
        "radial_projector_only_shift_at_rho180_sigma": (
            combinations["rho180_K360"]["radius_pull_sigma"] - original_180["radius_pull_sigma"]
        ),
    }


def execute(source_root: str | Path) -> dict:
    """Recompute full 6x4 factorial source diagnostics and frozen slow baseline."""
    import numpy as np
    import scipy
    import pandas as pd
    from native_eset.historical.hist001_source import verify_hist001_source

    source = Path(source_root)
    checked = verify_hist001_source(source)
    if checked["source_lock_sha256"] != SOURCE_SHA256:
        raise D2bIntegrityError("frozen March source identity mismatch")
    with TemporaryDirectory(prefix="hist001d_d2b_original_") as d:
        target = Path(d) / "hist001"
        shutil.copytree(source, target)
        verify_hist001_source(target)
        pack = target / "swells_pack_v2"
        with _verified_source_module_context(pack):
            import solv.run_setA_port_cand as original
            source_rows = original._load_tables(pack)
            if tuple(source_rows["lens_id"]) != LENS_IDS:
                raise D2bIntegrityError("historical lens data/ordering mismatch")
            anchor, _ = original._build_anchor(pack)
            gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
            grids = {
                n: {
                    "r": np.linspace(.02,120.,n),
                    "K": original._projection_matrix(np.linspace(.02,120.,n)),
                } for n in RADIAL_GRIDS
            }
            cached = {"anchor": anchor, "gate": gate, "grids": grids}
            results = [_one_lens(row, original, cached) for row in source_rows.to_dict("records")]
            slow = original.evaluate_portability_dataframe(pack, gate, gate_label=CANDIDATE)
            for diag, row in zip(results, slow.to_dict("records")):
                frozen = diag["factorial_density_projection_grid"]["rho180_K180"]
                if (diag["lens_id"] != row["lens_id"]
                        or abs(frozen["radius_pull_sigma"] - row["einstein_radius_pull_sigma"]) > 1e-9
                        or abs(frozen["mass_pull_sigma"] - row["mass_pull_sigma"]) > 1e-9
                        or frozen["joint_pass"] != bool(row["both_pass"])):
                    raise D2bIntegrityError("source-original frozen 180 baseline mismatch")
            verify_hist001_source(target)
    verify_hist001_source(source)
    if [sum(r["factorial_density_projection_grid"][f"rho{n}_K{n}"]["joint_pass"]
            for r in results) for n in (180,360)] != [6,3]:
        raise D2bIntegrityError("previous source-locked mesh result did not reproduce")
    return {
        "schema": "NATIVE_ESET_HIST001D_D2B_ROOT_CAUSE_DIAGNOSTIC_V1",
        "status": "HIST001D_GRID_ATTRIBUTION_DIAGNOSTIC_NO_ADMISSION",
        "source_lock_sha256": SOURCE_SHA256,
        "candidate": CANDIDATE,
        "root_interpolation": "source_linear_f_vs_same_M_linear_quadratic_critical_target",
        "bulge_reference_domain_kpc": [.02,120.],
        "factorial_pairs": [[a,b] for a,b in CROSS_PAIRS],
        "angular_counts": list(ANGLE_STEPS),
        "data_use": "SIX_ALREADY_FITTED_DEVELOPMENT_LENSES_NOT_HELDOUT",
        "results": results,
        "claims": dict(CLAIMS),
        "environment": {"python":sys.version.split()[0],"numpy":np.__version__,
                        "scipy":scipy.__version__,"pandas":pd.__version__},
        "interpretation": (
            "Radial projector/linear-root/periodic-angle component-level sensitivity; "
            "hybrid grids are numerical counterfactuals, not new fitted or physical models."
        ),
    }


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def run(source_root: str | Path, out_dir: str | Path) -> dict:
    from native_eset.evidence.receipts import canonical_json
    source_path = Path(source_root)
    if source_path.is_symlink():
        raise D2bIntegrityError("symlinked original source root forbidden")
    src, out = source_path.resolve(), Path(out_dir)
    if out.is_symlink() or out.resolve() == src or out.resolve().is_relative_to(src):
        raise D2bIntegrityError("output cannot overlap original source")
    if out.exists():
        raise FileExistsError("D2b report target already exists")
    report = execute(src)
    raw = canonical_json(report)
    receipt = {
        "schema": "NATIVE_ESET_HIST001D_D2B_RECEIPT_V1",
        "report_sha256": _sha(raw),
        "module_sha256": _sha(Path(__file__).read_bytes()),
        "source_lock_sha256": SOURCE_SHA256,
        "status": "HIST001D_ROOT_CAUSE_DIAGNOSTIC_NO_ADMISSION",
        "claims": dict(CLAIMS),
    }
    receipt_raw = canonical_json(receipt)
    out.mkdir(parents=True)
    (out/"report.json").write_bytes(raw)
    (out/"receipt.json").write_bytes(receipt_raw)
    (out/"receipt.sha256").write_text(_sha(receipt_raw)+"\n",encoding="ascii")
    return {"status":receipt["status"],"receipt_sha256":_sha(receipt_raw),
            "out_dir":str(out),"lens_cases":len(report["results"]),"claims":dict(CLAIMS)}


def _equivalent(left, right, path="report"):
    """Fail closed on changed evidence values even if report hashes are remade."""
    if type(left) is not type(right):
        raise D2bIntegrityError(f"mismatched data type at {path}")
    if isinstance(right, dict):
        if left.keys() != right.keys():
            raise D2bIntegrityError(f"missing/extra keys at {path}")
        for k in right:
            if k == "environment" and path == "report":
                # Other platform versions recorded but not part of numeric equality.
                continue
            _equivalent(left[k], right[k], path+"."+str(k))
    elif isinstance(right, list):
        if len(left) != len(right):
            raise D2bIntegrityError(f"missing/extra data at {path}")
        for i,(a,b) in enumerate(zip(left,right)):
            _equivalent(a,b,path+"["+str(i)+"]")
    elif type(right) is float:
        if not math.isfinite(left) or abs(left-right)>1e-8*max(1.,abs(right)):
            raise D2bIntegrityError(f"source numerical value mismatch at {path}")
    elif left != right:
        raise D2bIntegrityError(f"modified source diagnostic at {path}")


def verify(receipt_path: str | Path, source_root: str | Path,
           expected_sha256: str | None=None) -> dict:
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    p = Path(receipt_path)
    if p.name != "receipt.json" or p.is_symlink() or p.parent.is_symlink():
        raise D2bIntegrityError("unsafe receipt target")
    files = list(p.parent.iterdir())
    if {file.name for file in files} != {"receipt.json","report.json","receipt.sha256"}:
        raise D2bIntegrityError("unexpected receipt members")
    if any(q.is_symlink() or not q.is_file() for q in files):
        raise D2bIntegrityError("unsafe receipt member")
    raw=p.read_bytes();digest=_sha(raw)
    if (p.parent/"receipt.sha256").read_text(encoding="ascii") != digest+"\n":
        raise D2bIntegrityError("receipt SHA text mismatch")
    if expected_sha256 is not None and digest!=expected_sha256:
        raise D2bIntegrityError("external receipt SHA mismatch")
    receipt,report=strict_loads(raw),strict_loads((p.parent/"report.json").read_bytes())
    if (canonical_json(receipt)!=raw or
            canonical_json(report)!=(p.parent/"report.json").read_bytes()):
        raise D2bIntegrityError("noncanonical JSON evidence")
    if (receipt.get("schema")!="NATIVE_ESET_HIST001D_D2B_RECEIPT_V1"
            or receipt.get("status")!="HIST001D_ROOT_CAUSE_DIAGNOSTIC_NO_ADMISSION"
            or receipt.get("source_lock_sha256")!=SOURCE_SHA256
            or receipt.get("module_sha256")!=_sha(Path(__file__).read_bytes())
            or receipt.get("report_sha256")!=_sha((p.parent/"report.json").read_bytes())
            or receipt.get("claims")!=CLAIMS or len(receipt)!=6):
        raise D2bIntegrityError("receipt source/identity/claim mismatch")
    if (report.get("schema")!="NATIVE_ESET_HIST001D_D2B_ROOT_CAUSE_DIAGNOSTIC_V1"
            or report.get("status")!="HIST001D_GRID_ATTRIBUTION_DIAGNOSTIC_NO_ADMISSION"
            or report.get("claims")!=CLAIMS or report.get("source_lock_sha256")!=SOURCE_SHA256):
        raise D2bIntegrityError("report tried to change authority")
    independent=execute(source_root)
    _equivalent(report,independent)
    return {"status":"HIST001D_D2B_INDEPENDENT_SOURCE_REEXECUTION_PASS_NO_ADMISSION",
            "receipt_sha256":digest,"cases_verified":len(independent["results"]),
            "claims":dict(CLAIMS)}


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root",required=True,type=Path)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out",type=Path)
    mode.add_argument("--verify",type=Path)
    parser.add_argument("--expected-sha256")
    args=parser.parse_args()
    try:
        out=verify(args.verify,args.source_root,args.expected_sha256) if args.verify else run(args.source_root,args.out)
    except (OSError,ValueError,KeyError,TypeError,ImportError) as exc:
        print(json.dumps({"status":"HIST001D_D2B_FAIL_CLOSED","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(out,sort_keys=True));return 0

if __name__=="__main__":
    raise SystemExit(main())
