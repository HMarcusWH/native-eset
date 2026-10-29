"""HIST-001D: source-locked Set A mesh/angle diagnostics, NOT lensing validation.

All six cases are original fitted/development lenses. No parameter refit, new
holdout, source edit, modern covariant Weyl prediction or provider admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

SOURCE_SHA = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
REGIMES = (
    ("radial_coarse", 90, 120),
    ("frozen_baseline", 180, 120),
    ("radial_fine", 360, 120),
    ("angle_coarse", 180, 60),
    ("angle_fine", 180, 240),
    ("combined_fine", 360, 240),
)
CLAIM = {
    "historical_regression_only": True, "new_holdout_evaluated": False,
    "physical_weyl_lensing_derived": False, "empirical_validation": "NOT_ESTABLISHED",
    "native_v172_equivalence_proved": False, "physical_provider_admitted": False,
}


class Hist001DIntegrityError(ValueError):
    """Source, output inventory, numeric replay or nonpromotion check failed."""


def evaluate(pack: Path, radial_points: int, angular_points: int,
             *, inputs: tuple | None = None) -> list[dict]:
    """Run original, SHA-locked numerical ingredients with explicit resolution."""
    import numpy as np
    import solv.run_setA_port_cand as original
    from solv.baryons import J2141BaryonicModel
    from solv.cosmology import FlatLCDM
    from solv.dmalane import build_gate_components, epsilon_from_config
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.run_j2141_axisym_lens import (
        apply_shadow_projection_mode, hernquist_density,
        projected_disk_mass_exponential, solve_einstein_radius_projected,
    )
    from solv.shadow_density import compute_shadow_density

    if (radial_points, angular_points) not in {
        (n, a) for _, n, a in REGIMES
    }:
        raise Hist001DIntegrityError("unregistered grid/angle pair")
    if inputs is None:
        seta = original._load_tables(pack)
        anchor, _ = original._build_anchor(pack)
        gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
    else:
        seta, anchor, gate = inputs
    if tuple(seta.lens_id) != LENS_IDS:
        raise Hist001DIntegrityError("original six-lens identity or order changed")
    r = np.linspace(0.02, 120.0, radial_points)
    K = original._projection_matrix(r)
    cosmology = FlatLCDM(70.0, 0.3)
    rows = []
    for lens in seta.itertuples(index=False):
        bm = 10 ** float(lens.logM_bulge_chabrier_central)
        dm = 10 ** float(lens.logM_disc_chabrier_central)
        bre = float(lens.Re_bulge_arcsec) * float(lens.scale_kpc_per_arcsec)
        dr50 = float(lens.Re_disc_arcsec) * float(lens.scale_kpc_per_arcsec)
        qb, qd = float(lens.q_bulge), float(lens.q_disc)
        model = J2141BaryonicModel(bm, bre, dm, dr50)
        features = extract_gate_features_from_values(
            bm, bre, dm, dr50, qb, qd,
            ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
        )
        gb = model.total_vbar(r) ** 2 / r
        components = build_gate_components(gate, features=features, anchor=anchor)
        eps = epsilon_from_config(r, gb, gate, features=features, anchor=anchor)
        density = compute_shadow_density(
            r, gb, gb / eps, epsilon=eps,
            method=components.get("shadow_density_method", "mass_difference_gradient"),
        )
        bulge = K @ hernquist_density(r, bm, bre / 1.8153)
        disk = np.array([
            projected_disk_mass_exponential(R, dm, dr50 / 1.67835, qd,
                                            ntheta=angular_points)
            for R in r
        ])
        shadow_sphere = K @ np.nan_to_num(density, nan=0.0)
        lens_cfg = {
            "shadow_projection": "baryon_structure_circularized",
            "disk_axis_ratio_q": qd, "bulge_axis_ratio_q": qb,
        }
        shadow = apply_shadow_projection_mode(
            r, shadow_sphere, lens_cfg, bulge, disk, lens_cfg,
        )
        total = bulge + disk + shadow
        sigma_crit = cosmology.sigma_crit_msun_per_kpc2(
            float(lens.z_deflector), float(lens.z_source),
        )
        predicted_radius = (
            solve_einstein_radius_projected(r, total, sigma_crit)
            / float(lens.scale_kpc_per_arcsec)
        )
        predicted_mass = float(
            np.interp(float(lens.einstein_radius_arcsec_central)
                      * float(lens.scale_kpc_per_arcsec), r, total) / 1e10
        )
        radius_pull = (
            predicted_radius - float(lens.einstein_radius_arcsec_central)
        ) / float(lens.einstein_radius_arcsec_err_plus)
        mass_pull = (
            predicted_mass - float(lens.lensing_mass_1e10Msun_central)
        ) / float(lens.lensing_mass_1e10Msun_err_plus)
        if not all(math.isfinite(x) for x in (
            predicted_radius, predicted_mass, radius_pull, mass_pull,
        )):
            raise Hist001DIntegrityError("nonfinite numerical lens output")
        rows.append({
            "lens_id": str(lens.lens_id),
            "predicted_radius_arcsec": float(predicted_radius),
            "predicted_projected_mass_1e10_msun": predicted_mass,
            "radius_pull_sigma": float(radius_pull), "mass_pull_sigma": float(mass_pull),
            "radius_pass": bool(abs(radius_pull) <= 2),
            "mass_pass": bool(abs(mass_pull) <= 2),
            "joint_pass": bool(abs(radius_pull) <= 2 and abs(mass_pull) <= 2),
        })
    return rows


def summarize(groups: dict) -> list[dict]:
    if set(groups) != {name for name, _, _ in REGIMES}:
        raise Hist001DIntegrityError("numerical regimes incomplete")
    base = groups["frozen_baseline"]
    summary = []
    for name, radial, angular in REGIMES:
        rows = groups[name]
        if ([x["lens_id"] for x in rows] != list(LENS_IDS)
                or len(rows) != len(base)):
            raise Hist001DIntegrityError("six-lens inventory drift")
        summary.append({
            "regime": name, "radial_points": radial, "angular_points": angular,
            "joint_passes": sum(row["joint_pass"] for row in rows),
            "mean_abs_radius_pull_sigma": sum(
                abs(row["radius_pull_sigma"]) for row in rows
            ) / 6,
            "mean_abs_mass_pull_sigma": sum(
                abs(row["mass_pull_sigma"]) for row in rows
            ) / 6,
            "max_abs_radius_pull_shift_vs_baseline": max(
                abs(x["radius_pull_sigma"] - b["radius_pull_sigma"])
                for x, b in zip(rows, base)
            ),
            "max_abs_mass_pull_shift_vs_baseline": max(
                abs(x["mass_pull_sigma"] - b["mass_pull_sigma"])
                for x, b in zip(rows, base)
            ),
            "changed_joint_pass_lenses": [
                x["lens_id"] for x, b in zip(rows, base)
                if x["joint_pass"] != b["joint_pass"]
            ],
        })
    return summary


def execute(source_root: str | Path) -> dict:
    """Read source only, execute source-verified code on disposable copy."""
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    source = Path(source_root)
    verified = verify_hist001_source(source)
    if verified["source_lock_sha256"] != SOURCE_SHA:
        raise Hist001DIntegrityError("frozen source lock differs")
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        with TemporaryDirectory(prefix="hist001d-frozen-") as d:
            copy = Path(d) / "hist001"
            shutil.copytree(source, copy)
            verify_hist001_source(copy)
            pack = copy / "swells_pack_v2"
            sys.path.insert(0, str(pack))
            try:
                import solv.run_setA_port_cand as original
                anchor, _ = original._build_anchor(pack)
                gate = original._candidate_gate_config(
                    anchor, candidate_name=CANDIDATE,
                )
                inputs = (original._load_tables(pack), anchor, gate)
                groups = {
                    name: evaluate(pack, n, a, inputs=inputs)
                    for name, n, a in REGIMES
                }
                slow = original.evaluate_portability_dataframe(
                    pack, gate, gate_label=CANDIDATE,
                )
                if list(slow.lens_id) != list(LENS_IDS):
                    raise Hist001DIntegrityError("slow original source lens order changed")
                for candidate, original_row in zip(
                    groups["frozen_baseline"], slow.to_dict("records")
                ):
                    if (
                        abs(candidate["radius_pull_sigma"] - float(
                            original_row["einstein_radius_pull_sigma"]
                        )) > 1e-9
                        or abs(candidate["mass_pull_sigma"] - float(
                            original_row["mass_pull_sigma"]
                        )) > 1e-9
                        or candidate["joint_pass"] != bool(original_row["both_pass"])
                    ):
                        raise Hist001DIntegrityError(
                            "frozen 180/120 baseline disagrees with original solver"
                        )
                verify_hist001_source(copy)
            finally:
                sys.path.remove(str(pack))
    finally:
        sys.dont_write_bytecode = old_bytecode
    verify_hist001_source(source)
    return {
        "schema": "NATIVE_ESET_HIST001D_CONVERGENCE_DIAGNOSTIC_V1",
        "source_lock_sha256": SOURCE_SHA, "candidate": CANDIDATE,
        "data_use": "EXISTING_DEVELOPMENT_REGRESSION_ONLY",
        "fixed_cosmology": {"H0_km_s_Mpc": 70.0, "Omega_m": 0.3},
        "reference_grid": {
            "radial_points": 180, "angular_points": 120,
            "radial_start_kpc": 0.02, "radial_stop_kpc": 120.0,
        },
        "regimes": [
            {"id": name, "radial_points": n, "angular_points": a}
            for name, n, a in REGIMES
        ],
        "baseline_matches_original_slow_solver": True,
        "results": groups, "summary": summarize(groups),
        "claim_boundary": dict(CLAIM),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": scipy.__version__,
        },
        "interpretation": (
            "Frozen fitted projected-density discretization diagnostic only; "
            "no physical Weyl or independent holdout validation"
        ),
    }


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(source_root: str | Path, out_dir: str | Path) -> dict:
    """Create one immutable, independently verifiable nonpromoting receipt."""
    from native_eset.evidence.receipts import canonical_json

    source, dest = Path(source_root), Path(out_dir)
    if dest.resolve() == source.resolve() or dest.resolve().is_relative_to(source.resolve()):
        raise Hist001DIntegrityError("diagnostic cannot write into original source")
    if dest.exists():
        raise FileExistsError("output directory already exists; no overwrites")
    report = execute(source)
    report_bytes = canonical_json(report)
    receipt = {
        "schema": "NATIVE_ESET_HIST001D_DIAGNOSTIC_RECEIPT_V1",
        "status": "HIST001D_NUMERICAL_GRID_DIAGNOSTIC_ONLY",
        "report_sha256": _sha(report_bytes),
        "module_sha256": _sha(Path(__file__).read_bytes()),
        "source_lock_sha256": SOURCE_SHA,
        "claim_boundary": dict(CLAIM),
    }
    receipt_bytes = canonical_json(receipt)
    dest.mkdir(parents=True)
    (dest / "report.json").write_bytes(report_bytes)
    (dest / "receipt.json").write_bytes(receipt_bytes)
    (dest / "receipt.sha256").write_text(
        _sha(receipt_bytes) + "\n", encoding="ascii",
    )
    return {"status": receipt["status"], "receipt_sha256": _sha(receipt_bytes),
            "output_dir": str(dest), "summary": report["summary"],
            "claim_boundary": dict(CLAIM)}


def verify_receipt(receipt_path: str | Path, source_root: str | Path,
                   expected_sha256: str | None = None) -> dict:
    """Reexecute SHA-pinned original for all 36 lens/regime rows; reject selfhash forgeries."""
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads

    path = Path(receipt_path)
    folder = path.parent
    if path.name != "receipt.json" or folder.is_symlink():
        raise Hist001DIntegrityError("receipt path must be an immutable receipt.json")
    names = {p.name for p in folder.iterdir()}
    if names != {"report.json", "receipt.json", "receipt.sha256"}:
        raise Hist001DIntegrityError("missing/extra receipt file")
    if any(p.is_symlink() or not p.is_file() for p in folder.iterdir()):
        raise Hist001DIntegrityError("unsafe receipt member")
    receipt_bytes, report_bytes = path.read_bytes(), (folder / "report.json").read_bytes()
    digest = _sha(receipt_bytes)
    if (folder / "receipt.sha256").read_text(encoding="ascii") != digest + "\n":
        raise Hist001DIntegrityError("receipt self-check failed")
    if expected_sha256 is not None and digest != expected_sha256:
        raise Hist001DIntegrityError("receipt differs from externally pinned SHA")
    receipt, report = strict_loads(receipt_bytes), strict_loads(report_bytes)
    if (canonical_json(receipt) != receipt_bytes
            or canonical_json(report) != report_bytes):
        raise Hist001DIntegrityError("noncanonical JSON receipt/report")
    if (set(receipt) != {
        "schema", "status", "report_sha256", "module_sha256",
        "source_lock_sha256", "claim_boundary",
    } or receipt["schema"] != "NATIVE_ESET_HIST001D_DIAGNOSTIC_RECEIPT_V1"
            or receipt["status"] != "HIST001D_NUMERICAL_GRID_DIAGNOSTIC_ONLY"
            or receipt["report_sha256"] != _sha(report_bytes)
            or receipt["module_sha256"] != _sha(Path(__file__).read_bytes())
            or receipt["source_lock_sha256"] != SOURCE_SHA
            or receipt["claim_boundary"] != CLAIM):
        raise Hist001DIntegrityError("receipt schema/integrity/claim mismatch")
    if (report.get("schema") != "NATIVE_ESET_HIST001D_CONVERGENCE_DIAGNOSTIC_V1"
            or report.get("data_use") != "EXISTING_DEVELOPMENT_REGRESSION_ONLY"
            or report.get("source_lock_sha256") != SOURCE_SHA
            or report.get("candidate") != CANDIDATE
            or report.get("claim_boundary") != CLAIM
            or report.get("baseline_matches_original_slow_solver") is not True
            or report.get("regimes") != [
                {"id": name, "radial_points": n, "angular_points": a}
                for name, n, a in REGIMES
            ] or report.get("summary") != summarize(report["results"])):
        raise Hist001DIntegrityError("report numerical/authority metadata invalid")
    if report["summary"][1]["joint_passes"] != 6:
        raise Hist001DIntegrityError("historical 6/6 frozen reference lost")
    independently_recomputed = execute(source_root)
    for name, _, _ in REGIMES:
        actual, expected = report["results"][name], independently_recomputed["results"][name]
        if len(actual) != len(expected):
            raise Hist001DIntegrityError("missing/extra lens diagnostic row")
        for left, right in zip(actual, expected):
            if set(left) != set(right):
                raise Hist001DIntegrityError("unexpected lens diagnostic fields")
            for field, value in right.items():
                observed = left[field]
                if type(value) is bool or isinstance(value, str):
                    if observed != value:
                        raise Hist001DIntegrityError("lens identity/gate not reproduced")
                elif (type(observed) not in (int, float)
                      or not math.isfinite(observed)
                      or abs(observed - value) > 1e-9):
                    raise Hist001DIntegrityError("source numerical result not reproduced")
    return {
        "status": "HIST001D_SOURCE_REEXECUTED_DIAGNOSTIC_RECEIPT_VERIFIED_NO_ADMISSION",
        "receipt_sha256": digest, "source_lock_sha256": SOURCE_SHA,
        "original_rows_reexecuted": len(REGIMES) * len(LENS_IDS),
        "claim_boundary": dict(CLAIM),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        result = (
            verify_receipt(args.verify, args.source_root, args.expected_sha256)
            if args.verify is not None else run(args.source_root, args.out)
        )
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(json.dumps({"status": "HIST001D_FAIL_CLOSED", "error": str(exc)},
                         sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
