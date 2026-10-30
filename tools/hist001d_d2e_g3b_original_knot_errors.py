"""D2e-G3b: source-locked ORIGINAL March 180x120 knot-output discrepancy.

At 12 input-preregistered 180-radial-grid KNOTS, reconstruct the frozen
March K-matrix bulge and original 120-angle omitted-arc disk outputs with the
unchanged source functions. The original q_eff formula is an internal
intermediate, here derived from those two source-computed arrays.

Compare each exact returned binary64 to G1/G2b certified mathematical
continuum intervals using exact-rational a posteriori inequalities.

This is NOT a continuous-R source-error bound, a certified numerical root,
independent holdout, physical Weyl metric, or theory/provider admission.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from native_eset.historical.hist001d_g3b_knot_preregistration import (
    G3bRegistrationError, LENS_IDS, SOURCE_SHA256,
    original_source_grid, register_two_source_knots,
)
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

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "registry/hist001d_d2e_g3b_knots_v1.json"
REGISTRY_SHA256 = "b561182ef3569152408c75d97218b6daa80ab3bdab3e3037ce0b2d0eef3b0180"
G3A_SHA256 = "28156b62ccd888fbc26d08922d12f075a47eb1e8d2f4a058ee624ee357ec7836"
SOURCE_TABLE_SHA256 = "d087578dccfaea72dafb2098c925d4111c41015a56f59ca1292b20eccb797ac8"
SOURCE_SCALE_SHA256 = "6a91426ec9818d3d88244e0588c5f2014318cc5077bed0c971d5a02e91efc074"
SOURCE_D2E_SHA256 = "ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2"
CANDIDATE = "ra0_gated_geometry_sigmoid_reg_v2"
ROLES = ("observed_role", "d2d_role")
SCHEMA = "NATIVE_ESET_HIST001D_D2E_G3B_ORIGINAL_MARCH_180x120_KNOT_ERRORS_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_G3B_ORIGINAL_SOURCE_RECEIPT_V1"
STATUS = "G3B_ORIGINAL_MARCH_KNOT_DISCREPANCY_CERTIFIED_POINTWISE_NOT_ROOT"

CLAIMS = {
    "original_march_k_matrix_bulge_return_discrepancy_at_12_knots": True,
    "original_march_120_angle_disk_return_discrepancy_at_12_knots": True,
    "derived_original_march_qeff_discrepancy_at_12_knots": True,
    "frozen_development_lenses_only": True,
    "preregistered_original_grid_knot_indices": True,
    "original_march_all_180_grid_outputs_certified": False,
    "original_march_arbitrary_radius_numeric_error_certified": False,
    "interpolated_observed_or_d2d_radius_outputs_certified": False,
    "original_density_continuum_error_bounded": False,
    "critical_surface_density_error_bounded": False,
    "total_numerical_root_error_certified": False,
    "global_root_uniqueness_certified": False,
    "mass_outside_finite_domain_bounded": False,
    "current_native_v172_equivalence_proved": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "new_independent_holdout_scored": False,
    "original_source_modified": False,
    "canonical_theory_state_mutated": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class G3bError(ValueError):
    """Deny altered source, unregistered knot, mismatched value or forged claim."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_preregistration():
    from native_eset.serialization import strict_loads

    p = REGISTRY_PATH
    if p.is_symlink() or not p.is_file() or _sha(p.read_bytes()) != REGISTRY_SHA256:
        raise G3bError("input-only preregistration bytes changed")
    document = strict_loads(p.read_bytes())
    if (document.get("source_sha256") != SOURCE_SHA256
            or document.get("schema") !=
            "HIST001D_G3B_ORIGINAL_MARCH_180x120_KNOT_SELECTION_V1"
            or document.get("status") !=
            "INPUTS_AND_SOURCE_KNOT_SELECTION_PREREGISTERED_NOT_ERROR_CERTIFIED"
            or document.get("selector", {}).get("selection_uses_source_mass_outputs") is not False
            or len(document.get("preregistrations", [])) != 6
            or tuple(item["lens_id"] for item in document["preregistrations"]) != LENS_IDS
            or document.get("claims", {}).get("physical_provider_admitted") is not False):
        raise G3bError("untrusted source-knot preregistration")
    return document


def _load_g3a():
    p = Path(__file__).resolve().with_name("hist001d_d2e_g3a_pointwise_baryons.py")
    if p.is_symlink() or not p.is_file() or _sha(p.read_bytes()) != G3A_SHA256:
        raise G3bError("pinned G3a numerical prerequisite changed")
    spec = importlib.util.spec_from_file_location("d2e_g3b_source_locked_g3a", p)
    if spec is None or spec.loader is None:
        raise G3bError("cannot import frozen G3a proof source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (module.SOURCE_SHA256 != SOURCE_SHA256
            or module.CLAIMS["physical_provider_admitted"] is not False):
        raise G3bError("G3a source or physical permissions changed")
    return module


def _source_original_arrays(row, original, r):
    """Recreate original intermediate arrays via exact frozen original funcs.

    The frozen high-level evaluate_portability_dataframe does not return its
    bulge/disk/qeff arrays, so this reproduces *the same source expressions*,
    not an independent D2c projector nor a claim of direct array export.
    """
    import numpy as np

    bmass = 10 ** row["logM_bulge_chabrier_central"]
    dmass = 10 ** row["logM_disc_chabrier_central"]
    bre = row["Re_bulge_arcsec"] * row["scale_kpc_per_arcsec"]
    dre = row["Re_disc_arcsec"] * row["scale_kpc_per_arcsec"]
    qb = float(row["q_bulge"])
    qd = float(row["q_disc"])
    bm, dm, bre, dre = map(float, (bmass, dmass, bre, dre))
    if not (all(math.isfinite(x) and x > 0 for x in (bm, dm, bre, dre, qb, qd))
            and 0 < qb <= 1 and 0 < qd <= 1):
        raise G3bError("nonphysical frozen source baryon inputs")
    # These are LITERAL source expressions and frozen source functions.
    K = original._projection_matrix(r)
    bulge_rho = original.hernquist_density(r, bm, bre / 1.8153)
    bulge = K.dot(bulge_rho)
    disk = np.array([
        original.projected_disk_mass_exponential(
            R, dm, dre / 1.67835, qd, ntheta=120,
        )
        for R in r
    ])
    denominator = np.clip(bulge + disk, 1e-30, None)
    qeff = np.clip((qb * bulge + qd * disk) / denominator, 1e-3, 1.0)
    for arr in (bulge, disk, qeff):
        if arr.shape != (180,) or not np.all(np.isfinite(arr)) or np.min(arr) <= 0:
            raise G3bError("original source returned invalid baryon or qeff array")
    # Guard against a source q_eff circularization change using a strictly
    # increasing synthetic shadow array: this tests implementation identity,
    # NOT physical validity of the shadow density or lensing.
    synthetic = np.arange(1, 181, dtype=float)
    lens_cfg = {
        "shadow_projection": "baryon_structure_circularized",
        "disk_axis_ratio_q": qd, "bulge_axis_ratio_q": qb,
    }
    got = original.apply_shadow_projection_mode(
        r, synthetic, lens_cfg, bulge, disk, dict(lens_cfg),
    )
    expected = np.interp(
        r / np.sqrt(qeff), r, synthetic,
        left=synthetic[0], right=synthetic[-1],
    )
    if not np.array_equal(got, expected):
        raise G3bError("original qeff circularization formula changed")
    return {"bulge": bulge, "disk": disk, "qeff": qeff,
            "M_b": bm, "M_d": dm, "a": bre / 1.8153,
            "s": dre / 1.67835, "q_b": qb, "q_d": qd}


def one_lens(row, registered, original, r, g3a, g1, root_map):
    lid = str(row["lens_id"])
    if registered["lens_id"] != lid or lid not in LENS_IDS:
        raise G3bError("unregistered development lens")
    for name, value in (
        ("observed_arcsec", float(row["einstein_radius_arcsec_central"])),
        ("scale_kpc_per_arcsec", float(row["scale_kpc_per_arcsec"])),
        ("d2d_root_kpc", float(root_map[lid])),
    ):
        if registered[name] != value:
            raise G3bError("frozen source-only selector input changed")
    anchors = register_two_source_knots(
        registered["observed_arcsec"], registered["scale_kpc_per_arcsec"],
        registered["d2d_root_kpc"], r,
    )
    if (anchors["observed_role"]["source_knot_index_zero_based"]
            != registered["observed_index"]
            or anchors["d2d_role"]["source_knot_index_zero_based"]
            != registered["d2d_index"]
            or anchors["collision_shifted_d2d_one_index"]
            is not registered["collision_shift"]):
        raise G3bError("predeclared source-grid knot indices changed")
    values = _source_original_arrays(row, original, r)
    records = []
    for role in ROLES:
        index = anchors[role]["source_knot_index_zero_based"]
        radius = float(r[index])  # exact binary64 ORIGINAL GRID KNOT
        source_b = float(values["bulge"][index])
        source_d = float(values["disk"][index])
        source_q = float(values["qeff"][index])
        b = certified_hernquist_point(radius, values["M_b"], values["a"])
        fine = certified_periodic_exponential_disk_point(
            radius, values["M_d"], values["s"], values["q_d"],
            midpoints=MESH_MIDPOINTS,
            target_relative_width=TARGET_RELATIVE_WIDTH,
        )
        coarse = certified_elliptical_disk_radius_band(
            radius, radius, values["M_d"], values["s"], values["q_d"],
        )
        disk = g3a._analytic_disk_intersection(fine, coarse)
        bproof = certified_pointwise_source_error(
            source_b, b["lower_msun"], b["upper_msun"],
        )
        dproof = certified_pointwise_source_error(
            source_d, disk["lower_msun"], disk["upper_msun"],
        )
        outward = [
            g1._outward_mass(b["lower_msun"], upper=False),
            g1._outward_mass(b["upper_msun"], upper=True),
            g1._outward_mass(disk["lower_msun"], upper=False),
            g1._outward_mass(disk["upper_msun"], upper=True),
        ]
        qbox = frozen_baryonic_q_corners(
            *outward, values["q_b"], values["q_d"],
        )
        qproof = certified_pointwise_q_error(
            source_q,
            g3a._q_fraction(qbox["q_min"]),
            g3a._q_fraction(qbox["q_max"]),
        )
        records.append({
            "role": role, "source_knot_index_zero_based": index,
            "anchor_radius_kpc_binary64": anchors[role]["anchor_kpc_binary64"],
            "source_grid_knot_radius_kpc_binary64": radius,
            "source_bulge_k_matrix_msun_binary64": source_b,
            "source_disk_120_angle_omitted_arc_msun_binary64": source_d,
            "derived_frozen_original_qeff_binary64": source_q,
            "source_bulge_discrepancy_at_knot": bproof,
            "source_disk_discrepancy_at_knot": dproof,
            "derived_qeff_discrepancy_at_knot": qproof,
            "certified_mathematical_bulge_interval": b,
            "certified_mathematical_disk_full_azimuth_interval": fine,
            "independent_coarse_disk_crosscheck": coarse,
            "analytic_disk_intersection": disk,
            "analytic_qeff_corner_interval": qbox,
            "source_grid_mass_not_source_observed_radius_output": True,
            "source_numeric_error_between_knots_certified": False,
            "source_model_root_error_certified": False,
        })
    return {
        "lens_id": lid,
        "historical_fitted_development_only": True,
        "selector": anchors,
        "original_source_numeric_input_parameters": {
            "bulge_mass_msun_binary64": values["M_b"],
            "disc_mass_msun_binary64": values["M_d"],
            "hernquist_a_kpc_binary64": values["a"],
            "exponential_disc_scale_kpc_binary64": values["s"],
            "bulge_q_binary64": values["q_b"],
            "disc_q_binary64": values["q_d"],
        },
        "original_arrays_recreated_using_unmodified_source_functions": True,
        "original_high_level_evaluator_does_not_return_arrays": True,
        "qeff_derived_inside_source_formula_not_returned": True,
        "points": records,
    }


def execute(source_root):
    import numpy as np
    import pandas as pd
    import scipy

    from native_eset.historical.hist001_source import verify_hist001_source

    source = Path(source_root)
    if source.is_symlink() or not source.is_dir():
        raise G3bError("missing or unsafe original March source")
    if verify_hist001_source(source)["source_lock_sha256"] != SOURCE_SHA256:
        raise G3bError("original March 46+3 source SHA mismatch")
    pre = _load_preregistration()
    g3a = _load_g3a()
    g2b = g3a._load_g2b()
    g1 = g2b._load_g()
    a = g1._load_pinned_f()._load_e()._load_d2e_d()._load_d2e_a()
    d2c = a._load_pinned("hist001d_d2c.py", a.D2C_SHA256)
    with TemporaryDirectory(prefix="hist001d_g3b_original_source_") as temp:
        copy = Path(temp) / "hist001"
        shutil.copytree(source, copy)
        verify_hist001_source(copy)
        pack = copy / "swells_pack_v2"
        with d2c.source_modules(pack):
            import solv.run_setA_port_cand as original
            data = original._load_tables(pack)
            if tuple(data.lens_id) != LENS_IDS:
                raise G3bError("original Set A development lens order changed")
            anchor, _ = original._build_anchor(pack)
            gate = original._candidate_gate_config(
                anchor, candidate_name=CANDIDATE,
            )
            baseline = original.evaluate_portability_dataframe(
                pack, gate, gate_label=CANDIDATE,
            )
            if sum(bool(x) for x in baseline.both_pass) != 6:
                raise G3bError("original historical 180x120 fitted 6/6 changed")
            r = original_source_grid()
            lenses = [
                one_lens(row, item, original, r, g3a, g1, a.D2D_REFERENCE_ROOT_KPC)
                for (_, row), item in zip(
                    data.iterrows(), pre["preregistrations"],
                )
            ]
        verify_hist001_source(copy)
    verify_hist001_source(source)
    points = [p for lens in lenses for p in lens["points"]]
    if len(points) != 12:
        raise G3bError("original registered point count changed")
    return {
        "schema": SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "preregistration_sha256": REGISTRY_SHA256,
        "source_equivalent_original_march_180x120": True,
        "source_original_fitted_6of6": 6,
        "separate_D2d_finite_11520_3of6": 3,
        "fitted_development_lens_ids": list(LENS_IDS),
        "registered_knot_evaluation_count": len(points),
        "bulge_width_target_met_count": sum(
            bool(x["certified_mathematical_bulge_interval"]["target_met"])
            for x in points
        ),
        "disk_width_target_met_count": sum(
            bool(x["certified_mathematical_disk_full_azimuth_interval"]["target_met"])
            for x in points
        ),
        "lenses": lenses,
        "claims": dict(CLAIMS),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__, "scipy": scipy.__version__,
        },
        "limitations": (
            "Discrepancy only at 12 input-selected original 180-grid knots. "
            "Bulge is original March K-matrix sampled-density projection; "
            "disc is original March 120-angle omitted-arc trapezoid. "
            "q_eff is derived from those source-computed mass arrays using "
            "the unchanged source expression, not an emitted original result. "
            "No interpolated anchor radius or all-radius root certification; "
            "no continuous shadow error, outer matter, physical Weyl "
            "or observational validation."
        ),
    }


def run(source_root, output):
    from native_eset.evidence.receipts import canonical_json
    import native_eset.historical.hist001d_g3b_knot_preregistration as reg
    import native_eset.numerics.certified_pointwise_source_error as helper

    source, dest = Path(source_root), Path(output)
    if source.is_symlink() or dest.is_symlink() or dest.exists():
        raise G3bError("unsafe source or existing output directory")
    if (dest.resolve() == source.resolve()
            or dest.resolve().is_relative_to(source.resolve())):
        raise G3bError("cannot write G3b evidence inside original source")
    report = execute(source)
    report_raw = canonical_json(report)
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "preregistration_sha256": REGISTRY_SHA256,
        "G3a_source_dependency_sha256": G3A_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "knot_selector_sha256": _sha(Path(reg.__file__).read_bytes()),
        "pointwise_error_kernel_sha256": _sha(Path(helper.__file__).read_bytes()),
        "report_sha256": _sha(report_raw),
        "claims": dict(CLAIMS),
    }
    raw = canonical_json(receipt)
    dest.mkdir(parents=True)
    (dest / "report.json").write_bytes(report_raw)
    (dest / "receipt.json").write_bytes(raw)
    (dest / "receipt.sha256").write_text(_sha(raw) + "\n", encoding="ascii")
    return {
        "status": STATUS, "receipt_sha256": _sha(raw),
        "original_source_knot_points": report["registered_knot_evaluation_count"],
        "bulge_target_met_count": report["bulge_width_target_met_count"],
        "disk_target_met_count": report["disk_width_target_met_count"],
        "claims": dict(CLAIMS),
    }


def verify(receipt_path, source_root, expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.historical.hist001d_g3b_knot_preregistration as reg
    import native_eset.numerics.certified_pointwise_source_error as helper

    path = Path(receipt_path)
    if path.name != "receipt.json" or path.is_symlink() or path.parent.is_symlink():
        raise G3bError("unsafe G3b receipt path")
    members = list(path.parent.iterdir())
    if ({p.name for p in members} != {"report.json", "receipt.json", "receipt.sha256"}
            or any(p.is_symlink() or not p.is_file() for p in members)):
        raise G3bError("receipt inventory altered")
    raw = path.read_bytes()
    sha = _sha(raw)
    if expected_sha256 is not None and expected_sha256 != sha:
        raise G3bError("external expected SHA mismatch")
    if (path.parent / "receipt.sha256").read_text(encoding="ascii") != sha + "\n":
        raise G3bError("receipt sidecar SHA mismatch")
    report_raw = (path.parent / "report.json").read_bytes()
    receipt, report = strict_loads(raw), strict_loads(report_raw)
    if canonical_json(receipt) != raw or canonical_json(report) != report_raw:
        raise G3bError("noncanonical source numerical evidence")
    required = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "preregistration_sha256": REGISTRY_SHA256,
        "G3a_source_dependency_sha256": G3A_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "knot_selector_sha256": _sha(Path(reg.__file__).read_bytes()),
        "pointwise_error_kernel_sha256": _sha(Path(helper.__file__).read_bytes()),
        "report_sha256": _sha(report_raw), "claims": dict(CLAIMS),
    }
    if (receipt != required or report.get("schema") != SCHEMA
            or report.get("claims") != CLAIMS):
        raise G3bError("forged source numerical evidence or physics promotion")
    fresh = execute(source_root)
    try:
        _load_g3a()._load_g2b()._load_g()._load_pinned_f()._load_e()._load_d2e_d()._load_d2e_a()._compare(
            report, fresh,
        )
    except ValueError as exc:
        raise G3bError("fresh original source output discrepancy differs") from exc
    return {
        "status": "G3B_FRESH_ORIGINAL_MARCH_180x120_SOURCE_REEXECUTION_PASS",
        "receipt_sha256": sha,
        "registered_knot_outputs": fresh["registered_knot_evaluation_count"],
        "claims": dict(CLAIMS),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out", type=Path)
    action.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        result = (
            verify(args.verify, args.source_root, args.expected_sha256)
            if args.verify else run(args.source_root, args.out)
        )
    except (OSError, ValueError, TypeError, KeyError, ImportError, AssertionError,
            G3bRegistrationError) as exc:
        print(json.dumps({
            "status": "G3B_FAIL_CLOSED", "error": str(exc),
        }, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
