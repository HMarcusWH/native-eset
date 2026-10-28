from __future__ import annotations
import numpy as np
from scipy import integrate
from .constants import C_KMS, G_KPC_KMS2_MSUN, FOUR_PI, MPC_IN_KPC

class FlatLCDM:
    def __init__(self, H0: float = 70.0, Om0: float = 0.3):
        self.H0 = float(H0)
        self.Om0 = float(Om0)
        self.Ode0 = 1.0 - self.Om0

    def E(self, z):
        z = np.asarray(z, dtype=float)
        return np.sqrt(self.Om0 * (1.0 + z)**3 + self.Ode0)

    def comoving_distance_mpc(self, z: float) -> float:
        if z <= 0:
            return 0.0
        integral, _ = integrate.quad(lambda zp: 1.0 / float(self.E(zp)), 0.0, float(z), epsabs=1e-8, epsrel=1e-8)
        return (C_KMS / self.H0) * integral

    def angular_diameter_distance_kpc(self, z: float) -> float:
        return self.comoving_distance_mpc(z) / (1.0 + z) * MPC_IN_KPC

    def angular_diameter_distance_between_kpc(self, z1: float, z2: float) -> float:
        if z2 <= z1:
            return 0.0
        dc = self.comoving_distance_mpc(z2) - self.comoving_distance_mpc(z1)
        return dc / (1.0 + z2) * MPC_IN_KPC

    def sigma_crit_msun_per_kpc2(self, z_lens: float, z_src: float) -> float:
        Dd = self.angular_diameter_distance_kpc(z_lens)
        Ds = self.angular_diameter_distance_kpc(z_src)
        Dls = self.angular_diameter_distance_between_kpc(z_lens, z_src)
        if Dd <= 0 or Ds <= 0 or Dls <= 0:
            return np.nan
        return (C_KMS**2 / (FOUR_PI * G_KPC_KMS2_MSUN)) * (Ds / (Dd * Dls))
