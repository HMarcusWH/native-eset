"""Fail-closed, offline staging from externally acquired file bytes.

No Drive credentials in this source tree; user fetches authorized files separately.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
from native_eset.graph.snapshot import GraphIntegrityError, validate_lock
from native_eset.serialization import read_json


def prepare_verified_snapshot(source_dir: Path, lock_file: Path, destination: Path) -> dict:
    lock=validate_lock(read_json(lock_file))
    if lock.get("schema") != "NATIVE_ESET_THEORY_STATE_GRAPH_LOCK_V1":
        raise GraphIntegrityError("unsupported graph lock")
    expected={r["name"]:r["sha256"] for r in lock["files"]}
    if len(expected)!=lock["file_count"]:
        raise GraphIntegrityError("duplicate lock names")
    if {p.name for p in source_dir.iterdir()} != set(expected):
        raise GraphIntegrityError("missing or extra graph files")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("destination exists; cannot overwrite previously verified graph")
    destination.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix=".eset_verified_pending_",dir=destination.parent))
    try:
        for name,digest in sorted(expected.items()):
            src=source_dir/name
            if src.is_symlink() or not src.is_file() or name.startswith(".") or "/" in name or "\\" in name:
                raise GraphIntegrityError(f"invalid source partition {name}")
            dest=staging/name
            h=hashlib.sha256()
            with src.open("rb") as inp,dest.open("xb") as out:
                for block in iter(lambda:inp.read(1024*1024),b""):
                    h.update(block);out.write(block)
            if h.hexdigest()!=digest:
                raise GraphIntegrityError(f"source file integrity failure: {name}")
        # Cooperative exclusive reservation prevents two importers overwriting each other.
        guard = destination.with_name(destination.name + ".import-lock")
        owned = False
        try:
            with guard.open("xb"):
                owned = True
                if destination.exists() or destination.is_symlink():
                    raise FileExistsError("destination appeared during verified staging")
                os.rename(staging, destination)
        finally:
            if owned:
                guard.unlink()
        return {"status":"PASS_BYTE_CHECK_ONLY","destination":str(destination),
                "files":len(expected),"graph_expected_sha256":lock["graph_sha256"],
                "next":"Use GraphSnapshot.load to verify canonical normalized digest and endpoints"}
    finally:
        if staging.exists():shutil.rmtree(staging)
