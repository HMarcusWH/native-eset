# HIST-001D — Original March180 D120 angular-seam source audit (NONPROMOTING)

**3 November 2026. Source-conditional numerical-method audit, not physical validation.** This public note and its code are stacked on the original historical finite-H and final-IEEE754 postprocessing reviews. The protected release carries the authenticated original March nested sources and the numerical receipts; **the public repository contains no March source/data archives, no 180-node arrays, and no private numerical result files**.

## Original source and explicit mathematical comparison

The original `swells_pack_v2/solv/run_setA_port_cand.py` calls `projected_disk_mass_exponential(R, Md, Rd, q_d, ntheta=120)`. `run_j2141_axisym_lens.py` constructs `theta=np.linspace(0,2*pi,120,endpoint=False)` and computes `sigma0*np.trapezoid(inner,theta)` with

\[
F(a,R)=\frac{R_d^2}{a^2}\left[1-(1+aR/R_d)e^{-aR/R_d}\right],\quad
 a=\sqrt{\cos^2\theta+\sin^2\theta/q_d^2},\quad
 \sigma_0=\frac{M_d}{2\pi q_dR_d^2}.
\]

There are **120 angular nodes but 119 trapezoid segments**. Since the final point at `theta_119` is strictly less than `2*pi`, this definition does **not** add a periodic segment connecting `theta_119` to `theta_0` in the stencil. This is a source fact, not an inference from a continuum field model.

We define one **new alternative fixed-sample periodic stencil**, leaving all 120 source-computed `a_j` exactly as their archived binary64 numbers and choosing `h=theta_1-theta_0` as an exact rational:

\[
C_{\mathrm{seam}}(R)=\frac{\sigma_0 h}{2}[F(a_{119},R)+F(a_0,R)],\qquad
D_{120,\mathrm{closed}}(R)=D_{119}(R)+C_{\mathrm{seam}}(R).
\]

This **is not the exact full-azimuth angular integral**. The frozen step and the frozen endpoint `a` values are binary64 samples; their closing arc is a prescribed *quadrature convention*, not a substitute for a trigonometric continuum integration proof. Neither the original March published root nor the original D120 code is changed.

## Exact-real positivity and whole-crossing-cell bounds

For every `R>0`, with `a>0`, `Rd>0`, `sigma0>0`, `h>0`,

\[
F(a,R)=\int_0^R s e^{-as/R_d}\,ds>0,\qquad
\partial_RF(a,R)=R e^{-aR/R_d}>0.
\]

Therefore `C_seam` is **strictly positive and increasing** in `R` throughout the original positive-radius domain. In any original source root-containing radial cell `[R_k,R_{k+1}]`, its value is between the endpoint values. `seam_math.py` encloses these source-defined endpoint values using exact rational input from archived IEEE754, an alternating Taylor bound for `exp(-x)` and exact scaling/squaring. `verify_seam.py` independently checks the outward integer micro-solar-mass bounds with **a different positive-series/reciprocal exponential inequality**, and checks the source-locked input identities.

| Historical fitted lens | Root-cell seam at left (M☉, approximate) | Seam at right (M☉, approximate) | Counterfactual returned-root shift (kpc, floating diagnostic) |
|---|---:|---:|---:|
| J0822+1828 | 112,518,955.57 | 186,597,841.11 | +0.017110834 |
| J0915+4211 | 148,357,152.83 | 239,826,916.95 | +0.006828863 |
| J0930+2855 | 105,781,813.47 | 134,551,559.63 | +0.000020134 |
| J1021+2028 | 47,220,525.27 | 116,793,737.94 | +0.004991570 |
| J1111+2234 | 435,504,077.96 | 546,849,856.98 | +0.015894568 |
| J1135+3720 | 559,129,859.49 | 830,077,689.15 | +0.020980259 |

The archived receipt contains the **strict outward integer-micro-M☉ bounds**, exact binary64 source hashes, original crossing-cell endpoints and exact-source percentage-ratio enclosures. Rounded display values in this table are for navigation only. In the twelve root-cell endpoints, the missing-seam term amounts to approximately **0.90%–3.25% of the stored original D120 disk projection**, with significant dependence on source ellipticity and radius.

## Source-replay and counterfactual definition

In the archival computational environment, the stored original source D120 projection, source circularized S, and source sampled H reproduce bit-for-bit at **all 1080 (six ×180) source radii**. All stored source shadow densities are strictly positive, so the final zero clip is inactive at these source nodes; that fact is **not** a certificate of upstream Bessel, gradient or physical density accuracy.

A deliberately **non-original, no-refit counterfactual** adds the floating seam correction to the 180 stored disk nodes, recomputes only the same source-formula `q_eff`, `np.interp(r/sqrt(q_eff),r,S0)`, and sampled H, and reapplies the same *first sampled sign-change plus linear interpolation* root-return rule. The new roots are all larger than original by the small but nonzero values shown. The counterfactual is numerically reproducible **on the tested runtime**; no interval arithmetic has been propagated through its returned floating roots, and the shift values are **not certified root-shift inequalities**.

## Explicit firewall and next gate

This patch does not establish the source's full periodic angular integral, projection/quadrature truncation or SciPy transcendental accuracy, arbitrary-radius original March H, physical shadow density, independent Weyl lensing, current Native ESET v1.7.2 provider, D3/D4 blinded generalization, or cosmology/CDM replacement. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`. The old first-sign-change sampled model and the separately defined PL finite model and selected smooth continuation remain **three different objects**. All original SHA-locked inputs remain unchanged; original fitted 6/6 is not blinded validation.

The next precise upstream source tasks are (1) nonnegative `rho_S` from original acceleration/Bessel mass-difference gradient, including rounding, clipping and proof of source-to-analytic mathematical derivative; and (2) the original `K.dot(rho)` 180 radial matrix and its finite-grid/angular systematic error, keeping the original finite support and circularization. Independently certifying the true full-angle integral is an additional, separate task.
