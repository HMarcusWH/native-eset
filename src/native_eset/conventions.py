"""Unit and coordinate *contracts*, not automatic ESET frame-equivalence claims."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re


@dataclass(frozen=True)
class Unit:
    symbol: str
    # Dimensions (length, mass, time, temperature), integer powers.
    dimensions: tuple[int, int, int, int]
    to_si: str


UNITS = {
    "1": Unit("1", (0, 0, 0, 0), "1"),
    "m": Unit("m", (1, 0, 0, 0), "1"),
    "km": Unit("km", (1, 0, 0, 0), "1000"),
    "s": Unit("s", (0, 0, 1, 0), "1"),
    "yr": Unit("yr", (0, 0, 1, 0), "31557600"),
    "kg": Unit("kg", (0, 1, 0, 0), "1"),
    "K": Unit("K", (0, 0, 0, 1), "1"),
    "m/s": Unit("m/s", (1, 0, -1, 0), "1"),
    "km/s": Unit("km/s", (1, 0, -1, 0), "1000"),
    "m/s^2": Unit("m/s^2", (1, 0, -2, 0), "1"),
    "s^-1": Unit("s^-1", (0, 0, -1, 0), "1"),
    "Pa": Unit("Pa", (-1, 1, -2, 0), "1"),
    "Mpc": Unit("Mpc", (1, 0, 0, 0), "30856775814913673000"),
    "km/s/Mpc": Unit("km/s/Mpc", (0, 0, -1, 0), "1000/30856775814913673000"),
}


def decimal_string(text: str) -> Decimal:
    if (not isinstance(text, str) or len(text) > 128 or
            not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]{1,4})?", text)):
        raise ValueError("all numeric parameters require an explicit decimal string")
    try:
        value = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal: {text!r}") from exc
    if not value.is_finite() or abs(value.adjusted()) > 1000:
        raise ValueError("NaN and Infinity cannot be physical parameter values")
    return value


def compatible_units(source: str, target: str) -> bool:
    if source not in UNITS or target not in UNITS:
        raise ValueError(f"unknown explicit unit pair {source!r}, {target!r}")
    return UNITS[source].dimensions == UNITS[target].dimensions


def normalize_si(value: str, unit: str) -> Decimal:
    if unit not in UNITS:
        raise ValueError(f"unsupported unit {unit!r}; add a reviewed unit contract first")
    factor = UNITS[unit].to_si
    return decimal_string(value) * (decimal_string(factor.split('/')[0]) / decimal_string(factor.split('/')[1])
                                   if '/' in factor else decimal_string(factor))


FRAMES = frozenset({"GR_REFERENCE_FLRW", "NATIVE_V172_EINSTEIN_FIXED_MP",
                    "LEGACY_VARIABLE_F", "HISTORICAL_GEOMETRY_DM_A"})
GAUGES = frozenset({"NOT_APPLICABLE_BACKGROUND", "NEWTONIAN", "SYNCHRONOUS", "COVARIANT_LOCAL"})


def check_convention(frame: str, gauge: str, coordinate: str) -> None:
    if frame not in FRAMES or gauge not in GAUGES:
        raise ValueError("unknown frame/gauge, explicit registration required")
    if coordinate not in {"redshift", "N=ln(a)", "radius_m", "conformal_time", "proper_time"}:
        raise ValueError("unknown evolution coordinate")
    if frame == "GR_REFERENCE_FLRW" and (gauge != "NOT_APPLICABLE_BACKGROUND" or coordinate != "redshift"):
        raise ValueError("the GR control uses redshift and no perturbation gauge")
