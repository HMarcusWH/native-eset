"""Fail-closed signed label migration for the historical K180 S0 diagnostics.

The archived v1 key named `source_float_S0_at_Rmax_minus_exact_K180...`
actually encloses K180 - S0. Do not silently reinterpret historical bytes.
An explicitly named corrected field is -(K180-S0), with interval endpoints
reversed, and the archival legacy field is retained for reproducibility.
"""

def source_return_minus_k180_from_legacy(legacy):
    if (not isinstance(legacy, (list, tuple)) or len(legacy) != 2 or
            any(type(v) is not int for v in legacy) or legacy[0] > legacy[1]):
        raise ValueError('expected a sorted two-integer historical micro-Msun interval')
    return [-legacy[1], -legacy[0]]
