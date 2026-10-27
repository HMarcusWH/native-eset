"""Deterministic, predicate-filtered graph traversal. NOT logical implication."""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable, Any
from native_eset.graph.records import Relation
from native_eset.graph.snapshot import GraphSnapshot


_ALLOWED_DIRECTION = {"out", "in"}


@dataclass
class GraphQuery:
    snapshot: GraphSnapshot

    def __post_init__(self) -> None:
        self.by_out: dict[str, list[Relation]] = defaultdict(list)
        self.by_in: dict[str, list[Relation]] = defaultdict(list)
        for r in self.snapshot.relations:
            self.by_out[r.subject].append(r)
            self.by_in[r.object].append(r)
        for collection in (self.by_out, self.by_in):
            for rows in collection.values():
                rows.sort(key=lambda r: (r.predicate, r.subject, r.object, r.id))

    def _predicates(self, predicates: Iterable[str], direction: str) -> tuple[str, ...]:
        if direction not in _ALLOWED_DIRECTION:
            raise ValueError("explicit direction 'in' or 'out' required")
        if isinstance(predicates, str):
            raise ValueError("predicates must be a sequence, not a comma-separated string")
        result = tuple(sorted(set(predicates)))
        if not result or any(not isinstance(x, str) or not x for x in result):
            raise ValueError("explicit nonempty predicate filter required")
        from pathlib import Path
        from native_eset.serialization import read_json
        allowed = set(read_json(Path(__file__).with_name("vocabulary_v0_7_2.json"))["relation_types"])
        if set(result) - allowed:
            raise ValueError(f"unknown relation predicates: {sorted(set(result)-allowed)}")
        return result

    @staticmethod
    def _budget(value: int) -> None:
        if type(value) is not int or not 1 <= value <= 1_000_000:
            raise ValueError("graph expansion budget must be an integer 1..1000000")

    def node(self, obj_id: str) -> dict[str, Any]:
        try:
            return dict(self.snapshot.nodes[obj_id].raw)
        except KeyError as exc:
            raise KeyError(f"unknown graph node: {obj_id}") from exc

    def neighbors(self, obj_id: str, predicates: Iterable[str], *, direction: str) -> list[dict[str, Any]]:
        if direction not in _ALLOWED_DIRECTION:
            raise ValueError("explicit direction 'in' or 'out' required")
        if obj_id not in self.snapshot.nodes:
            raise KeyError(obj_id)
        pred = set(self._predicates(predicates, direction))
        rows = self.by_out[obj_id] if direction == "out" else self.by_in[obj_id]
        return [{"neighbor": r.object if direction == "out" else r.subject,
                 "predicate": r.predicate, "relation": r.id, "scope": r.scope,
                 "subject": r.subject, "object": r.object, "direction": direction}
                for r in rows if r.predicate in pred]

    def reachable(self, start: str, predicates: Iterable[str], *, direction: str,
                  max_nodes: int = 20000) -> dict[str, Any]:
        predicates = self._predicates(predicates, direction)
        self._budget(max_nodes)
        if start not in self.snapshot.nodes:
            raise KeyError(start)
        seen = {start}
        frontier = deque([(start, 0)])
        depths: dict[str, int] = {}
        while frontier:
            src, depth = frontier.popleft()
            for rel in self.neighbors(src, predicates, direction=direction):
                dest = rel["neighbor"]
                if dest not in seen:
                    seen.add(dest)
                    depths[dest] = depth+1
                    if len(seen) > max_nodes:
                        raise ValueError("reachability expansion budget exceeded")
                    frontier.append((dest, depth+1))
        return {"start": start, "direction": direction, "depths": dict(sorted(depths.items())),
                "predicate_filter": sorted(set(predicates)),
                "graph_sha256": self.snapshot.graph_sha256,
                "interpretation": "Structural traversal only, not scientific entailment"}

    def shortest_path(self, start: str, target: str, predicates: Iterable[str],
                      *, direction: str = "out", max_nodes: int = 20000) -> dict[str, Any] | None:
        predicates = self._predicates(predicates, direction)
        self._budget(max_nodes)
        if start not in self.snapshot.nodes or target not in self.snapshot.nodes:
            raise KeyError("unknown start or target node")
        pending: deque[str] = deque([start])
        parents: dict[str, tuple[str, dict[str, Any]] | None] = {start: None}
        while pending:
            src = pending.popleft()
            if src == target:
                break
            for edge in sorted(self.neighbors(src, predicates, direction=direction),
                               key=lambda x:(x["neighbor"],x["predicate"],x["relation"])):
                nxt = edge["neighbor"]
                if nxt in parents:
                    continue
                parents[nxt] = (src, edge)
                if len(parents) > max_nodes:
                    raise ValueError("path exploration budget exceeded")
                pending.append(nxt)
        if target not in parents:
            return None
        edges = []
        cursor = target
        while parents[cursor] is not None:
            parent, edge = parents[cursor]
            edges.append(edge)
            cursor = parent
        edges.reverse()
        return {"start":start,"target":target,"edge_count":len(edges),
                "edges":edges,"direction":direction,"graph_sha256":self.snapshot.graph_sha256,
                "interpretation":"Shortest typed structural path, not proof of physical/logical implication"}

    def blockers(self, target: str) -> dict[str, Any]:
        rows = self.neighbors(target, ["BLOCKS"], direction="in")
        for edge in rows:
            obj = self.snapshot.nodes[edge["subject"]]
            edge["blocker_declared_state"] = obj.raw.get("status", obj.raw.get("current_status", obj.raw.get("value")))
        return {"target":target,"blockers":rows,"graph_sha256":self.snapshot.graph_sha256,
                "interpretation":"Declared blockers; resolver adjudicates active state and exact scope"}

    def impact(self, changed: str, predicates: Iterable[str] = ("DEPENDS_ON", "REQUIRES", "REQUIRES_DOMAIN")) -> dict[str, Any]:
        return self.reachable(changed, predicates, direction="in")

    def diff(self, other: GraphSnapshot) -> dict[str, Any]:
        left = {**{n.id:n.raw for n in self.snapshot.nodes.values()},
                **{r.id:r.raw for r in self.snapshot.relations}}
        right = {**{n.id:n.raw for n in other.nodes.values()},
                 **{r.id:r.raw for r in other.relations}}
        return {"left_sha256":self.snapshot.graph_sha256,"right_sha256":other.graph_sha256,
                "added":sorted(right.keys()-left.keys()),
                "removed":sorted(left.keys()-right.keys()),
                "modified":sorted(k for k in left.keys()&right.keys() if left[k]!=right[k]),
                "interpretation":"Exact record delta. No implied new scientific authority."}
