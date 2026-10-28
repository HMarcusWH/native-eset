from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

import numpy as np

from .constants import ACCEL_KMS2_PER_KPC_TO_MPS2

A0_MPS2 = 1.1e-10
FEATURE_NAMES = (
    "ra0_kpc",
    "diskiness",
    "sigma_compact",
    "sigma_bulge",
    "compact_disk",
    "ratio_bre_dr50",
    "q_b",
    "q_d",
    "fbulge",
)


def safe_ratio(numerator: float, denominator: float, default: float = 1.0) -> float:
    try:
        num = float(numerator)
        den = float(denominator)
    except Exception:
        return float(default)
    if not np.isfinite(num) or not np.isfinite(den) or abs(den) < 1e-30:
        return float(default)
    return float(num / den)


def compute_transition_radius_kpc(model, a0_mps2: float = A0_MPS2, r_min_kpc: float = 1e-3, r_max_kpc: float = 200.0, n: int = 5000) -> float:
    rr = np.geomspace(float(r_min_kpc), float(r_max_kpc), int(n))
    gbar_rr = (model.total_vbar(rr) ** 2 / rr) * ACCEL_KMS2_PER_KPC_TO_MPS2
    idx = np.where(np.diff(np.sign(gbar_rr - a0_mps2)) != 0)[0]
    if len(idx):
        return float(rr[idx[-1]])
    return float(rr[np.argmin(np.abs(gbar_rr - a0_mps2))])


def extract_gate_features_from_values(
    bulge_mass_msun: float,
    bulge_re_kpc: float,
    disk_mass_msun: float,
    disk_r50_kpc: float,
    q_b: float,
    q_d: float,
    ra0_kpc: float | None = None,
) -> Dict[str, float]:
    bmass = float(bulge_mass_msun)
    bre = max(float(bulge_re_kpc), 1e-12)
    dmass = float(disk_mass_msun)
    dr50 = max(float(disk_r50_kpc), 1e-12)
    q_b = float(np.clip(q_b, 1e-3, 1.0))
    q_d = float(np.clip(q_d, 1e-3, 1.0))
    total = max(bmass + dmass, 1e-30)
    fbulge = bmass / total
    fdisk = 1.0 - fbulge
    return {
        "ra0_kpc": float(ra0_kpc) if ra0_kpc is not None else np.nan,
        "diskiness": float(fdisk * (1.0 - q_d)),
        "sigma_compact": float(total / (2.0 * np.pi * bre**2)),
        "sigma_bulge": float(bmass / (2.0 * np.pi * bre**2)),
        "compact_disk": float(dmass / (2.0 * np.pi * dr50**2)),
        "ratio_bre_dr50": float(bre / dr50),
        "q_b": q_b,
        "q_d": q_d,
        "fbulge": float(fbulge),
    }


def monomial_scale(features: Mapping[str, float], anchor: Mapping[str, float], exponents: Mapping[str, float] | None = None) -> float:
    exponents = exponents or {}
    scale = 1.0
    for key, exponent in exponents.items():
        ratio = safe_ratio(features.get(key, 1.0), anchor.get(key, 1.0), default=1.0)
        ratio = max(ratio, 1e-12)
        scale *= ratio ** float(exponent)
    return float(scale)


@dataclass(frozen=True)
class StructureTerm:
    family: str
    value: float
    parameters: Dict[str, float]



def build_structure_term(features: Mapping[str, float] | None, anchor: Mapping[str, float] | None, family: str = 'anchor_fixed', parameters: Mapping[str, float] | None = None) -> StructureTerm:
    features = dict(features or {})
    anchor = dict(anchor or features)
    parameters = dict(parameters or {})
    family = str(family or 'anchor_fixed').lower()
    if family in {'anchor_fixed', 'fixed', 'none'}:
        return StructureTerm(family=family, value=1.0, parameters=parameters)
    if family == 'diskiness_proxy':
        exponents = {'diskiness': float(parameters.get('diskiness_exp', 1.0)), 'q_d': float(parameters.get('q_d_exp', 0.0))}
        return StructureTerm(family=family, value=monomial_scale(features, anchor, exponents), parameters=parameters)
    if family == 'bulge_disk_mixture':
        exponents = {
            'fbulge': float(parameters.get('fbulge_exp', 0.5)),
            'q_b': float(parameters.get('q_b_exp', 0.0)),
            'q_d': float(parameters.get('q_d_exp', 0.0)),
        }
        return StructureTerm(family=family, value=monomial_scale(features, anchor, exponents), parameters=parameters)
    if family == 'compactness_proxy':
        exponents = {
            'sigma_compact': float(parameters.get('sigma_compact_exp', 1.0)),
            'sigma_bulge': float(parameters.get('sigma_bulge_exp', 0.0)),
            'ratio_bre_dr50': float(parameters.get('ratio_bre_dr50_exp', 0.0)),
        }
        return StructureTerm(family=family, value=monomial_scale(features, anchor, exponents), parameters=parameters)
    if family == 'hybrid_proxy':
        exponents = parameters.get('exponents', parameters)
        return StructureTerm(family=family, value=monomial_scale(features, anchor, exponents), parameters=parameters)
    raise ValueError(f'Unsupported structure family: {family}')
