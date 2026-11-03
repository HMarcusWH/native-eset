# HIST-001D — Source-conditional **between-node** mathematical mass-derivative and BV quadrature audit

**Draft / NONPROMOTING · 3 November 2026.** Historical six-lens `March180` source, original 180 frozen binary64 nodes, and selected analytic **acceleration-equivalent mathematical** mass law only. No physical density, Weyl metric, Native ESET provider, D3/D4 empirical validation, or claim upgrade.

## What the new result actually tests

The previous independent real-integral Bessel certificate (PR #60) covered **the 1,080 original stored radial nodes**. A pointwise positive derivative is not a proof between nodes. This branch extends the **same independently represented mathematical functions** across the complete original finite support of each of the six lenses:

\[
  r\in[r_{\min},r_{\max}],\qquad r_{\min}=\mathrm{binary64}(0.02)\ \mathrm{kpc},\quad r_{\max}=120\ \mathrm{kpc}.
\]

For each retained original lens, the mathematical mass is

\[
M_*(r)=B(r)G(r),\quad B(r)=\frac{M_b r^2}{(r+a)^2}+M_d y^3F(y),\quad
 y=\frac{r}{2R_d},\quad F=I_0K_0-I_1K_1,
\]
\[
G(r)=\frac{\delta f(r)}{1-\delta f(r)},\qquad f(r)=\frac{r^n}{r^n+r_0^n}.
\]

All source parameters and node data are the original frozen binary64 numbers interpreted exactly as rational numbers. The continuous interpolation **defines a selected mathematical continuation**; the March source never selected its derivative as a physical stress-energy density.

## Independent second-derivative identity and analytic cell envelope

With the standard modified-Bessel recurrence and Wronskian identities,

\[
 F'(y)=2\left(I_1K_0-I_0K_1+\frac{I_1K_1}{y}\right),\qquad
 F''(y)=4F-\frac{2F'}{y}-\frac{2I_1K_1}{y^2}.
\]

The prior independent `K0,K1` **real-integral** engine gives 512-bit directed enclosures for `F,F'` and `M_*,M_*'` at each historical node. The additional implementation reconstructs the `K` components without the prior logarithmic `K`-series via

\[
K_0=\frac{I_0F+I_1/y}{I_0^2+I_1^2},\qquad
K_1=\frac{I_0/y-I_1F}{I_0^2+I_1^2}.
\]

The exact `Fraction` verifier reconstructs positive-series `I0,I1` intervals separately and independently checks the resulting `F''` boxes for consistency.

The Bessel addition identity gives

\[
 F(y)=\frac4\pi\int_0^{\pi/2} K_0(2y\sin\theta)\sin^2\theta\,d\theta.
\]

Together with the positive Laplace integral `K0(z)=∫_0^∞exp(-z cosh t)dt`, it implies the **complete-monotonicity sign sequence** `F>0`, `F'<0`, `F''>0`, `F'''<0` for positive `y`. This is an explicit mathematical identity/assumption of the proposed certificate. It allows enclosure of `F,F',F''` **throughout a real radius cell by the endpoint intervals**, not by assuming that finite sampled positivity generalizes automatically.

On each subpanel `[a,b]`, the `B,G` chain rules produce an exact interval enclosure of

\[
 M_*''=B''G+2B'G'+BG''.
\]

If `C≥sup|M_*''|` on the panel and the independently bounded endpoint derivatives are positive, then every `r` in `[a,b]` satisfies

\[
\boxed{\ M_*'(r)\ \ge\ \min\{\underline{M_*'(a)},\underline{M_*'(b)}\}-\frac{b-a}{2}C\ }.
\]

The factor `1/2` follows from applying the mean-value inequality to the *nearest endpoint*; each real radius is no farther than half the panel width from at least one endpoint. The producer adaptively bisects original cells until the lower bound is strictly positive. The report retains exact dyadic boundaries and *outward* micro-solar-mass-per-kpc lower bounds, integer upper bounds for `|M*''|`, and every added Bessel point.

The source-free tests and the protected Fraction verifier are distinct tests: the latter does not import the producing 512-bit `X` interval class, special-function method or panel-bound producer. All objects remain subject to independent external mathematical review.

## Original K180 trapezoid versus *selected* continuous projection

Let `g(r)=M_*'(r)`, `phi_A(r)=1` for `r≤A` and `1−sqrt(1−A²/r²)` otherwise, with `0≤phi≤1`, and define

\[
P_*(A)=\int_{r_0}^{r_N}g(r)\phi_A(r)\,dr,\quad
Q_{\partial M,\mathrm{src}}(A)=\sum_{j=0}^{179} w_{j,\mathrm{stored}}g(r_j)\phi_A(r_j).
\]

Write original real-mesh cell widths `H_i=r_{i+1}−r_i`, and cover each original cell by audited dyadic subpanels `p` with width `h_p`, `U_p≥sup g` and `C_p≥sup|g'|`. On any original cell, the bounded-variation trapezoid error yields

\[
|T_i-P_i| \le \frac{H_i}{2}\sum_{p\subset i}\left[U_p\bigl(\phi_A(p_\ell)-\phi_A(p_r)\bigr)
+h_p C_p\phi_A(p_\ell)\right].
\]

For each source-defined crossing aperture band `A∈[A_L,A_U]`, the first kernel difference has its maximum at `A*=median(A_L,p_left,A_U)`; the second kernel factor is at most `phi_{A_U}(p_left)`. Add the exact-rational original binary64 stored-weight-versus-ideal-trapezoid correction. This produces an **all-real aperture-band upper bound** on `|Q_{∂M,src}−P_*|`, together with a direct positive-contribution enclosure on `P_*(A)` throughout the whole band.

These finite bounds are *not scientifically sharp enough for full historical H root transport*. They are positive mathematical existence/variation certificates, not a replacement for the prior cancellation-aware 101-panel root-band comparison or a claimed small global `K180` discretization error. In particular, `Q_{∂M,src}` is a different object from the actual frozen clipped-density `Q_src` and the ideal finite-difference mass stencil. Those three objects remain distinct.

## Status and explicit nonclaims

The protected release records original 46+3 SHA, saturated parent SHA, crossing-band parent SHA, individual original six 180-node SHA locks, each new output digest, 36 source-free tests and 32 structural adverse claims. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `global_ideal_K180_vs_continuum_root_error_proved=false`, `smooth_model_physical_Weyl_provider_admitted=false`, and `useful_for_original_March_root_gap=false`.

**Not** an arbitrary-input SciPy/NumPy ulp guarantee, the original March floating source's continuous physical density, off-grid original root uniqueness, a bounded full physical Weyl field, blinded D3/D4 test, provider-normalized ESET 4.0 physical observable, independent external peer review, or a no-particle-CDM/full-cosmology result. Keep release and stacked PR draft/unmerged until independent audit and all GitHub checks complete.
