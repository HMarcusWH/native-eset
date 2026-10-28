"""HIST-001A/1: offline inspection of a separately supplied original source pack.

This is a byte/inventory preflight, not a scientific admission, execution or
sandbox. It never imports or runs original solver code.
"""
from __future__ import annotations

import csv
import hashlib
import os
from pathlib import Path
from typing import Any

from native_eset.historical.hist001_approved import (
    SOURCE_LOCK_DIGEST, HistoricalSourceIntegrityError, approved_hist001,
)
from native_eset.serialization import read_json, require_relative_path, resolve_regular_file

MAX_SOURCE_BYTES = 2_000_000
MAX_TOTAL_BYTES = 10_000_000
EXPECTED_ROOT_ENTRIES = frozenset({"SOURCE_LOCK.json", "swells_pack_v2", "archived_rangefinder"})


def _file_hash(root: Path, name: str) -> str:
    """Require regular contained paths before hashing bounded bytes."""
    target = resolve_regular_file(root, require_relative_path(name))
    if target.stat().st_size > MAX_SOURCE_BYTES:
        raise HistoricalSourceIntegrityError("HIST-001 source file exceeds approved budget")
    return hashlib.sha256(target.read_bytes()).hexdigest()


def _regular_file_inventory(root: Path) -> tuple[set[str], int]:
    inventory: set[str] = set()
    size = 0
    for current, dirs, files in os.walk(root, followlinks=False):
        location = Path(current)
        if location.is_symlink():
            raise HistoricalSourceIntegrityError("symlink source directory forbidden")
        for d in dirs:
            if (location / d).is_symlink():
                raise HistoricalSourceIntegrityError("symlink inside historical source forbidden")
        for filename in files:
            path = location / filename
            if path.is_symlink() or not path.is_file():
                raise HistoricalSourceIntegrityError("nonregular historical source file forbidden")
            rel = path.relative_to(root).as_posix()
            require_relative_path(rel)
            inventory.add(rel)
            size += path.stat().st_size
            if len(inventory) > 100 or size > MAX_TOTAL_BYTES:
                raise HistoricalSourceIntegrityError("historical source inventory budget exceeded")
    return inventory, size


def verify_hist001_source(source_root: str | Path) -> dict[str, Any]:
    """Verify original code, fitted input tables, archived negatives and frozen identity.

    The source root is an explicit path, deliberately excluded from the RunSpec
    content hash to keep that identity portable across an installed wheel.
    """
    anchor = approved_hist001()
    root = Path(source_root).absolute()
    if root.is_symlink() or not root.is_dir():
        raise HistoricalSourceIntegrityError("HIST-001 requires an actual non-symlink source directory")
    if {p.name for p in root.iterdir()} != EXPECTED_ROOT_ENTRIES:
        raise HistoricalSourceIntegrityError("HIST-001 source root has missing or extra entries")
    try:
        original = resolve_regular_file(root, "SOURCE_LOCK.json")
        if hashlib.sha256(original.read_bytes()).hexdigest() != SOURCE_LOCK_DIGEST:
            raise HistoricalSourceIntegrityError("original SOURCE_LOCK.json bytes do not match package trust anchor")
        lock = read_json(original, max_bytes=20_000)
        if not isinstance(lock, dict) or not isinstance(lock.get("source_filenames_sha256"), dict):
            raise HistoricalSourceIntegrityError("unrecognized historical source-lock structure")
        files: dict[str, str] = lock["source_filenames_sha256"]
        negative: dict[str, Any] = lock["archived_negative_controls"]
        if len(files) != anchor["source_file_count"] or len(negative) != anchor["negative_record_count"]:
            raise HistoricalSourceIntegrityError("changed historical source or archived-negative inventory")
        expected = {"SOURCE_LOCK.json"}
        for name, digest in files.items():
            rel = "swells_pack_v2/" + require_relative_path(name)
            if _file_hash(root, rel) != digest:
                raise HistoricalSourceIntegrityError("historical original source mismatch: " + name)
            expected.add(rel)
        for name, entry in negative.items():
            rel = "archived_rangefinder/" + require_relative_path(name)
            if _file_hash(root, rel) != entry["sha256"]:
                raise HistoricalSourceIntegrityError("historical negative evidence mismatch: " + name)
            expected.add(rel)
        actual, total_bytes = _regular_file_inventory(root)
        if actual != expected:
            raise HistoricalSourceIntegrityError("historical original source has missing/extra file(s)")
        source_archive = lock["source_archive"]
        pins = {
            "id": ("finite_model_id",), "model_identity": ("theory_id",),
            "original_branch": ("original_branch",), "frozen_candidate": ("frozen_candidate",),
            "frozen_config": ("config_path",),
        }
        for key, (trusted_key,) in pins.items():
            if lock.get(key) != anchor[trusted_key]:
                raise HistoricalSourceIntegrityError("historical model identity mismatch: " + key)
        if (source_archive.get("sha256") != anchor["original_archive_sha256"] or
                source_archive.get("size_bytes") != anchor["original_archive_size_bytes"] or
                lock.get("physical_provider_admitted") is not False or
                lock.get("current_TheoryState_mutation") is not False or
                lock.get("data_role") != "REGRESSION_OR_ORIGINAL_CALIBRATION_NOT_HELD_OUT"):
            raise HistoricalSourceIntegrityError("historical source provenance or nonpromotion contract mismatch")
        for label, name in (("config_sha256", anchor["config_path"]),
                            ("baseline_sha256", anchor["baseline_path"]),
                            ("lens_table_sha256", anchor["lens_table_path"])):
            if files.get(name) != anchor[label]:
                raise HistoricalSourceIntegrityError("historical source fixture identity mismatch: " + name)
        baseline = read_json(resolve_regular_file(root / "swells_pack_v2", anchor["baseline_path"]),
                             max_bytes=50_000)
        config = read_json(resolve_regular_file(root / "swells_pack_v2", anchor["config_path"]),
                           max_bytes=50_000)
        if config.get("branch_id") != anchor["original_branch"] or baseline.get("branch_id") != anchor["original_branch"]:
            raise HistoricalSourceIntegrityError("historical frozen branch mismatch")
        lens = resolve_regular_file(root / "swells_pack_v2", anchor["lens_table_path"])
        with lens.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        lens_ids = [r["lens_id"] for r in rows]
        if lens_ids != anchor["expected_lens_ids"] or len(lens_ids) != len(set(lens_ids)):
            raise HistoricalSourceIntegrityError("historical six-lens membership or ordering mismatch")
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        if isinstance(exc, HistoricalSourceIntegrityError):
            raise
        raise HistoricalSourceIntegrityError("HIST-001 source verification failed: " + str(exc)) from exc
    return {"status": "HIST001_FROZEN_SOURCE_BYTES_VERIFIED_NO_EXECUTION",
            "backend_id": anchor["backend_id"], "finite_model_id": anchor["finite_model_id"],
            "source_lock_sha256": SOURCE_LOCK_DIGEST,
            "original_archive_sha256": anchor["original_archive_sha256"],
            "frozen_files": len(files), "archived_negative_records": len(negative),
            "source_bytes": total_bytes, "lens_ids": lens_ids,
            "data_use": anchor["data_use"], "source_history": anchor["source_history"],
            "capability_executable": False, "physical_provider_admitted": False,
            "current_native_v172_equivalence_proved": False,
            "empirical_validation": "NOT_ESTABLISHED"}
