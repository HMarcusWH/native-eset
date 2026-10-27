"""Immutable and reproducible scientific identity records.

Numeric model parameter strings are intentional: avoid hidden binary64 normalization drift.
Theory hash is distinct from an executable/run hash and the evidence envelope.
"""
from dataclasses import dataclass, field
import hashlib
import json
from collections.abc import Mapping
from types import MappingProxyType


def digest_document(value: object) -> str:
    binary = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                        allow_nan=False).encode("utf-8")
    return hashlib.sha256(binary).hexdigest()


@dataclass(frozen=True)
class ScientificIdentity:
    theory_id: str
    equation_source_sha256: str
    constitutive_id: str
    species_id: str
    initial_condition_id: str
    parameters: Mapping[str, str] = field(default_factory=dict)
    enabled_modules: tuple[str, ...] = ()

    def __post_init__(self):
        if not all(isinstance(x, str) and x for x in (self.theory_id, self.equation_source_sha256,
                    self.constitutive_id, self.species_id, self.initial_condition_id)):
            raise ValueError("All theory identity fields must be non-empty")
        if len(self.equation_source_sha256) != 64 or any(c not in "0123456789abcdef"
                for c in self.equation_source_sha256):
            raise ValueError("equation_source_sha256 must be a lowercase SHA-256 hex digest")
        if (not isinstance(self.parameters, Mapping) or
                not all(isinstance(k, str) and k and isinstance(v, str)
                        for k, v in self.parameters.items())):
            raise TypeError("Parameters must be explicitly serialized as strings")
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
        if (isinstance(self.enabled_modules, str) or
                not all(isinstance(x, str) and x for x in self.enabled_modules) or
                len(set(self.enabled_modules)) != len(self.enabled_modules)):
            raise ValueError("enabled modules must be a unique sequence of nonempty module IDs")
        object.__setattr__(self, "enabled_modules", tuple(self.enabled_modules))

    def content_sha256(self) -> str:
        return digest_document({
            "theory_id": self.theory_id,
            "equation_source_sha256": self.equation_source_sha256,
            "constitutive_id": self.constitutive_id,
            "species_id": self.species_id,
            "initial_condition_id": self.initial_condition_id,
            "parameters": dict(self.parameters),
            "enabled_modules": sorted(self.enabled_modules),
        })
