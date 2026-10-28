from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping

import numpy as np

from .gate_struct import monomial_scale, safe_ratio


@dataclass(frozen=True)
class ChargeTerms:
    family: str
    r0_scale: float
    delta_scale: float
    metadata: Dict[str, float | str]



def _clip_positive(value: float, floor: float = 1e-6) -> float:
    value = float(value)
    if not np.isfinite(value):
        return float(floor)
    return float(max(value, floor))


def _safe_log_ratio(features: Mapping[str, float], anchor: Mapping[str, float], key: str) -> float:
    ratio = _clip_positive(safe_ratio(features.get(key, 1.0), anchor.get(key, 1.0), default=1.0))
    return float(np.log(ratio))


def _sigmoid(value: float) -> float:
    value = float(np.clip(value, -60.0, 60.0))
    return float(1.0 / (1.0 + np.exp(-value)))



def build_charge_terms(features: Mapping[str, float] | None, anchor: Mapping[str, float] | None, family: str = 'fixed', parameters: Mapping[str, float] | None = None) -> ChargeTerms:
    features = dict(features or {})
    anchor = dict(anchor or features)
    parameters = dict(parameters or {})
    family = str(family or 'fixed').lower()
    if family in {'fixed', 'none', 'anchor_fixed'}:
        return ChargeTerms(family=family, r0_scale=1.0, delta_scale=1.0, metadata={'family': family})

    if family == 'compact_power':
        ra0_power = float(parameters.get('ra0_power', 0.0))
        ra0_ratio = _clip_positive(safe_ratio(features.get('ra0_kpc', 1.0), anchor.get('ra0_kpc', 1.0), default=1.0))
        r0_scale = ra0_ratio ** ra0_power
        r0_scale *= monomial_scale(features, anchor, parameters.get('r0_exponents', {}))
        delta_scale = monomial_scale(features, anchor, parameters.get('delta_exponents', {}))
        return ChargeTerms(
            family=family,
            r0_scale=_clip_positive(r0_scale),
            delta_scale=_clip_positive(delta_scale),
            metadata={'family': family, 'ra0_power': ra0_power},
        )

    if family == 'ra0_gated_geometry_sigmoid':
        ra0_power = float(parameters.get('ra0_power', 1.0))
        baseline_r0_exponents = dict(parameters.get('baseline_r0_exponents', parameters.get('r0_exponents', {'diskiness': -0.1, 'sigma_compact': 0.2})))
        baseline_delta_exponents = dict(parameters.get('baseline_delta_exponents', parameters.get('delta_exponents', {'sigma_compact': -0.2})))

        ra0_ratio = _clip_positive(safe_ratio(features.get('ra0_kpc', 1.0), anchor.get('ra0_kpc', 1.0), default=1.0))
        baseline_r0_scale = (ra0_ratio ** ra0_power) * monomial_scale(features, anchor, baseline_r0_exponents)
        baseline_delta_scale = monomial_scale(features, anchor, baseline_delta_exponents)

        w_cd = float(parameters.get('w_cd', 0.0))
        w_ratio = float(parameters.get('w_ratio', 0.0))
        w_qb = float(parameters.get('w_qb', 0.0))
        w_qd = float(parameters.get('w_qd', 0.0))
        contrast_width = max(float(parameters.get('contrast_width', 1.0)), 1e-6)
        ra0_turn = float(parameters.get('ra0_turn', 0.0))
        ra0_width = max(float(parameters.get('ra0_width', 1.0)), 1e-6)
        beta_r0 = float(parameters.get('beta_r0', 0.0))
        beta_delta = float(parameters.get('beta_delta', 0.0))

        geometry_contrast = (
            w_cd * _safe_log_ratio(features, anchor, 'compact_disk')
            + w_ratio * _safe_log_ratio(features, anchor, 'ratio_bre_dr50')
            + w_qb * _safe_log_ratio(features, anchor, 'q_b')
            - w_qd * _safe_log_ratio(features, anchor, 'q_d')
        )
        high_ra_gate = _sigmoid((np.log(ra0_ratio) - ra0_turn) / ra0_width)
        correction = high_ra_gate * np.tanh(geometry_contrast / contrast_width)

        r0_scale = _clip_positive(baseline_r0_scale * np.exp(beta_r0 * correction))
        delta_scale = _clip_positive(baseline_delta_scale * np.exp(beta_delta * correction))
        return ChargeTerms(
            family=family,
            r0_scale=r0_scale,
            delta_scale=delta_scale,
            metadata={
                'family': family,
                'ra0_power': ra0_power,
                'geometry_contrast': float(geometry_contrast),
                'high_ra_gate': float(high_ra_gate),
                'correction': float(correction),
                'beta_r0': beta_r0,
                'beta_delta': beta_delta,
            },
        )

    if family == 'relaxation_saturation':
        primary = str(parameters.get('primary_feature', 'sigma_compact'))
        feature_ratio = _clip_positive(safe_ratio(features.get(primary, 1.0), anchor.get(primary, 1.0), default=1.0))
        x0 = _clip_positive(parameters.get('x0_ratio', 1.0))
        m = max(float(parameters.get('m', 1.0)), 1e-6)
        beta_r0 = float(parameters.get('beta_r0', 1.0))
        beta_delta = float(parameters.get('beta_delta', -1.0))
        saturator = 1.0 / (1.0 + (feature_ratio / x0) ** m)
        reference = 1.0 / (1.0 + (1.0 / x0) ** m)
        r0_scale = _clip_positive((saturator / reference) ** beta_r0)
        delta_scale = _clip_positive((saturator / reference) ** beta_delta)
        return ChargeTerms(
            family=family,
            r0_scale=r0_scale,
            delta_scale=delta_scale,
            metadata={'family': family, 'primary_feature': primary},
        )

    if family == 'occupancy_concentration':
        w_fbulge = float(parameters.get('w_fbulge', 0.4))
        w_sigma = float(parameters.get('w_sigma_bulge', 0.4))
        w_ratio = float(parameters.get('w_ratio_bre_dr50', 0.2))
        occ = (
            w_fbulge * np.log(_clip_positive(features.get('fbulge', 1.0)))
            + w_sigma * np.log(_clip_positive(safe_ratio(features.get('sigma_bulge', 1.0), anchor.get('sigma_bulge', 1.0), default=1.0)))
            + w_ratio * np.log(_clip_positive(safe_ratio(features.get('ratio_bre_dr50', 1.0), anchor.get('ratio_bre_dr50', 1.0), default=1.0)))
        )
        alpha_r0 = float(parameters.get('alpha_r0', 0.5))
        alpha_delta = float(parameters.get('alpha_delta', -0.5))
        r0_scale = _clip_positive(np.exp(alpha_r0 * occ))
        delta_scale = _clip_positive(np.exp(alpha_delta * occ))
        return ChargeTerms(
            family=family,
            r0_scale=r0_scale,
            delta_scale=delta_scale,
            metadata={'family': family},
        )

    raise ValueError(f'Unsupported charge family: {family}')
