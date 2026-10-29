"""HIST-001B transition-radius precheck admission boundary.

The June ledger claims 600 grid-cell matches, but the original accelerated
implementation and original 600 input-case inventory are absent. This module
must not substitute newly generated cases and call the archive verified.
"""
from __future__ import annotations

from native_eset.historical.hist001b_source import (
    HISTORICAL_PRODUCER_STATUS, PRECHECK_STATUS,
)


class OriginalPrechecksUnavailable(ValueError):
    pass


REQUIRED_ORIGINAL_CASES = 600


def precheck_status() -> dict:
    return {
        "status": PRECHECK_STATUS,
        "required_cases": REQUIRED_ORIGINAL_CASES,
        "executed_original_cases": 0,
        "original_case_manifest_sha256": None,
        "original_accelerated_code_sha256": None,
        "grid_cell_equivalence_proved": False,
        "original_producer_status": HISTORICAL_PRODUCER_STATUS,
        "source_exact_replay_authorized": False,
    }


def require_original_600_prechecks(*, producer_sha256: str | None = None,
                                   case_manifest_sha256: str | None = None,
                                   claimed_matches: int | None = None) -> None:
    """Fail closed until trusted, non-caller-defined original identities exist.

    Even 600/600 claimed matches are not a proof without independently
    authenticated code and the exact original 600 input cases.
    """
    del producer_sha256, case_manifest_sha256, claimed_matches
    raise OriginalPrechecksUnavailable(
        "Original accelerated producer and original 600-case manifest "
        "not recovered; independent precheck authority is blocked"
    )


def independently_check_new_600_grid_cases(source_root: str | "Path") -> dict:
    """Run NEW deterministic 600-case scalar-vs-vectorized grid diagnostics.

    Deliberately NOT the unpreserved original 600 archived acceleration checks.
    This test is source-equivalent for the radial grid formula on 600 NEW inputs;
    it does not establish the original producer's identity, RNG or prechecks.
    """
    import hashlib
    import sys
    from pathlib import Path

    import numpy as np
    from scipy import special

    from native_eset.evidence.receipts import canonical_json
    from native_eset.historical.hist001_source import verify_hist001_source
    from native_eset.historical.hist001b_source import (
        HIST001A_SOURCE_LOCK_SHA256, require_no_symlink_components,
    )

    root = require_no_symlink_components(source_root)
    before = verify_hist001_source(root)
    if before["source_lock_sha256"] != HIST001A_SOURCE_LOCK_SHA256:
        raise ValueError("independent 600-case source identity differs")
    pack = Path(root) / "swells_pack_v2"
    sys.dont_write_bytecode = True
    if str(pack) not in sys.path:
        sys.path.insert(0, str(pack))

    import solv.run_setA_port_cand as original
    from solv.baryons import J2141BaryonicModel
    from solv.constants import G_KPC_KMS2_MSUN, ACCEL_KMS2_PER_KPC_TO_MPS2
    from solv.gate_struct import A0_MPS2, compute_transition_radius_kpc

    base = original._load_tables(pack).copy()
    expected_lenses = tuple(before["lens_ids"])
    if tuple(base["lens_id"]) != expected_lenses or len(base) != 6:
        raise ValueError("independent 600-case lens provenance mismatch")
    radius = np.geomspace(1e-3, 200.0, 5000)
    reference_indices = []
    newly_computed_indices = []
    for case in range(600):
        row = base.iloc[case % len(base)]
        width = (0.01, 0.02, 0.05, 0.10)[case % 4]
        # This is a NEW predeclared deterministic corpus, NOT historical RNG.
        rng = np.random.default_rng(
            np.random.SeedSequence([2141, 0xB001, case])
        )
        six_draws = rng.uniform(1 - width, 1 + width, 6)
        bulge_mass = 10**float(row.logM_bulge_chabrier_central) * six_draws[4]
        disc_mass = 10**float(row.logM_disc_chabrier_central) * six_draws[5]
        bulge_re = (float(row.Re_bulge_arcsec) *
                    float(row.scale_kpc_per_arcsec) * six_draws[2])
        disc_r50 = (float(row.Re_disc_arcsec) *
                    float(row.scale_kpc_per_arcsec) * six_draws[3])
        model = J2141BaryonicModel(
            bulge_mass, bulge_re, disc_mass, disc_r50
        )
        original_r = compute_transition_radius_kpc(
            model, a0_mps2=A0_MPS2
        )
        original_idx = int(np.argmin(np.abs(radius - original_r)))
        if radius[original_idx] != original_r:
            raise ValueError("original transition radius is not a grid point")

        # Independent computation of the underlying acceleration and selection
        # (without calling J2141BaryonicModel.total_vbar or its grid finder).
        a = bulge_re / 1.8153
        rd = disc_r50 / 1.67835
        y = radius / (2.0 * rd)
        v2_b = (G_KPC_KMS2_MSUN * bulge_mass * radius /
                (radius + a)**2)
        v2_d = (G_KPC_KMS2_MSUN * disc_mass / (2.0 * rd) *
                y**2 * (special.i0(y) * special.k0(y)
                        - special.i1(y) * special.k1(y)))
        acceleration = (
            np.clip(v2_b + v2_d, 0.0, None) / radius *
            ACCEL_KMS2_PER_KPC_TO_MPS2
        )
        crossing = np.flatnonzero(
            np.diff(np.sign(acceleration - A0_MPS2)) != 0
        )
        index = int(crossing[-1]) if len(crossing) else int(
            np.argmin(np.abs(acceleration - A0_MPS2))
        )
        if not np.isfinite(acceleration[index]):
            raise ValueError("non-finite independent transition acceleration")
        if index != original_idx or float(radius[index]) != original_r:
            raise ValueError("NEW independent transition-radius grid mismatch")
        reference_indices.append(original_idx)
        newly_computed_indices.append(index)
    after = verify_hist001_source(root)
    if after["source_lock_sha256"] != before["source_lock_sha256"]:
        raise ValueError("independent 600-case test changed frozen source")

    return {
        "schema": "HIST001B_NEW_INDEPENDENT_600_GRID_DIAGNOSTIC_V1",
        "status": "NEW_SYNTHETIC_600_GRID_CELLS_MATCHED_NOT_ORIGINAL_PRECHECKS",
        "source_lock_sha256": HIST001A_SOURCE_LOCK_SHA256,
        "new_case_generator": "SeedSequence([2141,0xB001,case])",
        "new_cases_executed": 600,
        "new_cases_matched": 600,
        "first_six_grid_indices": newly_computed_indices[:6],
        "grid_index_sha256": hashlib.sha256(
            canonical_json(newly_computed_indices)
        ).hexdigest(),
        "original_archived_cases_executed": 0,
        "original_600_prechecks_verified": False,
        "original_producer_verified": False,
        "original_rng_schedule_verified": False,
        "source_exact_replay_authorized": False,
        "physical_provider_admitted": False,
    }
