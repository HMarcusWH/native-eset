"""Independent GR + Lambda-CDM reference control. NOT a Native ESET prediction."""
from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class FlatGRLambdaCDM:
    omega_r: float = 0.0
    omega_m: float = 0.3
    omega_lambda: float = 0.7

    def __post_init__(self) -> None:
        x = (self.omega_r, self.omega_m, self.omega_lambda)
        if any(not isfinite(v) or v < 0 for v in x):
            raise ValueError("Nonnegative finite density fractions are required")
        if abs(sum(x) - 1.0) > 1e-12:
            raise ValueError("Flat control requires Omega_r + Omega_m + Omega_Lambda = 1")

    def E(self, z: float) -> float:
        if not isfinite(z) or z < 0:
            raise ValueError("This reference control accepts finite z >= 0 only")
        one_plus_z = 1 + z
        return sqrt(self.omega_r * one_plus_z ** 4
                    + self.omega_m * one_plus_z ** 3 + self.omega_lambda)
