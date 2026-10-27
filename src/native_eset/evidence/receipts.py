"""Portable receipt integrity. Hashes alone are not signatures or execution proofs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from native_eset.serialization import read_json, require_sha256, resolve_regular_file


class ReceiptIntegrityError(ValueError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_immutable(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as f:
        f.write(data)


def source_tree_digest(package_root: Path | None = None) -> str:
    from native_eset import controls
    package_dir = Path(controls.__file__).resolve().parent
    if package_root is not None:
        candidate = package_root / "src/native_eset"
        if not candidate.is_dir() or candidate.resolve() != package_dir:
            raise ReceiptIntegrityError("specified package checkout differs from imported code")
    paths = []
    for p in package_dir.rglob("*"):
        if "__pycache__" in p.parts:
            continue
        if p.is_symlink():
            raise ReceiptIntegrityError("symlink in executable package")
        if p.is_file() and p.suffix in {".py", ".json"}:
            paths.append(p)
    paths.sort(key=lambda p: p.relative_to(package_dir).as_posix())
    if not paths:
        raise ReceiptIntegrityError("source package not available")
    h = hashlib.sha256()
    for p in paths:
        h.update(p.relative_to(package_dir).as_posix().encode("utf-8"))
        h.update(b"\x00" + digest_bytes(p.read_bytes()).encode("ascii") + b"\n")
    return h.hexdigest()


def verify_run_receipt(path: Path, expected_sha256: str | None = None) -> dict:
    try:
        return _verify(path, expected_sha256)
    except ReceiptIntegrityError:
        raise
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ReceiptIntegrityError(f"invalid run receipt: {exc}") from exc


def _verify(path: Path, expected_sha256: str | None) -> dict:
    from native_eset.runner import RunSpec, run_identity, finite_model_digest, RUNTIME_CONTRACT, CLAIM_BOUNDARY
    from native_eset.conventions import decimal_string
    if path.name != "receipt.json" or path.is_symlink() or path.parent.is_symlink():
        raise ReceiptIntegrityError("must specify the regular generated receipt.json")
    folder = path.parent
    names = {"outputs.json", "run_spec.json", "receipt.json", "receipt.sha256"}
    if {p.name for p in folder.iterdir()} != names:
        raise ReceiptIntegrityError("incomplete or unexpected run artifact inventory")
    paths = {n: resolve_regular_file(folder, n) for n in names}
    raw = paths["receipt.json"].read_bytes()
    actual = digest_bytes(raw)
    if expected_sha256 is not None and require_sha256(expected_sha256) != actual:
        raise ReceiptIntegrityError("receipt differs from independently supplied expected digest")
    if paths["receipt.sha256"].read_text(encoding="ascii") != actual + "\n":
        raise ReceiptIntegrityError("receipt integrity mismatch")
    receipt = read_json(paths["receipt.json"])
    required = {"schema", "runtime_contract", "run_id", "backend_id", "theory_id", "model_id",
                "finite_model_sha256", "equation_id", "equation_source_sha256", "code_sha256",
                "spec_sha256", "data_use", "claim_boundary", "output_files", "environment", "gate_ledger"}
    if (not isinstance(receipt, dict) or set(receipt) != required or
            receipt["schema"] != "NATIVE_ESET_RUN_RECEIPT_V2" or receipt["runtime_contract"] != RUNTIME_CONTRACT):
        raise ReceiptIntegrityError("invalid receipt schema; legacy receipts require their original verifier")
    if canonical_json(receipt) != raw:
        raise ReceiptIntegrityError("receipt is not canonically serialized")
    for name in ("finite_model_sha256", "equation_source_sha256", "code_sha256", "spec_sha256"):
        require_sha256(receipt[name], name)
    artifact_hashes = receipt["output_files"]
    if not isinstance(artifact_hashes, dict) or set(artifact_hashes) != {"outputs.json", "run_spec.json"}:
        raise ReceiptIntegrityError("receipt requires exactly the output and original RunSpec")
    for name, expected in artifact_hashes.items():
        if digest_bytes(paths[name].read_bytes()) != require_sha256(expected):
            raise ReceiptIntegrityError(f"output digest mismatch: {name}")
    spec = RunSpec.read(paths["run_spec.json"])
    obj = spec.raw
    if spec.spec_sha256 != receipt["spec_sha256"] or artifact_hashes["run_spec.json"] != spec.spec_sha256:
        raise ReceiptIntegrityError("RunSpec digest is inconsistent")
    for field in ("backend_id", "theory_id", "model_id", "equation_id", "equation_source_sha256", "data_use"):
        if receipt[field] != obj[field]:
            raise ReceiptIntegrityError(f"receipt and RunSpec disagree: {field}")
    model_sha = finite_model_digest(obj)
    if receipt["finite_model_sha256"] != model_sha:
        raise ReceiptIntegrityError("finite model identity mismatch")
    env = receipt["environment"]
    if (not isinstance(env, dict) or set(env) != {"python", "platform", "release", "machine",
                                                "python_implementation", "byteorder", "floating_point"} or
            any(not isinstance(x, str) or len(x) > 512 for x in env.values()) or
            env["floating_point"] != "IEEE754_BINARY64" or env["byteorder"] not in {"big", "little"}):
        raise ReceiptIntegrityError("runtime environment is incomplete")
    expected_id = run_identity(spec.spec_sha256, receipt["code_sha256"], model_sha, env)
    if receipt["run_id"] != expected_id or folder.name != expected_id:
        raise ReceiptIntegrityError("receipt stored under wrong or inconsistent run ID")
    expected_gates = {"source_hash": "PASS", "scientific_backend": "CONTROL_ONLY", "real_ESET_physics": "NOT_RUN",
                      "physical_provider": "NOT_ADMITTED", "empirical_validation": "NOT_RUN"}
    if receipt["claim_boundary"] != CLAIM_BOUNDARY or receipt["gate_ledger"] != expected_gates:
        raise ReceiptIntegrityError("control receipt attempts scientific-status promotion")
    outputs = read_json(paths["outputs.json"])
    if (not isinstance(outputs, dict) or outputs.get("schema") != "NATIVE_ESET_CONTROL_OUTPUT_V1" or
            outputs.get("scope") != "EXTERNAL_REFERENCE_CONTROL_ONLY" or
            outputs.get("validation") != "NOT_ESET_EMPIRICAL_VALIDATION" or
            outputs.get("graph_status") != "NOT_A_GRAPH_ADMITTED_PROVIDER" or
            outputs.get("finite_model_sha256") != model_sha):
        raise ReceiptIntegrityError("output claim/schema mismatch")
    for key in ("model_id", "equation_id", "observable"):
        if outputs.get(key) != obj[key]:
            raise ReceiptIntegrityError(f"output identity mismatch: {key}")
    rows = outputs.get("values")
    if (not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows) or
            [r.get("z") for r in rows] != obj["redshifts"]):
        raise ReceiptIntegrityError("output coordinate rows do not match RunSpec")
    for row in rows:
        if row.get("unit") != "1" or not isinstance(row.get("numerics"), dict):
            raise ReceiptIntegrityError("output unit/numerical metadata mismatch")
        decimal_string(row.get("value"))
    return {"status": "VERIFIED_OUTPUT_AND_RECEIPT_BYTES_ONLY", "run_id": receipt["run_id"],
            "outputs_sha256": artifact_hashes["outputs.json"], "receipt_sha256": actual,
            "claimed_role": receipt["claim_boundary"],
            "integrity_anchor": "EXTERNAL_EXPECTED_DIGEST_MATCHED" if expected_sha256 else "SELF_CONTAINED_ONLY",
            "note": "Not a signature, solver replay, author authentication, or scientific admission"}
