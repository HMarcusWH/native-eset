"""G4a: source-locked six-lens FlatLCDM sigma_crit mathematical enclosure.

The original 46+3 March source is read-only. The independent rational
mathematical result encloses the exact frozen *binary64-scalar* cosmology,
not a physical/observational uncertainty. Returned original SciPy values
are bounded pointwise only at six source redshift pairs, not all redshifts.
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

from native_eset.numerics.certified_flatlcdm_sigma import (
    TARGET_RELATIVE_WIDTH,
    a_posteriori_source_output_discrepancy,
    certified_sigma_critical,
)

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
G3B_SOURCE_SHA256 = "353694da6a85c8ce0194cb60c5ab0526961b60c332d1b2931d0d186b81b495c7"
ORIGINAL_COSMOLOGY_SHA256 = "f4f9ed5d2a42db0728c799a02e2dea7587431b5cf9da9db26f27e45efbf3a953"
ORIGINAL_CONSTANTS_SHA256 = "34d3210728cd319ef3929cbb06015f3710cf5ee3b4300358e9706ecf100115f1"
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)
SCHEMA = "NATIVE_ESET_HIST001D_D2E_G4A_FLATLCDM_SIGMA_SOURCE_ERROR_V1"
RECEIPT_SCHEMA = "NATIVE_ESET_HIST001D_D2E_G4A_SOURCE_RECEIPT_V1"
STATUS = "G4A_FROZEN_LCDM_MATH_AND_SIX_SOURCE_OUTPUTS_CERTIFIED_NOT_PHYSICS"
CLAIMS = {
    "frozen_binary64_flatlcdm_math_sigma_crit_enclosed": True,
    "six_historical_source_sigma_outputs_discrepancy_bounded_pointwise": True,
    "original_source_46_plus_three_verified": True,
    "six_previously_fitted_development_lenses_only": True,
    "source_sigma_crit_errors_all_redshifts_certified": False,
    "source_cosmological_parameter_physical_error_bounded": False,
    "original_March_all_radius_baryonic_source_error_bounded": False,
    "all_R_model_root_existence_or_uniqueness_proved": False,
    "original_source_density_continuum_certified": False,
    "shadow_mass_outside_finite_domain_bounded": False,
    "independent_blinded_holdout_scored": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "current_native_v172_equivalence_proved": False,
    "canonical_theory_state_mutated": False,
    "original_source_modified": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class G4aError(ValueError):
    """Reject changed original source, forged evidence or scientific promotion."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pinned_g3b():
    """Read-only G3b prerequisite, loaded from a byte-verified source file."""
    path = Path(__file__).resolve().with_name("hist001d_d2e_g3b_original_knot_errors.py")
    if path.is_symlink() or not path.is_file() or _sha(path.read_bytes()) != G3B_SOURCE_SHA256:
        raise G4aError("G3b source dependency bytes changed")
    spec = importlib.util.spec_from_file_location("g4a_sha_pinned_g3b", path)
    if spec is None or spec.loader is None:
        raise G4aError("cannot import original G3b source prerequisite")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (module.SOURCE_SHA256 != SOURCE_SHA256
            or module.CLAIMS.get("physical_provider_admitted") is not False
            or module.LENS_IDS != LENS_IDS):
        raise G4aError("G3b frozen source identity or scientific permissions changed")
    return module


def _assert_original_cosmology_files(pack: Path) -> None:
    for relative, expected in (
        ("solv/cosmology.py", ORIGINAL_COSMOLOGY_SHA256),
        ("solv/constants.py", ORIGINAL_CONSTANTS_SHA256),
    ):
        file = pack / relative
        if file.is_symlink() or not file.is_file() or _sha(file.read_bytes()) != expected:
            raise G4aError("original cosmology source/constants file changed")


def _single_lens(row, source_cosmology, source_constants):
    lens_id = str(row["lens_id"])
    if lens_id not in LENS_IDS:
        raise G4aError("unregistered fitted development lens")
    z_lens = float(row["z_deflector"])
    z_source = float(row["z_source"])
    if not (math.isfinite(z_lens) and math.isfinite(z_source)
            and 0 < z_lens < z_source <= 10):
        raise G4aError("original fitted redshift pair outside source contract")
    original = float(source_cosmology.sigma_crit_msun_per_kpc2(z_lens, z_source))
    if not math.isfinite(original) or original <= 0:
        raise G4aError("original FlatLCDM sigma returned invalid binary64 value")
    proof = certified_sigma_critical(
        z_lens, z_source,
        omega_m=source_cosmology.Om0,
        omega_de=source_cosmology.Ode0,
        H0=source_cosmology.H0,
        C_KMS=source_constants.C_KMS,
        G_KPC_KMS2_MSUN=source_constants.G_KPC_KMS2_MSUN,
        FOUR_PI=source_constants.FOUR_PI,
        MPC_IN_KPC=source_constants.MPC_IN_KPC,
        target_relative_width=TARGET_RELATIVE_WIDTH,
    )
    error = a_posteriori_source_output_discrepancy(original, proof)
    if error["physical_lensing_error_bounded"] or error["source_numeric_error_all_redshifts_bounded"]:
        raise G4aError("source mathematical error incorrectly promoted to physics")
    return {
        "lens_id": lens_id,
        "historical_fitted_development_case_only": True,
        "original_source_redshift_deflector_binary64": z_lens,
        "original_source_redshift_source_binary64": z_source,
        "original_FlatLCDM_SciPy_returned_sigma_crit_binary64": original,
        "math_exact_binary64_scalar_sigma_crit_enclosure": proof,
        "source_sigma_crit_pointwise_discrepancy": error,
        "value_actually_returned_by_sha_locked_original_source": True,
        "proof_helper_itself_does_not_assert_original_source_provenance": True,
        "cosmological_observational_likelihood_certified": False,
        "other_redshifts_or_root_map_error_certified": False,
    }


def execute(source_root: str | Path):
    import numpy as np
    import pandas as pd
    import scipy
    from native_eset.historical.hist001_source import verify_hist001_source

    root = Path(source_root)
    if root.is_symlink() or not root.is_dir():
        raise G4aError("missing or unsafe original March source root")
    if verify_hist001_source(root)["source_lock_sha256"] != SOURCE_SHA256:
        raise G4aError("original 46+3 March source lock changed")
    _assert_original_cosmology_files(root / "swells_pack_v2")
    prerequisite = _pinned_g3b()
    # Reuse the SHA-pinned G3b -> G3a -> G2b -> G1 -> F -> E -> D -> A
    # historical source loader. Original source stays unchanged at all times.
    a = (prerequisite._load_g3a()._load_g2b()._load_g()._load_pinned_f()
         ._load_e()._load_d2e_d()._load_d2e_a())
    d2c = a._load_pinned("hist001d_d2c.py", a.D2C_SHA256)
    with TemporaryDirectory(prefix="hist001d_g4a_frozen_sigma_") as tmp:
        copy = Path(tmp) / "hist001"
        shutil.copytree(root, copy)
        verify_hist001_source(copy)
        pack = copy / "swells_pack_v2"
        _assert_original_cosmology_files(pack)
        with d2c.source_modules(pack):
            import solv.constants as constants
            import solv.run_setA_port_cand as source
            from solv.cosmology import FlatLCDM

            data = source._load_tables(pack)
            if tuple(data.lens_id) != LENS_IDS:
                raise G4aError("historical Set A lens list/order mutated")
            cosmo = FlatLCDM(70.0, 0.3)
            lenses = [_single_lens(row, cosmo, constants)
                      for row in data.to_dict("records")]
        verify_hist001_source(copy)
    verify_hist001_source(root)
    if len(lenses) != 6:
        raise G4aError("missing frozen source lens cases")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "G3b_pinned_source_sha256": G3B_SOURCE_SHA256,
        "original_cosmology_source_sha256": ORIGINAL_COSMOLOGY_SHA256,
        "original_constants_source_sha256": ORIGINAL_CONSTANTS_SHA256,
        "historical_fitted_development_lens_ids": list(LENS_IDS),
        "pointwise_original_sigma_crit_source_return_count": len(lenses),
        "sigma_mathematical_width_target_met_count": sum(
            bool(lens["math_exact_binary64_scalar_sigma_crit_enclosure"]["target_met"])
            for lens in lenses
        ),
        "original_source_sigma_value_inside_analytic_interval_count": sum(
            bool(lens["source_sigma_crit_pointwise_discrepancy"][
                "source_returned_inside_target_enclosure"])
            for lens in lenses
        ),
        "lenses": lenses,
        "claims": dict(CLAIMS),
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__,
            "pandas": pd.__version__, "scipy": scipy.__version__,
        },
        "limitations": (
            "Six source-returned binary64 FlatLCDM Sigma_crit values only. "
            "The mathematical interval treats all frozen source float scalars "
            "as exact dyadics, including FOUR_PI (not ideal real 4*pi). "
            "No general SciPy integration theorem, physical cosmological "
            "error, observational likelihood, global Einstein-root proof, "
            "or contemporary Native ESET provider."
        ),
    }


def run(source_root: str | Path, output: str | Path):
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.certified_flatlcdm_sigma as kernel

    source, dest = Path(source_root), Path(output)
    if source.is_symlink() or dest.is_symlink() or dest.exists():
        raise G4aError("unsafe source path or existing immutable output")
    if dest.resolve() == source.resolve() or dest.resolve().is_relative_to(source.resolve()):
        raise G4aError("cannot write G4a evidence inside frozen original source")
    report = execute(source)
    report_bytes = canonical_json(report)
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "G3b_source_dependency_sha256": G3B_SOURCE_SHA256,
        "original_cosmology_source_sha256": ORIGINAL_COSMOLOGY_SHA256,
        "original_constants_source_sha256": ORIGINAL_CONSTANTS_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "certified_sigma_kernel_sha256": _sha(Path(kernel.__file__).read_bytes()),
        "report_sha256": _sha(report_bytes),
        "claims": dict(CLAIMS),
    }
    receipt_bytes = canonical_json(receipt)
    dest.mkdir(parents=True)
    (dest / "report.json").write_bytes(report_bytes)
    (dest / "receipt.json").write_bytes(receipt_bytes)
    (dest / "receipt.sha256").write_text(_sha(receipt_bytes) + "\n", encoding="ascii")
    return {
        "status": STATUS,
        "receipt_sha256": _sha(receipt_bytes),
        "original_source_output_count": report["pointwise_original_sigma_crit_source_return_count"],
        "math_sigma_width_targets_met": report["sigma_mathematical_width_target_met_count"],
        "claims": dict(CLAIMS),
    }


def verify(receipt_path: str | Path, source_root: str | Path, expected_sha256=None):
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.certified_flatlcdm_sigma as kernel

    p = Path(receipt_path)
    if p.name != "receipt.json" or p.is_symlink() or p.parent.is_symlink():
        raise G4aError("unsafe original source sigma receipt path")
    if ({x.name for x in p.parent.iterdir()} !=
            {"report.json", "receipt.json", "receipt.sha256"}
            or any(not x.is_file() or x.is_symlink() for x in p.parent.iterdir())):
        raise G4aError("G4a source receipt inventory incomplete or forged")
    receipt_bytes = p.read_bytes()
    digest = _sha(receipt_bytes)
    if expected_sha256 is not None and digest != expected_sha256:
        raise G4aError("external expected receipt SHA mismatch")
    if (p.parent / "receipt.sha256").read_text(encoding="ascii") != digest + "\n":
        raise G4aError("receipt SHA-256 sidecar differs")
    report_bytes = (p.parent / "report.json").read_bytes()
    receipt, report = strict_loads(receipt_bytes), strict_loads(report_bytes)
    if canonical_json(receipt) != receipt_bytes or canonical_json(report) != report_bytes:
        raise G4aError("noncanonical original source sigma evidence")
    expected = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "G3b_source_dependency_sha256": G3B_SOURCE_SHA256,
        "original_cosmology_source_sha256": ORIGINAL_COSMOLOGY_SHA256,
        "original_constants_source_sha256": ORIGINAL_CONSTANTS_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "certified_sigma_kernel_sha256": _sha(Path(kernel.__file__).read_bytes()),
        "report_sha256": _sha(report_bytes),
        "claims": dict(CLAIMS),
    }
    if (receipt != expected or report.get("schema") != SCHEMA
            or report.get("status") != STATUS or report.get("claims") != CLAIMS):
        raise G4aError("forged source receipt or physical-provider promotion")
    fresh = execute(source_root)
    if fresh != report:
        raise G4aError("fresh original FlatLCDM source reexecution differs")
    return {
        "status": "G4A_FRESH_ORIGINAL_FLATLCDM_SOURCE_REEXECUTION_PASS",
        "receipt_sha256": digest,
        "pointwise_source_outputs": fresh["pointwise_original_sigma_crit_source_return_count"],
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
        output = (verify(args.verify, args.source_root, args.expected_sha256)
                  if args.verify else run(args.source_root, args.out))
    except (OSError, ValueError, TypeError, KeyError, ImportError, AssertionError) as exc:
        print(json.dumps({"status": "G4A_FAIL_CLOSED", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
