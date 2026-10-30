# HIST-001D/D2e-F — certified shadow-aperture intervals; conditional structured-root guard

**Research software increment, 30 October 2026.** The mathematical guarantee added here is an all-aperture enclosure **for the frozen, finite, nonnegative piecewise-linear shadow density** over each reported aperture band. The bridge from an Einstein-radius interval to a shadow-aperture interval **assumes sound baryonic mass ranges**; this upstream assumption is **not verified or certified** by the historical source.

## 1. Immutable historical identities

Source: SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` (46 March files plus 3 archived negative controls). All six SWELLS Set A cases were development/fitted lenses, not blinded holdouts. Historical original 180/120 fitted 6/6 remains **different** from the unrefitted independent D2d structured-shadow 11,520-grid 3/6. No solver, source, fit, observation, Theory-State authority, physical provider or current Native ESET v1.7.2 field equation is changed.

D2e-D [PR #24](https://github.com/HMarcusWH/native-eset/pull/24) established rigorous *pointwise* finite-nodal shadow cylinder mass intervals; D2e-E [PR #25](https://github.com/HMarcusWH/native-eset/pull/25) refined 12 fixed observed/root apertures to relative interval width below 1e-8 by exact-rational convex geometry and directed accumulation. Neither proves all-R total mass or global root uniqueness. D2e-B's `1e-6` total-mass accuracy assumption is still UNPROVED.

## 2. New unconditional finite-discrete shadow theorem

For a nonnegative 3D density `rho(r)` fixed as exact binary64 nodal values and linearly interpolated on `[0.02,120] kpc`, the cylindrical projected mass

```
M_sh(A) = 4π [
  integral[0.02,min(A,120)] rho(r) r² dr
  + integral[max(A,0.02),120] rho(r) r (r - sqrt(r²-A²)) dr
]
```

is **nondecreasing in A**, since increasing the aperture includes all mass previously included and adds only nonnegative mass. This holds for *every real* `A` between any exact binary64 endpoints `A_lo <= A_hi`. With D2e-E rigorous pointwise intervals `[L(A_lo),U(A_lo)]` and `[L(A_hi),U(A_hi)]`:

```
L(A_lo) <= M_sh(A) <= U(A_hi)  for every A∈[A_lo,A_hi].
```

D2e-F's `certified_shadow_mass_band()` implements precisely this implication and retains both original endpoint proof records. Its returned mass band mixes the true change of mass across aperture with numerical enclosure widths; **a wide mass band is not a quadrature error** and must never be used as a statistical uncertainty.

This part is rigorous only relative to the chosen frozen, finite density interpolant and exact binary64 aperture endpoints. It neither adds nor bounds unmodeled mass outside the source domain or the source-density continuum discretization error.

## 3. Separate CONDITIONAL radius-to-aperture construction

For any radius interval `[R_lo,R_hi]`, the historical frozen baryonic structured map is

```
q_eff(R) = clip[1e-3,1] ((q_b B(R)+q_d D(R))/(B(R)+D(R)))
A(R) = min(120, R/sqrt(q_eff(R))).
```

Assume independently supplied positive mathematical enclosures `B_lo<=B(R)<=B_hi` and `D_lo<=D(R)<=D_hi` genuinely hold **for all R** in that interval. Then the baryon-weighted ratio is fractional-linear in each positive mass variable and attains its minima and maxima on the four rectangular mass corners. Exact binary64-to-rational corner arithmetic gives `q_min,q_max` and

```
min(120,R_lo/sqrt(q_max)) <= A(R) <= min(120,R_hi/sqrt(q_min)).
```

Rational integer-isqrt bounds on the square roots and outward conversion to representable binary64 endpoint apertures ensure this **conditional** interval contains all real `A(R)`, **provided the mass box assumption is true**. The positive-mass corner theorem and outward conversion are mathematical results; the continuous `B(R),D(R)` enclosure is *not* established by the two source-evaluated endpoints, which have unbounded numerical projection error in this protocol. No claim of a certified total-mass or global root residual is permitted.

The new `conditional_normalized_root_residual_band()` combines exact-as-binary64 baryonic endpoint boxes, the certified shadow mass band, exact-as-binary64 critical surface density and rational Machin bounds for pi to construct a formally valid **conditional** enclosure of

```
G(R) = (B(R)+D(R)+M_sh(A(R)))/(π Sigma_crit R²) - 1.
```

Its sign labels are `POSITIVE_UNDER_INPUT_ASSUMPTION`, `NEGATIVE_UNDER_INPUT_ASSUMPTION` or `ZERO_NOT_EXCLUDED_UNDER_INPUT_ASSUMPTION`. They **cannot** certify model root absence, uniqueness, a source-accurate Einstein radius or physical lensing until the baryonic source-input interval assumptions are independently proved.

## 4. Source-backed bounded experiment

The official D2e-F source runner considers the six previously fitted Set A lenses. For each, form the fixed ±2% guard around the previously SHA-pinned D2d 11,520-point root. On those two radii, evaluate original D2c finite bulge/disc cylinder masses (periodic-disc angle integration 1024) and frozen q factors, without refitting. Retain the two exact binary64 endpoint mass values **as conditional box inputs**, not certified continuous bounds. Use exact-rational corner q enclosure to produce an outward binary64 effective shadow-aperture interval. Then source-recreate the exact 11,520-node March density and call D2e-E's adaptive pointwise certified mass evaluator at both aperture endpoints. This bounds the discrete shadow mass at **all apertures within each constructed band**, independent of any additional sample grid.

Store the source input and dependency SHAs, full six-lens guard bands, endpoint proof records, checked original source float-aperture endpoints, conditional normalized residual bounds, schema-tagged nonpromotion claims and source-reexecuted SHA receipts.

```bash
python tools/hist001d_d2e_f_shadow_guard.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_f
python tools/hist001d_d2e_f_shadow_guard.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_f/receipt.json
```

### Verification and strict release requirements

Tests cover exact baryonic q-corners over positive mass rectangles, outward endpoint square-root/float bounds, source-independent synthetic positive nonmonotone densities over an entire real aperture band, conditional sign classifications, invalid datasets, source SHA-46+3 integrity, rehashed-false numerical results, forged physical claims and receipt inventory attacks. CI repeats the full frozen A/B/C/D/E suite and a fresh official F source run plus independent process source reexecution on Ubuntu/Windows × Python 3.10, 3.12 and 3.13. After merging, collect the new A–F receipt artifacts; archive in Bootstrap Drive with exact-byte readback before advancing the living `00_START_HERE` pointer.

## 5. Scientific disposition / open gates

**Certified:** within each reported binary64 aperture band, the finite, exact-nodal piecewise-linear shadow mass lies inside its returned mass envelope for all *real aperture values*.

**Conditionally derived, NOT certified:** the radius/\(q_eff\) mapping and full structured-root residual over the ±2% root guard because the source-evaluated bulge/disc endpoint masses are not independently verified all-R enclosures.

**Still blocked:** original continuum density-gradient and clipping error, full-baryon numerical projection error, global root count (including tangent roots and unknown roots elsewhere), mass outside [0.02,120] kpc, physically sourced same-metric Weyl lensing, SWELLS D3 covariance/IMF, truly disjoint blinded D4 holdout, current Native v1.7.2 action/field transport and HIST-001B accelerated campaign provenance.

No `global_root_uniqueness`, `global_model_numerical_error_bound`, `mass_outside_finite_domain_bounded`, `physical_provider_admitted`, `empirical_validation`, `new_holdout_scored` or `native_v172_equivalence_proved` may be promoted by this PR.
