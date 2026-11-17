#!/usr/bin/env python3
"""G4b.1c archived finite-proxy evidence replay gate (candidate only).

This independent release-equipment wrapper authenticates four immutable external
mathematical proof kits and runs their *existing* source-specific checkers. It
is NOT an H(R) root-count theorem, original March numerical provider,
physical Weyl solution, current Native ESET theory equivalence, or validation.

The original source archive / 69,120 nodes stay EXTERNAL. Never vendor them in
this public research repository. All executed scripts must be exact hash-pinned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import zipfile

MODEL = "D2D_STYLE_11520_NODAL_WITH_CONTINUUM_BARYONS_NOT_ORIGINAL_MARCH_180X120"
SOURCE_LOCK_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
MAX_ZIP_BYTES = 5_000_000
MAX_MEMBER_BYTES = 6_000_000
MAX_EXPANDED_BYTES = 20_000_000
KITS = {
    "adapter": {
        "sha256": "11830c0729f3fe805b038e449c4c579d90ec3cb44f40cb76877c4e68cef1995b",
        "entry": "reproduce_source_locked_adapter_v1.py",
        "expected_result": "\"six_source_bound_G4b1b_input_inventories\": 6",
        "max_seconds": 120,
    },
    "existence": {
        "sha256": "a73f2d46934747f58e81fbb4bbe53ec627737246cf9843e89ed54c7ecb350580",
        "entry": "reproduce_g4b1c_narrow_0p10kpc_v1.py",
        "expected_result": "CLEAN_SOURCE_PINNED_EXACT_RATIONAL_SIX_NARROW_BRACKETS_PASS",
        "max_seconds": 205,
    },
    "prepeak": {
        "sha256": "cdcca9b8628c16e66dba2fd6eaaeec233ad01366240be1fdcd3cabed65129a9a",
        "entry": "reproduce_g4b1c_prepeak_v5.py",
        "expected_result": '"source_nodal_pairs": 69120',
        "max_seconds": 230,
    },
    "surface_slope": {
        "sha256": "b38a903e579f9ebadf7a806db586ab9af3b0c84a4ad00a2e6bb504d85d19e779",
        "entry": "reproduce_g4b1c_projected_shadow_slope_v1.py",
        "expected_result": "CLEAN REPLAY PASS g4b1c_projected_shadow_pre_root_band_independent_verifier_v1.py",
        "max_seconds": 230,
    },
}

class EvidenceGateError(ValueError):
    pass


def require(condition: bool, message: str):
    if not condition:
        raise EvidenceGateError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for part in iter(lambda: file.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def assert_zip_safe(path: Path):
    require(path.is_file() and not path.is_symlink(), "missing or linked source kit")
    require(path.stat().st_size <= MAX_ZIP_BYTES, "source kit exceeds bounded size")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        require(0 < len(entries) <= 64, "unexpected source kit member count")
        require(sum(x.file_size for x in entries) <= MAX_EXPANDED_BYTES,
                "source kit expanded size exceeds bound")
        names = [x.filename for x in entries]
        require(len(set(names)) == len(names), "duplicated source kit member")
        for entry in entries:
            name = PurePosixPath(entry.filename)
            require(not name.is_absolute() and all(part not in ("", ".", "..") for part in name.parts)
                    and "\\" not in entry.filename and not stat.S_ISLNK(entry.external_attr >> 16)
                    and not entry.is_dir() and entry.file_size <= MAX_MEMBER_BYTES,
                    "unsafe source kit path, link, or size")
        require(archive.testzip() is None, "source kit CRC failure")


def replay_one(kind: str, kit: Path) -> dict:
    require(kind in KITS, "unknown evidence kind")
    spec = KITS[kind]
    require(sha256(kit) == spec["sha256"], "external immutable kit SHA mismatch: " + kind)
    assert_zip_safe(kit)
    with tempfile.TemporaryDirectory(prefix="eset-g4b1c-" + kind + "-") as tmp:
        temp = Path(tmp)
        with zipfile.ZipFile(kit) as archive:
            archive.extractall(temp)
        entry = temp / spec["entry"]
        require(entry.is_file() and not entry.is_symlink(), "missing replay entry point")
        command = [sys.executable, str(entry)]
        if kind == "surface_slope":
            command.append(str(temp))
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        run = subprocess.run(command, cwd=temp, env=env, capture_output=True, text=True,
                             timeout=spec["max_seconds"], check=False)
        require(run.returncode == 0, "pinned evidence replay failed: " + kind + ": " + run.stderr[-500:])
        require(spec["expected_result"] in run.stdout,
                "evidence replay successful exit without required scoped witness: " + kind)
        return {"kind": kind, "kit_sha256": spec["sha256"],
                "source_kit_original_46plus3_sha256": SOURCE_LOCK_SHA256,
                "entrypoint": spec["entry"], "replay_exit": run.returncode,
                "transcript_sha256": hashlib.sha256(run.stdout.encode()).hexdigest(),
                "scope": "LOCAL_CONDITIONAL_FINITE_MATHEMATICAL_PROXY_ONLY"}


def run_all(paths: dict[str, Path]) -> dict:
    require(set(paths) == set(KITS), "all four independent kits required")
    results = [replay_one(name, paths[name]) for name in KITS]
    return {
        "schema": "HIST001D_G4B1C_EXTERNAL_KIT_REPLAY_GATE_V1",
        "status": "PASS_SCOPED_ARCHIVE_REPLAY_ONLY",
        "source_model": MODEL,
        "source_lock_sha256": SOURCE_LOCK_SHA256,
        "four_kits_authenticated_and_replayed": True,
        "results": results,
        "six_source_lenses": 6,
        "source_nodal_pairs": 69120,
        "existence_bracket_width_kpc": "1/10",
        "finite_proxy_root_existence_only": True,
        "full_root_count_or_uniqueness_certified": False,
        "tangencies_excluded": False,
        "original_march_180x120_numeric_all_R_root_theorem": False,
        "original_source_nodal_density_continuum_error_certified": False,
        "physical_same_source_weyl_lensing_derived": False,
        "native_v172_equivalence_proved": False,
        "physical_provider_admitted": False,
        "empirical_validation": "NOT_ESTABLISHED",
        "canonical_theory_state_mutated": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for kind in KITS:
        parser.add_argument("--" + kind.replace("_", "-"), type=Path)
    parser.add_argument("--only", choices=tuple(KITS), help="Bounded per-kit replay (one process per scientific kit)")
    parser.add_argument("--aggregate", type=Path, nargs=4,
                        help="Merge four independently emitted source-replay receipts; does not reexecute")
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args(argv)
    try:
        source_paths = {kind: getattr(arguments,kind) for kind in KITS}
        if arguments.aggregate is not None:
            require(arguments.only is None and not any(source_paths.values()),
                    "aggregate mode cannot silently mix in unexecuted source kits")
            fragments = []
            for path in arguments.aggregate:
                require(path.is_file() and not path.is_symlink(), "missing per-kit replay receipt")
                item = json.loads(path.read_bytes())
                require(set(item) == {"schema", "status", "result"} and
                        item["schema"] == "HIST001D_G4B1C_REPLAY_ONE_KIT_V1" and
                        item["status"] == "PASS_SCOPED_ONE_KIT_ONLY",
                        "invalid per-kit replay receipt")
                result = item["result"]
                require(type(result) is dict and set(result) == {
                    "kind", "kit_sha256", "source_kit_original_46plus3_sha256",
                    "entrypoint", "replay_exit", "transcript_sha256", "scope"},
                    "unexpected per-kit receipt field or physical claim")
                require(result.get("kind") in KITS and
                        result.get("entrypoint") == KITS[result["kind"]]["entry"] and
                        isinstance(result.get("transcript_sha256"), str) and
                        len(result["transcript_sha256"]) == 64 and
                        all(c in "0123456789abcdef" for c in result["transcript_sha256"]) and
                        result.get("kit_sha256") == KITS[result["kind"]]["sha256"] and
                        result.get("replay_exit") == 0 and
                        result.get("source_kit_original_46plus3_sha256") == SOURCE_LOCK_SHA256 and
                        result.get("scope") == "LOCAL_CONDITIONAL_FINITE_MATHEMATICAL_PROXY_ONLY",
                        "per-kit source replay receipt claim/identity mismatch")
                fragments.append(result)
            require({r["kind"] for r in fragments} == set(KITS),
                    "missing/duplicated independent scientific replay kind")
            obj = {
                "schema": "HIST001D_G4B1C_EXTERNAL_KIT_REPLAY_GATE_V1",
                "status": "PASS_SCOPED_ARCHIVE_REPLAY_ONLY",
                "source_model": MODEL, "source_lock_sha256": SOURCE_LOCK_SHA256,
                "four_kits_authenticated_and_replayed": True,
                "results": sorted(fragments,key=lambda x:list(KITS).index(x["kind"])),
                "six_source_lenses": 6,"source_nodal_pairs": 69120,
                "existence_bracket_width_kpc": "1/10",
                "finite_proxy_root_existence_only": True,
                "full_root_count_or_uniqueness_certified": False,"tangencies_excluded": False,
                "original_march_180x120_numeric_all_R_root_theorem": False,
                "original_source_nodal_density_continuum_error_certified": False,
                "physical_same_source_weyl_lensing_derived": False,
                "native_v172_equivalence_proved": False,
                "physical_provider_admitted": False,"empirical_validation": "NOT_ESTABLISHED",
                "canonical_theory_state_mutated": False,
            }
        elif arguments.only is not None:
            kind = arguments.only
            require(source_paths[kind] is not None and
                    all(v is None for k,v in source_paths.items() if k != kind),
                    "one and only one source kit path required in per-kit replay mode")
            obj = {"schema": "HIST001D_G4B1C_REPLAY_ONE_KIT_V1",
                   "status": "PASS_SCOPED_ONE_KIT_ONLY",
                   "result": replay_one(kind, source_paths[kind])}
        else:
            require(all(source_paths.values()), "all four scientific kit paths required")
            obj = run_all(source_paths)
        raw = (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
        if arguments.out:
            require(not arguments.out.exists() and not arguments.out.is_symlink(), "output exists or is linked")
            arguments.out.write_bytes(raw)
        print(raw.decode(), end="")
        return 0
    except (OSError, EvidenceGateError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status":"FAIL_CLOSED","error":str(exc)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
