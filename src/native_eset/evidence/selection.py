"""Conservative exposure ledger: changing a model ID does not restore a holdout."""
from __future__ import annotations
from dataclasses import dataclass
from native_eset.serialization import require_sha256
from .data_roles import DataContaminationError, DATA_ROLES


@dataclass(frozen=True)
class DatasetUse:
    dataset_sha256: str
    role: str
    model_id: str
    label: str
    parent_dataset_sha256: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        try:
            require_sha256(self.dataset_sha256, "dataset SHA-256")
            if isinstance(self.parent_dataset_sha256, str):
                raise ValueError("parent source digests must be a sequence")
            for item in self.parent_dataset_sha256:
                require_sha256(item, "parent dataset SHA-256")
        except ValueError as exc:
            raise DataContaminationError(str(exc)) from exc
        if (self.role not in DATA_ROLES or not isinstance(self.model_id, str) or not self.model_id or
                not isinstance(self.label, str) or not self.label):
            raise DataContaminationError("dataset usage requires exact role, model and label")
        object.__setattr__(self, "parent_dataset_sha256", tuple(self.parent_dataset_sha256))


def audit_holdout_conflicts(records: list[DatasetUse]) -> dict:
    # Group every declared dataset family by shared identity or ancestor hashes.
    parent: dict[str, str] = {}
    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for r in records:
        for other in r.parent_dataset_sha256:
            a, b = find(r.dataset_sha256), find(other)
            if a != b:
                parent[max(a, b)] = min(a, b)
        find(r.dataset_sha256)
    groups: dict[str, list[DatasetUse]] = {}
    for r in records:
        groups.setdefault(find(r.dataset_sha256), []).append(r)
    conflicts = []
    for family, rows in sorted(groups.items()):
        roles = {r.role for r in rows}
        if "HELD_OUT_VALIDATION" in roles and roles - {"HELD_OUT_VALIDATION"}:
            conflicts.append({"dataset_family_sha256": family,
                              "dataset_sha256s": sorted({r.dataset_sha256 for r in rows}),
                              "model_ids": sorted({r.model_id for r in rows}), "roles": sorted(roles)})
    return {"status": "FAIL_CLOSED_HOLDOUT_CONTAMINATION" if conflicts else "PASS_ROLE_DISJOINTNESS_ONLY",
            "conflicts": conflicts,
            "note": "Declared history only; absent lineage, human exposure, or undeclared derivatives remain unknown"}
