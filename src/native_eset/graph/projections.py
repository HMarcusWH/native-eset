"""Explicit ESET predicate views; none is a proof or authority promotion."""
from __future__ import annotations

PROJECTIONS = {
    "SCIENTIFIC_DEPENDENCY": frozenset({"DEPENDS_ON", "REQUIRES", "REQUIRES_DOMAIN"}),
    "EVIDENCE_AUDIT": frozenset({"SUPPORTS", "CONTRADICTS", "FALSIFIES", "DOES_NOT_ESTABLISH", "PROVIDES_PROVENANCE_FOR"}),
    "IDENTITY_STRUCTURE": frozenset({"PART_OF", "CONTAINS", "IMPLEMENTS", "INSTANTIATES", "MAPS_TO"}),
    "NONPROMOTION_CONSTRAINTS": frozenset({"BLOCKS", "CONSTRAINS", "DISJOINT_WITH", "KILLS_INSTANCE"}),
}


def select_projection(name: str) -> tuple[str, ...]:
    if name not in PROJECTIONS:
        raise ValueError(f"unsupported semantic projection {name}")
    return tuple(sorted(PROJECTIONS[name]))


def closure_comparison(a: set[str], b: set[str]) -> dict[str, object]:
    rel = ("EQUAL" if a == b else "LEFT_STRICT_SUBSET" if a < b else
           "RIGHT_STRICT_SUBSET" if b < a else "INCOMPARABLE")
    return {"relation":rel,"shared":sorted(a&b),"left_only":sorted(a-b),
            "right_only":sorted(b-a),"interpretation":"Structural sets, not logical equivalence"}
