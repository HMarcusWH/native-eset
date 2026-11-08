"""HIST-001D source-only, fail-closed binary64 sign-coverage orchestrator.

This module DOES NOT calculate or authenticate historical residuals. The sole sign
authority is the separately replayed two-engine mathematical interval sign API.
Theorem-cover mode additionally depends on the source-locked continuity/global
exactly-one-real-root theorem over the declared finite 0.02--120 kpc domain.

No physics, original compiled NumPy/libm sign, or observational validation claims.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Protocol

SCHEMA = "HIST001D_CERTIFIED_BINARY64_SIGN_COVERAGE_V1"
MODEL_ID = "HIST001D_MARCH180_SOURCE_CONNECTED_K180_D120_EXACT_REAL_HNEW"
SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
BRACKET_ZIP_SHA256 = "252d502a1a6607751c5604de221767a10ff6f28e253b0c92d4988773e65ebb29"
DOMAIN_LO = float(0.02)  # actual stored positive binary64 0.02, NOT rational 1/50
DOMAIN_HI = float(120.0)

# Navigation/expectation locks, NOT proof of sign or original-source accuracy.
BRACKETS_HEX = {
    "J0822+1828": ("0x1.cd5bc03f4138cp+0", "0x1.cd5bc03f4138dp+0"),
    "J0915+4211": ("0x1.64e3e6a2fbddep+0", "0x1.64e3e6a2fbddfp+0"),
    "J0930+2855": ("0x1.24ed39965d30cp+2", "0x1.24ed39965d30dp+2"),
    "J1021+2028": ("0x1.237de7bf54ab3p+0", "0x1.237de7bf54ab4p+0"),
    "J1111+2234": ("0x1.f830fcf0376a8p+1", "0x1.f830fcf0376a9p+1"),
    "J1135+3720": ("0x1.1c067a5345c8cp+1", "0x1.1c067a5345c8dp+1"),
}
HEX_SHA = re.compile(r"[0-9a-f]{64}\Z")
RATIONAL = re.compile(r"(-?(?:0|[1-9][0-9]*))/([1-9][0-9]*)\Z")
ALLOWED_STATUSES = frozenset({"POSITIVE", "NEGATIVE", "UNRESOLVED"})


class Unresolved(RuntimeError):
    """Any missing/invalid scientific proof precondition; no best-effort promotion."""


def is_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX_SHA.fullmatch(value))


def bit_of(value: float) -> int:
    """Ordered unsigned IEEE754 binary64 code for positive, finite inputs only."""
    if not isinstance(value, float) or not math.isfinite(value) or value <= 0.0:
        raise Unresolved("NONFINITE_NONPOSITIVE_OR_NON_BINARY64")
    return struct.unpack(">Q", struct.pack(">d", value))[0]


def float_of(code: int) -> float:
    if type(code) is not int or not 0 < code < 0x7FF0000000000000:
        raise Unresolved("BIT_CODE_OUTSIDE_POSITIVE_FINITE")
    return struct.unpack(">d", struct.pack(">Q", code))[0]


def canonical_json(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                       allow_nan=False) + "\n").encode("ascii")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()


def rational(value: Any) -> Fraction:
    if not isinstance(value, str) or len(value) > 2048:
        raise Unresolved("INVALID_RATIONAL_REPRESENTATION")
    m = RATIONAL.fullmatch(value)
    if not m:
        raise Unresolved("INVALID_RATIONAL_REPRESENTATION")
    n, d = int(m.group(1)), int(m.group(2))
    if n.bit_length() > 4096 or d.bit_length() > 4096:
        raise Unresolved("RATIONAL_SIZE_LIMIT")
    return Fraction(n, d)


@dataclass(frozen=True)
class SourceContract:
    model_id: str = MODEL_ID
    source_sha256: str = SOURCE_SHA256
    bracket_sha256: str = BRACKET_ZIP_SHA256
    uniqueness_sha256: str = ""
    scope: str = "SOURCE_REPLAYED_CANDIDATE_MATH"

    def validate(self) -> None:
        if self.model_id != MODEL_ID or self.source_sha256 != SOURCE_SHA256:
            raise Unresolved("SOURCE_OR_MATHEMATICAL_IDENTITY_MISMATCH")
        if self.bracket_sha256 != BRACKET_ZIP_SHA256 or not is_sha(self.uniqueness_sha256):
            raise Unresolved("BRACKET_OR_UNIQUENESS_PARENT_UNPINNED")
        if self.scope not in ("SOURCE_REPLAYED_CANDIDATE_MATH", "SYNTHETIC_TEST_ONLY"):
            raise Unresolved("UNRECOGNIZED_SCOPE")


class StrictSignAPI(Protocol):
    """Implement using the sealed source-bound *two-engine* API, never NumPy signs.

    replay_parents() MUST actually replay/verify source, bracket, global-theorem
    evidence. The scanner checks output structure but cannot substitute for that.
    A production adapter must reject changed SHA, original arrays or theorem scope.
    """
    def replay_parents(self, contract: SourceContract) -> Mapping[str, Any]: ...
    def point_guard(self, lens: str, x_hex: str) -> Mapping[str, Any]: ...
    # Optional for adaptive mode. Return a rigorous enclosure of the exact-real
    # residual on *every real* R in [lo,hi], or status UNRESOLVED.
    def range_guard(self, lens: str, lo_hex: str, hi_hex: str) -> Mapping[str, Any]: ...


def parent_attestation(api: StrictSignAPI, contract: SourceContract) -> dict:
    contract.validate()
    evidence = api.replay_parents(contract)
    if not isinstance(evidence, Mapping):
        raise Unresolved("PARENT_EVIDENCE_MISSING")
    required = {
        "model_id": contract.model_id,
        "source_sha256": contract.source_sha256,
        "bracket_sha256": contract.bracket_sha256,
        "uniqueness_sha256": contract.uniqueness_sha256,
        "scope": contract.scope,
        "verification_result": "PASS_SOURCE_REPLAY" if contract.scope != "SYNTHETIC_TEST_ONLY" else "PASS_SYNTHETIC_REPLAY",
        "theorem_claim": "CONTINUOUS_EXACTLY_ONE_REAL_ROOT_ON_FROZEN_DOMAIN",
        "domain_lo_hex": DOMAIN_LO.hex(),
        "domain_hi_hex": DOMAIN_HI.hex(),
    }
    for key, expected in required.items():
        if evidence.get(key) != expected:
            raise Unresolved("PARENT_ATTESTATION_INVALID_" + key)
    for key in ("verifier_sha256", "replay_receipt_sha256"):
        if not is_sha(evidence.get(key)):
            raise Unresolved("PARENT_ATTESTATION_MISSING_" + key)
    return dict(evidence)


def guard_sign(entry: Mapping[str, Any], *, lens: str, x_lo: float, x_hi: float,
               contract: SourceContract, guard_kind: str) -> tuple[str, list]:
    """Strict exact-rational enclosure signs from two engines, zero is unresolved.

    Unlike a floating sign, an interval with upper < 0 or lower > 0 proves sign.
    For a range, the adapter must prove an enclosure of all reals in [lo,hi].
    """
    if not isinstance(entry, Mapping) or entry.get("status") != "CERTIFIED":
        raise Unresolved("GUARD_INCONCLUSIVE_OR_MISSING")
    checks = {
        "schema": "HIST001D_TWO_ENGINE_SIGN_GUARD_V1",
        "kind": guard_kind,
        "model_id": contract.model_id,
        "source_sha256": contract.source_sha256,
        "lens": lens,
        "lo_hex": x_lo.hex(),
        "hi_hex": x_hi.hex(),
    }
    for key, expected in checks.items():
        if entry.get(key) != expected:
            raise Unresolved("GUARD_IDENTITY_MISMATCH_" + key)
    engines = entry.get("engines")
    if not isinstance(engines, list) or len(engines) != 2:
        raise Unresolved("NOT_EXACTLY_TWO_ENGINE_ENCLOSURES")
    names: set[str] = set()
    signs: list[str] = []
    traces: list[dict] = []
    for e in engines:
        if not isinstance(e, Mapping) or not isinstance(e.get("engine_id"), str):
            raise Unresolved("ENGINE_ID_MISSING")
        name = e["engine_id"]
        if not (1 <= len(name) <= 80) or name in names:
            raise Unresolved("ENGINE_IDENTITIES_NOT_DISTINCT")
        names.add(name)
        if not is_sha(e.get("proof_trace_sha256")):
            raise Unresolved("ENGINE_PROOF_TRACE_MISSING")
        lo = rational(e.get("lo"))
        hi = rational(e.get("hi"))
        if lo > hi:
            raise Unresolved("INVALID_INTERVAL_ORDER")
        if lo > 0:
            signs.append("POSITIVE")
        elif hi < 0:
            signs.append("NEGATIVE")
        else:
            raise Unresolved("ZERO_CONTAINED_BY_INTERVAL")
        traces.append({"engine_id": name, "proof_trace_sha256": e["proof_trace_sha256"],
                       "lo": e["lo"], "hi": e["hi"]})
    if len(set(signs)) != 1:
        raise Unresolved("TWO_ENGINES_DISAGREE")
    return signs[0], traces


def _segment(lo: int, hi: int, status: str, method: str,
             *, links: Mapping[str, Any], reason: str = "") -> dict:
    if lo > hi or status not in ALLOWED_STATUSES:
        raise Unresolved("INVALID_SEGMENT")
    return {"lo_hex": float_of(lo).hex(), "hi_hex": float_of(hi).hex(),
            "lo_bits": str(lo), "hi_bits": str(hi), "binary64_count": str(hi-lo+1),
            "classification": status, "method": method, "proof_links": dict(links),
            "reason": reason if status == "UNRESOLVED" else ""}


def verify_partition(segments: list, domain_low: int, domain_high: int) -> None:
    """Every single bit pattern in scope must be represented once, no gaps."""
    if not segments or type(domain_low) is not int or type(domain_high) is not int:
        raise Unresolved("COVERAGE_EMPTY_OR_INVALID")
    next_bit = domain_low
    for s in segments:
        if not isinstance(s, Mapping) or s.get("classification") not in ALLOWED_STATUSES:
            raise Unresolved("UNKNOWN_SEGMENT_STATUS")
        lo, hi = int(s["lo_bits"]), int(s["hi_bits"])
        if lo != next_bit or lo > hi:
            raise Unresolved("COVERAGE_GAP_OR_OVERLAP")
        if s.get("lo_hex") != float_of(lo).hex() or s.get("hi_hex") != float_of(hi).hex():
            raise Unresolved("COVERAGE_HEX_BITS_DISAGREE")
        if int(s.get("binary64_count", "-1")) != hi-lo+1:
            raise Unresolved("COVERAGE_COUNT_WRONG")
        if s.get("classification") != "UNRESOLVED" and not s.get("proof_links"):
            raise Unresolved("CLASSIFICATION_HAS_NO_PROOF_LINK")
        next_bit = hi+1
    if next_bit != domain_high+1:
        raise Unresolved("COVERAGE_INCOMPLETE")


def _failure(lens: str, reason: str, lo: int, hi: int, *, mode: str) -> dict:
    segment = _segment(lo, hi, "UNRESOLVED", "NONE", links={}, reason=reason)
    return {"lens": lens, "status": "UNRESOLVED", "mode": mode,
            "evaluations": 0, "segments": [segment], "root_bracket": None,
            "reason": reason}


def theorem_cover_one(lens: str, api: StrictSignAPI, contract: SourceContract,
                      attestation: Mapping[str, Any], *, max_evals: int = 2) -> dict:
    """Cover a complete finite binary64 domain *conditional* on global uniqueness."""
    dl, dh = bit_of(DOMAIN_LO), bit_of(DOMAIN_HI)
    if lens not in BRACKETS_HEX:
        raise Unresolved("UNKNOWN_LENS")
    try:
        if type(max_evals) is not int or max_evals < 2:
            raise Unresolved("INSUFFICIENT_EVALUATION_BUDGET")
        left_hex, right_hex = BRACKETS_HEX[lens]
        left, right = float.fromhex(left_hex), float.fromhex(right_hex)
        lb, rb = bit_of(left), bit_of(right)
        if not (dl <= lb < rb <= dh and rb == lb+1):
            raise Unresolved("NOT_ADJACENT_OR_OUTSIDE_DECLARED_DOMAIN")
        # All sign authority is delegated to the replayed two-engine API.
        ga = api.point_guard(lens, left.hex())
        sa, ta = guard_sign(ga, lens=lens, x_lo=left, x_hi=left,
                            contract=contract, guard_kind="POINT")
        gb = api.point_guard(lens, right.hex())
        sb, tb = guard_sign(gb, lens=lens, x_lo=right, x_hi=right,
                            contract=contract, guard_kind="POINT")
        if (sa, sb) != ("POSITIVE", "NEGATIVE"):
            raise Unresolved("ROOT_ENDPOINT_SIGN_ORIENTATION_WRONG")
        proof_links = {"root_bracketing_sha256": contract.bracket_sha256,
                       "global_uniqueness_sha256": contract.uniqueness_sha256,
                       "parent_replay_sha256": attestation["replay_receipt_sha256"],
                       "left_endpoint_two_engine_traces": ta,
                       "right_endpoint_two_engine_traces": tb}
        segments = [
            _segment(dl, lb, "POSITIVE", "GLOBAL_UNIQUENESS_CONTINUITY_AND_ENDPOINT_SIGN", links=proof_links),
            _segment(rb, dh, "NEGATIVE", "GLOBAL_UNIQUENESS_CONTINUITY_AND_ENDPOINT_SIGN", links=proof_links),
        ]
        verify_partition(segments, dl, dh)
        return {"lens": lens, "status": "CERTIFIED_CONDITIONAL", "mode": "THEOREM_COVER",
                "evaluations": 2, "segments": segments,
                "root_bracket": {"last_positive": left.hex(), "first_negative": right.hex(),
                                 "adjacent_binary64": True, "no_float_between": True,
                                 "root_is_floating_zero": False,
                                 "real_root_uniqueness": "INHERITED_GLOBAL_THEOREM"},
                "reason": ""}
    except Exception as exc:  # fail closed even when assertions disabled
        return _failure(lens, type(exc).__name__+":"+str(exc), dl, dh, mode="THEOREM_COVER")


def adaptive_cover_one(lens: str, api: StrictSignAPI, contract: SourceContract,
                       attestation: Mapping[str, Any], *, lo: float = DOMAIN_LO,
                       hi: float = DOMAIN_HI, max_evals: int = 128) -> dict:
    """General finite-binary64 scan with *rigorous* range sign inclusions.

    An `UNRESOLVED` range is bisected in ordered bit space. A singleton may be
    signed only by the strict two-engine point API. No uniqueness is inferred.
    Any budget exhaustion returns explicit unresolved leaf/remaining ranges.
    """
    try:
        low, high = bit_of(lo), bit_of(hi)
        if lens not in BRACKETS_HEX or not (bit_of(DOMAIN_LO) <= low <= high <= bit_of(DOMAIN_HI)):
            raise Unresolved("INVALID_LENS_OR_DOMAIN")
    except Exception as exc:
        dl, dh = bit_of(DOMAIN_LO), bit_of(DOMAIN_HI)
        return _failure(lens, str(exc), dl, dh, mode="ADAPTIVE_COVER")
    if type(max_evals) is not int or max_evals < 1:
        return _failure(lens, "INSUFFICIENT_EVALUATION_BUDGET", low, high, mode="ADAPTIVE_COVER")
    pending = [(low, high)]
    segments = []
    evaluations = 0
    while pending:
        a, b = pending.pop()
        if evaluations >= max_evals:
            segments.append(_segment(a, b, "UNRESOLVED", "NONE", links={}, reason="EVALUATION_BUDGET_EXHAUSTED"))
            continue
        evaluations += 1
        status = "UNRESOLVED"
        traces = []
        reason = "INCONCLUSIVE_GUARD"
        try:
            if a == b:
                raw = api.point_guard(lens, float_of(a).hex())
                kind = "POINT"
            else:
                raw = api.range_guard(lens, float_of(a).hex(), float_of(b).hex())
                kind = "RANGE_ALL_REAL"
            status, traces = guard_sign(raw, lens=lens, x_lo=float_of(a), x_hi=float_of(b),
                                        contract=contract, guard_kind=kind)
        except Exception as exc:
            reason = type(exc).__name__+":"+str(exc)
        if status != "UNRESOLVED":
            links = {"source_sha256": contract.source_sha256,
                     "parent_replay_sha256": attestation["replay_receipt_sha256"],
                     "two_engine_traces": traces,
                     "evaluation_scope": kind}
            segments.append(_segment(a, b, status, "DIRECT_TWO_ENGINE_ENCLOSURE", links=links))
        elif a == b:
            segments.append(_segment(a, b, "UNRESOLVED", "NONE", links={}, reason=reason))
        else:
            middle = (a+b)//2
            pending.append((middle+1, b))
            pending.append((a, middle))
    segments.sort(key=lambda z: int(z["lo_bits"]))
    verify_partition(segments, low, high)
    ok = all(s["classification"] != "UNRESOLVED" for s in segments)
    return {"lens": lens, "status": "CERTIFIED_CONDITIONAL" if ok else "UNRESOLVED",
            "mode": "ADAPTIVE_COVER", "evaluations": evaluations, "segments": segments,
            "root_bracket": None,
            "reason": "" if ok else "ONE_OR_MORE_UNRESOLVED_CELLS"}


def scan(api: StrictSignAPI | None, contract: SourceContract, *, mode: str = "THEOREM_COVER",
         lenses: tuple[str, ...] = tuple(BRACKETS_HEX), max_evals_per_lens: int = 128,
         lo: float = DOMAIN_LO, hi: float = DOMAIN_HI) -> dict:
    """Fail closed for *all six* if parent replay missing or mismatched."""
    if mode not in ("THEOREM_COVER", "ADAPTIVE_COVER"):
        raise ValueError("unknown mode")
    if not lenses or len(set(lenses)) != len(lenses) or any(l not in BRACKETS_HEX for l in lenses):
        raise ValueError("unknown or duplicate lens")
    dl, dh = bit_of(DOMAIN_LO), bit_of(DOMAIN_HI)
    requested_lo, requested_hi = (DOMAIN_LO, DOMAIN_HI) if mode == "THEOREM_COVER" else (lo, hi)
    try:
        req_low_bit, req_high_bit = bit_of(requested_lo), bit_of(requested_hi)
        if not dl <= req_low_bit <= req_high_bit <= dh:
            raise Unresolved("REQUESTED_DOMAIN_OUTSIDE_ORIGINAL_SOURCE_SUPPORT")
    except Exception as exc:
        # No fabricated coverage of a malformed or unauthorized domain.
        raise Unresolved("INVALID_REQUESTED_SCAN_DOMAIN:" + str(exc)) from exc
    parent = None
    failure = ""
    try:
        if api is None:
            raise Unresolved("PARENT_AND_SIGN_API_UNAVAILABLE")
        parent = parent_attestation(api, contract)
    except Exception as exc:
        failure = type(exc).__name__+":"+str(exc)
    results = []
    for lens in lenses:
        if failure:
            results.append(_failure(lens, failure, req_low_bit, req_high_bit, mode=mode))
        elif mode == "THEOREM_COVER":
            results.append(theorem_cover_one(lens, api, contract, parent,
                                             max_evals=max_evals_per_lens))
        else:
            results.append(adaptive_cover_one(lens, api, contract, parent, lo=lo, hi=hi,
                                              max_evals=max_evals_per_lens))
    overall = "CERTIFIED_CONDITIONAL" if all(r["status"] == "CERTIFIED_CONDITIONAL" for r in results) else "UNRESOLVED"
    payload = {"schema": SCHEMA, "status": overall, "model_id": MODEL_ID,
               "scan_domain_lo_hex": requested_lo.hex(), "scan_domain_hi_hex": requested_hi.hex(),
               "mathematical_claim_scope": "HISTORICAL_SOURCE_CONNECTED_EXACT_REAL_ONLY",
               "verification_scope": contract.scope,
               "source_sha256": SOURCE_SHA256,
               "requested_lenses": list(lenses),
               "bracketing_package_sha256": contract.bracket_sha256,
               "uniqueness_parent_sha256": contract.uniqueness_sha256,
               "original_compiled_float_signs_certified": False,
               "original_March_offgrid_root_certified": False,
               "physical_provider_admitted": False,
               "empirical_validation": "NOT_ESTABLISHED",
               "canonical_theory_state_changed": False,
               "parent_attestation": parent,
               "lens_results": results}
    return {**payload, "receipt_sha256": digest(payload)}


def validate_receipt(receipt: Mapping[str, Any], *, require_real_source: bool = False) -> None:
    """Structural validation only. For scientific replay, re-run source adapter.

    A self-rehashed adversarial receipt can still forge external interval data;
    never use this validator as a substitute for replaying those engines.
    """
    if not isinstance(receipt, Mapping) or receipt.get("schema") != SCHEMA:
        raise Unresolved("WRONG_SCHEMA")
    payload = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    if not is_sha(receipt.get("receipt_sha256")) or digest(payload) != receipt["receipt_sha256"]:
        raise Unresolved("RECEIPT_HASH_MISMATCH")
    if (receipt.get("model_id") != MODEL_ID or receipt.get("source_sha256") != SOURCE_SHA256 or
        receipt.get("bracketing_package_sha256") != BRACKET_ZIP_SHA256 or
        receipt.get("mathematical_claim_scope") != "HISTORICAL_SOURCE_CONNECTED_EXACT_REAL_ONLY"):
        raise Unresolved("AUTHORITY_IDENTITY_INVALID")
    if any(receipt.get(k) is not False for k in (
            "original_compiled_float_signs_certified", "original_March_offgrid_root_certified",
            "physical_provider_admitted", "canonical_theory_state_changed")):
        raise Unresolved("SCIENTIFIC_PROMOTION_FORBIDDEN")
    if receipt.get("empirical_validation") != "NOT_ESTABLISHED":
        raise Unresolved("EMPIRICAL_PROMOTION_FORBIDDEN")
    if require_real_source and receipt.get("verification_scope") != "SOURCE_REPLAYED_CANDIDATE_MATH":
        raise Unresolved("SYNTHETIC_SCOPE_NOT_SCIENCE")
    try:
        dlo = float.fromhex(receipt["scan_domain_lo_hex"])
        dhi = float.fromhex(receipt["scan_domain_hi_hex"])
        low_bit, high_bit = bit_of(dlo), bit_of(dhi)
        if not bit_of(DOMAIN_LO) <= low_bit <= high_bit <= bit_of(DOMAIN_HI):
            raise Unresolved("SCAN_DOMAIN_NOT_SOURCE_AUTHORIZED")
        if receipt["scan_domain_lo_hex"] != dlo.hex() or receipt["scan_domain_hi_hex"] != dhi.hex():
            raise Unresolved("NONCANONICAL_SCAN_DOMAIN")
    except Exception as exc:
        raise Unresolved("SCAN_DOMAIN_MISSING_OR_INVALID:" + str(exc)) from exc
    lr = receipt.get("lens_results")
    if not isinstance(lr, list) or len(lr) < 1 or len(set(x.get("lens") for x in lr)) != len(lr):
        raise Unresolved("LENS_SET_INVALID")
    if receipt.get("requested_lenses") != [x.get("lens") for x in lr]:
        raise Unresolved("REQUESTED_LENS_COVERAGE_INCOMPLETE")
    parent = receipt.get("parent_attestation")
    if parent is not None:
        if not isinstance(parent, Mapping):
            raise Unresolved("PARENT_ATTESTATION_SHAPE_INVALID")
        for key,expected in (("model_id",MODEL_ID),( "source_sha256",SOURCE_SHA256),
                             ("bracket_sha256",BRACKET_ZIP_SHA256),
                             ("uniqueness_sha256",receipt.get("uniqueness_parent_sha256")),
                             ("scope",receipt.get("verification_scope")),
                             ("theorem_claim","CONTINUOUS_EXACTLY_ONE_REAL_ROOT_ON_FROZEN_DOMAIN"),
                             ("domain_lo_hex",DOMAIN_LO.hex()),("domain_hi_hex",DOMAIN_HI.hex())):
            if parent.get(key) != expected:
                raise Unresolved("PARENT_RECEIPT_LINK_INVALID_"+key)
        if not is_sha(parent.get("replay_receipt_sha256")):
            raise Unresolved("PARENT_REPLAY_RECEIPT_HASH_UNBOUND")
    def check_endpoint_traces(traces, expected_sign):
        if not isinstance(traces,list) or len(traces)!=2:
            raise Unresolved("ENDPOINT_TWO_ENGINE_TRACES_MISSING")
        ids=set()
        for e in traces:
            if not isinstance(e,Mapping) or not isinstance(e.get("engine_id"),str) or e["engine_id"] in ids:
                raise Unresolved("ENDPOINT_ENGINE_IDENTITY_INVALID")
            ids.add(e["engine_id"])
            if not is_sha(e.get("proof_trace_sha256")):
                raise Unresolved("ENDPOINT_TRACE_NOT_BOUND")
            low, high = rational(e.get("lo")),rational(e.get("hi"))
            if low>high or (expected_sign=="POSITIVE" and low<=0) or (expected_sign=="NEGATIVE" and high>=0):
                raise Unresolved("ENDPOINT_INTERVAL_NOT_STRICT_"+expected_sign)
    for row in lr:
        lens = row.get("lens")
        if lens not in BRACKETS_HEX or row.get("status") not in ("CERTIFIED_CONDITIONAL", "UNRESOLVED"):
            raise Unresolved("LENS_OR_STATUS_INVALID")
        segs = row.get("segments")
        if row.get("mode") == "THEOREM_COVER":
            if (low_bit, high_bit) != (bit_of(DOMAIN_LO), bit_of(DOMAIN_HI)):
                raise Unresolved("THEOREM_COVER_REQUIRES_FULL_FROZEN_DOMAIN")
            verify_partition(segs, low_bit, high_bit)
            if row["status"] == "CERTIFIED_CONDITIONAL":
                if len(segs) != 2 or [s["classification"] for s in segs] != ["POSITIVE", "NEGATIVE"]:
                    raise Unresolved("THEOREM_SIGN_TOPOLOGY_INVALID")
                if segs[0]["hi_hex"] != float.fromhex(BRACKETS_HEX[lens][0]).hex():
                    raise Unresolved("BRACKET_LEFT_MISMATCH")
                if segs[1]["lo_hex"] != float.fromhex(BRACKETS_HEX[lens][1]).hex():
                    raise Unresolved("BRACKET_RIGHT_MISMATCH")
                if not isinstance(row.get("root_bracket"), Mapping):
                    raise Unresolved("ROOT_PROOF_MISSING")
                if row["root_bracket"].get("last_positive") != segs[0]["hi_hex"] or row["root_bracket"].get("first_negative") != segs[1]["lo_hex"]:
                    raise Unresolved("ROOT_BRACKET_NOT_BOUND_TO_COVERAGE")
                if row["root_bracket"].get("adjacent_binary64") is not True or row["root_bracket"].get("no_float_between") is not True or row["root_bracket"].get("root_is_floating_zero") is not False:
                    raise Unresolved("ROOT_CLAIM_SCOPE_INCORRECT")
                if parent is None:
                    raise Unresolved("THEOREM_COVER_WITHOUT_PARENT")
                for seg in segs:
                    links=seg.get("proof_links")
                    if (seg.get("method") != "GLOBAL_UNIQUENESS_CONTINUITY_AND_ENDPOINT_SIGN" or
                        not isinstance(links,Mapping) or
                        links.get("global_uniqueness_sha256") != receipt.get("uniqueness_parent_sha256") or
                        links.get("root_bracketing_sha256") != BRACKET_ZIP_SHA256 or
                        links.get("parent_replay_sha256") != parent["replay_receipt_sha256"]):
                        raise Unresolved("THEOREM_COVER_PARENT_PROOF_LINK_INVALID")
                    check_endpoint_traces(links.get("left_endpoint_two_engine_traces"),"POSITIVE")
                    check_endpoint_traces(links.get("right_endpoint_two_engine_traces"),"NEGATIVE")
            elif len(segs) != 1 or segs[0]["classification"] != "UNRESOLVED":
                raise Unresolved("FAIL_CLOSED_SEGMENT_INVALID")
        elif row.get("mode") == "ADAPTIVE_COVER":
            if not isinstance(segs, list) or not segs:
                raise Unresolved("NO_ADAPTIVE_COVERAGE")
            verify_partition(segs, low_bit, high_bit)
            for seg in segs:
                if seg["classification"] != "UNRESOLVED":
                    if parent is None or seg.get("method")!="DIRECT_TWO_ENGINE_ENCLOSURE":
                        raise Unresolved("ADAPTIVE_SOURCE_OR_METHOD_MISSING")
                    links=seg.get("proof_links",{})
                    if links.get("source_sha256") != SOURCE_SHA256 or links.get("parent_replay_sha256") != parent["replay_receipt_sha256"]:
                        raise Unresolved("ADAPTIVE_SOURCE_LINK_INVALID")
                    check_endpoint_traces(links.get("two_engine_traces"),seg["classification"])
            unresolved = any(s["classification"] == "UNRESOLVED" for s in segs)
            if unresolved != (row["status"] == "UNRESOLVED"):
                raise Unresolved("UNRESOLVED_PROPAGATION_INVALID")
        else:
            raise Unresolved("MODE_INVALID")
    if receipt.get("status") != ("CERTIFIED_CONDITIONAL" if all(r["status"] == "CERTIFIED_CONDITIONAL" for r in lr) else "UNRESOLVED"):
        raise Unresolved("AGGREGATE_STATUS_INVALID")
    if receipt["status"] == "CERTIFIED_CONDITIONAL" and receipt.get("parent_attestation") is None:
        raise Unresolved("CERTIFIED_WITHOUT_PARENT_ATTESTATION")


def verify_source_replay(receipt: Mapping[str, Any], api: StrictSignAPI,
                         contract: SourceContract, *, mode: str = "THEOREM_COVER",
                         max_evals_per_lens: int = 128) -> None:
    """Recompute both-engine point guards via adapter then exact-byte compare.

    The exact authorized scan domain is frozen in the receipt for replay.
    """
    validate_receipt(receipt, require_real_source=True)
    if receipt["status"] != "CERTIFIED_CONDITIONAL":
        raise Unresolved("SOURCE_REPLAY_CANNOT_PROMOTE_AN_UNRESOLVED_RECEIPT")
    if receipt.get("verification_scope") != contract.scope:
        raise Unresolved("CONTRACT_SCOPE_MISMATCH")
    lenses = tuple(x["lens"] for x in receipt["lens_results"])
    fresh = scan(api, contract, mode=mode, lenses=lenses,
                 max_evals_per_lens=max_evals_per_lens,
                 lo=float.fromhex(receipt["scan_domain_lo_hex"]),
                 hi=float.fromhex(receipt["scan_domain_hi_hex"]))
    if canonical_json(fresh) != canonical_json(receipt):
        raise Unresolved("SOURCE_REPLAY_RECEIPT_BYTES_MISMATCH")


class SyntheticOracle:
    """EXPLICITLY NON-SCIENTIFIC toy sign API: h_i(R)=midpoint(root floats)−R.

    It deliberately mimics output shape only; both engines share a trivial
    arithmetic formula. It is NOT a new independent Bessel proof engine.
    """
    def __init__(self, *, unavailable: bool = False, malformed: bool = False):
        self.unavailable = unavailable
        self.malformed = malformed

    def replay_parents(self, contract: SourceContract) -> dict:
        if self.unavailable:
            raise Unresolved("SYNTHETIC_PARENT_MISSING")
        return {"model_id": contract.model_id, "source_sha256": contract.source_sha256,
                "bracket_sha256": contract.bracket_sha256,
                "uniqueness_sha256": contract.uniqueness_sha256,
                "scope": "SYNTHETIC_TEST_ONLY", "verification_result": "PASS_SYNTHETIC_REPLAY",
                "theorem_claim": "CONTINUOUS_EXACTLY_ONE_REAL_ROOT_ON_FROZEN_DOMAIN",
                "domain_lo_hex": DOMAIN_LO.hex(), "domain_hi_hex": DOMAIN_HI.hex(),
                "verifier_sha256": "a"*64, "replay_receipt_sha256": "b"*64}

    @staticmethod
    def root(lens: str) -> Fraction:
        a,b = BRACKETS_HEX[lens]
        return (Fraction.from_float(float.fromhex(a))+Fraction.from_float(float.fromhex(b)))/2

    def _make(self, lens: str, lo_hex: str, hi_hex: str, kind: str) -> dict:
        low, high = Fraction.from_float(float.fromhex(lo_hex)), Fraction.from_float(float.fromhex(hi_hex))
        root = self.root(lens)
        lower, upper = root-high, root-low
        f = lambda a: f"{a.numerator}/{a.denominator}"
        result = {"schema": "HIST001D_TWO_ENGINE_SIGN_GUARD_V1",
                  "kind": kind, "model_id": MODEL_ID, "source_sha256": SOURCE_SHA256,
                  "lens": lens, "lo_hex": lo_hex, "hi_hex": hi_hex,
                  "status": "CERTIFIED" if lower > 0 or upper < 0 else "UNRESOLVED",
                  "engines": [{"engine_id": "SYNTHETIC_A", "lo": f(lower), "hi": f(upper),
                               "proof_trace_sha256": "c"*64},
                              {"engine_id": "SYNTHETIC_B", "lo": f(lower), "hi": f(upper),
                               "proof_trace_sha256": "d"*64}]}
        if self.malformed:
            result["model_id"] = "FORGED_MODEL"
        return result

    def point_guard(self, lens: str, x_hex: str) -> dict:
        return self._make(lens, x_hex, x_hex, "POINT")

    def range_guard(self, lens: str, lo_hex: str, hi_hex: str) -> dict:
        return self._make(lens, lo_hex, hi_hex, "RANGE_ALL_REAL")
