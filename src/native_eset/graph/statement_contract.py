"""Conservative statement compatibility checks; never infer equation equivalence.

Mathematical equivalence needs an explicit derivation/proof over its validity domain.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StatementContract:
    id: str
    theory_id: str
    source_sha256: str
    frame: str
    gauge: str
    validity_domain: str
    field_set: tuple[str,...]
    quantifier_scope: str
    normalization: str
    units: str

    def __post_init__(self) -> None:
        for field in (self.id,self.theory_id,self.source_sha256,self.frame,
                      self.gauge,self.validity_domain,self.quantifier_scope,self.normalization,self.units):
            if not isinstance(field,str) or not field:
                raise ValueError("unknown/empty statement contract field; no implied equivalence")
        if len(self.source_sha256)!=64 or any(c not in "0123456789abcdef" for c in self.source_sha256):
            raise ValueError("source SHA-256 required for every statement")
        if (not isinstance(self.field_set, (tuple, list)) or not self.field_set or
                not all(isinstance(f,str) and f for f in self.field_set) or
                len(set(self.field_set)) != len(self.field_set)):
            raise ValueError("nonempty unique explicit field set required")
        object.__setattr__(self, "field_set", tuple(self.field_set))


def compatibility(left:StatementContract,right:StatementContract)->dict[str,Any]:
    blockers=[]
    for key in ("theory_id","frame","gauge","validity_domain","field_set",
                "quantifier_scope","normalization","units"):
        if getattr(left,key)!=getattr(right,key):blockers.append(key)
    if blockers:
        state="INCOMPATIBLE_OR_UNDERIVED_MAPPING"
    elif left.source_sha256!=right.source_sha256:
        blockers.append("source_sha256")
        state="COMPATIBILITY_REQUIRES_EQUIVALENCE_PROOF"
    else:
        state="METADATA_MATCH_ONLY_NOT_MATHEMATICAL_EQUIVALENCE"
    return {"left":left.id,"right":right.id,"state":state,
            "unmatched_fields":blockers,"automatic_inheritance":False,
            "interpretation":"Matching metadata is necessary but not sufficient for equation equivalence"}
