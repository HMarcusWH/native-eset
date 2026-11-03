# HIST-001D original D120 omitted-seam candidate — mathematical + numerical method audit

NONPROMOTING. The protected archive carries the original SHA-authenticated March data; public GitHub carries **only** these source-only modules, synthetic tests and a scope note.

- `seam_math.py` — two distinct exact-rational exponential interval methods; rigorous endpoint seam bounds and analytic positivity/monotonicity identity.
- `source_seam_replay.py` — data-dependent original frozen binary64 D120, q/S and H replay, plus a newly defined *counterfactual* periodic seam. It uses protected SAT v1r1 and full H v1r1 parents; never reruns a refit.
- `verify_seam.py` — independent positive-series exponential bounds, source identity/percent audit and independent counterfactual numerical reconstruction.
- `adversarial_seam.py` — reject both semantic overclaims and source-specific tampering.
- `verify_release.py` — ZIP manifest and clean-input reproducibility checker.
- `tests/historical/test_hist001d_d120_seam_source_free.py` — 26 tests, no protected parents required.

Original angular routine uses 120 points but integrates 119 trapezoid intervals because of `endpoint=False`. The alternative closure is source-defined, with frozen step `h=theta[1]-theta[0]`, and is **not** an exact full-azimuth integral or a physical model.

Protected replay:

```sh
python reference/hist001d_d120_seam_candidate/source_seam_replay.py \
  --saturation inputs/saturation_v1r1.zip --finite-h inputs/full_h_v1r1.zip \
  --out results/recomputed.json
python reference/hist001d_d120_seam_candidate/verify_seam.py \
  --saturation inputs/saturation_v1r1.zip --finite-h inputs/full_h_v1r1.zip \
  --receipt results/recomputed.json
python -m pytest -q tests/historical/test_hist001d_d120_seam_source_free.py
```

All new root corrections are *diagnostics of the new stencil* only. The original 6/6 development fit is not D3/D4 validation. No physical provider, no full original off-grid error theorem, no cosmology validation.
