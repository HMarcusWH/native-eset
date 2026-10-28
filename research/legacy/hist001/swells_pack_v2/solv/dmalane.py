from __future__ import annotations

import numpy as np
from scipy import optimize

from .constants import ACCEL_KMS2_PER_KPC_TO_MPS2
from .gate_chg import build_charge_terms
from .gate_loc import apply_local_suppressor_to_epsilon
from .gate_struct import build_structure_term
from .shadow_density import compute_shadow_density


def epsilon_rar_shell(gbar_kms2_per_kpc, g_dagger_m_s2=1.1e-10, epsilon_floor=0.05):
    gbar_mps2 = np.clip(np.asarray(gbar_kms2_per_kpc, dtype=float) * ACCEL_KMS2_PER_KPC_TO_MPS2, 0.0, None)
    eps = 1.0 - np.exp(-np.sqrt(np.clip(gbar_mps2 / g_dagger_m_s2, 0.0, None)))
    return np.clip(eps, epsilon_floor, 1.0)



def epsilon_radius_proxy(r_kpc, delta_epsilon, r0_kpc, n, epsilon_floor=0.05):
    r = np.clip(np.asarray(r_kpc, dtype=float), 0.0, None)
    delta = float(delta_epsilon)
    r0 = max(float(r0_kpc), 1e-12)
    n = max(float(n), 1e-12)
    eps = 1.0 - delta * (r**n) / (r**n + r0**n)
    return np.clip(eps, epsilon_floor, 1.0)



def build_gate_components(gate_config, *, features=None, anchor=None):
    gate_config = dict(gate_config or {})
    mode = str(gate_config.get('mode', 'rar_shell')).lower()
    legacy = dict(gate_config.get('legacy_compat', {}))
    epsilon_floor = float(gate_config.get('epsilon_floor', legacy.get('epsilon_floor', 0.05)))
    components = {
        'mode': mode,
        'epsilon_floor': epsilon_floor,
        'shadow_density_method': str(gate_config.get('shadow_density', {}).get('method', gate_config.get('shadow_density_method', 'mass_difference_gradient'))),
    }
    if mode == 'rar_shell':
        components['g_dagger_m_s2'] = float(gate_config.get('g_dagger_m_s2', legacy.get('g_dagger_m_s2', 1.1e-10)))
        components['local_cutoff'] = dict(gate_config.get('local_cutoff', {'family': 'none'}))
        return components

    if mode not in {'radius_proxy', 'rational_radius_proxy', 'test1_radius_proxy'}:
        raise ValueError(f'Unsupported gate mode: {mode}')

    structure_cfg = dict(gate_config.get('structure', {'family': 'anchor_fixed'}))
    charge_cfg = dict(gate_config.get('charge', {'family': 'fixed'}))
    local_cfg = dict(gate_config.get('local_cutoff', {'family': 'none'}))

    base_r0 = float(gate_config.get('r0_kpc', legacy.get('r0_kpc', 1.0)))
    base_delta = float(gate_config.get('delta_epsilon', legacy.get('delta_epsilon', 0.0)))
    n = float(gate_config.get('n', legacy.get('n', 4.0)))

    structure_term = build_structure_term(features, anchor, family=structure_cfg.get('family', 'anchor_fixed'), parameters=structure_cfg.get('parameters'))
    charge_terms = build_charge_terms(features, anchor, family=charge_cfg.get('family', 'fixed'), parameters=charge_cfg.get('parameters'))

    r0_kpc = base_r0 * float(structure_term.value) * float(charge_terms.r0_scale)
    delta_epsilon = base_delta * float(charge_terms.delta_scale)
    delta_bounds = gate_config.get('delta_bounds', legacy.get('delta_bounds', [0.05, 0.95]))
    delta_min = float(delta_bounds[0]) if len(delta_bounds) >= 1 else 0.05
    delta_max = float(delta_bounds[1]) if len(delta_bounds) >= 2 else 0.95
    delta_epsilon = float(np.clip(delta_epsilon, delta_min, delta_max))

    components.update({
        'r0_kpc': float(r0_kpc),
        'delta_epsilon': float(delta_epsilon),
        'n': float(n),
        'structure_term': {'family': structure_term.family, 'value': float(structure_term.value), 'parameters': structure_term.parameters},
        'charge_term': {'family': charge_terms.family, 'r0_scale': float(charge_terms.r0_scale), 'delta_scale': float(charge_terms.delta_scale), 'metadata': charge_terms.metadata},
        'local_cutoff': local_cfg,
    })
    return components



def epsilon_from_components(r_kpc, gbar_kms2_per_kpc, components):
    mode = str(components.get('mode', 'rar_shell')).lower()
    epsilon_floor = float(components.get('epsilon_floor', 0.05))
    if mode == 'rar_shell':
        eps = epsilon_rar_shell(gbar_kms2_per_kpc, components['g_dagger_m_s2'], epsilon_floor)
    elif mode in {'radius_proxy', 'rational_radius_proxy', 'test1_radius_proxy'}:
        eps = epsilon_radius_proxy(r_kpc, components['delta_epsilon'], components['r0_kpc'], components['n'], epsilon_floor)
    else:
        raise ValueError(f'Unsupported gate mode: {mode}')
    local_cfg = dict(components.get('local_cutoff', {}))
    family = local_cfg.get('family', 'none')
    params = local_cfg.get('parameters', {})
    eps = apply_local_suppressor_to_epsilon(eps, gbar_kms2_per_kpc, family=family, parameters=params)
    return np.clip(eps, epsilon_floor, 1.0)



def epsilon_from_config(r_kpc, gbar_kms2_per_kpc, gate_config, *, features=None, anchor=None):
    gate_config = dict(gate_config or {})
    mode = str(gate_config.get('mode', 'rar_shell')).lower()
    has_modular = any(key in gate_config for key in ('structure', 'charge', 'local_cutoff', 'shadow_density', 'legacy_compat'))
    if not has_modular and mode == 'rar_shell':
        return epsilon_rar_shell(gbar_kms2_per_kpc, gate_config['g_dagger_m_s2'], gate_config.get('epsilon_floor', 0.05))
    if not has_modular and mode in {'radius_proxy', 'rational_radius_proxy', 'test1_radius_proxy'}:
        return epsilon_radius_proxy(r_kpc, gate_config['delta_epsilon'], gate_config['r0_kpc'], gate_config['n'], gate_config.get('epsilon_floor', 0.05))
    components = build_gate_components(gate_config, features=features, anchor=anchor)
    return epsilon_from_components(r_kpc, gbar_kms2_per_kpc, components)



def cumulative_potential(r_kpc, gtot_kms2_per_kpc):
    r = np.asarray(r_kpc, dtype=float)
    g = np.asarray(gtot_kms2_per_kpc, dtype=float)
    phi = np.zeros_like(r)
    if len(r) > 1:
        for i in range(len(r)-2, -1, -1):
            dr = r[i+1] - r[i]
            phi[i] = phi[i+1] - 0.5 * (g[i+1] + g[i]) * dr
    return phi



def solve_einstein_radius(r_dense_kpc, meff_dense_msun, sigma_crit):
    if not np.isfinite(sigma_crit):
        return np.nan

    def f(rr):
        m = np.interp(rr, r_dense_kpc, meff_dense_msun)
        return m - np.pi * rr**2 * sigma_crit

    vals = f(r_dense_kpc)
    sign = np.sign(vals)
    idx = np.where(np.diff(sign))[0]
    if idx.size == 0:
        return float(r_dense_kpc[int(np.argmin(np.abs(vals)))])
    i = int(idx[0])
    return float(optimize.brentq(f, float(r_dense_kpc[i]), float(r_dense_kpc[i+1])))
