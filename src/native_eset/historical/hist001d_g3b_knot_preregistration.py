"""Predeclared ORIGINAL March 180-point source-grid selection (G3b).

Pure input/geometry registration only. Does NOT compute original model mass
outputs, certify numerical discrepancies, or authorize any physics claim.
The two anchor roles select distinct SOURCE GRID KNOTS, not the off-knot
observed or D2d-root evaluation radii.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

SOURCE_SHA256 = "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
SCHEMA = "HIST001D_G3B_ORIGINAL_MARCH_KNOT_PREREGISTRATION_V1"
GRID_POINTS = 180
GRID_MIN_KPC = 0.02
GRID_MAX_KPC = 120.0
LENS_IDS = (
    "J0822+1828", "J0915+4211", "J0930+2855",
    "J1021+2028", "J1111+2234", "J1135+3720",
)


class G3bRegistrationError(ValueError):
    """Reject altered source grid, source-input roles or unsafe knot choices."""


def original_source_grid() -> np.ndarray:
    """Same literal grid construction as frozen March Set A source."""
    return np.linspace(0.02, 120.0, 180)


def register_two_source_knots(
    observed_radius_arcsec: float,
    scale_kpc_per_arcsec: float,
    d2d_root_kpc: float,
    grid: np.ndarray,
) -> dict[str, Any]:
    """Source-only deterministic selection: observed lower and D2d upper knot.

    Resolve a same-index collision by shifting the D2d role exactly one
    higher. Never inspect any baryonic/shadow outputs to select the knots.
    All returned radius values are exact represented float64 grid values.
    """
    if (not isinstance(grid, np.ndarray)
            or grid.dtype != np.dtype("float64")
            or grid.shape != (GRID_POINTS,)
            or not np.array_equal(grid, original_source_grid())):
        raise G3bRegistrationError("noncanonical frozen March source grid")
    vals = (observed_radius_arcsec, scale_kpc_per_arcsec, d2d_root_kpc)
    if any(isinstance(v, bool) or not isinstance(v, (float, int))
           or not math.isfinite(float(v)) or float(v) <= 0 for v in vals):
        raise G3bRegistrationError("invalid source-only anchor parameters")
    obs = float(observed_radius_arcsec) * float(scale_kpc_per_arcsec)
    root = float(d2d_root_kpc)
    if not (GRID_MIN_KPC < obs < GRID_MAX_KPC
            and GRID_MIN_KPC < root < GRID_MAX_KPC):
        raise G3bRegistrationError("anchor outside frozen finite radial grid")
    observed_index = int(np.searchsorted(grid, obs, side="right") - 1)
    root_index = int(np.searchsorted(grid, root, side="left"))
    collision = observed_index == root_index
    if collision:
        root_index += 1
    if not (0 <= observed_index < GRID_POINTS
            and 0 <= root_index < GRID_POINTS
            and observed_index != root_index):
        raise G3bRegistrationError("duplicate or unrepresentable source knots")
    return {
        "observed_role": {
            "anchor_kpc_binary64": obs,
            "source_knot_index_zero_based": observed_index,
            "source_knot_radius_kpc_binary64": float(grid[observed_index]),
        },
        "d2d_role": {
            "anchor_kpc_binary64": root,
            "source_knot_index_zero_based": root_index,
            "source_knot_radius_kpc_binary64": float(grid[root_index]),
        },
        "collision_shifted_d2d_one_index": collision,
        "outputs_at_source_knots_not_at_anchor_radii": True,
        "selection_based_on_baryonic_or_shadow_outputs": False,
        "source_mass_or_qeff_error_certified": False,
    }
