# HIST-001D/D2c — independent finite-domain projected-shadow mass and high-grid Cauchy diagnostic

**29 October 2026 · source-locked historical numerical study · noncanonical / nonpromoting.**

## Original identity and what is (not) tested

- Historical model: `LEGACY_ESET3_DM_A_FITTED_STRUCTURED_PROJECTION`, frozen candidate `ra0_gated_geometry_sigmoid_reg_v2`.
- Original March 14 SWELLS/J2141+Set A source lock: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` (46 source/config/data files + three original negative-control records).
- Original source recipes unchanged: `solv/dmalane.py` epsilon/gate, `solv/shadow_density.py` `mass_difference_gradient`, `solv/run_setA_port_cand.py` `_projection_matrix`, `solv/run_j2141_axisym_lens.py` Hernquist and disk geometry.
- **Six existing fitted/development lenses only.** No new observations, independent holdout or original B accelerated producer/600 prechecks.
- **Only the spherical projected shadow-density mass at one fixed effective aperture per lens** is independently integrated here; it is *not* a newly derived gravitational Weyl source/metric solution or a convergence proof of the complete Einstein-radius root.

## Independent integral and mathematical scope

The source forms a clipped nonnegative effective density from a finite-difference derivative of its radial shadow-mass proxy. It projects it over the **finite source domain** [0.02, 120] kpc, using an original radial trapezoid matrix and then circularizes the shadow by baryonic axis-ratio weights.

For a prescribed finite grid density represented by a **piecewise-linear interpolant**, this experiment integrates the *complete spherical cylinder enclosed mass*:

\[
M_{\mathrm{cyl}}(R)=4\pi\left[\int_{0.02}^{\min(R,120)}\rho(r)r^2\,dr+\int_{\max(R,0.02)}^{120}\rho(r)r\big(r-\sqrt{r^2-R^2}\big)\,dr\right].
\]

Inside `r≤R`, the piecewise-linear density times `r²` is a cubic integrated analytically on each cell. Outside, use `t=√(r²−R²)`, so the entire exterior integrand is the numerically stable `ρ(√(R²+t²))·t·R²/(√(R²+t²)+t) dt`. The transformed external integral is evaluated with independently specified **24-point and 48-point Gauss-Legendre quadrature**. A second SciPy `quad` implementation independently integrates each cell, with the same transformation, and reproduces the Gaussian values to floating-point precision on all six 180- and 360-point source fields. The original full `_projection_matrix @rho` is separately reexecuted at those grids and matches the source-equivalent two-knot readback.

**This tests quadrature agreement for a given discrete piecewise-linear density; it does not prove a rigorous upper bound or measure the error between that density and an unknown physical continuous one.** The original radial clip, finite-difference gradient, finite outer domain and fitted constitutive law are all retained, not repaired.

To avoid a moving target as the radial density is refined, each lens uses **one fixed effective aperture** `R_eff = R_observed/sqrt(q_eff_reference)`. The reference `q_eff` uses an independent adaptive finite-domain Hernquist bulge projection and **1024-angle full-periodic** disk mass at the observed radius; a 512-angle screen agrees. This differs deliberately from the original finite-grid-dependent `q_eff(R)` and is a new numerical *comparison convention*, not a source-exact historical output or newly fitted law.

## Seven-grid result (all six historical development lenses)

| Lens | Original 180-point K bias vs independent discrete-density integral | Fixed-density-field reference change 180→360 | Cauchy Δ 2880→5760 | Cauchy Δ 5760→11520 |
|---|---:|---:|---:|---:|
| J0822+1828 | +2.710% | -1.7784% | -0.00438% | -0.00109% |
| J0915+4211 | +3.789% | -1.9068% | -0.00414% | -0.00103% |
| J0930+2855 | +0.931% | -0.2803% | -0.00104% | -0.00026% |
| J1021+2028 | +3.383% | -2.8580% | -0.00461% | -0.00115% |
| J1111+2234 | +0.713% | -0.2262% | -0.00084% | -0.00021% |
| J1135+3720 | +2.116% | -1.0152% | -0.00324% | -0.00081% |

All six original 180-point K-matrix shadow masses are above the independently integrated piecewise-linear density values at the same **fixed** effective radius, with bias from **+0.71% to +3.79%**. These differences arise from radial quadrature / interpolation conventions for the same input density, not a newly inferred missing-mass component.

The independent fixed-aperture projected shadow masses systematically change with the source-density grid. Their latest two relative changes are smaller than **0.05%** for all six lenses, and the largest is **0.00461%** (2880→5760) and **0.00115%** (5760→11520). The 24/48 Gaussian comparison and transformed adaptive SciPy checks are within their 1e−9 relative numerical acceptance tolerance.

An illustrative second-order-tail estimate `|M_11520−M_5760|/3` is recorded but **NOT a mathematical upper bound**, and not a physical prediction uncertainty. This is a **retrospective engineering Cauchy screen** developed after previous 180–2880 exploration, not a third-party preregistration or strict mathematical certification. Passing it only supports local numerical stabilization of one finite-domain proxy value at each fixed observed aperture; it does not certify convergence uniformly in R, the complete structured-shadow mass curve, Einstein-radius root, finite-R cutoff or covariance with stellar mass.

## Diagnostics and claim ceiling

Source-verified code is run from a disposable copy; the original 46+3 byte inventory is checked before and after. Machine output includes every input radial grid, original K mass, independent quadrature mass, 24/48 difference, source K bias, transformed SciPy check on 180/360, Cauchy deltas, zero/negative source density bins, and explicit nonclaim fields. The independent receipt verifier reexecuted all six lenses and all seven radial grids, including numerical and authority checks. Self-rehashed forged numerical rows, provider-claim mutation, altered external hash, unexpected receipt files and unsafe output paths are blocked.

```bash
python tools/hist001d_d2c.py --source-root research/legacy/hist001 --out runs/hist001d_d2c
python tools/hist001d_d2c.py --source-root research/legacy/hist001 --verify runs/hist001d_d2c/receipt.json
```

- Local runner SHA-256: `c28910af318028f72b8710ebbe61f9f31ad3727ce3daa12750fd089620e7bfa4`
- Source-locked local report SHA-256: `5fa473d72b7db7caae742c38e96c553db4c844baa9e571d00e3dca0a378f6d61`
- Local full official receipt SHA-256: `b148a921816e4f5daffe857900295dd385c03a880e5c091c9ae9080378afac9b`
- Local independent check: 10 diagnostic/attack tests passing (the GitHub six-platform CI and any code release remain separate gates).

## Remaining work (do not claim closed)

1. **D2d**: independent full **structured shadow** projected-mass curve and complete numerical critical-radius root solution, uniformly controlled across R with source-justified precision and no refit; quantify coupling to baryonic projection / q_eff(R) and root bracketing. Keep any corrected implementation as a **distinct executable identity** from the original 180-point historical result.
2. **D2e**: distinguish source finite difference / clipping, inner and outer truncation, interpolation assumptions and long-range numerical errors; if possible derive guaranteed error estimates for a precisely defined interpolated finite density, then separate this from model uncertainty.
3. **D3**: published covariance, stellar IMF/M/L correlations, asymmetric observational error definitions and cosmological-distance priors. The original per-lens 2σ denominators are not a joint likelihood.
4. **D4**: select and pre-register a genuinely disjoint, outcome-masked holdout **before** any new outcome scoring, with rights/source and prior-pipeline-contact audit. No target has been selected here.
5. **D5**: a common sourced dynamical/metric and covariant Weyl lensing derivation. Historical equal potentials and the geometry-projection proxy are not that proof.
6. **HIST-001B**: original accelerated producer, RNG schedule and 600 input cases unrecovered; new deterministic 4,000 rows remain a distinct execution identity.

**Authority:** `historical_fitted_development_regression_only=true`; `new_holdout_scored=false`; `physical_weyl_lensing_derived=false`; `native_v172_equivalence_proved=false`; `physical_provider_admitted=false`; `empirical_validation=NOT_ESTABLISHED`; `canonical_theory_state_mutated=false`.
