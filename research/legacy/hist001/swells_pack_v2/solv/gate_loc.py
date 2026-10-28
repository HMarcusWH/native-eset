from __future__ import annotations

from typing import Mapping

import numpy as np

from .constants import ACCEL_KMS2_PER_KPC_TO_MPS2

DEFAULT_A0_MPS2 = 1.1e-10



def local_suppressor(gbar_kms2_per_kpc, family: str = 'none', parameters: Mapping[str, float] | None = None):
    parameters = dict(parameters or {})
    family = str(family or 'none').lower()
    gbar_mps2 = np.clip(np.asarray(gbar_kms2_per_kpc, dtype=float) * ACCEL_KMS2_PER_KPC_TO_MPS2, 0.0, None)
    a0 = max(float(parameters.get('a0_mps2', DEFAULT_A0_MPS2)), 1e-30)
    x = np.clip(gbar_mps2 / a0, 0.0, None)

    if family in {'none', 'fixed', 'disabled'}:
        return np.ones_like(x)
    if family == 'power_cutoff_n':
        n = max(float(parameters.get('n', 4.0)), 1e-6)
        return 1.0 / (1.0 + x**n)
    if family == 'logistic_cutoff':
        k = float(parameters.get('k', 6.0))
        x0 = float(parameters.get('x0', 1.0))
        return 1.0 / (1.0 + np.exp(k * (x - x0)))
    if family == 'tanh_cutoff':
        k = float(parameters.get('k', 4.0))
        x0 = float(parameters.get('x0', 1.0))
        return 0.5 * (1.0 - np.tanh(k * (x - x0)))
    if family == 'sharp_rational_cutoff':
        n = max(float(parameters.get('n', 6.0)), 1e-6)
        x0 = max(float(parameters.get('x0', 1.0)), 1e-6)
        return 1.0 / (1.0 + (x / x0) ** n)
    raise ValueError(f'Unsupported local cutoff family: {family}')



def apply_local_suppressor_to_epsilon(epsilon_base, gbar_kms2_per_kpc, family: str = 'none', parameters: Mapping[str, float] | None = None):
    eps = np.asarray(epsilon_base, dtype=float)
    suppress = np.clip(local_suppressor(gbar_kms2_per_kpc, family=family, parameters=parameters), 0.0, 1.0)
    return 1.0 - (1.0 - eps) * suppress
