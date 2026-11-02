# HIST-001D — source-defined smooth shadow-mass derivative versus March 180-node finite differences

**2 November 2026 | v1 | NONPROMOTING DIAGNOSTIC + CONDITIONAL TAYLOR ERROR LEMMA**

This result compares the *original March* `mass_difference_gradient` 180-grid density samples against an explicitly new **analytic-derivative interpretation of the unchanged source's acceleration-equivalent mass function**, at the same frozen radii and parameters. No 11,520-node D2d replacement shadow data are used. This is not a new physical Weyl density, an ESET v1.7.2 provider, an all-radius numerical error certificate, a historical off-grid solver result or an independent observational test.

## Source and immutable identity

The parent archive is `inputs/frozen_source_parent.zip`, SHA-256 `82a840767c61e1b6a838bbf3cf105d1b4ff5b854a883dfacd219e8e2b1bb67bf`. It nests the original source ZIP SHA `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e`, the original 46+3 composite SHA `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`, six stored 180-node source arrays and negative controls. Producer and independent verifier reopen the original ZIP and recheck all 46 source files and 3 negative controls. They do not edit the original files.

The original 180-node H array for each historical fitted development lens is reassembled **bitwise** from the stored March B,D,S and Sigma target (1,080 nodes). Separate actual source function replay of the stored shadow ρ agrees with the prior source-capture values within 2e-14 relative error, permitting 1–2 ULP host/vector variation; this current new run does **not** claim bitwise equality of that density replay.

## A source-defined but previously UNADMITTED continuous mathematical extension

At positive radius `R`, freeze the original model's stored scalar parameters as exact real numbers, write `y=R/(2 Rd)` and

\[
 M_{\rm bar,acc}(R)=M_b\frac{R^2}{(R+a)^2}+M_d\,y^3\,[I_0(y)K_0(y)-I_1(y)K_1(y)].
\]

This follows directly from the historical `J2141BaryonicModel.bulge_v2`, `disk_v2` and `gbar=vbar**2/R`, but is an *acceleration-equivalent* baryonic mass—not the separately projected Hernquist or disk mass. The source's `radius_proxy` gate has

\[
 f(R)=\frac{R^n}{R^n+r_0^n},\quad \varepsilon(R)=1-\delta f(R),\quad
 M_{\rm sh}(R)=M_{\rm bar,acc}(R)\frac{\delta f(R)}{1-\delta f(R)}.
\]

All six source-frozen models satisfy `r0>0`, `n>0`, and `0<delta<=0.95`, so for every finite `R>0`, `0<f<1` and `1-delta<epsilon<1`: the *epsilon floor* is inactive in this **mathematical** continuation. The historical finite sample generator also clips `Mshadow>=0` and the finite-difference density `rho>=0`. Whether any derivative/mass clipping boundaries are inactive at **all real radii** has NOT been certified. This candidate is a proposed smooth branch where the positive mass expression applies, not a ratified new physical source.

For `F=I0 K0-I1 K1`,

\[
 F'(y)=2\left(I_1 K_0-I_0 K_1+\frac{I_1 K_1}{y}\right),\quad
 M'_{\rm bar,acc}=\frac{2M_baR}{(R+a)^3}+\frac{M_d}{2R_d}\left(3y^2F+y^3F'\right),
\]

\[
 f'(R)=\frac{nR^{n-1}r_0^n}{(R^n+r_0^n)^2},\qquad
 M'_{\rm sh}=M'_{\rm bar,acc}\frac{\delta f}{\varepsilon}+M_{\rm bar,acc}\frac{\delta f'}{\varepsilon^2}.
\]

The new diagnostic density is `max(M'_sh/(original_stored_FOUR_PI*R**2),0)` at the ORIGINAL 180 radii only. Two independent numerical implementations use distinct SciPy Bessel derivative APIs; an independent 55-digit direct `mpmath.diff` check differentiates the entire Bessel-defined mass formula at 5–7 selected original knots per lens, without importing the producer's derivative routine. This checks the algebra numerically but is **not rigorous interval evaluation** of Bessel truncation/roundoff over a continuum.

## Recorded diagnostic: large first-bin gradient artefact

The original `np.gradient(...,r)` uses a one-sided secant at the first source radius 0.02 kpc; the source mesh next node is about 0.690 kpc away. The secant averages the source mass derivative over that wide interval and is not the local derivative at 0.02 kpc. Direct high-precision derivative evaluations at that original point show these *approximate* ratios (original frozen grid density / new smooth-formula density):

| Fitted lens | Source / smooth density at first node | Original source first-crossing PL root (kpc) | Alternative ANALYTIC-DENSITY replacement sampled root (kpc) | Largest absolute source/alternative H knot change (billion M_sun) |
|---|---:|---:|---:|---:|
| J0822+1828 | 6.80 × 10^6 | 1.829169 | 1.806324 | 0.669 |
| J0915+4211 | 7.72 × 10^6 | 1.408720 | 1.401946 | 0.846 |
| J0930+2855 | 11.33 × 10^6 | 4.665504 | 4.619325 | 1.299 |
| J1021+2028 | 4.32 × 10^6 | 1.142704 | 1.140058 | 0.174 |
| J1111+2234 | 10.84 × 10^6 | 3.956502 | 3.953530 | 0.239 |
| J1135+3720 | 7.83 × 10^6 | 2.200751 | 2.194711 | 0.312 |

The alternative reuses original March `K180` projector, frozen B/D, original 120-angle disk and q-dependent circularized aperture, and changes **only** the 180 radial shadow-density values from a source finite difference to the above analytical derivative. All other original numeric results and 6/6 historical development identities remain unchanged in their original artifacts. The alternative is a **different numerical diagnostic**, not a retuned model, a certified new original root result or a held-out score. All six alternative *sampled* H arrays happen to have one sign change; that observation proves no off-grid/root-topology theorem.

## Exact conditional finite-difference error lemma (source curvature bounds MISSING)

Take an actual smooth scalar source `M(R)` that is C^2 at boundaries and C^3 on interior neighboring cell unions. Let `h_-=r_i-r_(i-1)>0`, `h_+=r_(i+1)-r_i>0`. For the exact-real version of the historical `np.gradient` three-point nonuniform formula,

\[
 D_i=\frac{h_+}{h_-+h_+}\frac{M_i-M_{i-1}}{h_-}+\frac{h_-}{h_-+h_+}\frac{M_{i+1}-M_i}{h_+}.
\]

Taylor's theorem with integral remainder yields

\[
 |D_i-M'(r_i)|\le\frac{h_-h_+}{6}\sup_{[r_{i-1},r_{i+1}]}|M'''|.
\]

At the first and last nodes, the source uses one-sided order-one differences, with

\[
 |D_0-M'(r_0)|\le\frac{h_0}{2}\sup_{[r_0,r_1]}|M''|,
 \quad |D_{179}-M'(r_{179})|\le\frac{h_{178}}{2}\sup_{[r_{178},r_{179}]}|M''|.
\]

Both inequalities are exact mathematical statements **conditional on obtaining independently valid derivative supremum bounds on the selected source continuation**, which have not been computed. `clip_+(x)=max(0,x)` is 1-Lipschitz and thus preserves the derivative discrepancy inequality when applying the same positive factor `1/(stored_FOUR_PI*r_i^2)` to both sides. The actual source additionally rounds gbar/epsilon/mass, differences, clipping and division in binary64; these require a **separately certified floating point/operation-error allowance**.

The independent exact-`Fraction` synthetic tests show equality of the interior coefficient for a cubic and of the endpoint bound for a quadratic, including uneven source steps. But none of the six original models has certified interval upper bounds on `M''` or `M'''`, nor certified Bessel interval errors. The correct all-real numerical source-gradient verdict is explicitly **`UNRESOLVED_DERIVATIVE_SUPREMA_NOT_CERTIFIED`**, not `PASS`.

## How to replay

From a fresh extracted directory (Python 3.10+, NumPy, SciPy, mpmath, pytest installed), run:

```bash
python src/verify.py --check
python src/verify.py --stage producer
python src/verify.py --stage independent
python src/verify.py --stage qa
python -m pytest -q tests/test_source_free.py
python src/verify.py --check
```

The verifier checks all 46+3 historical source-file pins, original nodal file SHA digests, six per-lens numerical output files, independent high-precision source-derivative comparisons, original byte-locked March H samples, expected three machine result hashes and the self-contained manifest. The producer/independent/QA are executed in isolated child processes. The 18 tamper controls are integrity tests, not new mathematics. No source mutations or external network access are needed.

### Next actual work to reach the March numerical-error theorem

1. Source-select the explicit continuous mass/density branch and all relevant clipping/nonnegativity domains; independently certify Bessel and real-power interval bounds, including `M''` and `M'''` on each original source radius cell.
2. Bound source's actual *binary64* mass, gradient and clipping errors against that branch; then propagate node-density errors through positive original `K180` and the q-dependent circularized shadow mass map.
3. Independently bound the frozen K180 bulge/disk projection and `Sigma_crit` numerical errors against ONE common source continuum and establish **H and derivative/variation** bounds. Mere uniform H closeness is insufficient for uniqueness.
4. Only after complete source-compatible bounds consider original continuum root isolation, physical Weyl/Native v1.7.2 same-action transport, and D3/D4 independent observational tests.

Historical Set A fitted 6/6 versus the distinct D2d numerical 3/6 remain different identities. No physical provider, empirical validation, no-CDM cosmology, production scoring, external peer review or Theory-State graph v0.16.39 change is implied.
