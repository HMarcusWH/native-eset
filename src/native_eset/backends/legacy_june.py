"""Archived ESET-3/4 solver adapter. Requires exact recovered source and frozen inputs."""
from native_eset.backends.api import BackgroundOutput
from native_eset.identity import ScientificIdentity


class LegacyJuneBackend:
    def solve(self, identity: ScientificIdentity, **kwargs) -> BackgroundOutput:
        raise NotImplementedError(
            "Legacy June backend requires recovered source, source hash, source data, "
            "and frozen historical regression evidence. Do not substitute October equations."
        )
