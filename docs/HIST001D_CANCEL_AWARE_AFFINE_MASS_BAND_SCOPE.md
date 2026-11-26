# HIST-001D: signed affine-mass cylinder projection / Peano interpolation band audit

**Source-conditional mathematical candidate, 3 November 2026. NONPROMOTING.**

This packet is about the selected historical acceleration-equivalent mathematical mass continuation `M_*(r)` on the original finite radial support **only**. It is not a physically admitted density, original March off-grid algorithm, Weyl field, current Native ESET 4.0 physical provider, or D3/D4 empirical validation. All original 46+3 files, 6×180 original binary64 arrays, prior interval certificates and six data-dependent outputs remain in one SHA-locked protected parent ZIP. The public PR contains only implementation, tests, and this scope note.

## 1. Distinct mathematical operators and purpose

Let `a=r_min`, `b=r_max=120 kpc`, let `g(r)=M_*'(r)>0` on `[a,b]` as certified conditionally by the separately audited independent real-integral Bessel/inter-node source, and define the finite cylinder kernel

\[
 \phi_A(r)=\begin{cases}1,&r\leq A,\\1-\sqrt{1-A^2/r^2},&r>A.\end{cases}
\]

`Q_deriv(A) = Σ_{i=0}^{179} w_i^stored g(r_i) φ_A(r_i)` is the **original-weight, analytic-derivative-sampled** K180 mathematical operator, distinct from the actual clipped-source `Q_source` and from the original three-point mass-difference stencil. Its selected continuous comparison is

\[
P_*(A)=\int_a^b g(r)\phi_A(r)\,dr.
\]

The previous PR #61 established rigorous but very loose BV upper bounds on `|Q_deriv-P_*|` throughout six original source-defined crossing-aperture bands. The present packet seeks **signed, two-sided, band-uniform** bounds, preserving direct cancellation rather than bounding every radial trapezoid difference separately by its variation.

## 2. Exact affine-mass quadrature identity and moving cusp

Partition `[a,b]` into the **1,344 original-source-derived real-radial panels** from the earlier all-real `M_*'` and `|M_*''|` certificate. For panel `I=[l,u]` let `s_I=[M_*(u)-M_*(l)]/(u-l)>0` and `L_I(r)=M_*(l)+s_I(r-l)`; the source mass intervals enclose the endpoints.

By integration by parts, for `e_I(r)=M_*(r)-L_I(r)` (zero at the endpoints),

\[
 \int_I M_*'(r)\phi_A(r)\,dr
 =s_I\,J_I(A)+\int_I e_I(r)[-\partial_r\phi_A(r)]\,dr,
 \quad J_I(A)=\int_l^u\phi_A(r)\,dr.
\]

This identity holds across the moving `r=A` cusp: `φ` is continuous and absolutely continuous on each compact source interval, though its derivative is integrably singular on the right side of the cusp. No differentiability of `φ` **at** `A` is asserted.

For `u>A`, set `m=max(l,A)`, `S_x=sqrt(x²-A²)`. Then the exact kernel primitive is

\[
 J_I(A)=(u-l)-(S_u-S_m)+A\arctan\left(\frac{A(S_u-S_m)}{A^2+S_mS_u}\right).
\]

For `u<=A`, `J_I=u-l`. All sqrt and arctan operations are evaluated with **outward 512-bit integer intervals**. The arctangent routine uses repeated half-angle reduction until its argument is at most `1/4`, then alternating positive/negative Taylor truncations. Thus `P_lin(A)=Σ_I s_I J_I(A)` is an explicitly signed/cancellation-retaining mathematical proxy.

## 3. Certified curvature remainder, not a BV error on g·φ

The inherited **real-panel** second-derivative enclosure `m_I^- <= M_*''(r) <= m_I^+` implies the classical exact linear-interpolation remainder

\[
 -\frac{m_I^+}{2}(r-l)(u-r)\le e_I(r)
 \le -\frac{m_I^-}{2}(r-l)(u-r).
\]

Because `-φ'_A>=0`, the remainder is bounded by the positive geometric functional

\[
 W_I(A)=\int_l^u(r-l)(u-r)[-\phi_A'(r)]\,dr.
\]

For uniform `A` in each source-defined band `[A_L,A_U]`, the implementation bounds `W` using 12 source-free geometric subsegments per radial panel. On each such subsegment it takes the exact quadratic maximum and the source-cylinder variation envelope; each variation is maximized at `A=clamp(subsegment_left,A_L,A_U)`. The minimum with the unsubdivided coarse upper is retained. This produces a source-conditional `0<=W_I(A)<=W_I^+` for *every real A in the band*, without assuming a smooth `Q'(A)` at source radius knots.

The signed remainder `P_*-P_lin` therefore lies in

\[
 \left[ -\frac12\sum_I\max(0,m_I^+)W_I^+,\quad
 +\frac12\sum_I\max(0,-m_I^-)W_I^+\right].
\]

A **separate symmetric bound** uses only the earlier independently validated `C_I>=sup|M_*''|`: `|P_*-P_lin|<=Σ_I C_I W_I^+/2`. The independent checker recomputes this symmetric envelope with a separate exact-Fraction/rational-square-root path. The tighter signed curvature enclosure inherits the previous real-panel interval algebra; it has not undergone an independent external formal proof.

## 4. Uniform complete aperture-band enclosure

For every lens, divide the exact source-derived crossing-aperture band into **128 equal exact-rational subbands**. Both `Q_deriv` (positive nodal weights and M′ intervals) and `P_lin` (all slopes positive) are nondecreasing in `A`. On each `[α,β]`, with certified source-point enclosures,

\[
 Q_{\rm deriv}(\alpha)^- -P_{\rm lin}(\beta)^+ -E^+
 \le Q_{\rm deriv}(A)-P_*(A)
 \le Q_{\rm deriv}(\beta)^+ -P_{\rm lin}(\alpha)^- -E^-,
\]

where `[E^-,E^+]` is the full-band signed interpolation remainder. No sign of `Q_deriv-P_*` is assumed. The independent checker verifies all 768 inequalities, complete exact rational coverage, and **every one of the 774 original-derivative sampled Q values** against a separately implemented Fraction/square-root enclosure. It also redoes the symmetric Peano error calculation from the 1,344 inherited curvature ceilings.

| Lens | Signed whole-band `Q_deriv-P_*` enclosure (M☉, outward integer) | Previous BV absolute upper (M☉) | Improvement factor on absolute ceiling |
|---|---:|---:|---:|
| J0822+1828 | [−393,350,355, +765,923,781] | 21,313,118,324 | 27.8× |
| J0915+4211 | [−408,864,339, +566,260,836] | 19,804,275,684 | 35.0× |
| J0930+2855 | [−1,973,365,312, +4,513,502,097] | 109,259,279,817 | 24.2× |
| J1021+2028 | [−56,174,186, +107,313,849] | 2,750,928,712 | 25.6× |
| J1111+2234 | [−191,321,384, +274,734,712] | 8,011,485,715 | 29.2× |
| J1135+3720 | [−372,106,207, +761,691,808] | 19,212,630,160 | 25.2× |

These are mathematical **proof ceilings**, not observed scatter or error bars on physical fitted mass. The intervals are still wide and **all contain zero**. The new method improves the previous conservative BV majorant but does **not** certify the sign of the radial quadrature remainder on the complete band, nor the true original March off-grid-H root displacement or selected smooth-continuum global root uniqueness. Earlier separate fixed-aperture interval results are sharper at their specific points.

## 5. Reproducibility and firewall

The protected archive contains the exact SHA-locked PR #61 scientific parent, the new source-only implementation, six signed numerical receipts, the aggregate and independent Fraction arithmetic receipts, source-free tests, and adversarial guard. The canonical original 46+3 source SHA256 remains `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.

The derivative/mass boxes are selected **mathematical** continuations. Neither `physical_provider_admitted` nor `empirical_validation` changes. No source-selected physical shadow density, same-action Weyl map, Native ESET 4.0 v1.7.2 provider, D3/D4 blinded validation, no-CDM cosmology, root-uniqueness promotion, or publication claim is supplied. Keep the GitHub PR **draft/unmerged** pending exact-head CI and independent mathematical review of the integral and panel bounds.
