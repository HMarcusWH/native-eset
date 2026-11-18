"""Read-only, source-bound independent 1,400-panel mathematical audit.

The existing global-root proof engine (not new physics) recomputes every
sealed one-sided knot-safe exclusion leaf plus root interval derivative checks.
The full global *producer* is intentionally NOT rerun here.  Strictly
nonpromoting, no physical provider or compiled-float claims.

Requires an exact-hash release archive, its three exact-hash source parents,
and a clean extracted copy of the global proof engine outside this package.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import traceback
import zipfile

GLOBAL_SHA = "ee677eea7f2f7bcf5c90347f5c54658988090340d888870c7e60071263693fff"
SOURCE_SHA = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
EXPECTED = {
    "J0822+1828": 236,
    "J0915+4211": 231,
    "J0930+2855": 301,
    "J1021+2028": 204,
    "J1111+2234": 207,
    "J1135+3720": 221,
}
PROOF_FILES = (
    "source_model.py", "source_bind.py", "math_bounds.py", "fast_exp.py",
    "knot_offgrid_math.py", "independent_checker.py", "verify_release.py",
    "claim_guard.py",
)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                       allow_nan=False) + "\n").encode("ascii")


def run(engine_dir: Path, parent_dir: Path, archive: Path) -> dict:
    if sha(archive.read_bytes()) != GLOBAL_SHA:
        raise ValueError("GLOBAL_THEOREM_ARCHIVE_NOT_PINNED")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None or len(z.namelist()) != len(set(z.namelist())):
            raise ValueError("GLOBAL_THEOREM_ARCHIVE_CORRUPT")
        manifest=json.loads(z.read("MANIFEST_SHA256.json"))
        for n,item in manifest["files"].items():
            data=z.read(n)
            if sha(data)!=item["sha256"] or len(data)!=item["size_bytes"]:
                raise ValueError("GLOBAL_MANIFEST_MEMBER_HASH_MISMATCH")
        for n in PROOF_FILES:
            p=engine_dir/n
            if p.is_symlink() or not p.is_file() or p.read_bytes()!=z.read(n):
                raise ValueError("GLOBAL_PROOF_ENGINE_SOURCE_NOT_PINNED_"+n)
        meta=json.loads(z.read("RELEASE_METADATA.json"))
        if (meta.get("source_46plus3_sha256")!=SOURCE_SHA or meta.get("physical_provider_admitted") is not False
            or meta.get("scientific_authority_promoted") is not False):
            raise ValueError("GLOBAL_THEOREM_SCOPE_NOT_PINNED")
    if str(engine_dir) not in sys.path: sys.path.insert(0,str(engine_dir))
    # Run from a dedicated process, NOT from within the imported bracketer:
    # the proof engine modules share names but have different pinned sources.
    source=importlib.import_module("source_model")
    bound=importlib.import_module("source_bind")
    independent=importlib.import_module("independent_checker")
    cases=bound.capture(parent_dir)
    if tuple(c["lens"] for c in cases)!=tuple(EXPECTED):
        raise ValueError("GLOBAL_THEOREM_SOURCE_ROSTER_CHANGED")
    aggregate=json.loads((engine_dir/"results/RESULTS_AGGREGATE.json").read_bytes())
    if aggregate.get("total_strict_sign_exclusion_leaves") != 1400:
        raise ValueError("GLOBAL_THEOREM_AGGREGATE_CHANGED")
    results=[]
    for c in cases:
        row=independent.verify(c,engine_dir/"results")
        lens=c["lens"]
        frozen=(engine_dir/"results"/(lens.replace('+','p')+'_independent.json')).read_bytes()
        if source.canonical(row)!=frozen:
            raise ValueError("INDEPENDENT_PANEL_REPLAY_NOT_BYTE_IDENTICAL_"+lens)
        if row.get("independent_exclusion_panels_pass")!=EXPECTED[lens] or row.get("root_left_sign_pass") is not True or row.get("root_right_sign_pass") is not True:
            raise ValueError("INDEPENDENT_PANEL_COUNT_OR_SIGN_MISMATCH")
        results.append({"lens":lens,"exclusion_panels_recomputed":EXPECTED[lens],
                        "source_node_sha256":c["node_sha256"],
                        "independent_receipt_sha256":sha(frozen)})
    if sum(x["exclusion_panels_recomputed"] for x in results)!=1400:
        raise ValueError("INDEPENDENT_PANEL_COVERAGE_COUNT")
    return {"schema":"HIST001D_GLOBAL_THEOREM_INDEPENDENT_PANEL_REEXECUTION_V1",
            "status":"PASS_SOURCE_BOUND_INDEPENDENT_1400_PANEL_REPLAY",
            "source_sha256":SOURCE_SHA,"global_parent_zip_sha256":GLOBAL_SHA,
            "independent_exclusion_panels_recomputed":1400,
            "six_knot_safe_root_derivative_checks_recomputed":6,
            "results":results,
            "global_uniqueness_parent_full_producer_replayed":False,
            "mathematical_theorem_external_peer_reviewed":False,
            "physical_provider_admitted":False,
            "empirical_validation":"NOT_ESTABLISHED",
            "scientific_authority_promoted":False}


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--engine-dir",type=Path,required=True)
    p.add_argument("--parent-dir",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        result=run(args.engine_dir.resolve(strict=True),args.parent_dir.resolve(strict=True),args.archive.resolve(strict=True))
        code=0
    except Exception as e:
        result={"schema":"HIST001D_GLOBAL_THEOREM_INDEPENDENT_PANEL_REEXECUTION_V1",
                "status":"UNRESOLVED", "reason":type(e).__name__+":"+str(e)[:200],
                "global_uniqueness_parent_full_producer_replayed":False,
                "physical_provider_admitted":False,"scientific_authority_promoted":False}
        code=2
    result["receipt_sha256"]=sha(canonical(result))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(canonical(result))
    print(result["status"],"sha256=",sha(args.out.read_bytes()),flush=True)
    return code

if __name__=="__main__":sys.exit(main())
