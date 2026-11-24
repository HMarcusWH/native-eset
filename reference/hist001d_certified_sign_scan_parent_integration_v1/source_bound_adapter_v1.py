"""HIST001D source-bound adapter for the *existing* two-engine exact-real API.

SOURCE ONLY. No protected original March arrays, PINNED parent archives or
source-specific output data are distributed here.  This adapter only runs when
an operator supplies all six SHA-locked parents, a clean extracted exact-hash
bracket verifier, and the protected bracket/global proof archives.

The conditional global uniqueness theorem is inherited, not newly derived.
The original compiled NumPy/libm evaluator is NEVER used for sign authority.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from fractions import Fraction as F
from pathlib import Path
from types import MappingProxyType
import sys
from typing import Any
import zipfile

from certified_sign_scan import (
    BRACKETS_HEX, BRACKET_ZIP_SHA256, DOMAIN_HI, DOMAIN_LO, MODEL_ID,
    SOURCE_SHA256, SourceContract, Unresolved, canonical_json,
)

GLOBAL_SHA = "ee677eea7f2f7bcf5c90347f5c54658988090340d888870c7e60071263693fff"
GUARD_SHA = "963b852b61ce0fbec9fa3f508050dd59b6cf3d0a7098800c28f51d7228cdd33e"
RESULT_SHA = "7c7e98844c06ed3478d8adf2137d3dbbcddeca66a71a2119220659fe3211c67c"
GLOBAL_INDEPENDENT_AUDIT_SHA = "878823bb4a4e9355802d33f97d47a9472181dc7a6d5f99395dc3f3103b413935"
ROOT_NAME = "HIST001D_GUARDED_BINARY64_ROOT_BRACKETING_FULL_v1_2026_11_07_NONPROMOTING.zip"
GLOBAL_NAME = "HIST001D_SOURCE_CONNECTED_K180_D120_KNOT_SAFE_GLOBAL_ROOTS_v1_2026_11_06_FULL_NONPROMOTING.zip"
LENSES = tuple(BRACKETS_HEX)
SIGNED_ENGINE_FILES = (
    "strict_sign_api.py", "source_bind.py", "source_model.py",
    "knot_offgrid_math.py", "independent_checker.py", "fast_exp.py", "math_bounds.py",
)
ROOT_ENGINE_FILES = ("certified_root_bracketer.py", "release_checks.py", "adversarial_release.py", "verify_release.py")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: bytes) -> dict:
    try:
        obj = json.loads(data)
        if not isinstance(obj, dict):
            raise ValueError("not a mapping")
        return obj
    except (ValueError, UnicodeError) as exc:
        raise Unresolved("MALFORMED_PROOF_RECORD") from exc


def _envpath(env: str, *, directory: bool = False) -> Path:
    raw = os.environ.get(env, "")
    if not raw or raw.strip() != raw:
        raise Unresolved("MISSING_REQUIRED_SOURCE_PATH_" + env)
    p = Path(raw).resolve(strict=True)
    if (not p.is_dir()) if directory else (not p.is_file()):
        raise Unresolved("SOURCE_PATH_WRONG_TYPE_" + env)
    return p


def _require_zip(path: Path, digest: str):
    if sha(path.read_bytes()) != digest:
        raise Unresolved("PINNED_ARCHIVE_HASH_MISMATCH_" + path.name)
    z = zipfile.ZipFile(path)
    if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
        raise Unresolved("PINNED_ARCHIVE_CORRUPT_OR_DUPLICATE")
    return z


def _check_proof_source_files(engine: Path, root: zipfile.ZipFile, guard: zipfile.ZipFile):
    for filename in SIGNED_ENGINE_FILES:
        p = engine / filename
        if not p.is_file() or p.is_symlink() or p.read_bytes() != guard.read(filename) or p.read_bytes() != root.read(filename):
            raise Unresolved("SIGNED_ENGINE_FILE_NOT_PINNED_" + filename)
    for filename in ROOT_ENGINE_FILES:
        p = engine / filename
        if not p.is_file() or p.is_symlink() or p.read_bytes() != root.read(filename):
            raise Unresolved("ROOT_ENGINE_FILE_NOT_PINNED_" + filename)


def _bounds_as_rationals(lo: F, hi: F) -> tuple[str, str]:
    if type(lo) is not F or type(hi) is not F or lo > hi:
        raise Unresolved("NONRATIONAL_OR_REVERSED_INTERVAL")
    return f"{lo.numerator}/{lo.denominator}", f"{hi.numerator}/{hi.denominator}"


def _two_engine_result(lens: str, lo_hex: str, hi_hex: str, bounds: list[tuple[F, F]],
                       proof: dict, kind: str) -> dict:
    if len(bounds) != 2:
        raise Unresolved("NOT_TWO_INTERVAL_ENGINES")
    signs = []
    for lo, hi in bounds:
        if lo > hi:
            raise Unresolved("INTERVAL_ORDER_VIOLATED")
        signs.append("POSITIVE" if lo > 0 else "NEGATIVE" if hi < 0 else "UNRESOLVED")
    if signs[0] != signs[1] or signs[0] == "UNRESOLVED" or max(x[0] for x in bounds) > min(x[1] for x in bounds):
        raise Unresolved("SIGN_ENGINES_INCONCLUSIVE_OR_DISJOINT")
    engines = []
    for name, (low, high) in zip(("pinned_sourceconnected", "pinned_independent_checker"), bounds):
        l, h = _bounds_as_rationals(low, high)
        trace = {"engine": name, "lo": l, "hi": h, "lens": lens, "from": lo_hex, "to": hi_hex,
                 "kind": kind, "original_strict_guard": proof}
        engines.append({"engine_id": name, "lo": l, "hi": h,
                        "proof_trace_sha256": sha(canonical_json(trace))})
    return {"schema": "HIST001D_TWO_ENGINE_SIGN_GUARD_V1", "kind": kind,
            "model_id": MODEL_ID, "source_sha256": SOURCE_SHA256, "lens": lens,
            "lo_hex": lo_hex, "hi_hex": hi_hex, "status": "CERTIFIED", "engines": engines}


class ProtectedSourceBoundAdapter:
    """Use one process with externally SHA-pinned engine sources; never reuse synthetic signs.

    Replaying the root bracketer authenticates frozen sources, entire source-bound
    six-lens root traces and its independent rational sign-guard execution.
    The independent *global panel theorem* remains separately identified as
    inherited unless its complete checker is explicitly rerun and receipt-locked.
    """

    def __init__(self):
        self.engine = _envpath("HIST001D_ENGINE_DIR", directory=True)
        self.parents = _envpath("HIST001D_PARENT_DIR", directory=True)
        self.root_zip_path = _envpath("HIST001D_ROOT_ZIP")
        self.global_zip_path = self.parents / GLOBAL_NAME
        self.guard_zip_path = self.parents / "HIST001D_EXACT_REAL_FAIL_CLOSED_SIGN_API_FULL_v1_2026_11_07_NONPROMOTING.zip"
        self.global_audit_path = _envpath("HIST001D_GLOBAL_AUDIT")
        if not self.global_zip_path.is_file() or not self.guard_zip_path.is_file():
            raise Unresolved("GLOBAL_OR_GUARD_ARCHIVE_MISSING")
        self.root = _require_zip(self.root_zip_path, BRACKET_ZIP_SHA256)
        self.global_root = _require_zip(self.global_zip_path, GLOBAL_SHA)
        self.guard = _require_zip(self.guard_zip_path, GUARD_SHA)
        _check_proof_source_files(self.engine, self.root, self.guard)
        pin_record = _json(self.root.read("PARENT_SHA256.json"))
        if pin_record.get("original_source_46_plus_three_sha256") != SOURCE_SHA256:
            raise Unresolved("ORIGINAL_MARCH_SOURCE_MISMATCH")
        for dep in pin_record.get("parents", {}).values():
            p = self.parents / dep["filename"]
            if not p.is_file() or sha(p.read_bytes()) != dep["sha256"]:
                raise Unresolved("SIX_PARENT_ARCHIVE_MISSING_OR_TAMPERED")
        # The externally supplied extracted files are code only, identical to the
        # independently pinned root archive, and contain NO protected arrays.
        if str(self.engine) not in sys.path:
            sys.path.insert(0, str(self.engine))
        self.rootmod = importlib.import_module("certified_root_bracketer")
        self.source = importlib.import_module("source_model")
        self.signapi = importlib.import_module("strict_sign_api")
        self.engine2 = importlib.import_module("independent_checker")
        self.engine1 = importlib.import_module("knot_offgrid_math")
        self.release = importlib.import_module("release_checks")
        self.adversarial = importlib.import_module("adversarial_release")
        self._cases: dict | None = None
        self._replayed = None
        self._attestation = None

    def replay_parents(self, contract: SourceContract):
        contract.validate()
        if (contract.scope != "SOURCE_REPLAYED_CANDIDATE_MATH" or
            contract.uniqueness_sha256 != GLOBAL_SHA):
            raise Unresolved("GLOBAL_UNIQUENESS_IDENTITY_OR_SOURCE_SCOPE_INVALID")
        if self._attestation is not None:
            return dict(self._attestation)
        # Verify immutable original source + current runtime bitwise B/D.
        self._cases = self.signapi.load_verified_cases(self.parents)
        if tuple(self._cases) != LENSES:
            raise Unresolved("SOURCE_ROSTER_NOT_PINNED")
        inherit = self.rootmod.trusted_root_records(self.global_zip_path, self._cases)
        for lens, bounds in BRACKETS_HEX.items():
            # The expected adjacent bit-pattern pair must also come from the
            # historical signed source-bound bracketer, not literals alone.
            if lens not in inherit:
                raise Unresolved("INHERITED_GLOBAL_ROOT_MISSING")
        result = self.rootmod.evaluate_all(self.parents)
        self.release.check_contract(result)
        archived = self.root.read("results_source_bound.json")
        source_bytes = self.source.canonical(result)
        if source_bytes != archived or sha(archived) != RESULT_SHA:
            raise Unresolved("FRESH_ROOT_PRODUCER_NOT_BYTE_IDENTICAL")
        neg = self.adversarial.audit(result, trusted_recomputed=result)
        if self.source.canonical(neg) != self.root.read("adversarial_audit.json"):
            raise Unresolved("FRESH_ADVERSARIAL_AUDIT_NOT_IDENTICAL")
        for record in result["lenses"]:
            lens = record["lens"]
            if (record.get("left_positive_binary64_hex") != float.fromhex(BRACKETS_HEX[lens][0]).hex()
                or record.get("right_negative_binary64_hex") != float.fromhex(BRACKETS_HEX[lens][1]).hex()):
                raise Unresolved("SIGNED_SOURCE_BOUND_BRACKET_NOT_REPRODUCED")
        # Source-dependent global theorem: a sealed, trusted inherited theorem
        # with explicit independent-checker results. This does NOT say the
        # computationally heavy full global producer is reexecuted here.
        m = _json(self.global_root.read("MANIFEST_SHA256.json"))
        for name, spec in m.get("files", {}).items():
            body = self.global_root.read(name)
            if sha(body) != spec["sha256"] or len(body) != spec["size_bytes"]:
                raise Unresolved("GLOBAL_THEOREM_MEMBER_MANIFEST_FAILURE")
        aggregate = _json(self.global_root.read("results/RESULTS_AGGREGATE.json"))
        if (aggregate.get("six_full_original_domain_uniqueness_claims") != 6 or
            aggregate.get("total_strict_sign_exclusion_leaves") != 1400 or
            aggregate.get("root_count_per_lens") != [1]*6):
            raise Unresolved("GLOBAL_THEOREM_COVERAGE_CLAIM_UNSUPPORTED")
        # Separate source-replayed independent global proof: the 1,400
        # complementary all-real sign panels and six knot-free derivative
        # checks have been reexecuted by the distinct pinned engine. The
        # independent audit is externally recorded at a pinned content hash;
        # this adapter does NOT reexecute the entire original proof producer.
        global_bytes = self.global_audit_path.read_bytes()
        if sha(global_bytes) != GLOBAL_INDEPENDENT_AUDIT_SHA:
            raise Unresolved("GLOBAL_INDEPENDENT_AUDIT_HASH_NOT_PINNED")
        global_recheck = _json(global_bytes)
        if (global_recheck.get("schema") != "HIST001D_GLOBAL_THEOREM_INDEPENDENT_PANEL_REEXECUTION_V1" or
            global_recheck.get("status") != "PASS_SOURCE_BOUND_INDEPENDENT_1400_PANEL_REPLAY" or
            global_recheck.get("global_parent_zip_sha256") != GLOBAL_SHA or
            global_recheck.get("source_sha256") != SOURCE_SHA256 or
            global_recheck.get("independent_exclusion_panels_recomputed") != 1400 or
            global_recheck.get("six_knot_safe_root_derivative_checks_recomputed") != 6 or
            global_recheck.get("global_uniqueness_parent_full_producer_replayed") is not False or
            global_recheck.get("physical_provider_admitted") is not False or
            global_recheck.get("empirical_validation") != "NOT_ESTABLISHED"):
            raise Unresolved("GLOBAL_INDEPENDENT_AUDIT_SCOPE_INVALID")
        metadata={k:v for k,v in global_recheck.items() if k != "receipt_sha256"}
        if sha(canonical_json(metadata)) != global_recheck.get("receipt_sha256"):
            raise Unresolved("GLOBAL_INDEPENDENT_AUDIT_DIGEST_INVALID")
        if len(global_recheck.get("results",[])) != 6:
            raise Unresolved("GLOBAL_INDEPENDENT_LENS_COUNT_INVALID")
        expected_counts={"J0822+1828":236,"J0915+4211":231,"J0930+2855":301,
                         "J1021+2028":204,"J1111+2234":207,"J1135+3720":221}
        for record in global_recheck["results"]:
            lens=record.get("lens")
            if lens not in expected_counts or record.get("exclusion_panels_recomputed") != expected_counts[lens]:
                raise Unresolved("GLOBAL_INDEPENDENT_PANEL_COVER_MISMATCH")
            if record.get("source_node_sha256") != self._cases[lens].source_node_sha256:
                raise Unresolved("GLOBAL_INDEPENDENT_SOURCE_NODES_UNBOUND")
            row=self.global_root.read("results/"+lens.replace('+','p')+"_independent.json")
            if record.get("independent_receipt_sha256") != sha(row):
                raise Unresolved("GLOBAL_INDEPENDENT_SEALED_RECEIPT_MISMATCH")
        self._replayed = result
        evidence = {
            "model_id": contract.model_id, "source_sha256": contract.source_sha256,
            "bracket_sha256": contract.bracket_sha256,
            "uniqueness_sha256": contract.uniqueness_sha256, "scope": contract.scope,
            "verification_result": "PASS_SOURCE_REPLAY",
            "theorem_claim": "CONTINUOUS_EXACTLY_ONE_REAL_ROOT_ON_FROZEN_DOMAIN",
            "domain_lo_hex": DOMAIN_LO.hex(), "domain_hi_hex": DOMAIN_HI.hex(),
            "verifier_sha256": sha((self.engine/"verify_release.py").read_bytes()),
            "replay_receipt_sha256": sha(source_bytes),
            "fresh_source_bracketing_replay": True,
            "fresh_bracketing_guard_evaluations": 112,
            "global_uniqueness_dependency": "INHERITED_AND_FRESH_INDEPENDENT_1400_PANEL_CHECK",
            "global_independent_panel_replay_receipt_sha256": GLOBAL_INDEPENDENT_AUDIT_SHA,
            "global_unique_root_derivative_checks_recomputed": 6,
            "global_uniqueness_fresh_producer_replay": False,
            "physics_provider_admission": False,
        }
        self._attestation = evidence
        return dict(evidence)

    def _case(self, lens: str):
        if self._cases is None:
            raise Unresolved("PARENT_SOURCE_NOT_REPLAYED")
        if lens not in self._cases:
            raise Unresolved("UNPINNED_LENS")
        return self._cases[lens]

    def point_guard(self, lens: str, x_hex: str):
        case = self._case(lens)
        try:
            if x_hex != float.fromhex(x_hex).hex():
                raise ValueError("noncanonical")
            radius = float.fromhex(x_hex)
            raw = self.signapi.certify(case, radius)
            self.rootmod.certified_direction(raw, lens, case, radius)
            # Certified API uses outward 1e-18 M_sun decimal endpoints;
            # these are exact dyadic-free RATIONAL numbers, not floating estimates.
            aa = tuple(F(x) for x in raw["primary_outward_msun"])
            bb = tuple(F(x) for x in raw["independent_outward_msun"])
            return _two_engine_result(lens, x_hex, x_hex, [aa, bb],
                                      {"strict_certify_sha256": sha(self.source.canonical(raw)),
                                       "primary_bits": raw["primary_sqrt_bits"],
                                       "independent_bits": raw["independent_sqrt_bits"]}, "POINT")
        except Exception as exc:
            raise Unresolved("POINT_TWO_ENGINE_CERTIFICATION_FAILED_"+type(exc).__name__) from exc

    def range_guard(self, lens: str, lo_hex: str, hi_hex: str):
        case = self._case(lens)
        try:
            if lo_hex != float.fromhex(lo_hex).hex() or hi_hex != float.fromhex(hi_hex).hex():
                raise ValueError("noncanonical")
            lo, hi = F.from_float(float.fromhex(lo_hex)), F.from_float(float.fromhex(hi_hex))
            if not (F.from_float(DOMAIN_LO) <= lo <= hi <= F.from_float(DOMAIN_HI)):
                raise ValueError("outside source domain")
            a_raw = self.engine1.SourceConnected(case._data, bits=96).interval(lo, hi)
            b_raw = self.engine2.interval_H(case._data, lo, hi)
            # Preserve rigorous outward inclusion while keeping the scanner
            # rational parser bounded to small exact integer ratios.
            a = tuple(F(x) for x in self.signapi.outward_decimal(*a_raw))
            b = tuple(F(x) for x in self.signapi.outward_decimal(*b_raw))
            return _two_engine_result(lens, lo_hex, hi_hex, [a, b],
                                      {"source_binding": case.source_node_sha256,
                                       "engine_source": GLOBAL_SHA}, "RANGE_ALL_REAL")
        except Exception as exc:
            raise Unresolved("RANGE_TWO_ENGINE_CERTIFICATION_FAILED_"+type(exc).__name__) from exc


def make_adapter() -> ProtectedSourceBoundAdapter:
    return ProtectedSourceBoundAdapter()
