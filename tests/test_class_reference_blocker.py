import pytest
from native_eset.backends.class_reference import class_reference_run


def test_optional_class_stub_cannot_claim_computed_cosmology():
    with pytest.raises(NotImplementedError, match='NOT_IMPLEMENTED_SOURCE_LOCK_REQUIRED'):
        class_reference_run({'h': 0.7})
