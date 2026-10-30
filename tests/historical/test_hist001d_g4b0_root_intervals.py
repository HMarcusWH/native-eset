"""G4b.0: adversarial exact-rational root partition and conditional H inclusion."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from fractions import Fraction
from pathlib import Path

import pytest

from native_eset.numerics.hist001d_g4b_root_intervals import (
    G4b0Error, INITIAL_CELLS, LENS_IDS, MAX_DYADIC_DEPTH,
    R_MAX, R_MIN, SOURCE_LOCK_SHA256, Leaf,
    assert_complete_cover, conditional_H_box,
    initial_partition, leaf_from_path, split_leaf,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registry/hist001d_g4b0_root_partition_v1.json"


def test_exact_source_domain_and_partition_cover():
    cells = initial_partition()
    assert len(cells) == 64 == INITIAL_CELLS
    assert R_MIN == Fraction.from_float(0.02)
    assert R_MIN != Fraction(1, 50)  # original 0.02 is EXACT BINARY64
    assert R_MAX == Fraction(120)
    assert cells[0].path == "00:"
    assert cells[-1].path == "63:"
    assert cells[0].left == R_MIN
    assert cells[-1].right == R_MAX
    for l, r in zip(cells, cells[1:]):
        assert l.right == r.left
    proof = assert_complete_cover(cells)
    assert proof["complete_contiguous_real_domain_covered"] is True
    assert proof["root_existence_or_uniqueness_proved"] is False
    assert proof["original_source_all_radius_numerical_error_bounded"] is False
    assert proof["empirical_validation"] == "NOT_ESTABLISHED"


def test_split_a_cell_and_recover_full_exact_cover():
    cells = list(initial_partition())
    for _ in range(MAX_DYADIC_DEPTH):
        left, right = split_leaf(cells[4])
        assert left.right == right.left
        assert left.left == cells[4].left
        assert right.right == cells[4].right
        cells[4:5] = [left, right]
        assert_complete_cover(cells)
    assert cells[4].path == "04:" + "0" * MAX_DYADIC_DEPTH
    with pytest.raises(G4b0Error, match="depth"):
        split_leaf(cells[4])


def test_dropped_duplicated_unsorted_tampered_leaves_rejected():
    cells = list(initial_partition())
    bad = [
        cells[:-1],
        cells[:10] + cells[11:],
        cells[:7] + cells[6:],
        list(reversed(cells)),
        cells[:1] + cells[:1] + cells[1:],
        [Leaf("00:", cells[0].left, cells[0].right + Fraction(1, 2))] + cells[1:],
    ]
    for attempt in bad:
        with pytest.raises(G4b0Error):
            assert_complete_cover(attempt)
    for malformed in ("00", "64:", "0:", "../00:", "00:000000000", "a0:"):
        with pytest.raises(G4b0Error):
            leaf_from_path(malformed)
    with pytest.raises(G4b0Error):
        split_leaf(Leaf("00:", R_MIN, R_MIN))


def test_conditional_exact_H_signs_and_root_nonclaims():
    cell = leaf_from_path("63:")
    negative = conditional_H_box(cell, ("1","1"), ("1","1"), ("0","0"), ("1e20","1e20"))
    positive = conditional_H_box(cell, ("1e20","1e20"), ("1","1"), ("0","0"), ("1","1"))
    unresolved = conditional_H_box(cell, ("1","1e20"), ("1","1"), ("0","0"), ("1e10","1e10"))
    assert negative["conditional_sign"].startswith("STRICT_NEGATIVE")
    assert positive["conditional_sign"].startswith("STRICT_POSITIVE")
    assert unresolved["conditional_sign"] == "UNRESOLVED_ZERO_NOT_EXCLUDED"
    for box in (negative, positive, unresolved):
        lo = box["H_lower_exact_rational"]
        hi = box["H_upper_exact_rational"]
        l = Fraction(int(lo["num"]), int(lo["den"]))
        u = Fraction(int(hi["num"]), int(hi["den"]))
        assert l <= u
        assert box["continuum_mass_shadow_sigma_inputs_certified_by_this_function"] is False
        assert box["valid_for_every_real_R_in_cell_IF_INPUT_ENCLOSURES_SOUND"] is True
        assert box["source_numeric_root_error_bounded"] is False
        assert box["root_existence_or_uniqueness_proved"] is False
        assert box["physical_weyl_lensing_derived"] is False


@pytest.mark.parametrize("bulge,disk,shadow,sigma", [
    ((0,1),(1,1),(0,1),(1,1)),
    ((1,0),(1,1),(0,1),(1,1)),
    ((1,1),(0,1),(0,1),(1,1)),
    ((1,1),(1,1),(-1,1),(1,1)),
    ((1,1),(1,1),(0,1),(0,1)),
    ((1,1),(1,1),(0,1),(2,1)),
    ((1,1),(1,1),(0,1),(float("nan"),1)),
    ((True,1),(1,1),(0,1),(1,1)),
    ((1,1),(1,1),(0,1),("NaN","2")),
    ((1,1),(1,1),(0,1),("1e999","2e999")),
])
def test_unsound_input_boxes_fail_closed(bulge, disk, shadow, sigma):
    with pytest.raises(G4b0Error):
        conditional_H_box(leaf_from_path("00:"),bulge,disk,shadow,sigma)


def test_registry_matches_frozen_source_input_only_and_predecessor_sha():
    from native_eset.historical.hist001_source import verify_hist001_source

    record = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert record["schema"] == "HIST001D_D2E_G4B0_SOURCE_ONLY_PARTITION_REGISTRATION_V1"
    assert record["status"] == "FROZEN_INPUT_PARTITION_ONLY_NO_RESIDUAL_ROOT_CERTIFICATE"
    assert record["source_lock_sha256"] == SOURCE_LOCK_SHA256
    assert tuple(record["lens_ids"]) == LENS_IDS
    assert record["initial_cells"] == INITIAL_CELLS
    assert record["max_dyadic_depth"] == MAX_DYADIC_DEPTH
    assert verify_hist001_source(ROOT / "research/legacy/hist001")["source_lock_sha256"] == SOURCE_LOCK_SHA256
    for path, digest in record["source_file_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    assert record["claims"]["all_R_root_isolation_completed"] is False
    assert record["claims"]["root_uniqueness_certified"] is False
    assert record["claims"]["physical_provider_admitted"] is False
    assert record["claims"]["empirical_validation"] == "NOT_ESTABLISHED"
    p = ROOT / "tools/hist001d_d2e.py"
    spec = importlib.util.spec_from_file_location("g4b0_prior_d2e_roots", p)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert tuple(mod.D2D_REFERENCE_ROOT_KPC) == LENS_IDS
    assert record["d2d_finite_root_anchors_kpc_for_provenance_only"] == mod.D2D_REFERENCE_ROOT_KPC
    assert record["source_domain_exact_dyadic"]["lower"] == str(R_MIN)
    assert record["source_domain_exact_dyadic"]["upper"] == str(R_MAX)
    assert math.isfinite(float(R_MIN))
