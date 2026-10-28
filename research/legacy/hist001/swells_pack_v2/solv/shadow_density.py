from __future__ import annotations

import numpy as np

from .constants import FOUR_PI, G_KPC_KMS2_MSUN



def _compute_shadow_density_mass_difference(r_kpc, gbar_kms2_per_kpc, gtot_kms2_per_kpc):
    r = np.asarray(r_kpc, dtype=float)
    meff = np.where(r > 0, gtot_kms2_per_kpc * r**2 / G_KPC_KMS2_MSUN, 0.0)
    mbar_eff = np.where(r > 0, gbar_kms2_per_kpc * r**2 / G_KPC_KMS2_MSUN, 0.0)
    mshadow = np.clip(meff - mbar_eff, 0.0, None)
    rho = np.full_like(r, np.nan, dtype=float)
    mask = r > 0
    r_nonzero = r[mask]
    if r_nonzero.size >= 2:
        dm_dr = np.gradient(mshadow[mask], r_nonzero)
        rho_nonzero = np.clip(dm_dr / (FOUR_PI * np.clip(r_nonzero**2, 1e-12, None)), 0.0, None)
        rho[mask] = rho_nonzero
        rho[~mask] = rho_nonzero[0]
    else:
        rho[:] = 0.0
    return rho



def _compute_shadow_density_epsilon_gradient(r_kpc, gbar_kms2_per_kpc, epsilon):
    r = np.asarray(r_kpc, dtype=float)
    eps = np.clip(np.asarray(epsilon, dtype=float), 1e-6, None)
    mbar_eff = np.where(r > 0, gbar_kms2_per_kpc * r**2 / G_KPC_KMS2_MSUN, 0.0)
    mshadow = np.clip(mbar_eff * (1.0 / eps - 1.0), 0.0, None)
    rho = np.full_like(r, np.nan, dtype=float)
    mask = r > 0
    r_nonzero = r[mask]
    if r_nonzero.size >= 2:
        dm_dr = np.gradient(mshadow[mask], r_nonzero)
        rho_nonzero = np.clip(dm_dr / (FOUR_PI * np.clip(r_nonzero**2, 1e-12, None)), 0.0, None)
        rho[mask] = rho_nonzero
        rho[~mask] = rho_nonzero[0]
    else:
        rho[:] = 0.0
    return rho



def compute_shadow_density(r_kpc, gbar_kms2_per_kpc, gtot_kms2_per_kpc=None, *, epsilon=None, method: str = 'mass_difference_gradient'):
    method = str(method or 'mass_difference_gradient').lower()
    gbar = np.asarray(gbar_kms2_per_kpc, dtype=float)
    if method in {'mass_difference_gradient', 'mass_difference', 'legacy'}:
        if gtot_kms2_per_kpc is None:
            if epsilon is None:
                raise ValueError('mass_difference_gradient requires gtot or epsilon.')
            gtot_kms2_per_kpc = np.where(np.asarray(epsilon, dtype=float) > 0, gbar / np.asarray(epsilon, dtype=float), 0.0)
        return _compute_shadow_density_mass_difference(r_kpc, gbar, np.asarray(gtot_kms2_per_kpc, dtype=float))
    if method in {'epsilon_gradient_source', 'epsilon_gradient'}:
        if epsilon is None:
            if gtot_kms2_per_kpc is None:
                raise ValueError('epsilon_gradient_source requires epsilon or gtot.')
            epsilon = np.where(np.asarray(gtot_kms2_per_kpc, dtype=float) > 0, gbar / np.asarray(gtot_kms2_per_kpc, dtype=float), 1.0)
        return _compute_shadow_density_epsilon_gradient(r_kpc, gbar, epsilon)
    raise ValueError(f'Unsupported shadow density method: {method}')
