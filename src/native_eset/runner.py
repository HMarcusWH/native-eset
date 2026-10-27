"""Source-bound reference execution. No ESET physical backend is substituted here."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
from math import isfinite
from pathlib import Path
import platform
import sys
from typing import Any
from native_eset.capabilities import require_capability
from native_eset.conventions import check_convention, decimal_string
from native_eset.controls import FlatGRLambdaCDM
from native_eset.evidence.data_roles import check_data_role
from native_eset.evidence.receipts import canonical_json, digest_bytes, source_tree_digest, write_immutable
from native_eset.numerics.integrators import refined_simpson
from native_eset.serialization import read_json, require_sha256

RUNTIME_CONTRACT = "NATIVE_ESET_CONTROL_RUNNER_V2"
CONTROL_EQUATIONS = {"E_of_z": "control:gr-flat-lcdm-E2",
                     "chi_dimensionless_of_z": "control:gr-flat-lcdm-comoving-distance"}
CLAIM_BOUNDARY = "GR_REFERENCE_CONTROL_ONLY_NO_ESET_PHYSICAL_OUTPUT"


class InvalidRunSpec(ValueError):
    pass


def _validate(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise InvalidRunSpec("run spec must be a JSON object")
    required = {"schema", "backend_id", "theory_id", "model_id", "equation_id", "equation_source_sha256",
                "frame", "gauge", "coordinate", "observable", "redshifts", "parameters", "data_use",
                "claim_intent", "numerical_method", "absolute_tolerance"}
    if set(obj) != required or obj["schema"] != "NATIVE_ESET_RUN_SPEC_V1":
        raise InvalidRunSpec(f"run schema mismatch missing={sorted(required-set(obj))} extra={sorted(set(obj)-required)}")
    text_fields = required - {"parameters", "redshifts"}
    if any(not isinstance(obj[k], str) or not obj[k] or len(obj[k]) > 512 for k in text_fields):
        raise InvalidRunSpec("run specification text fields must be nonempty bounded strings")
    if not obj["model_id"].startswith("control:"):
        raise InvalidRunSpec("reference model IDs must be in the control: namespace")
    require_sha256(obj["equation_source_sha256"], "equation source SHA-256")
    require_capability(obj["backend_id"], obj["theory_id"], obj["observable"])
    if obj["frame"] != "GR_REFERENCE_FLRW":
        raise InvalidRunSpec("reference backend cannot run in an ESET gravitational frame")
    check_convention(obj["frame"], obj["gauge"], obj["coordinate"])
    check_data_role(obj["data_use"], obj["claim_intent"])
    if obj["claim_intent"] != "CONTROL_ONLY" or obj["data_use"] != "INTERNAL_TEST":
        raise InvalidRunSpec("RUN-000 accepts only GR control/internal tests")
    if obj["equation_id"] != CONTROL_EQUATIONS[obj["observable"]]:
        raise InvalidRunSpec("equation ID is not the implemented reference equation for this observable")
    method = "ANALYTIC" if obj["observable"] == "E_of_z" else "SIMPSON_REFINED"
    if obj["numerical_method"] != method:
        raise InvalidRunSpec(f"observable requires numerical_method={method}")
    zs = obj["redshifts"]
    if not isinstance(zs, list) or not 1 <= len(zs) <= 1000:
        raise InvalidRunSpec("nonempty redshift list <=1000 required")
    for z in zs:
        if not Decimal(0) <= decimal_string(z) <= Decimal(100):
            raise InvalidRunSpec("reference redshift domain is [0,100]")
    params = obj["parameters"]
    if not isinstance(params, dict) or set(params) != {"omega_r", "omega_m", "omega_lambda"}:
        raise InvalidRunSpec("GR control requires exactly three Omega fractions")
    for name, q in params.items():
        if not isinstance(q, dict) or set(q) != {"value", "unit"} or q["unit"] != "1":
            raise InvalidRunSpec(f"parameter {name} requires dimensionless value/unit contract")
        if not Decimal(0) <= decimal_string(q["value"]) <= Decimal(1):
            raise InvalidRunSpec("Omega fractions must be in [0,1]")
    if sum(decimal_string(q["value"]) for q in params.values()) != 1:
        raise InvalidRunSpec("three GR density fractions must sum to exactly 1")
    tol = decimal_string(obj["absolute_tolerance"])
    if not Decimal("1e-14") <= tol <= Decimal("1e-2"):
        raise InvalidRunSpec("reference refinement tolerance must be in [1e-14,1e-2]")
    return obj


@dataclass(frozen=True, init=False)
class RunSpec:
    _canonical_bytes: bytes
    spec_sha256: str

    def __init__(self, raw: dict[str, Any], spec_sha256: str | None = None):
        # Validate every constructor, not just the file reader. No mutable alias survives.
        obj = _validate(raw)
        data = canonical_json(obj)
        actual = digest_bytes(data)
        if spec_sha256 is not None and spec_sha256 != actual:
            raise InvalidRunSpec("caller supplied a stale/forged run specification digest")
        object.__setattr__(self, "_canonical_bytes", data)
        object.__setattr__(self, "spec_sha256", actual)

    @property
    def raw(self) -> dict[str, Any]:
        return json.loads(self._canonical_bytes)

    @classmethod
    def read(cls, file: str | Path) -> "RunSpec":
        return cls(read_json(Path(file), max_bytes=1_000_000))


def runtime_environment() -> dict[str, str]:
    return {"python": platform.python_version(), "platform": platform.system(),
            "release": platform.release(), "machine": platform.machine(),
            "python_implementation": platform.python_implementation(),
            "byteorder": sys.byteorder, "floating_point": "IEEE754_BINARY64"}


def finite_model_digest(obj: dict[str, Any]) -> str:
    return digest_bytes(canonical_json({k: obj[k] for k in
        ("theory_id", "backend_id", "equation_source_sha256", "frame", "gauge", "coordinate", "parameters")}))


def run_identity(spec_sha256: str, code_sha256: str, model_sha256: str,
                 environment: dict[str, str]) -> str:
    key = {"run_spec_sha256": spec_sha256, "code_sha256": code_sha256,
           "finite_model_sha256": model_sha256, "environment": environment,
           "runtime_implementation": RUNTIME_CONTRACT}
    return "control-" + digest_bytes(canonical_json(key))


def run_control(spec: RunSpec, output_root: Path, package_root: Path | None = None) -> dict[str, Any]:
    if not isinstance(spec, RunSpec):
        raise InvalidRunSpec("a validated RunSpec is required")
    # Revalidation at execution boundary also catches manually constructed/tampered instances.
    checked = RunSpec(spec.raw, spec.spec_sha256)
    obj = checked.raw
    cap = require_capability(obj["backend_id"], obj["theory_id"], obj["observable"])
    control = FlatGRLambdaCDM(**{k: float(v["value"]) for k, v in obj["parameters"].items()})
    from native_eset import controls
    source = Path(controls.__file__).resolve()
    if source.is_symlink() or not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != obj["equation_source_sha256"]:
        raise InvalidRunSpec("equation source changed; update RunSpec identity through reviewed PR")
    code_sha = source_tree_digest(package_root)
    environment = runtime_environment()
    model_sha = finite_model_digest(obj)
    run_id = run_identity(checked.spec_sha256, code_sha, model_sha, environment)
    folder = Path(output_root) / run_id
    if folder.exists() or folder.is_symlink():
        raise FileExistsError("immutable run exists; use verify rather than overwriting")
    observed = []
    for zs in obj["redshifts"]:
        z = float(decimal_string(zs))
        if obj["observable"] == "E_of_z":
            val = control.E(z)
            num = {"method": "ANALYTIC_EXPRESSION_BINARY64", "refinement": "NOT_APPLICABLE",
                   "roundoff_bound": "NOT_CERTIFIED"}
        else:
            result = refined_simpson(lambda zz: 1.0 / control.E(zz), 0, z, n=64,
                                     absolute_tolerance=float(decimal_string(obj["absolute_tolerance"])))
            val = result.value
            num = {"method": "SIMPSON_REFINED_64_128", "refinement_abs_change": repr(result.absolute_change),
                   "coarse": repr(result.coarse), "steps": result.steps,
                   "error_semantics": "REFINEMENT_CHECK_NOT_RIGOROUS_ERROR_BOUND"}
        if not isfinite(val):
            raise ArithmeticError("non-finite control output")
        observed.append({"z": zs, "value": repr(val), "unit": "1", "numerics": num})
    outputs = {"schema": "NATIVE_ESET_CONTROL_OUTPUT_V1", "scope": cap.model_role,
               "observable": obj["observable"], "equation_id": obj["equation_id"],
               "model_id": obj["model_id"], "finite_model_sha256": model_sha,
               "graph_status": "NOT_A_GRAPH_ADMITTED_PROVIDER", "values": observed,
               "validation": "NOT_ESET_EMPIRICAL_VALIDATION"}
    output_bytes, spec_bytes = canonical_json(outputs), canonical_json(obj)
    receipt = {"schema": "NATIVE_ESET_RUN_RECEIPT_V2", "runtime_contract": RUNTIME_CONTRACT,
               "run_id": run_id, "backend_id": cap.backend_id, "theory_id": obj["theory_id"],
               "model_id": obj["model_id"], "finite_model_sha256": model_sha,
               "equation_id": obj["equation_id"], "equation_source_sha256": obj["equation_source_sha256"],
               "code_sha256": code_sha, "spec_sha256": checked.spec_sha256,
               "data_use": obj["data_use"], "claim_boundary": CLAIM_BOUNDARY,
               "output_files": {"outputs.json": digest_bytes(output_bytes), "run_spec.json": digest_bytes(spec_bytes)},
               "environment": environment,
               "gate_ledger": {"source_hash": "PASS", "scientific_backend": "CONTROL_ONLY",
                               "real_ESET_physics": "NOT_RUN", "physical_provider": "NOT_ADMITTED",
                               "empirical_validation": "NOT_RUN"}}
    folder.mkdir(parents=True, exist_ok=False)
    try:
        write_immutable(folder / "outputs.json", output_bytes)
        write_immutable(folder / "run_spec.json", spec_bytes)
        receipt_bytes = canonical_json(receipt)
        write_immutable(folder / "receipt.sha256", (digest_bytes(receipt_bytes) + "\n").encode("ascii"))
        write_immutable(folder / "receipt.json", receipt_bytes)  # last: completed-run marker
    except BaseException:
        for file in folder.iterdir():
            if file.is_file() or file.is_symlink():
                file.unlink()
        folder.rmdir()
        raise
    return {"status": "NUMERICAL_CONTROL_PASS_NOT_ESET_PHYSICS", "run_id": run_id,
            "output_dir": str(folder), "receipt_sha256": digest_bytes(receipt_bytes),
            "source_tree_sha256": code_sha, "rows": len(observed)}
