"""HIST-001B narrow regression tests; nothing here grants physical admission."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"
MODULE_FILE = ROOT / "tools/hist001b_rangefinder.py"
spec = importlib.util.spec_from_file_location("hist001b_rangefinder", MODULE_FILE)
assert spec is not None and spec.loader is not None
hist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hist)


@pytest.fixture(scope="module")
def prepared():
    from native_eset.historical.hist001_source import verify_hist001_source

    source = verify_hist001_source(SOURCE)
    assert source["frozen_files"] == 46
    assert source["archived_negative_records"] == 3
    pack = SOURCE / "swells_pack_v2"
    sys.path.insert(0, str(pack))
    return pack, hist.prepare(pack)


def test_central_source_numeric_and_exact_lens_ids(prepared):
    pack, state = prepared
    result = hist.evaluate(state, state[1].copy())
    assert tuple(state[1]["lens_id"]) == hist.LENS_IDS
    assert result["n_both_pass"] == 6
    assert result["mean_abs_radius_pull_sigma"] == pytest.approx(
        0.975973270592819, abs=1e-8
    )
    assert result["mean_abs_mass_pull_sigma"] == pytest.approx(
        0.5980326367412955, abs=1e-8
    )
    hist.check_against_original(state, state[1].copy(), pack, result)


@pytest.mark.parametrize("width", hist.WIDTHS)
def test_frozen_rng_trial_port_matches_untouched_solver(prepared, width):
    pack, state = prepared
    for trial in (0, 1):
        altered = hist.perturb(state[1], width, trial)
        fast = hist.evaluate(state, altered)
        hist.check_against_original(state, altered, pack, fast)
        assert fast["n_both_pass"] in range(7)
        assert fast["n_radius_pass"] in range(7)
        assert fast["n_mass_pass"] in range(7)


def test_known_negative_half_circularization(prepared):
    pack, state = prepared
    result = hist.check_half_projection(pack, state)
    assert result["n_both_pass"] == 2
    assert result["n_radius_pass"] == 2
    assert result["n_mass_pass"] == 5
    assert result["mean_abs_radius_pull_sigma"] == pytest.approx(
        5.582136435311303, abs=1e-8
    )


def test_smoke_is_explicitly_not_an_independent_full_replay(tmp_path):
    result = hist.replay(
        SOURCE, tmp_path / "smoke", trials=3, smoke=True,
    )
    assert result["status"] == "HIST001B_SMOKE_ONLY_NOT_REEXECUTED"
    assert result["empirical_validation"] == "NOT_ESTABLISHED"
    assert result["physical_provider_admitted"] is False
    assert result["archived_reference_is_new_output"] is False
    assert [x["n_trials"] for x in result["results"]] == [3]
    assert (tmp_path / "smoke/audit.json").exists()
    assert json.loads((tmp_path / "smoke/audit.json").read_text()) == result


def test_invalid_mode_fails_before_output_directory(tmp_path):
    with pytest.raises(ValueError, match="exactly 1000"):
        hist.replay(SOURCE, tmp_path / "not-created", trials=2)
    assert not (tmp_path / "not-created").exists()
    with pytest.raises(ValueError, match="smoke limit"):
        hist.replay(SOURCE, tmp_path / "not-created", trials=100, smoke=True)
    assert not (tmp_path / "not-created").exists()


def test_refuse_output_overlap_and_overwrite(prepared, tmp_path):
    with pytest.raises(ValueError, match="new and disjoint"):
        hist.replay(SOURCE, SOURCE / "subdir", trials=2, smoke=True)
    (tmp_path / "exists").mkdir()
    with pytest.raises(ValueError, match="new and disjoint"):
        hist.replay(SOURCE, tmp_path / "exists", trials=2, smoke=True)


def test_duplicate_or_reordered_lens_identity_rejected(prepared):
    _, state = prepared
    altered = state[1].copy()
    altered.loc[0, "lens_id"] = altered.loc[1, "lens_id"]
    with pytest.raises(ValueError, match="wrong Set A"):
        hist.evaluate(state, altered)


def test_physical_outputs_and_current_native_remain_blocked():
    from native_eset.capabilities import CAPABILITIES
    assert CAPABILITIES["native-v1.7.2-one-map"].executable is False
    assert "CMB_TT" not in CAPABILITIES[
        "legacy-hist001-j2141-seta"
    ].observables
