"""Read-only graph snapshots with separate byte and semantic integrity checks.

A matching lock proves equality to that lock, not authorship. Scientific approval
requires the independent approved lock in resolver_adapter, not a user-selected lock.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from native_eset.graph.records import Node, Relation
from native_eset.serialization import read_json, strict_loads, require_sha256


class GraphIntegrityError(ValueError):
    """The requested snapshot is malformed, corrupted, stale or incompatible."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_graph_digest(objects: list[dict[str, Any]]) -> str:
    data = json.dumps(sorted(objects, key=lambda o: o["id"]), sort_keys=True,
                      separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def validate_lock(lock: object) -> dict[str, Any]:
    if not isinstance(lock, dict) or lock.get("schema") != "NATIVE_ESET_THEORY_STATE_GRAPH_LOCK_V1":
        raise GraphIntegrityError("unsupported graph snapshot lock schema")
    for name in ("file_count", "record_count", "relation_count", "verdict_count"):
        if type(lock.get(name)) is not int or lock[name] < 0:
            raise GraphIntegrityError(f"invalid lock count: {name}")
    files = lock.get("files")
    if not isinstance(files, list) or len(files) != lock["file_count"] or not files:
        raise GraphIntegrityError("graph lock file-count mismatch")
    names: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise GraphIntegrityError("invalid graph file entry")
        name = item.get("name")
        if (not isinstance(name, str) or not name.endswith(".jsonl") or
                name.startswith(".") or any(c in name for c in "/\\:\x00") or name in names):
            raise GraphIntegrityError("duplicated/unsafe graph partition names")
        names.add(name)
        require_sha256(item.get("sha256"), "partition SHA-256")
    require_sha256(lock.get("graph_sha256"), "graph SHA-256")
    if not isinstance(lock.get("release_version"), str) or not lock["release_version"]:
        raise GraphIntegrityError("graph release version required")
    return lock


def _parse_partition(data: bytes, name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n, line in enumerate(data.decode("utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = strict_loads(line)
        except (ValueError, RecursionError) as exc:
            raise GraphIntegrityError(f"invalid JSONL {name}:{n}: {exc}") from exc
        if (not isinstance(obj, dict) or
                not all(isinstance(obj.get(k), str) and obj[k] for k in ("id", "type", "name"))):
            raise GraphIntegrityError(f"missing graph id/type/name in {name}:{n}")
        rows.append(obj)
    return rows


@dataclass(frozen=True, init=False)
class GraphSnapshot:
    root: Path
    _lock_json: bytes
    nodes: Mapping[str, Node]
    relations: tuple[Relation, ...]
    graph_sha256: str
    _source_blobs: Mapping[str, bytes]

    def __init__(self, root: Path, lock: Mapping[str, Any], nodes: Mapping[str, Node],
                 relations: tuple[Relation, ...], graph_sha256: str,
                 source_blobs: Mapping[str, bytes] | None = None):
        object.__setattr__(self, "root", Path(root))
        object.__setattr__(self, "_lock_json", json.dumps(dict(lock), sort_keys=True,
                           ensure_ascii=False, allow_nan=False).encode("utf-8"))
        object.__setattr__(self, "nodes", MappingProxyType(dict(nodes)))
        object.__setattr__(self, "relations", tuple(relations))
        object.__setattr__(self, "graph_sha256", graph_sha256)
        object.__setattr__(self, "_source_blobs", MappingProxyType(dict(source_blobs or {})))

    @property
    def lock(self) -> dict[str, Any]:
        return json.loads(self._lock_json)

    def source_blobs(self) -> dict[str, bytes]:
        return dict(self._source_blobs)

    def all_records(self) -> list[dict[str, Any]]:
        return [n.raw for n in self.nodes.values()] + [r.raw for r in self.relations]

    @classmethod
    def load(cls, source_dir: str | Path, lock_file: str | Path, *,
             vocabulary_file: str | Path | None = None) -> "GraphSnapshot":
        try:
            return cls._load(source_dir, lock_file, vocabulary_file=vocabulary_file)
        except GraphIntegrityError:
            raise
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as exc:
            raise GraphIntegrityError(f"malformed graph input: {exc}") from exc

    @classmethod
    def _load(cls, source_dir: str | Path, lock_file: str | Path, *,
              vocabulary_file: str | Path | None) -> "GraphSnapshot":
        src = Path(source_dir).resolve()
        lock = validate_lock(read_json(Path(lock_file)))
        expected = {f["name"]: f["sha256"] for f in lock["files"]}
        if not src.is_dir():
            raise GraphIntegrityError("graph source directory does not exist")
        # Reject .jsonl.txt and other files the original resolver might also read.
        found = {p.name for p in src.iterdir()}
        if found != set(expected):
            raise GraphIntegrityError(f"graph source inventory mismatch: missing={sorted(set(expected)-found)}, extra={sorted(found-set(expected))}")
        vocab_path = Path(vocabulary_file) if vocabulary_file else Path(__file__).with_name("vocabulary_v0_7_2.json")
        vocab = read_json(vocab_path)
        permitted_types, permitted_preds = set(vocab["object_types"]), set(vocab["relation_types"])
        objects: list[dict[str, Any]] = []
        keys: set[str] = set()
        source_blobs: dict[str, bytes] = {}
        for name, expected_sha in sorted(expected.items()):
            p = src / name
            if p.is_symlink() or not p.is_file() or p.stat().st_size > 150_000_000:
                raise GraphIntegrityError(f"unsafe/oversized graph partition: {name}")
            data = p.read_bytes()
            if len(data) > 150_000_000 or hashlib.sha256(data).hexdigest() != expected_sha:
                raise GraphIntegrityError(f"source hash mismatch: {name}")
            source_blobs[name] = data
            for row in _parse_partition(data, name):
                if row["id"] in keys:
                    raise GraphIntegrityError(f"duplicate graph id: {row['id']}")
                keys.add(row["id"])
                if row["type"] not in permitted_types:
                    raise GraphIntegrityError(f"unknown graph type: {row['type']}")
                if row["type"] == "Relation":
                    if not all(isinstance(row.get(k), str) and row[k] for k in ("subject", "predicate", "object")):
                        raise GraphIntegrityError(f"malformed relation: {row['id']}")
                    if row["predicate"] not in permitted_preds:
                        raise GraphIntegrityError(f"unknown relation predicate: {row['predicate']}")
                objects.append(row)
        digest = canonical_graph_digest(objects)
        if digest != lock["graph_sha256"]:
            raise GraphIntegrityError("canonical normalized graph SHA-256 mismatch")
        raw_relations = [o for o in objects if o["type"] == "Relation"]
        if (len(objects) != lock["record_count"] or len(raw_relations) != lock["relation_count"] or
                sum(o["type"] == "Verdict" for o in objects) != lock["verdict_count"]):
            raise GraphIntegrityError("graph record/relation/verdict count mismatch")
        by_id = {o["id"]: o for o in objects}
        nodes = {o["id"]: Node(o["id"], o["type"], o["name"], o, digest)
                 for o in objects if o["type"] != "Relation"}
        relations = []
        for r in raw_relations:
            if r["subject"] not in by_id or r["object"] not in by_id:
                raise GraphIntegrityError(f"missing relation endpoint: {r['id']}")
            # Parallel relations with distinct IDs/scopes are not discarded.
            relations.append(Relation(r["id"], r["subject"], r["predicate"], r["object"], r.get("scope"), r, digest))
        for o in objects:
            for field, required_type in (("authority_refs", "Authority"), ("source_refs", None)):
                refs = o.get(field, [])
                if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
                    raise GraphIntegrityError(f"invalid {field} on {o['id']}")
                for ref in refs:
                    if ref not in by_id or (required_type and by_id[ref]["type"] != required_type):
                        raise GraphIntegrityError(f"{o['id']} has missing/wrong {field}: {ref}")
        return cls(src, lock, nodes, tuple(sorted(relations, key=lambda r: r.id)), digest, source_blobs)

    def statistics(self) -> dict[str, Any]:
        return {"release": self.lock["release_version"], "sha256": self.graph_sha256,
                "nodes": len(self.nodes), "relations": len(self.relations),
                "record_count": len(self.nodes) + len(self.relations),
                "node_types": dict(sorted(Counter(n.type for n in self.nodes.values()).items())),
                "scope": "VERIFIED_SOURCE_GRAPH_READ_ONLY_NOT_PHYSICAL_ADMISSION"}
