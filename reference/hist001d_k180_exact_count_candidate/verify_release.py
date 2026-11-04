#!/usr/bin/env python3
"""Fail-closed SHA, mathematical claims and replay checks for protected EXACT-16.

Everything runs within the unpacked archive. No network, original repository
write, physical provider admission or scientific Theory-State mutation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from knot_count_contract import ORIGINAL_SOURCE_SHA, PARENT_SHA, verify_all

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
SOURCE = ROOT / "reference/hist001d_k180_exact_count_candidate"

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def payload_sha(path: Path) -> str:
    if not path.is_file():
        raise ValueError("missing required file " + str(path))
    return sha(path.read_bytes())

def integrity():
    file = ROOT / "MANIFEST_SHA256.json"
    manifest = json.loads(file.read_text(encoding="utf-8"))
    if manifest.get("schema") != "HIST001D_MSTAR_KNOT_SAFE_EXACT16_PROTECTED_RELEASE_SHA256_V1":
        raise ValueError("manifest schema mismatch")
    if manifest.get("physical_provider_admitted") is not False or manifest.get("empirical_validation") != "NOT_ESTABLISHED":
        raise ValueError("manifest claim promotion")
    entries = manifest["files"]
    declared = set(entries)
    actual = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts
        and ".pytest_cache" not in p.parts and p.name != "MANIFEST_SHA256.json"
    }
    if declared != actual:
        raise ValueError(f"manifest membership mismatch extra={sorted(actual-declared)} missing={sorted(declared-actual)}")
    for rel, expected in entries.items():
        if payload_sha(ROOT / rel) != expected:
            raise ValueError("SHA256 mismatch in " + rel)
    if payload_sha(ROOT / "inputs/zero16_parent_v1r2.zip") != PARENT_SHA:
        raise ValueError("protected parent mismatch")
    if payload_sha(ROOT / "inputs/cancel_parent_v1.zip") != "639ee5973a59a63c14e63d59522c03d659de10dd6d7c195586de13e8186159c9":
        raise ValueError("cancellation parent mismatch")
    print("INTEGRITY_PASS", len(entries), "files", flush=True)
    return manifest

def run(path: str, *args: str):
    subprocess.run([sys.executable, str(SOURCE / path), *args], check=True, cwd=ROOT)

def sealed_result_digests():
    return {p.name: payload_sha(p) for p in RESULTS.glob("*.json")}

def claims():
    def load(prefix):
        return [json.loads((RESULTS / f"{prefix}_{j}.json").read_bytes()) for j in range(6)]
    rows = verify_all(load("inputs_lens"), load("local_lens"),
                      load("exclusion_lens"), load("independent_lens"))
    a = json.loads((RESULTS / "exact_count_aggregate.json").read_bytes())
    if (a.get("total_exact_zeros_on_six_specified_A_bands") != 16
            or a.get("physical_provider_admitted") is not False
            or a.get("empirical_validation") != "NOT_ESTABLISHED"
            or a.get("original_March_Einstein_root_count_certified") is not False
            or a.get("selected_Mstar_full_H_root_count_certified") is not False
            or a.get("scientific_authority_promoted") is not False
            or a.get("source_original_46plus3_sha256") != ORIGINAL_SOURCE_SHA):
        raise ValueError("aggregate claim promotion")
    if [(x["lens"], x["exact_local_mathematical_zero_count"]) for x in rows] != list(a["zero_count_each_lens"].items()):
        raise ValueError("aggregate lens/count mismatch")
    if a.get("coverage") != rows:
        raise ValueError("aggregate coverage mismatch")
    q = json.loads((RESULTS / "adversarial_exact_count.json").read_bytes())
    if q.get("count") != 40 or q.get("all_rejected") is not True or any(x["result"] != "REJECTED" for x in q.get("cases", [])):
        raise ValueError("adversarial record invalid")
    print("CLAIMS_PASS exact16 six bands", sum(x["derivative_panels"] for x in rows), "derivative", sum(x["excluded_panels"] for x in rows), "excluded")

def ensure_unchanged(before):
    after = sealed_result_digests()
    if before != after:
        raise ValueError("source-dependent results differ from original sealed bytes")


def main():
    ap = argparse.ArgumentParser()
    flags = ap.add_mutually_exclusive_group()
    flags.add_argument("--quick", action="store_true")
    flags.add_argument("--independent", action="store_true")
    flags.add_argument("--full", action="store_true")
    args = ap.parse_args()
    integrity()
    claims()
    before = sealed_result_digests()
    if args.independent or args.full:
        for j in range(6):
            run("independent_knot_verify.py", "--lens", str(j))
        run("assemble_exact_count.py")
        run("adversarial_exact_count.py")
        ensure_unchanged(before)
        print("INDEPENDENT_EXACT128_ALL_6_PASS", flush=True)
    if args.full:
        run("prepare_parent.py")
        for j in range(6):
            run("materialize_inputs.py", "--lens", str(j))
            run("certify_local_uniqueness.py", "--lens", str(j))
            run("exclude_gaps.py", "--lens", str(j), "--seconds", "720")
            run("independent_knot_verify.py", "--lens", str(j))
        run("assemble_exact_count.py")
        run("adversarial_exact_count.py")
        ensure_unchanged(before)
        print("FULL_SOURCE_EXACT16_ALL_6_PASS", flush=True)
    integrity()
    claims()
    print("EXACT16_RELEASE_PASS", flush=True)

if __name__ == "__main__":
    main()
