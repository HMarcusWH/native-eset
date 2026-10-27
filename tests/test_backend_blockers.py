import pytest
from native_eset.backends.legacy_june import LegacyJuneBackend
from native_eset.backends.v172 import NativeV172Backend
from native_eset.identity import ScientificIdentity


def test_unimported_physics_cannot_be_executed():
    x = ScientificIdentity("TEST_ONLY", "a"*64, "A","B","C")
    for backend in (LegacyJuneBackend(), NativeV172Backend()):
        with pytest.raises(NotImplementedError):
            backend.solve(x)
