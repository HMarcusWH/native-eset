"""Current Native v1.7.2 one-map backend placeholder. Never fabricate P1R/P3 output."""
from native_eset.backends.api import BackgroundOutput
from native_eset.identity import ScientificIdentity


class NativeV172Backend:
    def solve(self, identity: ScientificIdentity, **kwargs) -> BackgroundOutput:
        raise NotImplementedError(
            "Current v1.7.2 solver not imported or provenance-verified. "
            "Required: exact one-map equations, full MEM work/entropy transport, "
            "species, Bianchi/residual checks, and source-frozen identity."
        )
