"""Supplemental HIST-001B provenance. Never modify HIST-001A's trusted source lock.

Archived bytes and later support scripts are verifiable; the original accelerated
producer and its 600-case precheck implementation have NOT been recovered.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

HIST001B_MASTER_SHA256 = "8609eb7896114f26f9355553208930bbdba5402d20a8c3454bc80c114f81f9f0"
HIST001B_MARCH_SHA256 = "283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e"
HIST001A_SOURCE_LOCK_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
HISTORICAL_PRODUCER_STATUS = "ORIGINAL_ACCELERATED_PRODUCER_NOT_RECOVERED"
PRECHECK_STATUS = "ORIGINAL_600_PRECHECKS_NOT_REEXECUTED"
ARCHIVE_PREFIX = "reg_v2_fixed_law_geometry_morphology_nuisance_"

# Independently hashed from the SHA-verified June master. Neither these files
# nor a caller-supplied manifest grants permission to claim original execution.
APPROVED_ARCHIVE_SHA256 = {
    "00_execution_ledger.json": "24e6d96bcd838f91da4e943421d594a37d0f90ef4e4fdedbb5ad96e4bb73ce22",
    "fixed_law_geometry_nuisance_survival.py": "329074375fff7f54596f0f690778fa5eae9fc52871a1aaf48a2bc28beef3c8da",
    "fixed_law_geometry_nuisance_survival_parallel.py": "1b7d112db6b60290e983745fb8470f9bddc1ff935ed5088e21635f3d8693980f",
    ARCHIVE_PREFIX + "survival_curve_summary.json": "ade89fedadc03a8bb3f88ef67016fa318d675856f4e041a1e2a134281fcfa182",
    ARCHIVE_PREFIX + "w01pct.csv": "fb3dc88cc12836fc5320cc5ae5966f0223acdc94c5f55b3b1c495661d42338b1",
    ARCHIVE_PREFIX + "w01pct_summary.json": "b7f6ceabe08251e25ac01ea32779c7c96215a373f17e87e185170781a9abdd47",
    ARCHIVE_PREFIX + "w02pct.csv": "cd64034a620c27e2f2c3dc28f5b06bc8b3e34bfbf164f58547405896a3686232",
    ARCHIVE_PREFIX + "w02pct_summary.json": "bb2a01b6eed15f1305ce2fc0045f06886979c42c3c6fd4b866b7d8505f603089",
    ARCHIVE_PREFIX + "w05pct.csv": "3cc5dcd60a305d77be2cc4778291e09c63482197f7fa366e0bd09278076d93e6",
    ARCHIVE_PREFIX + "w05pct_summary.json": "4bd2036226b1bb1ba31b0679f5e0f42f3e363088633677a4a6fee1f05cecaae7",
    ARCHIVE_PREFIX + "w10pct.csv": "c151e5e6e2fb3ebf5a51eb3e60ac299de0079eb66825cc0e796cc2838a844de7",
    ARCHIVE_PREFIX + "w10pct_summary.json": "c2fb8623dd283dcb1aa3431ee89ddb9f75c9df6b3221558d082453d67fb28bae",
}
ARCHIVED_COUNTS = {0.01: (323, 844), 0.02: (140, 631),
                   0.05: (23, 239), 0.10: (3, 69)}


class Hist001BSourceError(ValueError):
    """Supplementary B evidence is absent, modified or unsafe."""


def require_no_symlink_components(path: str | Path) -> Path:
    """Reject symlink roots AND ancestors before any resolve() erases them."""
    p = Path(os.path.abspath(os.fspath(path)))
    for component in (p, *p.parents):
        if component.is_symlink():
            raise Hist001BSourceError("symlink component forbidden: " + str(component))
    return p


def verify_archive_bytes(filename: str | Path, expected_sha256: str,
                         *, max_bytes: int = 40_000_000) -> dict:
    p = require_no_symlink_components(filename)
    if not p.is_file() or p.stat().st_size > max_bytes:
        raise Hist001BSourceError("missing or oversized source archive")
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    if sha != expected_sha256:
        raise Hist001BSourceError("supplemental archive SHA mismatch")
    return {"sha256": sha, "size_bytes": p.stat().st_size, "archive_verified": True}


def verify_b_oracle(oracle_root: str | Path) -> dict:
    """Verify the *flat, separately extracted* approved archived 12-file subset.

    The archive is NOT a scientific oracle for the missing producer's RNG.
    These source digests are embedded independently of any provided manifest.
    """
    root = require_no_symlink_components(oracle_root)
    if not root.is_dir() or not root.is_absolute():
        raise Hist001BSourceError("B oracle must be an existing regular directory")
    actual = {p.name for p in root.iterdir()}
    if actual != set(APPROVED_ARCHIVE_SHA256):
        raise Hist001BSourceError("B oracle missing or unexpected archived members")
    total = 0
    for name, digest in APPROVED_ARCHIVE_SHA256.items():
        target = require_no_symlink_components(root / name)
        if not target.is_file():
            raise Hist001BSourceError("B oracle member is not a regular file: " + name)
        size = target.stat().st_size
        if size > 200_000:
            raise Hist001BSourceError("B oracle source exceeds per-file size budget")
        total += size
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise Hist001BSourceError("B archived byte mismatch: " + name)
    if total > 1_000_000:
        raise Hist001BSourceError("B oracle archive subset exceeds budget")
    return {
        "status": "HIST001B_ARCHIVED_BYTES_VERIFIED_NOT_PRODUCER",
        "archived_file_count": len(APPROVED_ARCHIVE_SHA256),
        "archived_files": dict(APPROVED_ARCHIVE_SHA256),
        "original_accelerated_producer_verified": False,
        "original_600_prechecks_verified": False,
        "original_rng_schedule_verified": False,
        "physical_provider_admitted": False,
    }


def missing_original_producer() -> dict:
    """There is deliberately no override/acceptance-by-self-reported status."""
    return {
        "producer_status": HISTORICAL_PRODUCER_STATUS,
        "precheck_status": PRECHECK_STATUS,
        "rng_status": "ARCHIVED_RNG_DRAW_SCHEDULE_NOT_PROVEN",
        "source_exact_authorized": False,
    }
