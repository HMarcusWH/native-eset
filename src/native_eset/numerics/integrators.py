"""Reference Simpson quadrature with an explicit refinement/convergence contract.

This is a simple control quadrature, not a coupled ESET stiff/DAE solver.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Callable


class NumericalNonconvergence(ArithmeticError):
    pass


@dataclass(frozen=True)
class QuadratureResult:
    value: float
    coarse: float
    absolute_change: float
    steps: int


def simpson(f: Callable[[float], float], a: float, b: float, n: int) -> float:
    if type(n) is not int or n < 2 or n % 2 or n > 131072:
        raise ValueError("Simpson steps must be even, 2..131072")
    if not all(isfinite(x) for x in (a,b)) or b < a:
        raise ValueError("finite bounds with b >= a required")
    if a==b:return 0.0
    h=(b-a)/n
    total=f(a)+f(b)
    for k in range(1,n):
        total+=(4 if k%2 else 2)*f(a+h*k)
    output=h*total/3
    if not isfinite(output):
        raise NumericalNonconvergence("nonfinite integral")
    return output


def refined_simpson(f: Callable[[float],float], a: float,b:float,
                    *, n:int=64, absolute_tolerance:float=1e-7)->QuadratureResult:
    if not isfinite(absolute_tolerance) or absolute_tolerance<=0:
        raise ValueError("positive finite error tolerance required")
    coarse=simpson(f,a,b,n)
    fine=simpson(f,a,b,2*n)
    delta=abs(fine-coarse)
    if delta>absolute_tolerance:
        raise NumericalNonconvergence(f"not converged: abs refinement difference {delta} exceeds {absolute_tolerance}")
    return QuadratureResult(fine,coarse,delta,2*n)
