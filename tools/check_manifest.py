#!/usr/bin/env python3
"""Exact checkout byte inventory. This manifest is an integrity list, not a signature."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

IGNORED_DIRS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", ".venv", "build", "dist", "runs", ".cache"}
IGNORED_SUFFIX = {".pyc", ".pyo", ".swp"}


def candidates(root: Path) -> dict[str, str]:
    rows = {}
    for directory, dirs, files in os.walk(root):
        base = Path(directory)
        for name in list(dirs):
            p = base / name
            if p.is_symlink():
                raise ValueError(f"symlink directory in release source: {p.relative_to(root)}")
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not d.endswith(".egg-info"))
        for name in sorted(files):
            p = base / name
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                raise ValueError(f"symlink file in release source: {rel}")
            if p.suffix in IGNORED_SUFFIX or rel == "MANIFEST_SHA256.json" or name == ".DS_Store":
                continue
            rows[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return dict(sorted(rows.items()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--git-index", action="store_true", help="also verify staged blob bytes, not only checkout bytes")
    args = parser.parse_args()
    path = args.root / "MANIFEST_SHA256.json"
    try:
        live = candidates(args.root)
        if args.write:
            path.write_bytes((json.dumps({"manifest_version": 1, "files": live}, sort_keys=True, indent=2) + "\n").encode("utf-8"))
            print("MANIFEST_WRITE", len(live))
            return 0
        expected = json.loads(path.read_text(encoding="utf-8"))
        if expected.get("manifest_version") != 1 or expected.get("files") != live:
            old = expected.get("files", {})
            print("MANIFEST_FAIL", "missing", sorted(set(old)-set(live)),
                  "unexpected", sorted(set(live)-set(old)),
                  "changed", sorted(k for k in set(live) & set(old) if live[k] != old[k]))
            return 1
        if args.git_index:
            staged = {}
            result = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=args.root,
                                    capture_output=True, check=True)
            for entry in result.stdout.split(b"\0"):
                if not entry:
                    continue
                meta, name = entry.split(b"\t", 1)
                file_mode, sha, stage = meta.split()
                if file_mode not in {b"100644", b"100755"} or stage != b"0":
                    raise ValueError("symlink/submodule/unmerged index entry")
                raw = subprocess.run(["git", "cat-file", "blob", sha.decode("ascii")], cwd=args.root,
                                     capture_output=True, check=True).stdout
                staged[name.decode("utf-8")] = hashlib.sha256(raw).hexdigest()
            required = {**live, "MANIFEST_SHA256.json": hashlib.sha256(path.read_bytes()).hexdigest()}
            if staged != required:
                raise ValueError("Git-index inventory/bytes differ from the audited source manifest")
            print("GIT_INDEX_MANIFEST_PASS", len(staged))
        print("MANIFEST_PASS", len(live))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print("MANIFEST_ERROR", str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
