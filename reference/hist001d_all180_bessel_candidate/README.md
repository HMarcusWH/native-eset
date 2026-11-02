# HIST-001D/D2e — original March 180-node all-node rational Bessel and K180 comparison (NONPROMOTING)

**2 November 2026 · Candidate mathematical/numerical evidence only · independent external mathematical review not completed.**

## 1. Source identity and what is compared

This archive retains the **original unchanged March `reg_v2` 46-source-file/3-negative-control corpus** solely inside its SHA-256-pinned nested parent ZIP (`inputs/frozen_smooth_shadow_gradient_parent.zip`, SHA256 `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`), with source composite SHA256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. The original six × 180 binary64 sampled radius, trapezoid weight, bulge/shadow density and B/D/S0/S components are decoded from that archive and their exact source hashes rechecked. **No D2d 11,520-node regenerated shadow density is introduced.**

The exact *source-frozen mathematical comparison* is between:

- `D_stored,j = C4pi_stored * r_j² * rho_shadow_stored,j`, using only the actual frozen IEEE-754 original March density and stored coefficient;
- `D_ideal,j`, the original 180-radial **nonuniform three-point** finite-difference stencil applied instead to the explicitly defined exact-real smooth acceleration-equivalent shadow mass `Msh*(r)` at the same source radii;
- `Msh*'(r_j)`, its exact-real derivative at those same frozen sample radii.

`Msh*` is **not** an independently derived physical Weyl source or an assertion that the original floating code evaluates it exactly away from its recorded sample points. Its formula is the originally source-aligned Bessel baryonic acceleration-equivalent mass plus frozen radius gate:

```
y = r/(2 Rd)
F(y) = I0(y)K0(y)-I1(y)K1(y)
Mbar_acc(r) = Mb*r²/(r+a)² + Md*y³*F(y)
f(r)=r^n/(r^n+r0^n)
Msh*(r)=Mbar_acc(r)*delta*f(r)/(1-delta*f(r))
```

Every source scalar is interpreted as its original exact stored binary64 rational. All original source rho samples and the selected smooth candidate derivatives are proven strictly positive at their **180 frozen radii per lens**, not continuously at all radii.

## 2. Two separately implemented exact rational checks

`all180_math.py` and `all180_producer.py` use 512-bit outward integer/dyadic intervals, analytic Bessel derivatives, 180-term I/K series, positive tail inequalities, 160-term directed atanh logarithms and Euler's constant enclosed by harmonic/Bernoulli 1024/16 rational bounds. `all180_independent.py` does not import either implementation: it uses an independent 608-bit interval class, manual IEEE-754 bit decoding, an algebraically combined Bessel product, a different 200-term series, independent Euler 2048/18 bounds, and Lagrange coefficients rather than weighted two-secants. Both verify all 46 original files and three negatives.

The Bessel integer-order power series and positive tail controls follow the DLMF formulae, [§10.31](https://dlmf.nist.gov/10.31). The real-positive digamma/Bernoulli remainder sign and first-neglected-term bound follow [DLMF §5.11(ii)](https://dlmf.nist.gov/5.11.ii); `ln` and `exp` are bounded directly by positive/remainder-controlled rational series, not numerical SciPy/mpmath values.

Every original lens has 180 mathematical `Msh*` value and derivative enclosures, 180 rigorously bounded source-versus-ideal-stencil comparisons, and an independently checked integer outward interval containing `D_stored - Msh*'(r_j)`. **The maximum a posteriori source-versus-ideal finite-stencil difference is strictly below 1 M☉/kpc on the original 1,080 stored inputs.** This is not a universal bound on SciPy/NumPy function evaluations for arbitrary input values.

## 3. Propagated all-real frozen-cylinder difference bound

Use exactly the original stored positive trapezoid weights `w_j`, radii `r_j`, and finite-cylinder kernel `k(A,r_j)` with

```
k(A,r) = r²                      for A >= r
       = r*(r-sqrt(r²-A²))       for 0 <= A < r
0 <= phi(A,r) := k(A,r)/r² <= 1
```

The original stored-density and selected smooth-derivative-sampled mathematical **K180** cylindrical projection operators share the same kernel and weights. Because the same stored `C4pi` is used to convert the stored and smooth derivatives to 180-node densities, their difference is exactly

```
Delta_S0_K180(A) = sum_j w_j*(D_stored,j-Msh*'(r_j))*phi(A,r_j)
```

Consequently, for every real 0<=A<=120 kpc,

```
|Delta_S0_K180(A)| <= sum_j w_j * max(|lower_j|,|upper_j|)
```

where `[lower_j,upper_j]` are the independently source-attested rational enclosures of `D_stored,j-Msh*'(r_j)`. This is a rigorous, **conservative all-real** bound between **two defined 180-node K180 mathematical projections**. It does not enclose original floating K-matrix multiplication rounding or any K180-vs-smooth-continuum radial integration error.

A separate tighter **original sampled sign-change-cell** bound uses the original positive B_PL,D_PL baryon masses and exact original `q_b,q_d`, hence `q_eff>=min(q_b,q_d)>0`; for `R` in the sampled crossing cell `[R_i,R_(i+1)]`, the circularized aperture is `A(R)<=min(120,R_(i+1)/sqrt(q_min))`. Rational outward square-root guards (producer 120-bit; independent 184-bit) and the nondecreasing `phi(A,r)` then certify `|Delta_S0_K180(A(R))| <= sum w_j*E_j*phi(Aupper,r_j)` across the entire source crossing cell. This is about a **mathematical source-frozen circularization extension**, not proof of the source's arbitrary-R floating code or complete H-root topology.

| Original fitted development lens | Max source-vs-ideal FD upper (M☉/kpc) | Global all-real K180 difference upper (M☉) | Crossing-cell K180 upper (M☉) |
|---|---:|---:|---:|
| J0822+1828 | 0.061977 | 3,142,927,254 | 1,074,673,662 |
| J0915+4211 | 0.164782 | 4,045,230,322 | 1,168,557,575 |
| J0930+2855 | 0.027883 | 6,222,203,764 | 1,943,508,289 |
| J1021+2028 | 0.018732 | 840,347,482 | 185,204,566 |
| J1111+2234 | 0.049255 | 1,151,993,991 | 189,475,713 |
| J1135+3720 | 0.041915 | 1,516,195,026 | 582,941,267 |

The source original March **fitted development 6/6** remains distinct from D2d regenerated **numerical 3/6**, the mathematical D2d 11,520-node continuum proxy, the source-frozen composed-PL comparator, and the newly sampled smooth-derivative diagnostic. Nothing here changes those tests, their pre-existing observational use, or an underlying ESET field equation.

## 4. Reproduction and bounded stages

First perform `python verify_archive.py` from the clean ZIP extraction. It verifies the entire artifact manifest and the exact parent SHA, not the arithmetic. `python -m pytest -q test_all180_source_free.py` runs 28 standalone synthetic mathematical checks.

For independently replayed data-dependent mathematics (run in separate, bounded stages), use:

```
python all180_producer.py --lens-index 0
python all180_independent.py --lens-index 0
# repeat for --lens-index 1,2,3,4,5; each is independent
python all180_aggregate.py
python crossing_band_bound.py
python crossing_band_independent.py
python all180_adversarial_qa.py
python verify_archive.py
```

Every result JSON is SHA-locked in `MANIFEST_SHA256.json`; a clean replay must reproduce exact bytes. The independent signed node bounds are recomputed, not merely trusted from the producer. The 20 adversarial guards test source identity, rational-claim ceilings, malformed arrays, overwritten scientific status and raw-archive corruption. They are integrity and claim-boundary tests, not 20 separate mathematical proofs.

## 5. Scientific nonclaims and the next real gate

**`physical_provider_admitted=false`; `empirical_validation=NOT_ESTABLISHED`; canonical Theory-State v0.16.39 unchanged.** This is *not* a physical mass density, Weyl metric, source-matched current Native ESET v1.7.2 theory, six-lens heldout validation, no-particle-CDM result, or a physical original March 180×120 error/root-count theorem.

Even after this **entire original 180-node fixed-input comparison**, the remaining gates are: a rigorously selected **continuous physical/smooth source target**, K180 radial-quadrature accuracy against that target, original SciPy/NumPy operation-level error for arbitrary inputs, the original D120 omitted-angle approximation, source q/A and full H derivative/variation propagation. The derived K180 node-substitution ceilings are still too large to transfer original-root uniqueness or observational physical authority. Report an unresolved physical/numerical gate rather than retuning the old six fitted lenses.
