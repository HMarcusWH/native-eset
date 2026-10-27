import pytest
from native_eset.identity import ScientificIdentity


def mk(**kw):
    data = dict(theory_id="TEST_ONLY",equation_source_sha256="0"*64,
                constitutive_id="A",species_id="B",initial_condition_id="C",
                parameters={"m":"0.001"},enabled_modules=())
    data.update(kw)
    return ScientificIdentity(**data)


def test_identity_is_stable_and_parameter_sensitive():
    assert mk().content_sha256() == mk().content_sha256()
    assert mk().content_sha256() != mk(parameters={"m":"0.002"}).content_sha256()
    assert mk().content_sha256() != mk(enabled_modules=("DM_A",)).content_sha256()
    assert mk().content_sha256() != mk(theory_id="ANOTHER").content_sha256()


def test_unserialized_parameters_rejected():
    with pytest.raises(TypeError):
        mk(parameters={"m": 1e-3})


def test_parameter_mapping_is_frozen_snapshot():
    mutable = {"m": "0.001"}
    model = mk(parameters=mutable)
    before = model.content_sha256()
    mutable["m"] = "0.4"
    assert model.content_sha256() == before
    with pytest.raises(TypeError):
        model.parameters["m"] = "0.03"
