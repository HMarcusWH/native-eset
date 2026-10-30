"""G4b.0 source-only all-R finite-proxy partition, NOT a root proof.

Pin the original historical 46+3 source, the six development lens IDs,
D2e finite-model root anchors (labels ONLY), and G4a predecessor bytes;
freeze a full-domain exact-rational 64-cell starter partition. An optional
pure H-box helper is conditional on *separately* certified input boxes.
No historical source, fitted coefficient, theory provider or holdout is changed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

from native_eset.numerics.hist001d_g4b_root_intervals import (
    INITIAL_CELLS, LENS_IDS, MAX_DYADIC_DEPTH, MAX_LEAVES, R_MAX, R_MIN,
    SCHEMA as PARTITION_SCHEMA, SOURCE_LOCK_SHA256,
    assert_complete_cover, initial_partition,
)

SOURCE_SHA256 = SOURCE_LOCK_SHA256
G4A_SHA256 = "63d0b78115a3f44914e27bdf3646eebc37cca30a6c8e31bece81c4a5efe11b3b"
D2E_SHA256 = "ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2"
REGISTRY_SHA256 = "86f78ae0583799542241046f3642008c596ee4769b8534e31b641f886beb8035"
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/hist001d_g4b0_root_partition_v1.json"
SCHEMA = "HIST001D_D2E_G4B0_SOURCE_INPUT_PARTITION_REPORT_V1"
RECEIPT_SCHEMA = "HIST001D_D2E_G4B0_SOURCE_INPUT_PARTITION_RECEIPT_V1"
STATUS = "G4B0_FULL_DOMAIN_PARTITION_FROZEN_NO_RESIDUAL_OR_ROOT_CERTIFICATE"

CLAIMS = {
    "six_fitted_development_lenses_only": True,
    "original_March_46_plus_three_source_locked": True,
    "exact_rational_full_domain_partition_proven": True,
    "actual_finite_model_residual_enclosures_computed": False,
    "root_existence_or_uniqueness_certified": False,
    "all_R_numerical_source_error_bounded": False,
    "source_gradient_continuum_bounded": False,
    "source_critical_surface_density_physical_error_bounded": False,
    "original_source_modified": False,
    "new_independent_blinded_holdout_scored": False,
    "physical_weyl_lensing_derived": False,
    "physical_provider_admitted": False,
    "canonical_theory_state_mutated": False,
    "empirical_validation": "NOT_ESTABLISHED",
}


class G4b0Error(ValueError):
    """Source-root/registration drift or forged input-only evidence."""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _registered() -> dict:
    from native_eset.serialization import strict_loads
    if (REGISTRY.is_symlink() or not REGISTRY.is_file()
            or _sha(REGISTRY.read_bytes()) != REGISTRY_SHA256):
        raise G4b0Error("registered exact partition bytes changed")
    obj = strict_loads(REGISTRY.read_bytes())
    if (obj.get("schema") != "HIST001D_D2E_G4B0_SOURCE_ONLY_PARTITION_REGISTRATION_V1"
            or obj.get("status") != "FROZEN_INPUT_PARTITION_ONLY_NO_RESIDUAL_ROOT_CERTIFICATE"
            or obj.get("source_lock_sha256") != SOURCE_SHA256
            or tuple(obj.get("lens_ids", [])) != LENS_IDS
            or obj.get("initial_cells") != INITIAL_CELLS
            or obj.get("max_dyadic_depth") != MAX_DYADIC_DEPTH
            or obj.get("max_leaf_budget") != MAX_LEAVES
            or obj.get("source_domain_exact_dyadic") !=
            {"lower": str(R_MIN), "upper": str(R_MAX)}
            or obj.get("claims", {}).get("physical_provider_admitted") is not False
            or obj.get("claims", {}).get("root_uniqueness_certified") is not False):
        raise G4b0Error("predeclared partition identity/claim mismatch")
    for name, digest in obj["source_file_sha256"].items():
        file = ROOT / name
        if (file.is_symlink() or not file.is_file()
                or _sha(file.read_bytes()) != digest):
            raise G4b0Error("pinned predecessor/source-input file bytes altered")
    if obj["source_file_sha256"].get("tools/hist001d_d2e.py") != D2E_SHA256:
        raise G4b0Error("unexpected D2e source root contract")
    if (obj["source_file_sha256"].get("tools/hist001d_d2e_g4a_flatlcdm_sigma.py")
            != G4A_SHA256):
        raise G4b0Error("unexpected G4a numerical prerequisite")
    return obj


def _pinned_d2e():
    path = ROOT / "tools/hist001d_d2e.py"
    if path.is_symlink() or _sha(path.read_bytes()) != D2E_SHA256:
        raise G4b0Error("D2e finite-model reference changed")
    spec = importlib.util.spec_from_file_location("g4b0_frozen_d2e", path)
    if spec is None or spec.loader is None:
        raise G4b0Error("cannot load frozen D2e source reference")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (module.SOURCE_SHA256 != SOURCE_SHA256
            or tuple(module.D2D_REFERENCE_ROOT_KPC) != LENS_IDS
            or module.CLAIMS["physical_provider_admitted"] is not False):
        raise G4b0Error("D2e source identity or scientific scope changed")
    return module


def execute(source_root: str | Path) -> dict:
    from native_eset.historical.hist001_source import verify_hist001_source

    root = Path(source_root)
    if root.is_symlink() or not root.is_dir():
        raise G4b0Error("missing or linked original source")
    original = verify_hist001_source(root)
    if (original["source_lock_sha256"] != SOURCE_SHA256
            or original["frozen_files"] != 46
            or original["archived_negative_records"] != 3):
        raise G4b0Error("original March source/inventory SHA changed")
    plan = _registered()
    d2e = _pinned_d2e()
    if d2e.D2D_REFERENCE_ROOT_KPC != plan[
        "d2d_finite_root_anchors_kpc_for_provenance_only"
    ]:
        raise G4b0Error("D2d provenance-only root anchor changed")
    source_file = root / "swells_pack_v2/cleaned/lens_set_A_run_fo_74bb5e.csv"
    if source_file.is_symlink() or not source_file.is_file():
        raise G4b0Error("original fitted development input table unavailable")
    with source_file.open(encoding="utf-8", newline="") as fd:
        records = list(csv.DictReader(fd))
    if tuple(x.get("lens_id") for x in records) != LENS_IDS:
        raise G4b0Error("historical six fitted development lens identity changed")
    initial = initial_partition()
    cover = assert_complete_cover(initial)
    lens_items = [
        {
            "lens_id": label,
            "provenance_only_separate_D2d_finite_root_kpc": float(
                d2e.D2D_REFERENCE_ROOT_KPC[label]
            ),
            "initial_cells": [leaf.record() for leaf in initial],
            "full_exact_source_domain_cover": dict(cover),
            "source_output_mass_sigma_shadow_or_root_computed": False,
        }
        for label in LENS_IDS
    ]
    again = verify_hist001_source(root)
    if again["source_lock_sha256"] != SOURCE_SHA256:
        raise G4b0Error("original source modified by registration")
    return {
        "schema": SCHEMA, "partition_schema": PARTITION_SCHEMA,
        "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "preregistration_sha256": REGISTRY_SHA256,
        "pinned_G4a_runner_sha256": G4A_SHA256,
        "pinned_D2e_reference_sha256": D2E_SHA256,
        "six_previously_fitted_development_lens_ids": list(LENS_IDS),
        "predeclared_initial_cell_count_per_lens": INITIAL_CELLS,
        "total_initial_source_domain_cells": len(lens_items) * len(initial),
        "maximum_predeclared_dyadic_depth": MAX_DYADIC_DEPTH,
        "full_domain_mathematical_partition_proven": True,
        "root_or_residual_evaluation_performed": False,
        "lenses": lens_items, "claims": dict(CLAIMS),
        "limitations": (
            "Input-only exact partition spanning the historical 0.02-to-120-kpc "
            "finite source domain, with registered D2d root anchors used as labels "
            "only. NO original March or D2d residuals/root counts computed, no "
            "all-R source numerical accuracy, no physical Weyl/empirical validation."
        ),
    }


def run(source_root: str | Path, output: str | Path) -> dict:
    from native_eset.evidence.receipts import canonical_json
    import native_eset.numerics.hist001d_g4b_root_intervals as helper

    source, dest = Path(source_root), Path(output)
    if (source.is_symlink() or dest.is_symlink() or dest.exists()
            or dest.resolve().is_relative_to(source.resolve())):
        raise G4b0Error("unsafe or existing immutable report output")
    report = execute(source)
    payload = canonical_json(report)
    receipt = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "preregistration_sha256": REGISTRY_SHA256,
        "pinned_G4a_runner_sha256": G4A_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "partition_helper_sha256": _sha(Path(helper.__file__).read_bytes()),
        "report_sha256": _sha(payload), "claims": dict(CLAIMS),
    }
    bytes_ = canonical_json(receipt)
    dest.mkdir(parents=True)
    (dest / "report.json").write_bytes(payload)
    (dest / "receipt.json").write_bytes(bytes_)
    (dest / "receipt.sha256").write_text(_sha(bytes_) + "\n", encoding="ascii")
    return {
        "status": STATUS, "receipt_sha256": _sha(bytes_),
        "initial_partition_cells": report["total_initial_source_domain_cells"],
        "root_or_residual_evaluated": False, "claims": dict(CLAIMS),
    }


def verify(receipt_path: str | Path, source_root: str | Path,
           expected_sha256: str | None = None) -> dict:
    from native_eset.evidence.receipts import canonical_json
    from native_eset.serialization import strict_loads
    import native_eset.numerics.hist001d_g4b_root_intervals as helper

    path = Path(receipt_path)
    if path.name != "receipt.json" or path.is_symlink() or path.parent.is_symlink():
        raise G4b0Error("unsafe source-input receipt path")
    inventory = list(path.parent.iterdir())
    if ({x.name for x in inventory} != {"report.json","receipt.json","receipt.sha256"}
            or any(x.is_symlink() or not x.is_file() for x in inventory)):
        raise G4b0Error("source-input receipt inventory altered")
    raw = path.read_bytes()
    digest = _sha(raw)
    if expected_sha256 is not None and expected_sha256 != digest:
        raise G4b0Error("externally pinned receipt SHA mismatch")
    if (path.parent / "receipt.sha256").read_text(encoding="ascii") != digest+"\n":
        raise G4b0Error("receipt SHA sidecar mismatch")
    report_raw = (path.parent / "report.json").read_bytes()
    receipt, report = strict_loads(raw), strict_loads(report_raw)
    if canonical_json(receipt) != raw or canonical_json(report) != report_raw:
        raise G4b0Error("noncanonical source-input record")
    required = {
        "schema": RECEIPT_SCHEMA, "status": STATUS,
        "source_lock_sha256": SOURCE_SHA256,
        "preregistration_sha256": REGISTRY_SHA256,
        "pinned_G4a_runner_sha256": G4A_SHA256,
        "runner_sha256": _sha(Path(__file__).read_bytes()),
        "partition_helper_sha256": _sha(Path(helper.__file__).read_bytes()),
        "report_sha256": _sha(report_raw), "claims": dict(CLAIMS),
    }
    if (receipt != required or report.get("schema") != SCHEMA
            or report.get("status") != STATUS or report.get("claims") != CLAIMS):
        raise G4b0Error("forged source-input receipt or scientific promotion")
    fresh = execute(source_root)
    if fresh != report:
        raise G4b0Error("fresh independent original-source input replay differs")
    return {"status": "G4B0_FRESH_SOURCE_INPUT_PARTITION_REEXECUTION_PASS",
            "receipt_sha256": digest,
            "source_only_initial_cells": fresh["total_initial_source_domain_cells"],
            "root_proof_certified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    op = parser.add_mutually_exclusive_group(required=True)
    op.add_argument("--out", type=Path)
    op.add_argument("--verify", type=Path)
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()
    try:
        result = (
            verify(args.verify, args.source_root, args.expected_sha256)
            if args.verify else run(args.source_root, args.out)
        )
    except (OSError, ValueError, KeyError, TypeError, ImportError,
            AssertionError, csv.Error, shutil.Error) as exc:
        print(json.dumps({"status": "G4B0_FAIL_CLOSED", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
