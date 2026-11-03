# HIST-001D — Original March Bessel → mass → nonuniform gradient → clipped density → frozen K180

**3 November 2026 · historical six-lens source conditional · mathematical candidate · NONPROMOTING.**

## Exact scope and locked source

- Historical original source: `swells_pack_v2/solv/{baryons.py,dmalane.py,shadow_density.py,run_swells_setA_p_c13a1d.py}` from original 46-file ZIP SHA-256 `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e`. Original 46+3 source/negative-control composite SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
- Original six source-frozen 180×8 binary64 node arrays, positive original K180 trapezoid weights and exact original source scalar parameters are nested in the authenticated protected saturation v1r1 ZIP (SHA-256 `99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce`). Never substitute D2d 11,520 nodes.
- Newly captured output from **the exact original source functions** on the currently recorded NumPy/SciPy runtime: six binary64 `Mshadow` arrays (protected only), obtained from source `gbar`, `epsilon_radius_proxy`, `meff-mbar`, and `np.clip`, followed by `np.gradient`, source FOUR_PI division and nonnegative clipping. The exact 1,080 stored `rho_S` binary64 results are reproduced **bit-for-bit**. Every stored source mass, its gradient and clipped density is positive; source epsilon is strictly above the floor at every node.
- A *separate* mathematical continuation `M_*(r)` is the exact-real analytic acceleration-equivalent mass formula with unchanged source binary64 parameters and Bessel combinations. Its use does not select a physical density, Weyl potential or current ESET v1.7.2 model.

## Distinct mathematical objects, not interchangeable

For source-frozen radii `r_i`, define the source's captured float masses `m_i^float` as **exact dyadic rationals**. Set

\[
  d_i^{\rm src}=C_{4\pi,\rm stored}r_i^2\rho^{\rm stored}_{S,i},\qquad
  D_i[m]={\rm exact\ nonuniform\ three\ point\ gradient\ of\ nodal\ }m,
\]

using one-sided first/last stencils and the same 3-point interior nonuniform stencil as `numpy.gradient` (but here evaluated exactly). The two nonnegative finite-node K180 radial projections are

\[
 Q_{\rm src}(A)=\sum_i w_i\,d_i^{\rm src}\,\phi_A(r_i),\quad
 Q_{\rm float\,mass}(A)=\sum_i w_i\,D_i[m^{\rm float}]\,\phi_A(r_i),
\]

where `phi_A(r)=1` for `r<=A` and `1-sqrt(1-A²/r²)` otherwise. For **every real aperture A>=0** on the original finite source support, `0<=phi_A<=1` and the frozen `w_i>0`, hence

\[
 \boxed{\sup_{A\ge0}|Q_{\rm src}(A)-Q_{\rm float\,mass}(A)|
 \le \sum_{i=0}^{179} w_i|d_i^{\rm src}-D_i[m^{\rm float}]|=:E_{\rm round}.}
\]

The new independent checker uses manual IEEE754 decoding and an algebraically distinct nonuniform slope formula. It verifies the source-stored `rho_S`, source-replayed `m_i^float`, all 180 slope differences and the exact fractional weighted sum. This is a **fixed-dataset a posteriori numerical decomposition**, not a general floating-operation theorem.

The original prior 512-bit Bessel certificate supplies `b_i` for `|d_i^{src}-D_i[M_*(r_j)]|<=b_i` at **all 180 frozen nodes** (and previous independent 608-bit implementation). Therefore

\[
 \sup_{A\ge0}|Q_{\rm src}(A)-Q_{\rm ideal\,M_*}(A)|\le\sum_iw_i b_i=:E_{\rm prior};
 \quad \sup_{A\ge0}|Q_{\rm float\,mass}(A)-Q_{\rm ideal\,M_*}(A)|\le E_{\rm prior}+E_{\rm round}.
\]

This triangle inference is conservative. It is **not** a quadrature error for `Q` versus an integral through real `r`, nor a physical-root error.

## Exact outward source arithmetic results in solar masses

| Historical fitted development lens | Newly separated `E_round` upper | Inherited `E_prior` upper |
|---|---:|---:|
| J0822+1828 | 0.002669 | 1.072079 |
| J0915+4211 | 0.004786 | 2.390655 |
| J0930+2855 | 0.010360 | 0.540857 |
| J1021+2028 | 0.000692 | 0.271028 |
| J1111+2234 | 0.004623 | 0.729836 |
| J1135+3720 | 0.001328 | 0.721396 |

All values above are upward-rounded integer micro-M☉ ceilings from exact binary64 rational input and/or previously protected interval bounds. No coefficient was refitted. The first new error accounts for stored-rho numerical rounding relative to exact differentiation of the **replayed float mass samples**, not numerical input error in those mass samples themselves.

At each lens's four nodes surrounding the historical sampled crossing, 512-bit original Bessel/gate `M_*` enclosures and a separately implemented 608-bit route **overlap**, and a posteriori source-float `Mshadow - M_*`, source-float baryonic acceleration-equivalent mass minus Bessel `A_*`, and source-float epsilon minus the exact gate are outward enclosed. The individual signed intervals are in the protected JSON, rather than misleadingly rounded prose.

## Why this does not close the actual remaining physical problem

The previously measured fixed-aperture K180 versus selected smooth **continuous projection** discrepancies of 0.21%–1.72%, and the six strictly positive full crossing-aperture band gaps, are much larger than this tiny fixed-input floating-gradient stage. That distinction is a mathematical consequence of comparing different objects (discrete finite-difference stencil versus integral and source model), not evidence that the original historical lenses are physical solutions.

No claim of arbitrary-input SciPy Bessel ulp accuracy; no general platform-portable binary64 theorem; no full original off-grid solver; no physical continuous dark source selection; no D120 original omitted-angle physical error bound; no native action-normalized metric/Weyl provider; no D3/D4 blind validation; no no-particle-CDM cosmology; no theory graph promotion. `physical_provider_admitted=false` and `empirical_validation=NOT_ESTABLISHED` remain locked.

### What remains after this source-step

1. If an **original numerical continuous model** is wanted, define it explicitly independently of the 180-node fitted sampled-root convention, prove the source Bessel and gradient truncation errors on the chosen continuum, and propagate through original radial/angular/circularized projection and full-H variation.
2. Separately derive an **action-authorized physical density and Weyl-lensing map** before any physical strong-lensing claim; the selected mathematical M* continuation is not sufficient.
3. Independent mathematical review of the 512/608-bit Bessel Taylor-envelope implementations remains an assurance dependency; a repeated local replay does not replace it.
