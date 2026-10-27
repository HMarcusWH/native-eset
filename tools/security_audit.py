#!/usr/bin/env python3
"""Bounded filename and high-confidence secret-pattern preflight; not a full scanner.

Default input is the Git INDEX (not just the working files). A release without Git
may explicitly use its SHA-verified manifest. No absent-Git green fallback exists.
Only paths/reason codes are emitted; never print a matched secret value.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

BAD_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".sqlite", ".db", ".fits", ".fit", ".fts", ".ipynb"}
BAD_BASENAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "service_account.json"}
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".sh", ".ps1"}
PATTERNS = {
    "PRIVATE_KEY_HEADER": re.compile(rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "GITHUB_CLASSIC_TOKEN": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
    "GITHUB_FINE_GRAINED_TOKEN": re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{50,255}\b"),
    "GOOGLE_SERVICE_ACCOUNT_KEY": re.compile(rb'"private_key"\s*:\s*"-----BEGIN'),
}
MAX_TEXT_BYTES = 2_000_000


def scan(paths: list[str]) -> list[str]:
    findings = []
    for value in paths:
        p = PurePosixPath(value)
        if (p.suffix.lower() in BAD_SUFFIXES or p.name.lower() in BAD_BASENAMES or
                (p.name.startswith(".env.") and p.name != ".env.example") or
                "runs" in p.parts or ".." in p.parts or p.is_absolute()):
            findings.append(value)
    return sorted(set(findings))


def scan_content(path: str, data: bytes) -> list[dict[str, str]]:
    p = PurePosixPath(path)
    if p.suffix not in TEXT_SUFFIXES and p.name not in {".env.example", ".gitignore", ".gitattributes"}:
        return []
    if len(data) > MAX_TEXT_BYTES:
        return [{"path": path, "reason": "OVERSIZED_TEXT_REQUIRES_REVIEW"}]
    return [{"path": path, "reason": reason} for reason, pattern in PATTERNS.items() if pattern.search(data)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()
    try:
        blobs = {}
        if args.manifest:
            root = args.manifest.resolve().parent
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            for name, expected in manifest["files"].items():
                p = root / name
                if not p.resolve().is_relative_to(root) or p.is_symlink():
                    raise ValueError("unsafe manifest path")
                data = p.read_bytes()
                if hashlib.sha256(data).hexdigest() != expected:
                    raise ValueError(f"manifest source changed: {name}")
                blobs[name] = data
            mode = "SHA_VERIFIED_RELEASE_FILES"
        else:
            result = subprocess.run(["git", "ls-files", "--stage", "-z"], capture_output=True, check=True)
            for item in result.stdout.split(b"\0"):
                if not item:
                    continue
                meta, raw_name = item.split(b"\t", 1)
                file_mode, sha, stage = meta.split()
                name = raw_name.decode("utf-8")
                if file_mode not in {b"100644", b"100755"} or stage != b"0":
                    raise ValueError(f"symlink/submodule/unmerged index entry: {name}")
                blobs[name] = subprocess.run(["git", "cat-file", "blob", sha.decode("ascii")],
                                             capture_output=True, check=True).stdout
            if not blobs:
                raise ValueError("empty Git index is not an audited release")
            mode = "GIT_INDEX_BYTES"
        findings = [{"path": p, "reason": "FORBIDDEN_FILENAME"} for p in scan(list(blobs))]
        for name, data in blobs.items():
            findings.extend(scan_content(name, data))
        print(json.dumps({"status": "FAIL" if findings else "PASS_BOUNDED_PREFLIGHT", "mode": mode,
                          "files_checked": len(blobs), "findings": findings,
                          "scope": "NOT_A_COMPREHENSIVE_SECRET_OR_SECURITY_AUDIT"}, sort_keys=True))
        return 1 if findings else 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "NOT_VERIFIED", "reason": type(exc).__name__, "message": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
