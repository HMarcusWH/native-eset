"""Interface contract for independently sourced scientific backends."""
from dataclasses import dataclass
from typing import Protocol, Any
from native_eset.identity import ScientificIdentity


@dataclass(frozen=True)
class BackgroundOutput:
    source_identity: str
    metadata: dict[str, str]
    independent_coordinate: tuple[float, ...]
    normalized_hubble: tuple[float, ...]
    residuals: dict[str, float]
    internal_only: bool = True


class BackgroundSolver(Protocol):
    def solve(self, identity: ScientificIdentity, **kwargs: Any) -> BackgroundOutput: ...
