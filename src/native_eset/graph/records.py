"""Immutable source wrappers. Raw JSON properties return defensive deep copies."""
from __future__ import annotations
from dataclasses import dataclass
import json
import builtins
from typing import Any, Mapping


def _encode(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


@dataclass(frozen=True, init=False)
class Node:
    id: str
    type: str
    name: str
    _raw_json: bytes
    snapshot_sha256: str

    def __init__(self, id: str, type: str, name: str, raw: Mapping[str, Any], snapshot_sha256: str):
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "type", type)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "_raw_json", _encode(dict(raw)))
        object.__setattr__(self, "snapshot_sha256", snapshot_sha256)

    @property
    def raw(self) -> dict[str, Any]:
        return json.loads(self._raw_json)


@dataclass(frozen=True, init=False)
class Relation:
    id: str
    subject: str
    predicate: str
    object: str
    _scope_json: bytes
    _raw_json: bytes
    snapshot_sha256: str

    def __init__(self, id: str, subject: str, predicate: str, object: str,
                 scope: Any, raw: Mapping[str, Any], snapshot_sha256: str):
        for key, value in (("id", id), ("subject", subject), ("predicate", predicate),
                           ("object", object), ("snapshot_sha256", snapshot_sha256)):
            builtins.object.__setattr__(self, key, value)
        builtins.object.__setattr__(self, "_scope_json", _encode(scope))
        builtins.object.__setattr__(self, "_raw_json", _encode(dict(raw)))

    @property
    def scope(self) -> Any:
        return json.loads(self._scope_json)

    @property
    def raw(self) -> dict[str, Any]:
        return json.loads(self._raw_json)
