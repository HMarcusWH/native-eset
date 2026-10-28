from __future__ import annotations
import numpy as np
from scipy import special
from .constants import G_KPC_KMS2_MSUN

def parse_pm_string(value):
    s = str(value).strip()
    if s in {"", "nan", "None"}:
        return np.nan, np.nan, np.nan
    s = s.replace("−", "-")
    if "±" in s:
        c, e = s.split("±", 1)
        return float(c), float(e), float(e)
    m = __import__("re").match(r"^\s*([+-]?\d*\.?\d+)\+([+-]?\d*\.?\d+)/-([+-]?\d*\.?\d+)\s*$", s)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    return float(s), np.nan, np.nan

class J2141BaryonicModel:
    def __init__(self, bulge_mass_msun, bulge_re_kpc, disk_mass_msun, disk_r50_kpc):
        self.bulge_mass_msun = float(bulge_mass_msun)
        self.bulge_re_kpc = float(bulge_re_kpc)
        self.disk_mass_msun = float(disk_mass_msun)
        self.disk_r50_kpc = float(disk_r50_kpc)
        self.bulge_scale_kpc = self.bulge_re_kpc / 1.8153
        self.disk_scale_kpc = self.disk_r50_kpc / 1.67835

    def bulge_v2(self, r_kpc):
        r = np.asarray(r_kpc, dtype=float)
        a = self.bulge_scale_kpc
        with np.errstate(divide="ignore", invalid="ignore"):
            v2 = G_KPC_KMS2_MSUN * self.bulge_mass_msun * r / (r + a)**2
        return np.where(r > 0, v2, 0.0)

    def disk_v2(self, r_kpc):
        r = np.asarray(r_kpc, dtype=float)
        Rd = self.disk_scale_kpc
        y = r / (2.0 * Rd)
        I0 = special.i0(y)
        I1 = special.i1(y)
        K0 = special.k0(np.where(y == 0, 1e-12, y))
        K1 = special.k1(np.where(y == 0, 1e-12, y))
        term = I0 * K0 - I1 * K1
        v2 = G_KPC_KMS2_MSUN * self.disk_mass_msun / (2.0 * Rd) * (y**2) * term
        return np.where(r > 0, v2, 0.0)

    def total_vbar(self, r_kpc):
        return np.sqrt(np.clip(self.bulge_v2(r_kpc) + self.disk_v2(r_kpc), 0.0, None))
