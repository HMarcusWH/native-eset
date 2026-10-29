"""HIST-001B: fail-closed independent geometry-nuisance replay.

This is a historical FITTED regression and RNG audit, not an admitted
Native ESET v1.7.2 lensing or cosmological observable provider. The
original 46 historical files are never edited or refitted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Prevent imports from writing __pycache__ into the SHA-locked original
# historical source tree. This standalone CLI owns the interpreter process.
sys.dont_write_bytecode = True

WIDTHS = (0.01, 0.02, 0.05, 0.10)
SEED_ROOT = 2141
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
FRACTIONAL = ("q_bulge", "q_disc", "Re_bulge_arcsec", "Re_disc_arcsec")
MASSES = ("logM_bulge_chabrier_central", "logM_disc_chabrier_central")
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)


def prepare(pack: Path) -> tuple:
    import solv.run_setA_port_cand as original
    from solv.cosmology import FlatLCDM

    base = original._load_tables(pack).copy()
    if tuple(base["lens_id"]) != LENS_IDS:
        raise ValueError("historical six-lens identity/order changed")
    anchor, _ = original._build_anchor(pack)
    gate = original._candidate_gate_config(anchor, candidate_name=CANDIDATE)
    r = np.linspace(0.02, 120.0, 180)
    projection = original._projection_matrix(r)
    theta = np.linspace(0, 2 * np.pi, 120, endpoint=False)
    cosmology = FlatLCDM(70.0, 0.3)
    sigma = [
        cosmology.sigma_crit_msun_per_kpc2(float(row.z_deflector), float(row.z_source))
        for row in base.itertuples()
    ]
    return original, base, anchor, gate, r, projection, theta, sigma


def perturb(base: pd.DataFrame, width: float, trial: int) -> pd.DataFrame:
    # Recovered multiprocessing-source RNG, not inferred from archived outcomes.
    rng = np.random.default_rng(np.random.SeedSequence([SEED_ROOT, int(trial)]))
    table = base.copy()
    for column in FRACTIONAL:
        table[column] = table[column].astype(float) * rng.uniform(
            1 - width, 1 + width, size=len(table)
        )
    for column in MASSES:
        table[column] = table[column].astype(float) + np.log10(
            rng.uniform(1 - width, 1 + width, size=len(table))
        )
    for column in ("q_bulge", "q_disc"):
        table[column] = table[column].clip(1e-3, 1.0)
    return table


def _disk_projection(r: np.ndarray, mass: float, disk_scale: float,
                     q: float, theta: np.ndarray) -> np.ndarray:
    # Vectorized over radius only; same original 120-angle trapezoid formula.
    q = float(np.clip(q, 1e-3, 1.0))
    angles = np.sqrt(np.cos(theta) ** 2 + np.sin(theta) ** 2 / q**2)
    x = r[:, None] * angles[None, :] / disk_scale
    inner = disk_scale**2 / angles[None, :]**2 * (
        1 - np.exp(-x) * (1 + x)
    )
    surface = mass / (2 * np.pi * q * disk_scale**2)
    return surface * np.trapezoid(inner, theta, axis=1)


def evaluate(prepared: tuple, table: pd.DataFrame) -> dict:
    from solv.baryons import J2141BaryonicModel
    from solv.gate_struct import (
        A0_MPS2, compute_transition_radius_kpc, extract_gate_features_from_values,
    )
    from solv.dmalane import build_gate_components, epsilon_from_config
    from solv.shadow_density import compute_shadow_density
    from solv.run_j2141_axisym_lens import (
        apply_shadow_projection_mode, hernquist_density,
        solve_einstein_radius_projected,
    )

    _, _, anchor, gate, radius, projection, theta, sigma = prepared
    records = []
    for i, row in enumerate(table.itertuples()):
        bulge_mass = 10**float(row.logM_bulge_chabrier_central)
        disk_mass = 10**float(row.logM_disc_chabrier_central)
        bulge_radius = row.Re_bulge_arcsec * row.scale_kpc_per_arcsec
        disk_radius = row.Re_disc_arcsec * row.scale_kpc_per_arcsec
        qb, qd = float(row.q_bulge), float(row.q_disc)
        model = J2141BaryonicModel(
            bulge_mass, bulge_radius, disk_mass, disk_radius,
        )
        features = extract_gate_features_from_values(
            bulge_mass, bulge_radius, disk_mass, disk_radius, qb, qd,
            ra0_kpc=compute_transition_radius_kpc(model, a0_mps2=A0_MPS2),
        )
        gbar = model.total_vbar(radius)**2 / radius
        components = build_gate_components(
            gate, features=features, anchor=anchor,
        )
        epsilon = epsilon_from_config(
            radius, gbar, gate, features=features, anchor=anchor,
        )
        density = compute_shadow_density(
            radius, gbar, gbar / epsilon, epsilon=epsilon,
            method=components.get("shadow_density_method", "mass_difference_gradient"),
        )
        bulge_proj = projection.dot(
            hernquist_density(radius, bulge_mass, bulge_radius / 1.8153)
        )
        disk_proj = _disk_projection(
            radius, disk_mass, disk_radius / 1.67835, qd, theta,
        )
        shadow_spherical = projection.dot(np.nan_to_num(density, nan=0.0))
        lens = {
            "shadow_projection": "baryon_structure_circularized",
            "disk_axis_ratio_q": qd,
            "bulge_axis_ratio_q": qb,
        }
        shadow = apply_shadow_projection_mode(
            radius, shadow_spherical, lens, bulge_proj, disk_proj, lens,
        )
        total = bulge_proj + disk_proj + shadow
        predicted_radius = solve_einstein_radius_projected(
            radius, total, sigma[i],
        )
        radius_pull = (
            predicted_radius / row.scale_kpc_per_arcsec
            - row.einstein_radius_arcsec_central
        ) / row.einstein_radius_arcsec_err_plus
        mass_pull = (
            np.interp(
                row.einstein_radius_arcsec_central * row.scale_kpc_per_arcsec,
                radius, total,
            ) / 1e10 - row.lensing_mass_1e10Msun_central
        ) / row.lensing_mass_1e10Msun_err_plus
        if not (math.isfinite(radius_pull) and math.isfinite(mass_pull)):
            raise ValueError("non-finite historical regression output")
        records.append((str(row.lens_id), float(radius_pull), float(mass_pull)))
    if tuple(row[0] for row in records) != LENS_IDS:
        raise ValueError("wrong Set A lens rows")
    radius_pass = [abs(x[1]) <= 2 for x in records]
    mass_pass = [abs(x[2]) <= 2 for x in records]
    failed = [
        x[0] for x, a, b in zip(records, radius_pass, mass_pass) if not a or not b
    ]
    return {
        "n_both_pass": 6 - len(failed),
        "n_radius_pass": sum(radius_pass),
        "n_mass_pass": sum(mass_pass),
        "mean_abs_radius_pull_sigma": sum(abs(x[1]) for x in records) / 6,
        "mean_abs_mass_pull_sigma": sum(abs(x[2]) for x in records) / 6,
        "failed_lenses": ";".join(failed),
        **{f"fail_{x[0]}": x[0] in failed for x in records},
    }


def check_against_original(prepared: tuple, table: pd.DataFrame,
                           pack: Path, fast: dict) -> None:
    """Source-original slow evaluator is independent of the fast contractions."""
    from solv.scoring import seta_suite_score

    original, _, _, gate, *_ = prepared
    loader = original._load_tables
    try:
        original._load_tables = lambda _root: table.copy()
        raw = original.evaluate_portability_dataframe(
            pack, gate, gate_label=CANDIDATE,
        )
    finally:
        original._load_tables = loader
    slow = {row.metric: row.value for row in seta_suite_score(raw).itertuples()}
    for key in slow:
        if key.startswith("mean_abs_"):
            if not math.isclose(fast[key], slow[key], abs_tol=1e-9, rel_tol=0):
                raise ValueError("fast/source numerical disagreement: " + key)
        elif key != "n_lenses_tested" and fast[key] != slow[key]:
            raise ValueError("fast/source gate disagreement: " + key)


def check_half_projection(pack: Path, prepared: tuple) -> dict:
    """Independent no-refit Set A half-circularization negative control."""
    from solv.scoring import seta_suite_score

    original, *_ = prepared
    old = original.apply_shadow_projection_mode

    def half(r, m, config, bulge, disk, metadata):
        qb = float(config["bulge_axis_ratio_q"])
        qd = float(config["disk_axis_ratio_q"])
        qeff = np.clip(
            (qb * bulge + qd * disk) / np.clip(bulge + disk, 1e-30, None),
            1e-3, 1.0,
        )
        factor = 1 - 0.5 * (1 - np.sqrt(qeff))
        return np.interp(r / factor, r, m, left=m[0], right=m[-1])

    try:
        original.apply_shadow_projection_mode = half
        rows = original.evaluate_portability_dataframe(
            pack, prepared[3], gate_label=CANDIDATE,
        )
    finally:
        original.apply_shadow_projection_mode = old
    scores = {row.metric: row.value for row in seta_suite_score(rows).itertuples()}
    expected = {
        "n_both_pass": 2, "n_radius_pass": 2, "n_mass_pass": 5,
        "mean_abs_radius_pull_sigma": 5.582136435311303,
        "mean_abs_mass_pull_sigma": 1.8743997197121056,
        "failed_lenses": "J0822+1828;J0915+4211;J0930+2855;J1111+2234",
    }
    for key, value in expected.items():
        if isinstance(value, float):
            if not math.isclose(float(scores[key]), value, abs_tol=1e-8, rel_tol=0):
                raise ValueError("half-circularization archival mismatch: " + key)
        elif scores[key] != value:
            raise ValueError("half-circularization archival mismatch: " + key)
    return {key: scores[key] for key in expected}


def replay(source_root: Path, output_root: Path, *,
           trials: int = 1000, smoke: bool = False) -> dict:
    # Trust source bytes before importing ANY recovered historical module.
    from native_eset.historical.hist001_source import verify_hist001_source

    source_root = source_root.resolve(strict=True)
    verified = verify_hist001_source(source_root)
    if verified["frozen_files"] != 46 or verified["archived_negative_records"] != 3:
        raise ValueError("historical source inventory changed")
    if not smoke and trials != 1000:
        raise ValueError("the full audit requires exactly 1000 trials per width")
    if smoke and not (1 <= trials <= 8):
        raise ValueError("smoke limit must be 1..8 trials")
    pack = source_root / "swells_pack_v2"
    output_root = output_root.absolute()
    if (output_root == source_root or output_root.is_relative_to(source_root)
            or source_root.is_relative_to(output_root) or output_root.exists()):
        raise ValueError("output must be new and disjoint from the frozen source")
    sys.path.insert(0, str(pack))
    prepared = prepare(pack)
    archived_file = source_root / "archived_rangefinder" / (
        "reg_v2_fixed_law_geometry_morphology_nuisance_survival_curve_summary.json"
    )
    archived = json.loads(archived_file.read_text(encoding="utf-8"))
    original = {float(x["rel_width"]): x for x in archived["summaries"]}
    if set(original) != set(WIDTHS) or [original[x]["n_at_6_of_6"] for x in WIDTHS] != [
        323, 140, 23, 3
    ]:
        raise ValueError("unexpected frozen archive reference")
    half = check_half_projection(pack, prepared)
    output_root.mkdir(parents=True)
    results = []
    widths = (0.01,) if smoke else WIDTHS
    for width in widths:
        csv_path = output_root / f"width_{round(width * 100):02d}pct.csv"
        rows = []
        for trial in range(trials):
            table = perturb(prepared[1], width, trial)
            fast = evaluate(prepared, table)
            if trial < 2:
                check_against_original(prepared, table, pack, fast)
            rows.append({"trial": trial, **fast})
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        six = sum(row["n_both_pass"] == 6 for row in rows)
        five = sum(row["n_both_pass"] >= 5 for row in rows)
        results.append({
            "width": width, "n_trials": trials, "six_of_six": six,
            "five_or_more": five,
            "archived_six_of_six": original[width]["n_at_6_of_6"],
            "archived_five_or_more": original[width]["n_at_5_or_more"],
            "trial_csv": csv_path.name,
            "trial_csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
            "archived_count_match": six == original[width]["n_at_6_of_6"]
            and five == original[width]["n_at_5_or_more"],
        })
    match = all(x["archived_count_match"] for x in results)
    full = not smoke
    status = (
        "HIST001B_SOURCE_EXACT_REPLAY_MATCHED_NOT_VALIDATED" if full and match
        else "HIST001B_ARCHIVED_REPLAY_MISMATCH_FAIL_CLOSED" if full
        else "HIST001B_SMOKE_ONLY_NOT_REEXECUTED"
    )
    report = {
        "schema": "NATIVE_ESET_HIST001B_REPLAY_AUDIT_V1",
        "status": status, "seed_root": SEED_ROOT,
        "seed_scheme": "SeedSequence([2141, trial])",
        "candidate": CANDIDATE,
        "perturbed_inputs": list(FRACTIONAL + MASSES),
        "trial_schedule": "four frozen 1/2/5/10% widths" if full else "1% smoke only",
        "source_lock_sha256": verified.get("source_lock_sha256"),
        "fixed_original_files": 46,
        "fixed_archived_negative_records": 3,
        "source_original_comparison": "first two trials of each executed width",
        "half_circularization": half,
        "archived_reference_is_new_output": False,
        "physical_provider_admitted": False,
        "native_v172_equivalence_proved": False,
        "empirical_validation": "NOT_ESTABLISHED",
        "results": results,
        "note": (
            "The archived 600-transition-check acceleration implementation and "
            "exact old trial RNG realization are not proved recovered. "
            "A count mismatch is a blocker, not a tolerance-adjustment request."
        ),
    }
    (output_root / "audit.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--trials", type=int, default=1000)
    args = parser.parse_args()
    try:
        report = replay(args.source_root, args.out, trials=args.trials, smoke=args.smoke)
    except (ValueError, OSError, KeyError) as exc:
        print(json.dumps({"status": "HIST001B_FAIL_CLOSED", "error": str(exc)}))
        return 2
    print(json.dumps({
        "status": report["status"],
        "results": report["results"],
        "half_circularization": report["half_circularization"],
    }, sort_keys=True))
    return 0 if args.smoke or all(x["archived_count_match"] for x in report["results"]) else 4


if __name__ == "__main__":
    raise SystemExit(main())
