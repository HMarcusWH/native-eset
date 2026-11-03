# HIST-001D — Source-defined historical March180 complete-H bridge

**3 November 2026 · DRAFT / SOURCE-CONDITIONAL MATHEMATICAL CANDIDATE · NONPROMOTING**

This result is built on source-locked historical March `reg_v2` 180×120 Set A data and on the previous *conditional selected mathematical smooth mass* \(M_*(r)\). It does **not** authorize a physical Native ESET v1.7.2 Weyl/lensing provider, empirical validation, no-particle-CDM cosmology, or the original floating SciPy/NumPy solver's arbitrary-input error. The historical six lenses were development/fitted lenses. All protected original arrays and parent archives remain outside public GitHub.

## 1. Three different root objects that must not be conflated

The original March routine evaluates arrays at 180 radii and returns its root by **linear interpolation across a sign change of the sampled final residual**. For a new off-grid radius the source did not evaluate the underlying continuous forward operator at each possible real radius. A root of the nodal-residual piecewise-linear interpolant is therefore not automatically a root of the component-wise off-grid model.

Define a *new, explicitly named, source-consistent mathematical finite extension* using exactly the original stored binary64 nodal values as rationals:

\[
B_{\rm PL}(R)=\operatorname{PL}(B_j)(R),\qquad D_{\rm PL}(R)=\operatorname{PL}(D_j)(R),
\]
\[
q(R)=\frac{q_bB_{\rm PL}(R)+q_dD_{\rm PL}(R)}{B_{\rm PL}(R)+D_{\rm PL}(R)},\qquad
A(R)=\min(120,R/\sqrt{q(R)}),
\]
\[
H_{\rm finite}(R)=B_{\rm PL}(R)+D_{\rm PL}(R)
+\operatorname{PL}(S_{0,j})(A(R))-\pi_{\rm source}\,\Sigma_{\rm source}R^2.
\]

The `min(120, ...)` saturation of the `S0` lookup is built into `np.interp`'s right endpoint convention; the crossing cells are unsaturated. `PL(S0)` is an interpolation of the original **source-returned 180 spherical shadow mass values**. This is *not* a fresh K180 quadrature at arbitrary off-grid R, and not the continuous physical Hernquist/source/Weyl model.

Define separately the same-geometry **selected mathematical smooth shadow** comparison:

\[
H_*(R)=B_{\rm PL}(R)+D_{\rm PL}(R)+P_*(A(R))
-\pi_{\rm source}\Sigma_{\rm source}R^2,
\quad P_*(A)=\int_{r_{\min}}^{120}M_*'(r)\phi(A,r)dr.
\]

The exact source `pi` uses stored original `4*np.pi` divided by four (the same binary64 pi), and `Sigma` is the stored original lens-specific binary64 value. No retuning occurs. Prior `q` proofs require positive original B and D and verify strict monotonicity of A(R) for the piecewise-linear B/D extension across all 179 original source cells.

## 2. Global exactly-one-root theorem for the *finite mathematical extension*

For each original source R cell away from its single archived sampled crossing, the signed `H_finite(R)` is bounded on a dyadic subdivision by monotonic original B and D, monotonic `S0`, strictly increasing q-circularized A, and increasing quadratic target. The full original 0.02–120 kpc support has **1,150** individually checked sign-excluding non-crossing subbands with zero gaps or unresolved cells, using exact-rational arithmetic and directed rational square roots.

Each of the six crossing cells has a source-conditional exact derivative upper bound, split at source A-knot crossings as needed. The eight crossing-cell derivative leaves are **strictly negative**. At the endpoints of each crossing cell, H_finite is strictly positive on the left and negative on the right. Thus, by the intermediate value theorem and strict decrease, the defined H_finite has exactly **one** real root on the *entire original source 0.02–120 kpc domain* for each lens. These are precise mathematical claims for the explicitly defined finite PL extension, not the original floating off-grid source's unknown behavior.

| Lens | Unique finite PL-extension root (kpc, rounded navigation) | Reported sampled-root interpolant (kpc) | H_finite at reported sampled radius (M☉, outward integer interval) |
|---|---:|---:|---:|
| J0822+1828 | 1.8651737371 | 1.8291685754 | [695094513, 695094514] |
| J0915+4211 | 1.4226626334 | 1.4087200113 | [353552261, 353552262] |
| J0930+2855 | 4.6650247429 | 4.6655035358 | [-11295391, -11295390] |
| J1021+2028 | 1.2022175721 | 1.1427035157 | [1555063655, 1555063656] |
| J1111+2234 | 3.9662424385 | 3.9565020834 | [388105089, 388105090] |
| J1135+3720 | 2.2239125056 | 2.2007508694 | [683568794, 683568795] |

The precise root brackets in `results/full_H_finite_receipt.json` are rational and have width below \(4\times10^{-11}\) kpc. This source-level interpolation distinction is a *numerical-model identity question*, not evidence for or against a physical theory.

The independent witness-arithmetic checker recomputes every global signed interval and derivative upper bound with an **alternative exact integer rational-square-root enclosure** (`isqrt(n*d)/d`), verifies exact interval coverage/adjacency and unique root brackets, and returns 1,150 signed subbands plus eight derivative subbands PASS. It is not an independently reconstructed physical source or a second Bessel engine.

## 3. Transfer the previous whole-band shadow inequality into full H

The previously source-locked whole-band result states \(Q_{\rm March}(A)-P_*(A)>L_i\) for each original crossing-cell aperture band. On each **aperture source cell**, \(Q_{\rm March}(A)\) is convex because its original frozen radial weights and clipped densities are nonnegative and the shell cylinder kernel has positive second derivative up to saturation. Therefore the chord of its 180 source-node values lies above Q(A) within each aperture cell. Earlier independently replayed source-node exact enclosures establish

\[
\left|S_{0,j}^{\rm source}-Q_{\rm March}(r_j)\right|<1\,M_\odot
\quad(\hbox{all 180 source nodes}).
\]

Consequently, on the full original crossing-cell aperture band,

\[
\operatorname{PL}(S_{0,j}^{\rm source})(A)-Q_{\rm March}(A)>-1\,M_\odot,
\]

and **with the same B, D, q and target**,

\[
\boxed{H_{\rm finite}(R)-H_*(R)>L_i-1\,M_\odot}
\]

for every real R in that source crossing cell. The six transferred lower thresholds are +21,805,298, +4,150,092, +103,251,441, +1,489,372, +9,140,999, and +30,566,151 \(M_\odot\). No cancellation with the baryonic or target terms is possible **within these two specifically named full-H definitions**, because they are shared identically; this is not a statement about an independently chosen physical geometry or continuous baryonic source.

## 4. Smooth selected continuum: existence and root ordering, not uniqueness

The previous all-real selected \(M_*'(r)>0\) source-conditional Bessel/interval audit allows monotonic transport from outward rational enclosures of \(A(R)\). The fixed-angle-cusp-free integral implementation then supplies direct intervals for \(P_*(A)\) at both crossing-cell endpoints, yielding the following full-H outward integers:

| Lens | H_*(R_left) **lower** (M☉) | H_*(R_right) **upper** (M☉) |
|---|---:|---:|
| J0822+1828 | +6,692,748,885 | -3,851,090,919 |
| J0915+4211 | +632,972,313 | -20,482,325,555 |
| J0930+2855 | +12,868,952,515 | -3,921,073,442 |
| J1021+2028 | +9,385,037,763 | -4,723,915,419 |
| J1111+2234 | +20,753,598,305 | -3,263,472,747 |
| J1135+3720 | +5,306,756,965 | -17,877,442,188 |

Thus each H_* has **at least one** zero inside its original source crossing cell by continuity. Further, H_* lies strictly below H_finite throughout the whole cell. Since H_finite strictly decreases and vanishes exactly once at \(R_{\rm finite}\), the selected H_* has no root at or to the right of \(R_{\rm finite}\) within the cell. Therefore **at least one H_* root lies strictly to the left of R_finite**, but **uniqueness or exact positions for H_* are not established**. Potential H_* roots in other source cells are not excluded.

The fixed-source selected Bessel mass law is a **mathematical historical continuation**, not a physical Native ESET 4.0 matter source. The endpoint interval engine is inherited from the earlier source-conditional code family. Independent formal mathematical review, a separately implemented Bessel interval engine, original off-grid SciPy/NumPy operation-level error, and an admitted same-source physical dynamics/lensing map remain open.

## 5. Integrity and reproduction

External original 46+3 source composite SHA256: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. Protected saturation v1r1 SHA256: `99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce`. Protected six-band v1r2 SHA256: `cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77`. Source diagnostic JSON SHA256: `298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812`.

`full_h_finite_source.py` computes the six exact PL-extension mathematical root-count receipts; `verify_full_h_witness.py` independently recalculates every source-bound rational witness and coverage partition; `continuum_endpoint.py` source-locked evaluates each selected H_* endpoint pair with the prior derivative positivity gate; `assemble_full_h_bridge.py` composes all six without widening any claim; `validate_bridge_summary.py` enforces the claim firewall and adversarial mutations; and `tools/replay_source_locked.py` repeats these under the prior archives and exact source hashes. A companion six-platform public CI test is **source-free** and checks algebraic/theorem mechanics only. Protected data-dependent replay is outside public GitHub.

**What this does not prove:** true original floating-arbitrary-radius March H error or true original unmodified sampled-root implementation as a continuum root; uniqueness of selected mathematical smooth H; admissible source density or a covariant same-solution metric/Weyl provider; observational D3/D4 validation; no-particle-CDM/full-cosmology claim; or a change to canonical v0.16.39 and G4b.1b. Status stays `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED` and candidate-only.
