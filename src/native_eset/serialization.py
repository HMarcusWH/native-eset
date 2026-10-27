"""Bounded, unambiguous JSON and path contracts for untrusted input files."""
from __future__ import annotations
import json
import math
import re
from pathlib import Path
from typing import Any

_SHA = re.compile(r"[0-9a-f]{64}\Z")


def require_sha256(value: object, label: str = "SHA-256") -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ValueError(f"{label} must be 64 lowercase hexadecimal characters")
    return value


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {token}")


def _finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("JSON float exceeds the finite binary64 domain")
    return value


def strict_loads(data: str | bytes) -> Any:
    if isinstance(data, bytes):
        data = data.decode("utf-8-sig")
    return json.loads(data, object_pairs_hook=_unique_pairs, parse_constant=_invalid_constant, parse_float=_finite_float)


def read_json(path: Path, max_bytes: int = 8_000_000) -> Any:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"JSON input must be a regular non-symlink file: {path.name}")
    if path.stat().st_size > max_bytes:
        raise ValueError(f"JSON input exceeds its resource budget: {path.name}")
    data = path.read_bytes()
    if len(data) > max_bytes:
        raise ValueError("JSON input grew beyond its resource budget")
    return strict_loads(data)


def require_relative_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("invalid relative artifact path")
    parts = value.split("/")
    if any(p in {"", ".", ".."} or ":" in p for p in parts):
        raise ValueError("unsafe relative artifact path")
    return value


def resolve_regular_file(root: Path, relative: str) -> Path:
    require_relative_path(relative)
    base = root.resolve()
    p = base
    for part in relative.split("/"):
        p = p / part
        if p.is_symlink():
            raise ValueError("symlink artifact paths are forbidden")
    if not p.is_file() or not p.resolve().is_relative_to(base):
        raise ValueError(f"missing or escaping artifact path: {relative}")
    return p
