# HIST-001D — Source-conditional radial discretization: signed stencil-versus-derivative versus integral decomposition

**Research-only / nonpromoting mathematical candidate · 3 November 2026.** The original March six-lens 180-radius source is retained in frozen source ZIPs; all historical 46+3 source identities and original binary64 radius/weight/density records are checked. This is an algebraic and numerical statement about *one separately selected mathematical continuation* `M_*(r)`, not a new Native ESET field-equation provider or a physical Weyl lens.

## 1. Three different radial operators

Let the original stored exact binary64 radius and nonnegative shadow-density data be `(r_i, w_i, rho_i)`, `i=0..179`, with stored `C4pi`. For real aperture `A>=0`, define `phi_A(r)=1` if `A>=r`, else `1-sqrt(1-A^2/r^2)`. It is continuous, takes values in `[0,1]`, and is nondecreasing in `A`. Define:

- `Q_src(A)=sum_i w_i*C4pi*r_i^2*rho_i*phi_A(r_i)` — the frozen original stored K180 operator with original clipping and stored weights.
- `Q_deriv(A)=sum_i w_i*M_*'(r_i)*phi_A(r_i)` — sampled **exact analytic derivative** of the separately selected smooth historical acceleration-equivalent mass.
- `Q_stencil(A)=sum_i w_i*D_i[M_*(r_j)]*phi_A(r_i)` — exact-real nonuniform three-point/endpoint finite-difference stencil of the analytic mass sampled on the original frozen nodes.
- `P_*(A)=integral_(r_min to r_max) M_*'(r)*phi_A(r) dr` — the *mathematical* continuous radial-cylinder projection, using the same fixed support.

The following is an **exact algebraic identity of mathematical objects**, not a physical theorem:

`Q_src - P_* = (Q_src-Q_deriv)+(Q_deriv-P_*)`.

Further, `Q_src-Q_deriv=(Q_src-Q_stencil)+(Q_stencil-Q_deriv)`.

## 2. What the new packet proves conditionally

The independently audited previous all-180-node 512-bit Bessel certificates provide **signed** integer intervals `[a_i,b_i] M_sun/kpc` enclosing `C4pi*r_i²*rho_i - M_*'(r_i)` at *all original stored radii*. This packet does **not** recreate their Bessel proof; it verifies their exact SHA lineage and integrates those signed intervals with the original stored positive weights. For each aperture band `L<=A<=U`, monotonicity of the *exact finite-cylinder* kernel gives `phi_L(r_i)<=phi_A(r_i)<=phi_U(r_i)`. Thus one may enclose each signed term by the minimum and maximum of the four endpoint products `{a_i phi_L,a_i phi_U,b_i phi_L,b_i phi_U}`, then sum using exact rational arithmetic. Every square-root enclosure is verified by rational squared inequalities.

Six original **source-defined crossing-aperture bands** (obtained by the already-specified mathematical PL-q circularization of their original 180-R crossing cells) are certified in one panel per lens. All six `Q_src-Q_deriv` lower bounds remain positive everywhere on their full bands.

The inherited all-aperture exact-rational node-stencil bounds `|Q_src-Q_stencil|<=E_prior` are respectively `1.072079, 2.390655, 0.540857, 0.271028, 0.729836, 0.721396 M_sun` for the six lenses. Consequently, **the exact analytic mass finite-difference stencil itself**, not merely floating source density arithmetic, satisfies `Q_stencil-Q_deriv>0` across all six source-defined aperture bands.

## 3. Outward integer fixed-aperture results

For the six original 180-node diagnostic apertures (the ones already authenticated in the prior fixed-A certificate), all intervals below are in `M_sun`. Each row is a *signed interval*, not a floating best fit. `Q_deriv-P_*` is obtained by interval subtraction of the independently stored fixed-A `Q_src-P_*` enclosure from the new `Q_src-Q_deriv` bound.

| Lens | `Q_src-Q_deriv` interval | `Q_deriv-P_*` interval | sign of latter |
|---|---:|---:|---|
| J0822+1828 | [338,763,352, 338,763,357] | [-84,454,958, -70,841,855] | negative |
| J0915+4211 | [191,128,392, 191,128,395] | [-25,555,726, -15,861,354] | negative |
| J0930+2855 | [1,139,077,354, 1,139,077,365] | [137,469,823, 224,181,886] | positive |
| J1021+2028 | [48,521,202, 48,521,206] | [-8,348,978, -6,247,471] | negative |
| J1111+2234 | [104,276,981, 104,276,990] | [-40,318,418, -26,531,088] | negative |
| J1135+3720 | [210,917,407, 210,917,414] | [107,124,828, 116,886,135] | positive |

The finite-difference overshoot and radial quadrature remainder **partially cancel** for four lenses but **reinforce** for J0930 and J1135. Neither contribution alone equals the originally reported residual or any physical mass inferred from an independent Weyl solution.

## 4. Whole original crossing aperture bands: positive ideal-stencil bias

The following are conservative *integer floor lower bounds* on `Q_stencil(A)-Q_deriv(A)` throughout the whole original crossing aperture band, including source-aperture knot crossings. All are positive. No unresolved subbands occurred.

| Lens | Lower bound (M_sun) |
|---|---:|
| J0822+1828 | +152,756,855 |
| J0915+4211 | +139,498,208 |
| J0930+2855 | +888,492,444 |
| J1021+2028 | +9,957,512 |
| J1111+2234 | +72,710,901 |
| J1135+3720 | +135,147,377 |

The bound is intentionally conservative, obtained by one interval product box per entire band and subtraction of the independently inherited all-aperture source-versus-ideal-stencil allowance. This source-only code does not use a smoothness argument incorrectly through `A=r_i`; the kernel is monotone even where its derivative is singular.

## 5. Independence, verifiers and status limits

The new producer and the new separate verifier use only standard-library rational arithmetic, no NumPy/SciPy, and no Bessel function evaluation. The verifier **manually decodes binary64**, uses independent integer bisection rather than the producer's integer square-root routine, checks all original radii/weights, recomputes all six point intervals and all whole-band witness boxes, verifies gap-free coverage and the prior fixed-A interval subtraction. This verifies the *new rational aggregation*, not the mathematical correctness of inherited 512-bit Bessel derivative enclosures. The claim guard rejects **39/39** altered identities, bounds, geometry or physical/promotional claims; source-free mathematical test suite passes **22/22** tests.

Original 46+3 composite SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.

Parent upstream float/mass archive SHA-256 `d853e4184a570bb1de508658a53ac83eb2d12244b0b14699c14c314448cac5e5`.

Parent fixed-A continuum archive SHA-256 `54eeec715a8f2b9514b88d7806cef84cb90aea54cdada0e0c11bf9489362051e`.

Parent six-crossing-band archive SHA-256 `cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77`.

**Hard nonclaims:** no arbitrary-real-radius `numpy.gradient` guarantee (the original gradient is discrete); no universal source-offgrid SciPy Bessel ulp certificate; no complete new full-real-`A` signed quadrature error theorem outside the six source bands; no certified physical radial density or same-source Einstein/Weyl/action equation; no true original unsampled continuous lensing root, selected `H_*` uniqueness, D3/D4 blinded test, native sound horizon, no-particle-CDM or complete cosmology claim. Physical-provider admission remains `false`, empirical validation `NOT_ESTABLISHED`, canonical Theory-State v0.16.39 unchanged, all GitHub changes draft/nonpromoting.

**Next independent scientific assurance:** externally reproduce the prior 512/608-bit Bessel and interval proofs with a mathematically different method, certify source selection of a physical continuum from an action and covariant Weyl map, and only then consider physical gravitational lensing or no-refit validation claims.
