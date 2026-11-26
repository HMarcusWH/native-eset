# HIST-001D — Original March 180-node component-interpolated residual: one-root mathematical candidate

**Date:** 2 November 2026. **Scientific status:** `LOCAL_SOURCE_LOCKED_CONDITIONAL_MATHEMATICAL_CANDIDATE_NONPROMOTING`.

This work deliberately defines **a new exact-real off-grid comparator** from the **original March 180-node recorded source arrays**, rather than supplying an off-grid definition retroactively to the historical solver. The source is SHA-pinned and the six original stored residual arrays are byte-for-byte replay-matched at knots; *no later 11,520-node D2d shadow density is substituted*. All scalar nodes are interpreted as exact IEEE-754 binary64 values before the mathematics.

## Exact target, restricted scope

On the original binary64 radius interval `[0.02,120]` kpc, let `B_PL,D_PL,S0_PL,T_PL` denote piecewise-linear interpolations of the **original March** 180-node `B` projected bulge, `D` omitted-arc 120-angle disk, `S0` raw spherical shadow and `T_i=source_float64(pi*r_i**2*Sigma_crit)` critical target. `q_b,q_d` are the stored historical source scalar floats. Define

\[
q_{\mathrm{PL}}(R)=\frac{q_b B_{\mathrm{PL}}(R)+q_d D_{\mathrm{PL}}(R)}{B_{\mathrm{PL}}(R)+D_{\mathrm{PL}}(R)},\quad A_{\mathrm{PL}}(R)=\min\bigl(120,R/\sqrt{q_{\mathrm{PL}}(R)}\bigr)
\]

\[
H^*_{180}(R)=B_{\mathrm{PL}}(R)+D_{\mathrm{PL}}(R)+S_{0,\mathrm{PL}}(A_{\mathrm{PL}}(R))-T_{\mathrm{PL}}(R).
\]

`H*` is a **new continuous mathematical function**. The original solver calculates its final H only at 180 nodes and selects a first sign-change using linear interpolation. That *other* interpolant, `PL(H_original)`, is not generally identical to `H*`. Nor is `H*` the exact floating routine at arbitrary R, a continuous Hernquist/disk/shadow matter field, the distinct D2d 11,520-node proxy or a physical Weyl lens.

## Conditional mathematical result

Two separately coded exact-rational implementations recover **1,273 strict-sign cells** covering all real R outside six short root corridors: 210, 201, 278, 192, 194, 198 respectively. Every cell is a specified dyadic subdivision of an exact original radius interval. The **independent** verifier reconstructs all cells from their index/path, checks exact contiguous tilings (no gaps, overlaps or dropped source endpoints), and independently computes sound H interval signs from affine core + monotone finite raw shadow.

Each root corridor is explicitly inside an original 180-grid cell and has rigorous `H*(left)>0>H*(right)` and rigorously **negative total H* derivative upper bound**, allowing finitely many nondifferentiable S0 interpolation knots and radius nodes. Thus continuity + IVT + piecewise absolute continuity and strict negative derivative a.e. imply **exactly one real mathematical H* zero in each corridor**. The strict-sign covering excludes all other real zeros/tangencies **for this defined mathematical H* model only**.

The six corridors were subsequently bisected 20 times using **rigorous point enclosures**, producing exact rational root brackets of width `0.06/2^20≈5.722×10^-8 kpc`. The independent checker reconfirms their strict endpoint signs. It also reconstructs the independently recorded original March `PL(H_original)` root from the original two binary64 sign-change samples; each original source PL root lies strictly **to the right** of the new comparator's bracket by a certified positive distance.

| Frozen source lens | Certified H* root bracket (display kpc) | Original March sampled-PL root (display kpc) | Strict lower separation (display kpc) | Independent negative H* derivative upper (billion solar mass/kpc) |
|---|---:|---:|---:|---:|
| J0822+1828 | 1.7842557182–1.7842557755 | 1.8291685754 | >0.0449127999 | -14.913575 |
| J0915+4211 | 1.4023754959–1.4023755531 | 1.4087200113 | >0.0063444581 | -36.245143 |
| J0930+2855 | 4.6242316856–4.6242317429 | 4.6655035358 | >0.0412717929 | -6.553029 |
| J1021+2028 | 1.1305592155–1.1305592728 | 1.1427035157 | >0.0121442429 | -20.735111 |
| J1111+2234 | 3.9536775627–3.9536776199 | 3.9565020834 | >0.0028244635 | -34.859742 |
| J1135+3720 | 2.1813159294–2.1813159866 | 2.2007508694 | >0.0194348827 | -34.354478 |

The original source first-H and derived H* at each source knot differ by **strictly less than 1 solar mass** under a directed exact-rational bound; this is an output-identity check and not a uniform off-grid error theorem. Numeric table displays are never accepted as proof inputs.

## Interval arithmetic and independent method

- Source integrity: parent input ZIP SHA-256 `8178dfb07aa4c070b5f10e7de2c1e4130ffe777efb08d57382f4aae9cfcd4132`, nested original March `v1r1` SHA-256 `0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1`, original archived 46-file ZIP SHA-256 `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e` and original 46+3 composite SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. The second checker independently opens and rehashes original files, negative controls, all six node arrays and original H outputs.
- `B_PL,D_PL,T_PL` are positive/nondecreasing at original nodes; `S0_PL` is nondecreasing. On an original cell, `q_PL=N/P` with N,P positive affine; q is monotone within the cell. The producer uses 56/64/72-bit dyadic directed sqrt bounds. Its conservative cell residual lower/upper uses component monotonicity. Independently, the verifier decodes each binary64 via exponent/mantissa integers and uses the alternative rational sqrt floor `isqrt(n*d)/d`, and combines affine B+D−T as a single exact core.
- The derivative bound is `H*'=B'_PL+D'_PL+S0'_PL(A)A'−T'_PL`. The producer bounds `A'` with the sign-aware exact affine quotient q' and all potential intersected raw-shadow slopes. The separate verifier uses a **less specialized absolute q' bound** and enumerates all shadow intervals touched by the outward aperture band; it independently proves the derivative strictly negative on every root corridor.
- This is mathematical **conditional** evidence pending a human/external proof review. The separate mathematical software verifier is not equivalent to peer review or to a formal proof assistant checking every lemma.

## Reproduction

Run in a fresh unpacked archive directory with Python 3.10+ and NumPy installed (NumPy only for stored source binary64 target reconstruction and historical node correspondence; all interval inequalities use integer/Fraction arithmetic):

```bash
python verify_bundle.py --check
python verify_bundle.py --stage producer
python verify_bundle.py --stage independent
python verify_bundle.py --stage qa
python verify_bundle.py --check
```

The replay must match all three immutable result SHA-256 digests and every member hash. Adversarial QA generates 23 intentional false source/claim/cell/interval objects, independently rehashes each outer object and requires rejection, including an actual corrupted original input ZIP. All source-file SHA locks are checked at runtime; mutated or missing source fails closed. SHA identity and math reproducibility do **not** authenticate real-world physical validity.

## Remaining original-March scientific obligations

The original code only returns the 180-node numerical source outputs; the historic first-root uses `PL(H_original)` on those values, not the above newly defined component-composed `H*`. Their strict root separation **demonstrates off-grid definition sensitivity**, not a measured physical error or a change in ESET law. In particular, a 1 M☉ source-knot discrepancy is NOT a uniform error between the two functions between nodes. An actual common smooth source continuum would still require independently certified K180 projection quadrature, density-gradient/clipping and boundary support, 120-angle omitted arc versus physically selected disk, q-dependent aperture, numerical σ_crit, derivative/variation transfer, and physically sourced Weyl lensing. The six historical fitted Set A 6/6 and independent D2d 11,520-node numerical 3/6 remain distinct. No new D3 covariance, D4 preregistered heldout sample, contemporary Native ESET v1.7.2 action equivalence, no-CDM cosmology, P3 provider, production scoring, empirical validation or Theory-State graph change is claimed. Canonical v0.16.39, CDM retained.
