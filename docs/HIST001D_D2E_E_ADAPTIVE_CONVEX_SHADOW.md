# HIST-001D/D2e-E — adaptive convex geometry bounds for exact discrete shadow mass

**Date:** 30 October 2026. **Scientific ceiling:** independently bounded *discrete nodal, fixed-aperture* spherical shadow-cylinder mass only. No certified upstream density law, baryonic q_eff, global Einstein-root count, physics Weyl field or independent observational validation.

## Input identity and positive result from D2e-D

The frozen March historical source lock SHA-256 is `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` for 46 original files plus three negative records. The source's already fitted six SWELLS development lenses retain their **historical 6/6** 180-point regression. The distinct unrefitted D2d full structured finite-domain projection retains **3/6** on all seven radial-density grids.

D2e-D [PR #24](https://github.com/HMarcusWH/native-eset/pull/24) source-locks an exact-rational enclosure for **30 selected fixed apertures**, using positive shell monotonicity. Its observed maximum relative enclosure width was `0.0005918717008142001` (0.0592%), and the largest certified relative Gauss24 projection difference upper was `0.0003056544838269976` (0.0306%). Neither certifies the D2e-B `1e-6` full-radius mass-error assumption or any root topology.

D2e-E is a new numerical algorithm identity that tightens the same finite **piecewise-linear sampled density** integral. Unlike a post hoc numerical grid-difference, the reported width is a directed enclosure of a precise mathematical object. Only two fixed trial radii per development lens are evaluated (observed Einstein radius, source-locked D2d 11,520-grid root), each passed through the unchanged floating baryonic `q_eff(R)` map. Thus 12 apertures are tested, not all possible radii.

## Mathematical kernel: exact convex geometry

With exact binary64-to-rational input nodes and a fixed exact-as-binary64 effective aperture `A`, finite shadow cylinder mass is

```
M(A)/(4*pi) = integral[a,A] rho(r) r^2 dr
            + integral[A,b] rho(r) g(r,A) dr
g(r,A) = A^2*r/(r + sqrt(r^2-A^2)), r >= A.
```

Every inner mass cell is integrated **exactly** as a polynomial in rational arithmetic because the density is the frozen piecewise-linear interpolation. On each outer cell, `g(r,A)` is positive, decreasing and strictly convex for `A>0`, `r>A`.

Set `t=A^2/r^2` between 0 and 1. Direct differentiation yields

```
g''(r,A) = 2 - (2-3*t)/(1-t)^(3/2).
```

For `t >= 2/3`, this is positive. For `0<t<2/3`, positivity follows from `h(t)=2(1-t)^(3/2)-(2-3t)`, where `h(0)=0` and `h'(t)=3(1-sqrt(1-t))>0`. This is an analytical mathematical inequality; no sampling or estimated Lipschitz constant is needed.

Convexity provides an exact **upper chord** through outward-bounded cell-endpoint values of `g`, and an exact **lower tangent** at the cell midpoint. The lower tangent's derivative is enclosed by exact integer-isqrt square-root bounds; derivative-direction choices are adjusted for left versus right half because `r-mid` changes sign. Both chord and tangent are linear in radius, as is the source interpolated density. Their product is a quadratic and is integrated exactly as a rational polynomial. The nonnegative integral also permits clamping a negative lower tangent integral to zero without invalidating the lower bound.

The proof kernel recursively subdivides the outer shell with largest candidate interval width (the heap ordering is **only a heuristic**, not a mathematical step). Crucially, after each batch of 256 refinements, it recomputes both total bounds **from all active cells** using directed 70-digit Decimal contexts. Old interval contributions are not subtracted using potentially unsound rounding. Pi is enclosed via the rational alternating Machin-series proof inherited from D2e-D. The returned interval remains valid whether or not the precision target is achieved.

## Fixed numerical protocol and controlled failure

- Frozen source radial grid: 11,520 points over [0.02,120] kpc
- Fixed aperture roles: observed Einstein radius and D2d high-grid root, each with original `q_eff`
- Discrete-integral interval target: `relative_interval_width_upper <= 1e-8`
- Maximum adaptive splits: 16,384; check after every 256
- Directed decimal precision: 70 digits; integer square-root precision: 88 bits
- Non-success result: `VALID_ENCLOSURE_BUT_TARGET_NOT_MET` with actual bounds, **never a fabricated certified target**
- Target success result: `TARGET_CERTIFIED_FOR_FROZEN_DISCRETE_SHADOW`, not an Einstein root or physical provider certificate

The new interval is independently compared against the prior D2e-D monotone interval at the **same binary64 aperture**. If it escapes that valid interval, execution refuses the result. The D2c Gauss24 and Gauss48 values are compared with the new interval; their one-sided error bound applies exclusively to this discrete target.

## Reproduction and CI

```bash
python tools/hist001d_d2e_e_adaptive_projection.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_e
python tools/hist001d_d2e_e_adaptive_projection.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_e/receipt.json
```

The runner verifies all 46+3 original source/negative files before and after disposable-copy execution; pins D2e-D and the new kernel source SHA, reports full 12-aperture results, and writes canonical report/receipt/sidecar hashes. Verification reexecutes the original source and recomputes the mathematical bounds in a separate process. Synthetic tests cover exact annulus mass, nonmonotone positive rho, convex tangents/chords, old/new interval containment, explicit budget exhaustion, source mutation and forgery rejection.

The release CI is Ubuntu/Windows × Python 3.10/3.12/3.13, including original HIST-001D/D2b/D2c/D2d/D2e-A/B/C/D regressions, standalone official D2e-E source run+fresh verifier, Ruff, checkout manifest, security checks and built-wheel testing. On successful merge to main, A/B/C/D/E report/receipt triplets are uploaded as reproducibility artifacts; an independently downloaded, checked Drive copy must be archived before advancing the living Drive current-state pointer.

## Remaining mathematical and physical blockers

**D2e issue #19 stays OPEN:** no all-radius interval bound for baryonic masses, the approximate `q_eff(R)` map or the upstream gradient/clipped density continuum; no global uniqueness/root multiplicity including near-tangencies or the unresolved 2% root guard; no bound on physical shadow mass outside [0.02,120] kpc. In particular, even a 1e-8 certified discrete **shadow** mass width at twelve apertures does **NOT** prove D2e-B's assumed 1e-6 bound for **total** mass over all radii.

D3 remains the primary published asymmetric/correlated observational uncertainty and IMF-likelihood lane; D4 requires a genuinely disjoint preregistered blinded holdout; D5 requires common sourced metric/stress-energy and physical Weyl lensing; HIST-001B original accelerated historical RangeFinder/RNG/600 and HIST-001E current-theory equivalence are separately unresolved.

**No promotion:** `global_error_bound_established=false`, `root_uniqueness_mathematically_certified=false`, `d2e_b_all_radius_mass_assumption_proved=false`, `physical_provider_admitted=false`, `physical_weyl_lensing_derived=false`, `new_holdout_scored=false`, `native_v172_equivalence_proved=false`, `empirical_validation=NOT_ESTABLISHED`.
