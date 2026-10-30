"""Input-only G3b 180x120 source-knot registration; no source outputs inspected."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from native_eset.historical.hist001d_g3b_knot_preregistration import (
    G3bRegistrationError, LENS_IDS, SOURCE_SHA256,
    original_source_grid, register_two_source_knots,
)

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "registry/hist001d_d2e_g3b_knots_v1.json"
SOURCE = ROOT / "research/legacy/hist001"
FROZEN = SOURCE / "swells_pack_v2"
D2E = ROOT / "tools/hist001d_d2e.py"


def _load_d2e_roots():
    spec = importlib.util.spec_from_file_location("g3b_prereg_frozen_d2e", D2E)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.SOURCE_SHA256 == SOURCE_SHA256
    return module.D2D_REFERENCE_ROOT_KPC


def test_original_march_source_input_selection_preregistered():
    from native_eset.historical.hist001_source import verify_hist001_source

    item = json.loads(RECORD.read_text(encoding="utf-8"))
    original = verify_hist001_source(SOURCE)
    assert original["source_lock_sha256"] == SOURCE_SHA256
    assert item["source_sha256"] == SOURCE_SHA256
    assert item["status"] == "INPUTS_AND_SOURCE_KNOT_SELECTION_PREREGISTERED_NOT_ERROR_CERTIFIED"
    for name, expected_sha in item["source_file_sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected_sha
    assert item["grid"] == {
        "source_expression": "np.linspace(0.02, 120.0, 180)",
        "dtype": "float64", "points": 180, "lower_kpc": 0.02, "upper_kpc": 120.0,
    }
    assert item["selector"]["selection_uses_source_mass_outputs"] is False

    fitted = pd.read_csv(FROZEN / "cleaned/lens_set_A_run_fo_74bb5e.csv")
    scales = pd.read_csv(FROZEN / "cleaned/setA_scale_kpc_per_arcsec.csv")
    rows = fitted.merge(scales, on="lens_id", how="left")
    roots = _load_d2e_roots()
    assert tuple(rows.lens_id) == LENS_IDS
    assert tuple(roots) == LENS_IDS
    assert len(item["preregistrations"]) == 6
    grid = original_source_grid()
    assert grid.shape == (180,) and grid.dtype == np.dtype("float64")
    assert grid[0] == 0.02 and grid[-1] == 120.0
    assert len({r["lens_id"] for r in item["preregistrations"]}) == 6

    selected = []
    for data, row in zip(item["preregistrations"], rows.to_dict("records")):
        lens = data["lens_id"]
        assert lens == row["lens_id"]
        assert data["observed_arcsec"] == float(row["einstein_radius_arcsec_central"])
        assert data["scale_kpc_per_arcsec"] == float(row["scale_kpc_per_arcsec"])
        assert data["d2d_root_kpc"] == float(roots[lens])
        out = register_two_source_knots(
            data["observed_arcsec"], data["scale_kpc_per_arcsec"],
            data["d2d_root_kpc"], grid,
        )
        oi = out["observed_role"]["source_knot_index_zero_based"]
        di = out["d2d_role"]["source_knot_index_zero_based"]
        assert (oi, di) == (data["observed_index"], data["d2d_index"])
        assert out["collision_shifted_d2d_one_index"] is data["collision_shift"]
        assert oi != di
        assert out["observed_role"]["source_knot_radius_kpc_binary64"] == float(grid[oi])
        assert out["d2d_role"]["source_knot_radius_kpc_binary64"] == float(grid[di])
        assert out["outputs_at_source_knots_not_at_anchor_radii"] is True
        assert out["source_mass_or_qeff_error_certified"] is False
        selected.append((lens, oi, di))
    assert len(selected) == 6
    assert selected[2] == ("J0930+2855", 7, 8)
    for key, value in item["claims"].items():
        assert value is False or (key == "empirical_validation" and value == "NOT_ESTABLISHED")


@pytest.mark.parametrize("observed,scale,root", [
    (0.0, 2.0, 2.0),
    (float("nan"), 2.0, 2.0),
    (0.5, -1.0, 2.0),
    (True, 2.0, 2.0),
    (0.5, 2.0, 200.0),
    (100.0, 2.0, 2.0),
])
def test_unsupported_source_inputs_fail_closed(observed, scale, root):
    with pytest.raises(G3bRegistrationError):
        register_two_source_knots(observed, scale, root, original_source_grid())


def test_altered_grid_and_dtype_fail_closed():
    grid = original_source_grid()
    changed = grid.copy()
    changed[3] = np.nextafter(changed[3], float("inf"))
    with pytest.raises(G3bRegistrationError, match="noncanonical"):
        register_two_source_knots(.83, 2.089629900424512, 1.9335521276132295, changed)
    with pytest.raises(G3bRegistrationError, match="noncanonical"):
        register_two_source_knots(.83, 2.089629900424512, 1.9335521276132295,
                                  grid.astype("float32"))
    with pytest.raises(G3bRegistrationError, match="noncanonical"):
        register_two_source_knots(.83, 2.089629900424512, 1.9335521276132295, list(grid))


def test_g3b_preregistration_never_silently_becomes_physics():
    obj = json.loads(RECORD.read_text(encoding="utf-8"))
    assert obj["qeff_provenance"].startswith("DERIVED_USING_FROZEN_SOURCE_EXPRESSION")
    assert obj["membership"].endswith("NOT_HOLDOUT")
    assert obj["source_bulge_output"].startswith("ORIGINAL_MARCH_K_MATRIX")
    assert obj["source_disk_output"].startswith("ORIGINAL_MARCH_120_ANGLE")
    assert obj["claims"]["physical_provider_admitted"] is False
    assert obj["claims"]["new_independent_holdout_scored"] is False
